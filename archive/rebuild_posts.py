"""再構築用 - 優先記事を一括生成・投稿"""
import os
import sys
import json
import time
import requests
import base64

# 環境変数
WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

# カテゴリID
CATEGORIES = {
    '逃げる準備': 52,
    '自宅で耐える': 53,
    '車中泊避難': 54,
    'ペット防災': 55,
    '防災の知識': 56,
}

# 投稿する記事リスト（優先順）
ARTICLES = [
    {
        'keyword': '防災用ポータブル電源 おすすめ',
        'title_hint': '【2026年】防災用ポータブル電源おすすめ5選｜停電3日を乗り切る実力派を比較',
        'category': '自宅で耐える',
        'tags': ['ポータブル電源', '停電対策', '防災グッズ', '一人暮らし'],
        'search_kws': ['ポータブル電源 防災', 'ポータブル電源 大容量', 'Jackery ポータブル電源'],
    },
    {
        'keyword': '非常食 おすすめ 一人暮らし',
        'title_hint': '非常食おすすめ10選｜一人暮らし向け・5年保存で本当に美味しいのは？',
        'category': '自宅で耐える',
        'tags': ['非常食', '備蓄', '長期保存食', '一人暮らし'],
        'search_kws': ['非常食 セット', '非常食 おいしい', 'アルファ米 非常食'],
    },
    {
        'keyword': '防災セット 一人暮らし おすすめ',
        'title_hint': '防災セットおすすめ比較｜一人暮らし向け厳選3つを徹底レビュー',
        'category': '逃げる準備',
        'tags': ['防災セット', '防災リュック', '一人暮らし', '避難袋'],
        'search_kws': ['防災セット 一人暮らし', '防災リュック', '防災グッズ セット'],
    },
    {
        'keyword': '防災用簡易トイレ おすすめ',
        'title_hint': '防災用簡易トイレおすすめ5選｜実際に使って分かった選び方のコツ',
        'category': '自宅で耐える',
        'tags': ['簡易トイレ', '携帯トイレ', '断水対策', '防災グッズ'],
        'search_kws': ['携帯トイレ 防災', '非常用トイレ 50回分', '簡易トイレ 凝固剤'],
    },
    {
        'keyword': '防災グッズ 何から揃える',
        'title_hint': '防災グッズ何から揃える？優先順位と予算別プラン【初心者向け】',
        'category': '防災の知識',
        'tags': ['防災グッズ', '初心者', '一人暮らし', '優先順位'],
        'search_kws': ['防災グッズ 最低限', '防災 何から', '防災グッズ 一人暮らし'],
    },
]


def rakuten_search_url(keyword):
    """楽天市場検索アフィリエイトURL生成"""
    from urllib.parse import quote
    affiliate_id = '3cf10f1c.c1048eb5.3cf10f1d.5f17f763'
    encoded = quote(keyword)
    return f'https://hb.afl.rakuten.co.jp/hgc/{affiliate_id}/?pc=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F{encoded}%2F&m=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F{encoded}%2F'


def call_gemini(prompt):
    """Gemini APIで記事生成"""
    for attempt in range(3):
        resp = requests.post(
            GEMINI_URL,
            params={'key': GEMINI_API_KEY},
            json={
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {'maxOutputTokens': 8192, 'temperature': 0.7},
            },
            timeout=120,
        )
        if resp.status_code == 429:
            wait = 60 * (attempt + 1)
            print(f'  レート制限: {wait}秒待機...')
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()['candidates'][0]['content']['parts'][0]['text']
    resp.raise_for_status()
    return ''


