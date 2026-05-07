"""再利用ブロックとしてアフィリエイトリンクを一元管理する"""
import os, base64, json, requests
from urllib.parse import quote

WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']
AFF_ID = os.environ.get('RAKUTEN_AFFILIATE_ID', '')

def rakuten(kw):
    encoded = quote(kw, safe='')
    base = f'https://search.rakuten.co.jp/search/mall/{encoded}/'
    if AFF_ID:
        return f'https://hb.afl.rakuten.co.jp/hgc/{AFF_ID}/?pc={quote(base, safe="")}'
    return base

def wp_auth():
    creds = f'{WP_USER}:{WP_PASSWORD}'
    token = base64.b64encode(creds.encode()).decode()
    return {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}

def create_block(title, html_content):
    """再利用ブロックを作成"""
    # Gutenbergブロック形式でラップ
    block_content = f'<!-- wp:html -->\n{html_content}\n<!-- /wp:html -->'
    resp = requests.post(
        f'{WP_URL}/wp-json/wp/v2/blocks',
        json={
            'title': title,
            'content': block_content,
            'status': 'publish',
        },
        headers=wp_auth(),
    )
    resp.raise_for_status()
    d = resp.json()
    return d['id'], d['title']['raw']

def button_html(url, text, color='#bf0000'):
    return f'<p style="margin-top:16px"><a href="{url}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:{color};color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">{text}</a></p>'

# 登録するアフィリエイトタグ一覧
AFFI_TAGS = [
    {
        'title': 'affi_ポータブル電源_防災_楽天',
        'keyword': 'ポータブル電源 防災',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_ポータブル電源_大容量_楽天',
        'keyword': 'ポータブル電源 大容量',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_Jackery_ポータブル電源_楽天',
        'keyword': 'Jackery ポータブル電源',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_非常食_セット_楽天',
        'keyword': '非常食 セット',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_非常食_おいしい_楽天',
        'keyword': '非常食 おいしい 長期保存',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_アルファ米_楽天',
        'keyword': 'アルファ米 非常食',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_防災セット_一人暮らし_楽天',
        'keyword': '防災セット 一人暮らし',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_防災リュック_楽天',
        'keyword': '防災リュック',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_防災グッズ_セット_楽天',
        'keyword': '防災グッズ セット',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_携帯トイレ_防災_楽天',
        'keyword': '携帯トイレ 防災',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_非常用トイレ_50回_楽天',
        'keyword': '非常用トイレ 50回分',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_簡易トイレ_凝固剤_楽天',
        'keyword': '簡易トイレ 凝固剤',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_防災グッズ_最低限_楽天',
        'keyword': '防災グッズ 最低限',
        'button_text': '楽天市場で防災グッズを見る →',
    },
    {
        'title': 'affi_保存水_2L_楽天',
        'keyword': '保存水 2L 長期保存',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_保存水_500ml_楽天',
        'keyword': '保存水 500ml 防災',
        'button_text': '楽天市場で詳細を見る →',
    },
    {
        'title': 'affi_備蓄水_10年_楽天',
        'keyword': '備蓄水 10年保存',
        'button_text': '楽天市場で詳細を見る →',
    },
]

def main():
    print("=" * 60)
    print("📦 アフィリエイトタグ（再利用ブロック）を一括登録")
    print("=" * 60)

    results = []
    for tag in AFFI_TAGS:
        url = rakuten(tag['keyword'])
        html = button_html(url, tag['button_text'])
        block_id, title = create_block(tag['title'], html)
        ref_code = f'<!-- wp:block {{"ref":{block_id}}} /-->'
        print(f"✅ ID:{block_id} | {title}")
        print(f"   使用コード: {ref_code}")
        results.append({
            'id': block_id,
            'title': title,
            'keyword': tag['keyword'],
            'ref': ref_code,
        })

    print("\n" + "=" * 60)
    print(f"🎉 {len(results)}個のアフィリエイトタグを登録完了")
    print("=" * 60)

    # マッピングファイルを保存
    with open('data/affi_blocks.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n📄 マッピング保存: data/affi_blocks.json")

    return results

if __name__ == '__main__':
    main()
