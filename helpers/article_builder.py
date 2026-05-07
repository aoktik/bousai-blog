"""記事HTML組み立てモジュール - 構造化データ → Gutenberg互換HTML

LLM API なしで、テンプレート + データから1,500字以上の品質ある記事を生成する。
すべてのスタイルは aoktik.online のブランドカラーに統一。
"""
from typing import List, Dict, Any
from urllib.parse import quote

from helpers.internal_links import card as scene_card, link, ARTICLES, url
from helpers.a8 import a8_button, rakuten_button, amazon_button


# ブランドカラー
NAVY = '#1a365d'
ACCENT = '#e94560'
GOLD = '#ffc107'
LIGHT_BG = '#f8fafc'
INFO_BG = '#f0f9ff'
WARN_BG = '#fff3cd'
SUCCESS_BG = '#e8f5e9'


# =================================================================
# 基本ブロック
# =================================================================
def heading(text: str, level: int = 2) -> str:
    return f'<!-- wp:heading {{"level":{level}}} -->\n<h{level}>{text}</h{level}>\n<!-- /wp:heading -->'


def paragraph(text: str, align: str = None) -> str:
    if align:
        return f'<!-- wp:paragraph {{"align":"{align}"}} -->\n<p style="text-align:{align}">{text}</p>\n<!-- /wp:paragraph -->'
    return f'<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->'


def list_block(items: List[str], ordered: bool = False) -> str:
    tag = 'ol' if ordered else 'ul'
    lis = '\n'.join(f'<li>{i}</li>' for i in items)
    return f'<{tag}>\n{lis}\n</{tag}>'


def callout(text: str, kind: str = 'info', title: str = None) -> str:
    """注釈ボックス - kind: info / warn / success"""
    color = {'info': '#00a8e1', 'warn': '#ffc107', 'success': '#22c55e'}.get(kind, '#00a8e1')
    bg = {'info': INFO_BG, 'warn': WARN_BG, 'success': SUCCESS_BG}.get(kind, INFO_BG)
    title_html = f'<p style="font-weight:bold;margin:0 0 8px 0">{title}</p>' if title else ''
    return (
        f'<div style="background:{bg};border-left:4px solid {color};'
        f'padding:20px;margin:24px 0;border-radius:0 8px 8px 0">'
        f'{title_html}<p style="margin:0">{text}</p></div>'
    )


def stat_box(number: str, description: str, source: str = None) -> str:
    """統計ボックス - 数字 + 説明 + 出典"""
    src_html = f'<p style="margin:8px 0 0 0;font-size:12px;color:#888">出典: {source}</p>' if source else ''
    return (
        f'<div style="background:{LIGHT_BG};border:2px solid {NAVY};padding:24px;'
        f'margin:24px 0;border-radius:12px;text-align:center">'
        f'<p style="font-size:48px;font-weight:bold;color:{ACCENT};margin:0">{number}</p>'
        f'<p style="margin:8px 0 0 0;color:#333">{description}</p>'
        f'{src_html}</div>'
    )


# =================================================================
# 商品カード
# =================================================================
def product_card(
    name: str,
    price: str,
    good: str,
    caution: str = '',
    who: str = '',
    search_keyword: str = '',
    rating: int = 5,
) -> str:
    stars = '⭐' * rating
    caution_html = f'<p><strong>⚠️ 注意点：</strong>{caution}</p>' if caution else ''
    who_html = f'<p><strong>👤 こんな人に：</strong>{who}</p>' if who else ''
    btn = rakuten_button(search_keyword or name, '楽天市場で価格を見る') if search_keyword or name else ''

    return (
        f'<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;'
        f'margin:24px 0;background:#fafafa">'
        f'<h3 style="margin-top:0">{name}</h3>'
        f'<p style="color:#666;font-size:14px">評価：{stars}</p>'
        f'<p style="color:#666;font-size:14px">価格帯：'
        f'<strong style="color:{ACCENT};font-size:18px">{price}</strong></p>'
        f'<p><strong>✅ ここが良い：</strong>{good}</p>'
        f'{caution_html}{who_html}{btn}</div>'
    )


# =================================================================
# 比較表
# =================================================================
def comparison_table(headers: List[str], rows: List[List[str]]) -> str:
    """レスポンシブな比較表"""
    th = ''.join(f'<th style="padding:12px;text-align:left">{h}</th>' for h in headers)
    body_rows = []
    for i, row in enumerate(rows):
        bg = LIGHT_BG if i % 2 == 0 else 'transparent'
        cells = ''.join(f'<td style="padding:10px">{c}</td>' for c in row)
        body_rows.append(f'<tr style="background:{bg}">{cells}</tr>')

    return (
        f'<div style="overflow-x:auto;margin:24px 0">'
        f'<table style="width:100%;border-collapse:collapse;font-size:15px">'
        f'<thead><tr style="background:{NAVY};color:#fff">{th}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        f'</table></div>'
    )


