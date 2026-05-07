"""再構築用 - 記事を直接WordPressに投稿するスクリプト"""
import os
import sys
import json
import base64
import requests
from urllib.parse import quote

WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']
RAKUTEN_AFF_ID = os.environ.get('RAKUTEN_AFFILIATE_ID', '')

CATEGORIES = {
    '逃げる準備': 52,
    '自宅で耐える': 53,
    '車中泊避難': 54,
    'ペット防災': 55,
    '防災の知識': 56,
}

def rakuten_url(keyword):
    encoded = quote(keyword, safe='')
    base = f"https://search.rakuten.co.jp/search/mall/{encoded}/"
    if RAKUTEN_AFF_ID:
        return f"https://hb.afl.rakuten.co.jp/hgc/{RAKUTEN_AFF_ID}/?pc={quote(base, safe='')}"
    return base

def wp_auth():
    creds = f"{WP_USER}:{WP_PASSWORD}"
    token = base64.b64encode(creds.encode()).decode()
    return {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}

def wp_get_or_create_tag(name):
    url = f"{WP_URL}/wp-json/wp/v2/tags"
    resp = requests.get(url, params={'search': name, 'per_page': 100}, headers=wp_auth())
    for tag in resp.json():
        if isinstance(tag, dict) and tag.get('name') == name:
            return tag['id']
    resp = requests.post(url, json={'name': name}, headers=wp_auth())
    return resp.json().get('id', 1)

def wp_post(title, content, category_id, tags):
    tag_ids = [wp_get_or_create_tag(t) for t in tags]
    resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        json={
            'title': title,
            'content': content,
            'status': 'publish',
            'categories': [category_id],
            'tags': tag_ids,
        },
        headers=wp_auth(),
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get('id'), data.get('link', '')

def post_article(title, content, category, tags):
    cat_id = CATEGORIES[category]
    post_id, url = wp_post(title, content, cat_id, tags)
    print(f"✅ [{category}] {title}")
    print(f"   ID={post_id} | {url}")
    return post_id, url

if __name__ == '__main__':
    # 記事データをstdinからJSON読み込み
    articles = json.load(sys.stdin)
    results = []
    for a in articles:
        pid, url = post_article(a['title'], a['content'], a['category'], a['tags'])
        results.append({'id': pid, 'title': a['title'], 'url': url})
    print(json.dumps(results, ensure_ascii=False, indent=2))
