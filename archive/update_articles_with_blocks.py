"""全記事のアフィリエイトリンクを再利用ブロック参照に置き換える"""
import os, base64, json, re, requests
from urllib.parse import quote

WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']
AFF_ID = os.environ.get('RAKUTEN_AFFILIATE_ID', '')

def wp_auth():
    creds = f'{WP_USER}:{WP_PASSWORD}'
    token = base64.b64encode(creds.encode()).decode()
    return {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}

def rakuten(kw):
    encoded = quote(kw, safe='')
    base = f'https://search.rakuten.co.jp/search/mall/{encoded}/'
    if AFF_ID:
        return f'https://hb.afl.rakuten.co.jp/hgc/{AFF_ID}/?pc={quote(base, safe="")}'
    return base

# マッピング読み込み
with open('data/affi_blocks.json', 'r', encoding='utf-8') as f:
    affi_blocks = json.load(f)

# キーワード→ブロックIDマッピング
keyword_to_block = {b['keyword']: b['id'] for b in affi_blocks}

# 各記事で使うブロックのマッピング
ARTICLE_BLOCK_MAP = {
    # 記事ID: [(置換対象キーワード, ブロックID), ...]
    409: [  # ポータブル電源
        ('ポータブル電源 防災', 417),
        ('ポータブル電源 大容量', 418),
        ('Jackery ポータブル電源', 419),
    ],
    411: [  # 非常食
        ('非常食 セット', 420),
        ('非常食 おいしい 長期保存', 421),
        ('アルファ米 非常食', 422),
    ],
    412: [  # 防災セット
        ('防災セット 一人暮らし', 423),
        ('防災リュック', 424),
        ('防災グッズ セット', 425),
    ],
    413: [  # 簡易トイレ
        ('携帯トイレ 防災', 426),
        ('非常用トイレ 50回分', 427),
        ('簡易トイレ 凝固剤', 428),
    ],
    414: [  # 何から揃える
        ('防災グッズ 最低限', 429),
        ('防災セット 一人暮らし', 423),
        ('非常食 セット', 420),
    ],
    380: [  # 保存水
        ('保存水 2L 長期保存', 430),
        ('保存水 500ml 防災', 431),
        ('備蓄水 10年保存', 432),
    ],
}

def replace_links_with_blocks(content, block_mappings):
    """記事内のアフィリエイトリンクを再利用ブロック参照に置き換え"""
    for keyword, block_id in block_mappings:
        url = rakuten(keyword)
        # URLの一部をエスケープした形でもマッチするように
        # aタグ全体を含むpタグを検索して置き換え
        # パターン: <p style="margin-top:16px">...<a href="URL"...>テキスト</a>...</p>
        # または: <a href="URL"...style="...background:#bf0000..."...>テキスト</a> を含むブロック

        # 楽天URLの一部をパターンとして使う
        url_part = quote(keyword, safe='')

        # パターン1: <p>タグに包まれたボタンリンク
        pattern1 = re.compile(
            r'<p[^>]*>\s*<a\s+href="[^"]*' + re.escape(url_part) + r'[^"]*"[^>]*>.*?</a>\s*</p>',
            re.DOTALL | re.IGNORECASE
        )

        # パターン2: 商品カード内のリンク（divの中のaタグ）
        pattern2 = re.compile(
            r'<a\s+href="[^"]*' + re.escape(url_part) + r'[^"]*"[^>]*style="[^"]*background[^"]*"[^>]*>.*?</a>',
            re.DOTALL | re.IGNORECASE
        )

        block_ref = f'<!-- wp:block {{"ref":{block_id}}} /-->'

        # パターン1で置換
        new_content = pattern1.sub(block_ref, content)
        if new_content != content:
            content = new_content
            continue

        # パターン2で置換（pタグなしのケース）
        pattern2_with_p = re.compile(
            r'<p[^>]*>[\s\n]*<a\s+href="[^"]*' + re.escape(url_part) + r'[^"]*"[^>]*>.*?</a>[\s\n]*</p>',
            re.DOTALL | re.IGNORECASE
        )
        new_content = pattern2_with_p.sub(block_ref, content)
        if new_content != content:
            content = new_content
            continue

        # パターン3: hb.afl.rakuten.co.jp のIDで検索
        pattern3 = re.compile(
            r'<p[^>]*>\s*<a\s+href="https://hb\.afl\.rakuten\.co\.jp/hgc/' + re.escape(AFF_ID) + r'/\?pc=[^"]*' + re.escape(url_part) + r'[^"]*"[^>]*>.*?</a>\s*</p>',
            re.DOTALL | re.IGNORECASE
        )
        new_content = pattern3.sub(block_ref, content)
        if new_content != content:
            content = new_content

    return content


def main():
    print("=" * 60)
    print("🔄 全記事のアフィリエイトリンクを再利用ブロックに置換")
    print("=" * 60)

    for post_id, mappings in ARTICLE_BLOCK_MAP.items():
        # 記事取得（context=editでrawコンテンツを取得）
        resp = requests.get(
            f'{WP_URL}/wp-json/wp/v2/posts/{post_id}?context=edit',
            headers=wp_auth(),
        )
        resp.raise_for_status()
        post = resp.json()
        title = post['title']['rendered']
        original_content = post['content']['raw']

        print(f"\n📝 ID:{post_id} | {title[:40]}...")

        # リンク置換
        new_content = replace_links_with_blocks(original_content, mappings)

        # 変更があれば更新
        replacements = new_content.count('<!-- wp:block')
        if new_content != original_content:
            resp = requests.post(
                f'{WP_URL}/wp-json/wp/v2/posts/{post_id}',
                json={'content': new_content},
                headers=wp_auth(),
            )
            resp.raise_for_status()
            print(f"   ✅ 更新完了 | ブロック参照: {replacements}箇所")
        else:
            print(f"   ⚠️ パターンマッチなし（手動確認が必要かも）")

    print("\n" + "=" * 60)
    print("🎉 全記事の更新完了")
    print("=" * 60)


if __name__ == '__main__':
    main()
