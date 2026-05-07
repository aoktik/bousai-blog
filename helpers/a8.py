"""A8.net アフィリエイトリンク管理"""
import os
from urllib.parse import quote

from helpers.env import load_env

load_env()


# A8 リンクと計測 img タグのペアを定義
A8_LINKS = {
    'prime_video': {
        'url': os.environ.get('A8_PRIME_VIDEO_LINK', ''),
        'img': os.environ.get('A8_PRIME_VIDEO_IMG', ''),
        'rel': 'sponsored nofollow noopener',
    },
}


def a8_button(
    key: str,
    label: str = 'Amazon Prime Videoで見る',
    color: str = '#00a8e1',
    text_color: str = '#fff',
    icon: str = '▶️',
) -> str:
    """A8アフィリエイトボタンHTML（計測imgタグ付き）を返す"""
    info = A8_LINKS.get(key)
    if not info or not info.get('url'):
        return ''  # 未設定なら出力しない

    url = info['url']
    img = info.get('img', '')
    rel = info.get('rel', 'sponsored nofollow noopener')

    btn = (
        f'<p style="text-align:center;margin:20px 0">'
        f'<a href="{url}" rel="{rel}" target="_blank" '
        f'style="display:inline-block;background:{color};color:{text_color};'
        f'padding:16px 36px;text-decoration:none;border-radius:8px;'
        f'font-weight:bold;font-size:17px;box-shadow:0 2px 8px rgba(0,0,0,0.15)">'
        f'{icon} {label}</a>'
    )
    if img:
        btn += f'<img border="0" width="1" height="1" src="{img}" alt="">'
    btn += '</p>'
    return btn


def rakuten_button(keyword: str, label: str = '楽天市場で探す') -> str:
    """楽天検索アフィリエイトボタン"""
    aff_id = os.environ.get('RAKUTEN_AFFILIATE_ID', '')
    rakuten_url = f'https://search.rakuten.co.jp/search/mall/{quote(keyword, safe="")}/'
    if aff_id:
        url = f'https://hb.afl.rakuten.co.jp/hgc/{aff_id}/?pc={quote(rakuten_url, safe="")}'
    else:
        url = rakuten_url
    return (
        f'<p style="text-align:center;margin:16px 0">'
        f'<a href="{url}" target="_blank" rel="sponsored noopener" '
        f'style="display:inline-block;background:#bf0000;color:#fff;'
        f'padding:14px 32px;text-decoration:none;border-radius:6px;'
        f'font-weight:bold;font-size:16px">🛒 {label}</a></p>'
    )


def amazon_button(keyword: str, label: str = 'Amazonで見る', tag: str = 'aoktik-22') -> str:
    """Amazon 検索リンク（アソシエイト）"""
    url = f'https://www.amazon.co.jp/s?k={quote(keyword, safe="")}&tag={tag}'
    return (
        f'<p style="text-align:center;margin:16px 0">'
        f'<a href="{url}" target="_blank" rel="sponsored noopener" '
        f'style="display:inline-block;background:#ff9900;color:#000;'
        f'padding:14px 32px;text-decoration:none;border-radius:6px;'
        f'font-weight:bold;font-size:16px">🎬 {label}</a></p>'
    )
