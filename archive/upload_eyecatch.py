"""全記事のアイキャッチ画像をWordPressにアップロードしてfeatured imageに設定"""
import os
import sys
import time
import json
import requests
from pathlib import Path
from base64 import b64encode

WP_URL = os.environ.get('WP_URL', 'https://www.aoktik.online')
WP_USER = os.environ.get('WP_USER', '')
WP_PASSWORD = os.environ.get('WP_PASSWORD', '')

credentials = b64encode(f"{WP_USER}:{WP_PASSWORD}".encode()).decode()
auth_header = {"Authorization": f"Basic {credentials}"}
json_headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json",
}

EYECATCH_DIR = Path(__file__).parent / 'data' / 'eyecatch'

ARTICLES = [
    (414, "何から揃える？優先順位と予算別プラン"),
    (409, "防災用ポータブル電源おすすめ5選"),
    (411, "非常食おすすめ10選"),
    (412, "防災セットおすすめ比較"),
    (413, "防災用簡易トイレおすすめ5選"),
    (380, "防災用保存水おすすめ5選"),
    (482, "家族で始める防災計画"),
    (483, "賃貸でもできる防災対策"),
    (484, "車載防災グッズ"),
    (485, "ペットの防災対策"),
    (486, "防災アプリおすすめ"),
]


def upload_image(post_id: int, title: str) -> int:
    img_path = EYECATCH_DIR / f"eyecatch_{post_id}.png"
    if not img_path.exists():
        print(f"  SKIP: {img_path} not found")
        return 0

    filename = f"eyecatch-{post_id}.png"
    with open(img_path, 'rb') as f:
        data = f.read()

    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "image/png",
    }

    resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        headers=headers,
        data=data,
        timeout=30,
    )

    if resp.status_code not in (200, 201):
        print(f"  ERROR upload: {resp.status_code} {resp.text[:200]}")
        return 0

    media_id = resp.json().get('id')
    print(f"  Uploaded media ID: {media_id}")
    return media_id


def set_featured_image(post_id: int, media_id: int) -> bool:
    resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
        headers=json_headers,
        json={"featured_media": media_id},
        timeout=30,
    )
    if resp.status_code == 200:
        print(f"  Featured image set for post {post_id}")
        return True

    # page の場合
    resp2 = requests.post(
        f"{WP_URL}/wp-json/wp/v2/pages/{post_id}",
        headers=json_headers,
        json={"featured_media": media_id},
        timeout=30,
    )
    if resp2.status_code == 200:
        print(f"  Featured image set for page {post_id}")
        return True

    print(f"  ERROR set featured: post={resp.status_code}, page={resp2.status_code}")
    return False


def main():
    success = 0
    for post_id, title in ARTICLES:
        print(f"\n[{post_id}] {title}")

        media_id = upload_image(post_id, title)
        if not media_id:
            continue

        time.sleep(3)

        if set_featured_image(post_id, media_id):
            success += 1

        time.sleep(3)

    print(f"\n{'='*40}")
    print(f"Complete: {success}/{len(ARTICLES)} articles updated")


if __name__ == '__main__':
    main()
