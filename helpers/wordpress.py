"""WordPress REST API 投稿モジュール"""
import os
import base64
import requests

WP_BASE = os.environ.get('WP_URL', 'https://www.aoktik.online')


def _auth() -> dict:
    creds = f"{os.environ['WP_USER']}:{os.environ['WP_PASSWORD']}"
    token = base64.b64encode(creds.encode()).decode()
    return {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
    }


def _get_or_create_term(endpoint: str, name: str) -> int:
    """カテゴリまたはタグのIDを取得（なければ新規作成）"""
    url = f"{WP_BASE}/wp-json/wp/v2/{endpoint}"
    resp = requests.get(url, params={'search': name, 'per_page': 100}, headers=_auth())
    for term in resp.json():
        if isinstance(term, dict) and term.get('name') == name:
            return term['id']
    resp = requests.post(url, json={'name': name}, headers=_auth())
    return resp.json().get('id', 1)


def post(title: str, content: str, category: str, tags: list = None, status: str = 'publish') -> str:
    """WordPressに記事を投稿し、公開URLを返す"""
    cat_id  = _get_or_create_term('categories', category)
    tag_ids = [_get_or_create_term('tags', t) for t in (tags or [])]

    resp = requests.post(
        f"{WP_BASE}/wp-json/wp/v2/posts",
        json={
            'title':      title,
            'content':    content,
            'status':     status,
            'categories': [cat_id],
            'tags':       tag_ids,
        },
        headers=_auth(),
    )
    resp.raise_for_status()
    return resp.json().get('link', '')
