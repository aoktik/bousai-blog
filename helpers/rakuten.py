"""楽天アフィリエイトリンク生成モジュール（API不使用）"""
import os
from urllib.parse import quote


def affiliate_search_url(keyword: str) -> str:
    """楽天市場の検索結果ページへのアフィリエイトURLを生成"""
    aff_id       = os.environ.get('RAKUTEN_AFFILIATE_ID', '')
    rakuten_url  = f"https://search.rakuten.co.jp/search/mall/{quote(keyword, safe='')}/"
    if aff_id:
        return f"https://hb.afl.rakuten.co.jp/hgc/{aff_id}/?pc={quote(rakuten_url, safe='')}"
    return rakuten_url


def get_search_links(keywords: list) -> dict:
    """キーワードリストから {キーワード: アフィリエイトURL} の辞書を返す"""
    return {kw: affiliate_search_url(kw) for kw in keywords}
