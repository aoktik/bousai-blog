"""WordPress REST API クライアント

すべての .py スクリプトはこのモジュール経由でWordPressと通信する。
- .env からの認証情報自動ロード
- WAF（SiteGuard）対策：JPEG 自動変換、403時の待機リトライ
- posts / pages 両対応
"""
import os
import time
import base64
import secrets
from io import BytesIO
from pathlib import Path

import requests

from helpers.env import load_env

load_env()


WP_BASE = os.environ.get('WP_URL', 'https://www.aoktik.online').rstrip('/')


def _auth_basic() -> str:
    creds = f"{os.environ['WP_USER']}:{os.environ['WP_PASSWORD']}"
    return base64.b64encode(creds.encode()).decode()


def _auth_header() -> dict:
    """ファイルアップロード用（Content-Type を含めない）"""
    return {'Authorization': f'Basic {_auth_basic()}'}


def _json_headers() -> dict:
    """JSON POST 用"""
    return {
        'Authorization': f'Basic {_auth_basic()}',
        'Content-Type': 'application/json',
    }


# =================================================================
# 既存API（後方互換）
# =================================================================
def _get_or_create_term(endpoint: str, name: str) -> int:
    url = f"{WP_BASE}/wp-json/wp/v2/{endpoint}"
    resp = requests.get(url, params={'search': name, 'per_page': 100}, headers=_json_headers())
    for term in resp.json():
        if isinstance(term, dict) and term.get('name') == name:
            return term['id']
    resp = requests.post(url, json={'name': name}, headers=_json_headers())
    return resp.json().get('id', 1)


def post(title: str, content: str, category: str, tags: list = None, status: str = 'publish') -> str:
    """新規記事を投稿し公開URLを返す（既存インターフェース維持）"""
    cat_id = _get_or_create_term('categories', category)
    tag_ids = [_get_or_create_term('tags', t) for t in (tags or [])]
    resp = requests.post(
        f"{WP_BASE}/wp-json/wp/v2/posts",
        json={
            'title': title,
            'content': content,
            'status': status,
            'categories': [cat_id],
            'tags': tag_ids,
        },
        headers=_json_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get('link', '')


# =================================================================
# 新API
# =================================================================
def get_post(post_id: int, raw: bool = True) -> dict:
    """記事/固定ページを取得。posts → pages の順で試す。

    raw=True の場合は context=edit で生コンテンツを返す（更新用途）。
    """
    params = {'context': 'edit'} if raw else {}
    for endpoint in ('posts', 'pages'):
        resp = requests.get(
            f"{WP_BASE}/wp-json/wp/v2/{endpoint}/{post_id}",
            params=params,
            headers=_auth_header(),
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
    raise ValueError(f"Post/Page {post_id} not found")


def update_post(post_id: int, **fields) -> dict:
    """記事/固定ページを更新。posts → pages の順でフォールバック。

    fields: title, content, status, featured_media, categories, tags 等
    """
    for endpoint in ('posts', 'pages'):
        resp = requests.post(
            f"{WP_BASE}/wp-json/wp/v2/{endpoint}/{post_id}",
            json=fields,
            headers=_json_headers(),
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()
    resp.raise_for_status()
    return {}


def set_featured_image(post_id: int, media_id: int) -> bool:
    """アイキャッチ画像を設定（posts/pages両対応）"""
    try:
        update_post(post_id, featured_media=media_id)
        return True
    except Exception:
        return False


def upload_image(file_path, filename: str = None, max_retries: int = 3) -> int:
    """画像をメディアライブラリにアップロード。

    WAF 対策:
    - PNG は JPEG q70 に自動変換（>30KB 時はさらに q60→q50 へ落とす）
    - ランダムなファイル名で WAF キーワード回避
    - 403時は 15秒待機して再試行

    Returns: media_id (失敗時は 0)
    """
    file_path = Path(file_path)
    data, content_type, ext = _prepare_image_for_upload(file_path)

    if filename is None:
        # WAFキーワード回避のためランダム短文字
        filename = f"img-{secrets.token_hex(4)}.{ext}"

    headers = {
        **_auth_header(),
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': content_type,
    }

    for attempt in range(max_retries):
        resp = requests.post(
            f"{WP_BASE}/wp-json/wp/v2/media",
            headers=headers,
            data=data,
            timeout=60,
        )
        if resp.status_code in (200, 201):
            return resp.json().get('id', 0)
        if resp.status_code == 403:
            # WAFブロック: さらに圧縮して再試行
            if ext == 'jpg' and attempt < max_retries - 1:
                quality = 50 - (attempt * 10)
                if quality >= 30:
                    data, _, _ = _prepare_image_for_upload(file_path, force_quality=quality)
            time.sleep(15 + attempt * 5)
            continue
        # その他のエラー
        time.sleep(5)
    return 0


def _prepare_image_for_upload(file_path: Path, force_quality: int = None) -> tuple:
    """画像を WAF 通過しやすい形に変換 → (bytes, content_type, ext)"""
    try:
        from PIL import Image
    except ImportError:
        # Pillow 未インストールでも生バイナリで送信
        return file_path.read_bytes(), 'image/png', 'png'

    img = Image.open(file_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 大きすぎる画像はリサイズ（最大 1200x1200）
    max_dim = 1200
    if img.width > max_dim or img.height > max_dim:
        img.thumbnail((max_dim, max_dim))

    quality = force_quality if force_quality else 70
    buf = BytesIO()
    img.save(buf, 'JPEG', quality=quality, optimize=True)
    data = buf.getvalue()

    # まだ大きければ品質を下げる
    if force_quality is None and len(data) > 60_000:
        buf = BytesIO()
        img.save(buf, 'JPEG', quality=55, optimize=True)
        data = buf.getvalue()

    return data, 'image/jpeg', 'jpg'
