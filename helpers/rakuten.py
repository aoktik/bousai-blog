"""楽天市場 商品検索APIモジュール"""
import os
import requests
from urllib.parse import quote

RAKUTEN_API = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'


def _affiliate_url(item_url: str) -> str:
    """楽天アフィリエイトURLを手動構築"""
    aff_id = os.environ.get('RAKUTEN_AFFILIATE_ID', '')
    if not aff_id or not item_url:
        return item_url
    return (
        f"https://hb.afl.rakuten.co.jp/hgc/{aff_id}/"
        f"?pc={quote(item_url, safe='')}&link_type=text&ut={aff_id}"
    )


def search(keyword: str, hits: int = 6) -> list:
    """楽天市場で商品を検索し、商品情報のリストを返す"""
    try:
        resp = requests.get(RAKUTEN_API, params={
            'applicationId': os.environ['RAKUTEN_APP_ID'],
            'keyword':       keyword,
            'hits':          hits,
            'sort':          '-reviewCount',
            'formatVersion': 2,
        }, timeout=30)
        resp.raise_for_status()
        items = resp.json().get('Items', [])
    except Exception as e:
        print(f'楽天API エラー: {e}')
        return []

    result = []
    for item in items:
        imgs    = item.get('mediumImageUrls', [])
        img_url = imgs[0]['imageUrl'].replace('?_ex=128x128', '?_ex=400x400') if imgs else ''
        result.append({
            'name':    item.get('itemName', '')[:80],
            'price':   item.get('itemPrice', 0),
            'url':     _affiliate_url(item.get('itemUrl', '')),
            'image':   img_url,
            'shop':    item.get('shopName', ''),
            'reviews': item.get('reviewCount', 0),
            'rating':  item.get('reviewAverage', 0.0),
            'desc':    item.get('itemCaption', '')[:200],
        })
    return result
