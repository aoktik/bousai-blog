"""記事を構造化データから生成・投稿

使い方の例:
    from scripts.new_article import publish

    article = {
        'title': '...',
        'category': '防災グッズレビュー',
        'tags': ['防災', '...'],
        'intro': [<p>段落1</p>, <p>段落2</p>],
        'sections': [
            {'h2': '...', 'body': [<p>...</p>, <ul>...</ul>]},
            ...
        ],
        'related': [414, 411],   # 内部リンク（自動でカード化）
        'a8': ['prime_video'],   # A8ボタン
        'rakuten_keyword': '防災セット',
    }
    post_id, url = publish(article)

`helpers/internal_links.py` の ARTICLES に1行追加すれば、
shell 1コマンドで シーンページにも自動反映できる。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from helpers import wordpress
from helpers.internal_links import card, link, ARTICLES
from helpers.a8 import a8_button, rakuten_button


def _build_content(article: dict) -> str:
    """構造化データから Gutenberg 互換 HTML を組み立てる"""
    parts = []

    for p_html in article.get('intro', []):
        parts.append('<!-- wp:paragraph -->')
        parts.append(p_html)
        parts.append('<!-- /wp:paragraph -->')

    # A8 ボタン（intro直後）
    for k in article.get('a8', []):
        btn = a8_button(k)
        if btn:
            parts.append(btn)

    for sec in article.get('sections', []):
        parts.append('<!-- wp:heading {"level":2} -->')
        parts.append(f'<h2>{sec["h2"]}</h2>')
        parts.append('<!-- /wp:heading -->')
        for body_html in sec.get('body', []):
            parts.append(body_html)

    related = article.get('related', [])
    if related:
        parts.append('<!-- wp:heading {"level":2} -->')
        parts.append('<h2>関連記事</h2>')
        parts.append('<!-- /wp:heading -->')
        for aid in related:
            parts.append(card(aid))

    if article.get('rakuten_keyword'):
        parts.append(rakuten_button(article['rakuten_keyword']))

    parts.append(
        '<p style="font-size:12px;color:#999">※本記事にはアフィリエイトリンクが含まれます。</p>'
    )

    return '\n\n'.join(parts)


def publish(article: dict, status: str = 'draft') -> tuple:
    """記事を投稿し (post_id, url) を返す"""
    content = _build_content(article)

    url = wordpress.post(
        title=article['title'],
        content=content,
        category=article.get('category', '防災の基礎知識'),
        tags=article.get('tags', []),
        status=status,
    )
    # post() は URL のみ返すので、ID を抽出するには別途取得
    # （ここでは URL のみ返却）
    return None, url


if __name__ == '__main__':
    # サンプル実行
    sample = {
        'title': 'テスト記事 - サンプル',
        'category': '防災の基礎知識',
        'tags': ['テスト'],
        'intro': ['<p>これはサンプル記事です。</p>'],
        'sections': [
            {'h2': '見出し1', 'body': ['<p>本文1</p>']},
        ],
        'related': [414, 411],
        'rakuten_keyword': '防災セット',
    }
    print('=== Generated content preview ===')
    print(_build_content(sample))