# =================================================================
# 関連記事セクション
# =================================================================
def related_articles_section(article_ids: List[int], title: str = 'あわせて読みたい') -> str:
    if not article_ids:
        return ''
    cards = '\n'.join(scene_card(aid) for aid in article_ids if aid in ARTICLES)
    return heading(title, 2) + '\n' + cards


def action_list(items: List[Dict[str, Any]]) -> str:
    """ステップ別アクションリスト
    items: [{'step': 1, 'text': '...', 'link_id': 411}, ...]
    """
    parts = [
        f'<div style="background:{INFO_BG};border:2px solid #00a8e1;'
        f'padding:24px;margin:24px 0;border-radius:12px">'
        f'<h3 style="color:{NAVY};margin-top:0">📋 視聴後アクションリスト</h3>'
    ]
    for item in items:
        step = item.get('step', '')
        text = item.get('text', '')
        link_id = item.get('link_id')
        link_html = f' → {link(link_id)}' if link_id else ''
        parts.append(f'<p><strong>STEP {step}：</strong>{text}{link_html}</p>')
    parts.append('</div>')
    return ''.join(parts)


# =================================================================
# CTA / 結論
# =================================================================
def cta_buttons(rakuten_kw: str = None, amazon_kw: str = None, a8_key: str = None) -> str:
    parts = []
    if a8_key:
        parts.append(a8_button(a8_key))
    if amazon_kw:
        parts.append(amazon_button(amazon_kw))
    if rakuten_kw:
        parts.append(rakuten_button(rakuten_kw))
    return '\n'.join(parts)


def closing_paragraph() -> str:
    return paragraph(
        '<span style="font-size:12px;color:#999">'
        '※本記事にはアフィリエイトリンクが含まれます。リンク経由で購入いただくと、'
        '当ブログの運営費に充てさせていただきます。読者の皆様に追加費用は一切発生しません。'
        '</span>'
    )


# =================================================================
# テンプレートからの組み立て
# =================================================================
def build_article(template: Dict[str, Any]) -> str:
    """構造化テンプレート → Gutenberg HTML 完成記事

    テンプレートのスキーマ:
    {
        'title': str,
        'intro': [str, ...],         # 各要素は1段落
        'sections': [
            {
                'h2': str,
                'paragraphs': [str, ...],   # 任意
                'list': [str, ...],         # 任意
                'callout': {'text': str, 'kind': 'info|warn|success', 'title': str},  # 任意
                'stat': {'number': str, 'description': str, 'source': str},          # 任意
                'products': [product_dict, ...],     # 任意
                'comparison': {'headers': [...], 'rows': [[...], ...]},  # 任意
                'related_link': int,         # 任意。記事末尾に「→ 関連記事」リンクを追加
            },
            ...
        ],
        'related': [article_id, ...],
        'cta': {'rakuten_kw': str, 'amazon_kw': str, 'a8_key': str},
    }
    """
    parts = []

    # H1 タイトル（WordPressが title フィールドから自動でh1表示するため不要だが、念のため）

    # イントロ
    for p in template.get('intro', []):
        parts.append(paragraph(p))

    # CTA を冒頭に1個（任意）
    cta = template.get('cta', {})
    if cta.get('a8_key'):
        parts.append(a8_button(cta['a8_key']))

    # セクション
    for sec in template.get('sections', []):
        parts.append(heading(sec['h2'], 2))
        for p in sec.get('paragraphs', []):
            parts.append(paragraph(p))
        if sec.get('list'):
            parts.append(list_block(sec['list']))
        if sec.get('stat'):
            parts.append(stat_box(**sec['stat']))
        if sec.get('callout'):
            parts.append(callout(**sec['callout']))
        for prod in sec.get('products', []):
            parts.append(product_card(**prod))
        if sec.get('comparison'):
            parts.append(comparison_table(**sec['comparison']))
        if sec.get('related_link'):
            aid = sec['related_link']
            if aid in ARTICLES:
                parts.append(paragraph(f'👉 関連記事：{link(aid)}'))

    # 関連記事
    related_ids = template.get('related', [])
    if related_ids:
        parts.append(related_articles_section(related_ids))

    # CTA
    cta_html = cta_buttons(
        rakuten_kw=cta.get('rakuten_kw'),
        amazon_kw=cta.get('amazon_kw'),
        a8_key=None,  # a8 は冒頭で出したのでここでは出さない
    )
    if cta_html:
        parts.append(heading('まとめ買い・最安値チェック', 2))
        parts.append(cta_html)

    # クロージング
    parts.append(closing_paragraph())

    return '\n\n'.join(parts)


def estimate_chars(html: str) -> int:
    """HTMLからタグを除いた本文の概算文字数"""
    import re
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\s+', '', text)
    return len(text)
