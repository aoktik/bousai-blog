"""記事マスタ + シーンページマッピング

新しい記事を追加したら ARTICLES に1行追加するだけで、
内部リンク・シーンページ自動追加すべてに反映される。
"""
import os

WP_BASE = os.environ.get('WP_URL', 'https://www.aoktik.online').rstrip('/')


# シーン別固定ページ ID
SCENE_PAGES = {
    'jitaku':  508,  # 🏠 自宅で備える
    'hinan':   509,  # 🎒 避難する
    'family':  510,  # 👨‍👩‍👧‍👦 家族で備える
    'mansion': 511,  # 🏢 住まい別に備える
    'manabu':  512,  # 📚 知識で備える
    'stock':   513,  # 📦 備蓄する
}

SCENE_NAMES = {
    'jitaku':  ('🏠', '自宅で備える'),
    'hinan':   ('🎒', '避難する'),
    'family':  ('👨‍👩‍👧‍👦', '家族で備える'),
    'mansion': ('🏢', '住まい別に備える'),
    'manabu':  ('📚', '知識で備える'),
    'stock':   ('📦', '備蓄する'),
}

SCENE_HUB_PAGE_ID = 520  # シーン別ガイドのハブ


# 記事マスタ
# scenes は SCENE_PAGES のキーから複数選択可能
# desc はシーンページに表示する短い説明（省略可）
ARTICLES = {
    414: {
        'title': '防災グッズ何から揃える？優先順位と予算別プラン',
        'short': '防災グッズの優先順位と予算別プラン',
        'scenes': ['hinan', 'mansion', 'manabu'],
        'desc': '初心者向け。予算3,000円〜10,000円の3プランで最低限の備えが完了',
    },
    409: {
        'title': '防災用ポータブル電源おすすめ5選',
        'short': 'ポータブル電源おすすめ5選',
        'scenes': ['jitaku', 'mansion', 'stock'],
        'desc': '停電3日を乗り切る容量・出力・価格帯別のポータブル電源比較',
    },
    411: {
        'title': '非常食おすすめ10選',
        'short': '非常食おすすめ10選',
        'scenes': ['jitaku', 'family', 'stock'],
        'desc': '実食レビューで本当に美味しい非常食を厳選。一人暮らし向けの量で紹介',
    },
    412: {
        'title': '防災セットおすすめ比較',
        'short': '防災セットおすすめ比較',
        'scenes': ['hinan', 'mansion', 'stock'],
        'desc': '一人暮らし向け防災セット3つを徹底比較',
    },
    413: {
        'title': '防災用簡易トイレおすすめ5選',
        'short': '簡易トイレおすすめ5選',
        'scenes': ['jitaku', 'hinan', 'mansion', 'stock'],
        'desc': '凝固剤の性能・消臭力・使いやすさで比較',
    },
    380: {
        'title': '防災用保存水おすすめ5選',
        'short': '保存水おすすめ5選',
        'scenes': ['jitaku', 'family', 'stock'],
        'desc': '5年・7年・15年保存水を徹底比較。一人暮らしに必要な量も解説',
    },
    482: {
        'title': '女性のための防災グッズ選び',
        'short': '女性のための防災グッズ',
        'scenes': ['hinan', 'mansion'],
        'desc': '避難所で本当に必要なものを女性目線で厳選',
    },
    483: {
        'title': '子どもを守る防災対策',
        'short': '子どもを守る防災対策',
        'scenes': ['family', 'manabu'],
        'desc': '年齢別おすすめグッズと備蓄のコツ',
    },
    484: {
        'title': 'ペットとの防災',
        'short': 'ペットとの防災',
        'scenes': ['family'],
        'desc': '犬・猫の飼い主が備えるべきグッズと避難の知識',
    },
    485: {
        'title': 'マンション・アパートの防災対策',
        'short': 'マンション・アパートの防災',
        'scenes': ['mansion'],
        'desc': '集合住宅特有のリスクと対処法',
    },
    486: {
        'title': 'ローリングストック入門',
        'short': 'ローリングストック入門',
        'scenes': ['jitaku', 'family', 'stock', 'manabu'],
        'desc': '月+500円で始める「期限切れゼロ」の備蓄術',
    },
    504: {
        'title': 'Amazon Prime Videoで学ぶ防災',
        'short': 'Prime Videoで学ぶ防災',
        'scenes': ['family', 'manabu'],
        'desc': '震災・災害を描いた映画・ドラマ10選',
    },
}


# =================================================================
# URL / リンク生成
# =================================================================
def url(article_id: int) -> str:
    """記事の永続URLを返す"""
    return f"{WP_BASE}/?p={article_id}"


def page_url(page_id: int) -> str:
    return f"{WP_BASE}/?page_id={page_id}"


def link(article_id: int, text: str = None) -> str:
    """<a>タグHTMLを返す"""
    a = ARTICLES.get(article_id, {})
    text = text or a.get('short') or a.get('title') or f"記事{article_id}"
    return f'<a href="{url(article_id)}">{text}</a>'


def card(article_id: int, desc: str = None) -> str:
    """シーンページ用の記事カードHTMLを返す"""
    a = ARTICLES.get(article_id, {})
    title = a.get('title', f'記事{article_id}')
    desc = desc or a.get('desc', '')
    href = url(article_id)
    return f'''<div style="border:2px solid #e2e8f0;border-radius:12px;padding:20px;margin:12px 0;background:#fff">
<h3 style="margin:0 0 8px 0;font-size:17px"><a href="{href}" style="color:#1a365d;text-decoration:none">{title}</a></h3>
<p style="margin:0;font-size:14px;color:#666">{desc}</p>
<p style="margin:8px 0 0 0"><a href="{href}" style="color:#e94560;font-weight:bold;text-decoration:none;font-size:14px">記事を読む →</a></p>
</div>'''


# =================================================================
# シーンページ操作
# =================================================================
def articles_in_scene(scene_key: str) -> list:
    """指定シーンに属する記事ID一覧"""
    return [aid for aid, info in ARTICLES.items() if scene_key in info.get('scenes', [])]


def scenes_for_article(article_id: int) -> list:
    """記事が登場すべきシーンのキー一覧"""
    return ARTICLES.get(article_id, {}).get('scenes', [])


def scene_page_id(scene_key: str) -> int:
    return SCENE_PAGES[scene_key]


# 「今後追加予定」プレースホルダーの目印（update_scene_pages.py で使用）
SCENE_PLACEHOLDER_MARKER = '<div style="border:2px dashed'


if __name__ == '__main__':
    # 検証出力
    print(f"Articles: {len(ARTICLES)}")
    for scene_key, page_id in SCENE_PAGES.items():
        emoji, name = SCENE_NAMES[scene_key]
        ids = articles_in_scene(scene_key)
        print(f"  {emoji} {name} (page {page_id}): {len(ids)}記事 → {ids}")
