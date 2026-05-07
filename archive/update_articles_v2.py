"""全記事のアフィリエイトリンクを再利用ブロック参照に置き換え（v2）"""
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

# 各記事でどのキーワードリンクをどのブロックに置換するか
# 記事ID -> [(楽天検索キーワード, ブロックID), ...]
ARTICLE_MAP = {
    409: [  # ポータブル電源
        ('Jackery ポータブル電源', 419),
        ('ポータブル電源 防災', 417),
        ('ポータブル電源 大容量', 418),
    ],
    411: [  # 非常食
        ('アルファ米 非常食', 422),
        ('非常食 おいしい 長期保存', 421),
        ('非常食 セット', 420),
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


def replace_links(content, mappings):
    """楽天アフィリエイトリンクを再利用ブロック参照に置換"""
    replaced_count = 0
    for keyword, block_id in mappings:
        url = rakuten(keyword)
        block_ref = f'<!-- wp:block {{"ref":{block_id}}} /-->'

        # URLをそのまま検索（記事内にこのURLが含まれているか）
        if url in content:
            # このURLを含むaタグ+pタグ全体を置換
            # パターン: <p style="..."><改行><a href="URL"...>テキスト</a><改行></p>
            escaped_url = re.escape(url)
            pattern = re.compile(
                r'<p[^>]*>\s*\n?\s*<a\s+href="' + escaped_url + r'"[^>]*>.*?</a>\s*\n?\s*</p>',
                re.DOTALL
            )
            new_content = pattern.sub(block_ref, content)
            if new_content != content:
                count = content.count(url) - new_content.count(url)
                replaced_count += count
                content = new_content
            else:
                # pタグなしのパターン（div内など）
                # aタグだけを置換
                pattern2 = re.compile(
                    r'<a\s+href="' + escaped_url + r'"[^>]*>.*?</a>',
                    re.DOTALL
                )
                new_content = pattern2.sub(block_ref, content)
                if new_content != content:
                    replaced_count += 1
                    content = new_content

    return content, replaced_count


def main():
    print("=" * 60)
    print("🔄 全記事のリンクを再利用ブロックに置換 (v2)")
    print("=" * 60)

    total_replaced = 0
    for post_id, mappings in ARTICLE_MAP.items():
        resp = requests.get(
            f'{WP_URL}/wp-json/wp/v2/posts/{post_id}?context=edit',
            headers=wp_auth(),
        )
        resp.raise_for_status()
        post = resp.json()
        title = post['title']['raw']
        original = post['content']['raw']

        print(f"\n📝 ID:{post_id} | {title[:45]}...")

        new_content, count = replace_links(original, mappings)

        if new_content != original:
            resp = requests.post(
                f'{WP_URL}/wp-json/wp/v2/posts/{post_id}',
                json={'content': new_content},
                headers=wp_auth(),
            )
            resp.raise_for_status()
            print(f"   ✅ {count}箇所のリンクをブロック参照に置換")
            total_replaced += count
        else:
            # デバッグ: 何が含まれているか確認
            urls_found = re.findall(r'hb\.afl\.rakuten\.co\.jp[^"]+', original)
            print(f"   ⚠️ マッチなし | 記事内の楽天URL数: {len(urls_found)}")
            if urls_found:
                for kw, bid in mappings:
                    expected_url = rakuten(kw)
                    if expected_url in original:
                        print(f"      ✓ '{kw}' のURL存在確認OK")
                    else:
                        print(f"      ✗ '{kw}' のURL見つからず")

    print(f"\n{'=' * 60}")
    print(f"🎉 完了 | 合計 {total_replaced} 箇所を置換")
    print("=" * 60)


if __name__ == '__main__':
    main()