def generate_article(article):
    """高品質な記事を生成"""
    links = {kw: rakuten_search_url(kw) for kw in article['search_kws']}
    links_text = '\n'.join([f'・{kw}: {url}' for kw, url in links.items()])

    # 他の記事への内部リンクを生成
    internal_links = []
    for other in ARTICLES:
        if other['keyword'] != article['keyword']:
            internal_links.append(f"・{other['title_hint'][:30]}（/{other['keyword'].replace(' ', '-')}/）")
    internal_links_text = '\n'.join(internal_links[:3])

    prompt = f"""あなたは防災専門のアフィリエイトブログ「防災グッズ完全ガイド」（https://www.aoktik.online）のライターです。
一人暮らしの20〜30代向けに、初心者でもわかりやすく実用的な防災情報を提供しています。

【今回の記事テーマ】
メインキーワード：「{article['keyword']}」
タイトル案：「{article['title_hint']}」

【重要：記事の差別化ポイント】
- 「実際に使ってみた」という一人称の体験談を交える（例：「筆者も実際に○○を試してみましたが〜」）
- 読者が「なぜこれが必要なのか」を過去の災害事例で具体的に伝える
- 比較表は必須。読者が一目で判断できるようにする
- 初心者が迷うポイントを先回りして解消する

【文体】
- 「〜ですよね」「〜しましょう」と語りかける柔らかいトーン
- 専門用語は（）で補足
- 段落は短め、スマホで読みやすく

【必須の記事構成】
1. <h1>{article['title_hint']}</h1>

2. <p>リード文</p>（300文字程度）
   - 読者の不安への共感
   - 過去の災害で困った具体例を1つ
   - この記事で解決できること

3. <h2>【結論】忙しい人向け・おすすめTOP3</h2>
   - 最初に結論を出す（離脱防止）
   - 簡潔な比較表

4. <h2>{article['keyword'].split()[0]}が必要な理由【実体験あり】</h2>
   - 具体的な災害事例と数字
   - 「筆者の体験」を1エピソード入れる

5. <h2>失敗しない選び方｜チェックポイント4つ</h2>
   - <ul><li>形式で4つのポイント
   - 各ポイントに「初心者がよくやる失敗」を添える

6. <h2>おすすめランキング詳細レビュー</h2>
   - 実在する人気商品を3〜5つ紹介
   - 商品カード形式（下記フォーマット）

7. <h2>実際の使用シーン・活用のコツ</h2>
   - 具体的な使い方を3パターン

8. <h2>よくある質問（FAQ）</h2>
   - Q&A形式で4問

9. <h2>まとめ：今日からできる防災の第一歩</h2>
   - チェックリスト形式
   - 最後に行動を促す一文

【楽天市場の購入リンク（必ず使用）】
{links_text}

【比較表フォーマット（必須）】
<table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>順位</th><th>商品名</th><th>価格帯</th><th>特徴</th><th>おすすめ度</th></tr>
（各商品の行、1位は背景色 #fff8e1 で強調）
</table>

【商品カードフォーマット】
<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>🥇 第1位：商品名</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">¥〇〇,〇〇〇前後</strong></p>
<p><strong>✅ ここが良い：</strong>〜</p>
<p><strong>⚠️ 注意点：</strong>〜</p>
<p><strong>👤 こんな人に：</strong>〜</p>
<p style="margin-top:16px">
<a href="[楽天リンク]" target="_blank" rel="noopener sponsored"
   style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">
楽天市場で詳細を見る →</a>
</p>
</div>

【内部リンク（記事末尾の「関連記事」セクションで使用）】
<div style="background:#f0f8ff;border-radius:8px;padding:20px;margin:24px 0">
<h3>📚 あわせて読みたい</h3>
<ul>
{internal_links_text}
</ul>
</div>
※ 上記リンクはプレースホルダーなので、リンクのhrefは「#」にしてください。

【出力ルール】
- HTMLのみ出力（マークダウン・コードブロック禁止）
- 文字数：3000〜4500文字（長めでSEO有利）
- 最初の要素は必ず<h1>から
- キーワード「{article['keyword']}」をh1・リード文・最初のh2に含める
- 商品は実在する人気商品名を記載（ブランド名+商品名）
"""
    return call_gemini(prompt)


def parse_article(text):
    """タイトルと本文を分離"""
    import re
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        text = text.strip()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.IGNORECASE | re.DOTALL)
    if m:
        title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        body = text[m.end():].strip()
    else:
        lines = text.split('\n')
        title = re.sub(r'^#+\s*', '', lines[0]).strip()
        body = '\n'.join(lines[1:]).strip()
    return title, body


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


def main():
    print("=" * 60)
    print("🔨 サイト再構築 - 優先記事の生成・投稿")
    print("=" * 60)

    results = []
    for i, article in enumerate(ARTICLES, 1):
        print(f"\n[{i}/{len(ARTICLES)}] {article['title_hint'][:40]}...")
        print(f"  カテゴリ: {article['category']}")

        # 記事生成
        print("  📝 記事生成中...")
        raw = generate_article(article)
        title, content = parse_article(raw)
        print(f"  タイトル: {title}")
        print(f"  文字数: {len(content)}文字")

        # 投稿
        print("  📤 WordPress投稿中...")
        cat_id = CATEGORIES[article['category']]
        post_id, url = wp_post(title, content, cat_id, article['tags'])
        print(f"  ✅ 投稿完了: ID={post_id}")
        print(f"     URL: {url}")

        results.append({'title': title, 'url': url, 'id': post_id})

        # レート制限対策
        if i < len(ARTICLES):
            print("  ⏳ 5秒待機...")
            time.sleep(5)

    print("\n" + "=" * 60)
    print("🎉 全記事の投稿完了!")
    print("=" * 60)
    for r in results:
        print(f"  • {r['title']}")
        print(f"    {r['url']}")

    return results


if __name__ == '__main__':
    main()
