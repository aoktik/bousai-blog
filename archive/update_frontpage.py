"""トップページ(固定ページID:371)をカテゴリ導線型に改修"""
import os, base64, requests
from urllib.parse import quote, unquote

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

# 記事URL
url_portable = 'https://www.aoktik.online/%e3%80%902026%e5%b9%b4%e7%89%88%e3%80%91%e9%98%b2%e7%81%bd%e7%94%a8%e3%83%9d%e3%83%bc%e3%82%bf%e3%83%96%e3%83%ab%e9%9b%bb%e6%ba%90%e3%81%8a%e3%81%99%e3%81%99%e3%82%815%e9%81%b8%ef%bd%9c%e5%81%9c/'
url_food = 'https://www.aoktik.online/%e9%9d%9e%e5%b8%b8%e9%a3%9f%e3%81%8a%e3%81%99%e3%81%99%e3%82%8110%e9%81%b8%ef%bd%9c%e4%b8%80%e4%ba%ba%e6%9a%ae%e3%82%89%e3%81%97%e5%90%91%e3%81%91%e3%83%bb5%e5%b9%b4%e4%bf%9d%e5%ad%98%e3%81%a7/'
url_set = 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e3%82%bb%e3%83%83%e3%83%88%e3%81%8a%e3%81%99%e3%81%99%e3%82%81%e6%af%94%e8%bc%83%ef%bd%9c%e4%b8%80%e4%ba%ba%e6%9a%ae%e3%82%89%e3%81%97%e5%90%91%e3%81%91%e5%8e%b3%e9%81%b83%e3%81%a4/'
url_toilet = 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e7%94%a8%e7%b0%a1%e6%98%93%e3%83%88%e3%82%a4%e3%83%ac%e3%81%8a%e3%81%99%e3%81%99%e3%82%815%e9%81%b8%ef%bd%9c%e5%ae%9f%e9%9a%9b%e3%81%ab%e4%bd%bf%e3%81%a3%e3%81%a6%e5%88%86%e3%81%8b/'
url_start = 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e3%82%b0%e3%83%83%e3%82%ba%e4%bd%95%e3%81%8b%e3%82%89%e6%8f%83%e3%81%88%e3%82%8b%ef%bc%9f%e5%84%aa%e5%85%88%e9%a0%86%e4%bd%8d%e3%81%a8%e4%ba%88%e7%ae%97%e5%88%a5%e3%83%97%e3%83%a9/'
url_water = 'https://www.aoktik.online/%e7%81%bd%e5%ae%b3%e7%94%a8%e4%bf%9d%e5%ad%98%e6%b0%b4%e3%81%ae%e9%81%b8%e3%81%b3%e6%96%b9%e3%81%a8%e3%81%8a%e3%81%99%e3%81%99%e3%82%81%e5%95%86%e5%93%81/'

link_set = rakuten('防災セット 一人暮らし')

new_title = '防災グッズ完全ガイド｜一人暮らしのための備えと対策'

new_content = f'''
<div style="text-align:center;padding:50px 20px;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);border-radius:16px;margin-bottom:40px">
<h1 style="color:#fff;font-size:2em;margin-bottom:12px">一人暮らしの防災、<br>何から始める？</h1>
<p style="color:rgba(255,255,255,0.8);font-size:1.1em;margin-bottom:24px">初めてでも迷わない。シーン別の防災準備ガイド</p>
<a href="{url_start}" style="display:inline-block;background:#e94560;color:#fff;padding:14px 32px;border-radius:25px;font-weight:bold;font-size:1em;text-decoration:none">何から揃える？ 優先順位を見る →</a>
</div>

<h2 style="text-align:center;margin-bottom:8px">シーン別に備える</h2>
<p style="text-align:center;color:#666;margin-bottom:30px">あなたに必要な防災準備は、生活スタイルによって違います</p>

<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:40px">

<div style="border:2px solid #eee;border-radius:12px;padding:25px;text-align:center">
<p style="font-size:2.5em;margin-bottom:8px">🎒</p>
<h3 style="color:#0f3460;margin-bottom:8px">逃げる準備</h3>
<p style="font-size:0.9em;color:#666;margin-bottom:16px">非常用持ち出し袋の中身を完全解説。最低限これだけは。</p>
<a href="{url_set}" style="color:#e94560;font-weight:bold;text-decoration:none">おすすめ防災セット →</a>
</div>

<div style="border:2px solid #eee;border-radius:12px;padding:25px;text-align:center">
<p style="font-size:2.5em;margin-bottom:8px">🏠</p>
<h3 style="color:#0f3460;margin-bottom:8px">自宅で耐える</h3>
<p style="font-size:0.9em;color:#666;margin-bottom:16px">在宅避難3日間を乗り切る備蓄品リスト。水・食料・電源・トイレ。</p>
<a href="{url_water}" style="color:#e94560;font-weight:bold;text-decoration:none">備蓄水の選び方 →</a>
</div>

<div style="border:2px solid #eee;border-radius:12px;padding:25px;text-align:center">
<p style="font-size:2.5em;margin-bottom:8px">⚡</p>
<h3 style="color:#0f3460;margin-bottom:8px">停電に備える</h3>
<p style="font-size:0.9em;color:#666;margin-bottom:16px">停電3日を乗り切るポータブル電源。スマホも家電も使える。</p>
<a href="{url_portable}" style="color:#e94560;font-weight:bold;text-decoration:none">ポータブル電源おすすめ →</a>
</div>

<div style="border:2px solid #eee;border-radius:12px;padding:25px;text-align:center">
<p style="font-size:2.5em;margin-bottom:8px">🚽</p>
<h3 style="color:#0f3460;margin-bottom:8px">トイレ問題を解決</h3>
<p style="font-size:0.9em;color:#666;margin-bottom:16px">断水時に最も困るのがトイレ。簡易トイレの備蓄は必須です。</p>
<a href="{url_toilet}" style="color:#e94560;font-weight:bold;text-decoration:none">簡易トイレおすすめ →</a>
</div>

<div style="border:2px solid #eee;border-radius:12px;padding:25px;text-align:center">
<p style="font-size:2.5em;margin-bottom:8px">🍚</p>
<h3 style="color:#0f3460;margin-bottom:8px">非常食を備える</h3>
<p style="font-size:0.9em;color:#666;margin-bottom:16px">5年保存で本当に美味しい非常食だけを厳選。もう不味くない。</p>
<a href="{url_food}" style="color:#e94560;font-weight:bold;text-decoration:none">非常食おすすめ10選 →</a>
</div>

<div style="border:2px solid #eee;border-radius:12px;padding:25px;text-align:center">
<p style="font-size:2.5em;margin-bottom:8px">💡</p>
<h3 style="color:#0f3460;margin-bottom:8px">防災の知識</h3>
<p style="font-size:0.9em;color:#666;margin-bottom:16px">何から買う？いくらかかる？初心者の疑問にすべて答えます。</p>
<a href="{url_start}" style="color:#e94560;font-weight:bold;text-decoration:none">何から揃える？ →</a>
</div>

</div>

<div style="background:#fff8e1;border-radius:12px;padding:30px;margin-bottom:40px">
<h2 style="text-align:center;margin-bottom:20px">📖 まず読むべき記事 TOP3</h2>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">

<div style="background:#fff;border-radius:8px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
<span style="background:#e94560;color:#fff;font-size:0.75em;padding:3px 8px;border-radius:4px">人気No.1</span>
<h4 style="margin-top:10px;font-size:0.95em"><a href="{url_start}" style="color:#1a1a2e;text-decoration:none">防災グッズ何から揃える？<br>優先順位と予算別プラン</a></h4>
</div>

<div style="background:#fff;border-radius:8px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
<span style="background:#0f3460;color:#fff;font-size:0.75em;padding:3px 8px;border-radius:4px">高単価</span>
<h4 style="margin-top:10px;font-size:0.95em"><a href="{url_portable}" style="color:#1a1a2e;text-decoration:none">防災用ポータブル電源<br>おすすめ5選【2026年版】</a></h4>
</div>

<div style="background:#fff;border-radius:8px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
<span style="background:#28a745;color:#fff;font-size:0.75em;padding:3px 8px;border-radius:4px">コスパ◎</span>
<h4 style="margin-top:10px;font-size:0.95em"><a href="{url_set}" style="color:#1a1a2e;text-decoration:none">防災セットおすすめ比較<br>一人暮らし向け厳選3つ</a></h4>
</div>

</div>
</div>

<div style="background:#f8f9fa;border-radius:12px;padding:30px;margin-bottom:40px">
<h2 style="text-align:center;margin-bottom:8px">🛒 予算別・おすすめスタートプラン</h2>
<p style="text-align:center;color:#666;margin-bottom:24px">完璧を目指さなくてOK。今日1つ買うだけで昨日より安全に。</p>

<table border="1" cellpadding="12" style="border-collapse:collapse;width:100%;font-size:14px;background:#fff">
<tr style="background:#2c3e50;color:#fff"><th>予算</th><th>買うもの</th><th>備えレベル</th></tr>
<tr style="background:#fff8e1"><td><strong>¥5,000</strong></td><td>水2L×6本 + 簡易トイレ15回 + モバイルバッテリー</td><td>⭐ 最低限クリア</td></tr>
<tr><td><strong>¥15,000</strong></td><td>上記 + 非常食3日分 + ラジオライト + カセットコンロ</td><td>⭐⭐ しっかり備え</td></tr>
<tr><td><strong>¥50,000</strong></td><td>上記 + 防災セット + ポータブル電源</td><td>⭐⭐⭐ 万全</td></tr>
</table>
</div>

<div style="text-align:center;padding:40px 20px;background:linear-gradient(135deg,#0f3460,#1a1a2e);border-radius:12px;margin-bottom:40px">
<h2 style="color:#fff;margin-bottom:12px">まず何から買えばいい？</h2>
<p style="color:rgba(255,255,255,0.8);margin-bottom:20px">予算5,000円から始める防災。優先順位つきで解説します。</p>
<a href="{url_start}" style="display:inline-block;background:#e94560;color:#fff;padding:14px 32px;border-radius:25px;font-weight:bold;font-size:1em;text-decoration:none">予算別おすすめプランを見る →</a>
</div>

<div style="background:#f0f8ff;border-radius:12px;padding:30px">
<h2 style="margin-bottom:16px">📋 このサイトについて</h2>
<p>「防災グッズ完全ガイド」は、一人暮らしの20〜30代に向けた防災情報サイトです。</p>
<p>「何を買えばいいか分からない」「面倒で後回しにしてしまう」——そんな方のために、本当に必要なものだけを、予算と優先順位をつけて紹介しています。</p>
<p>すべての記事で実際に商品を比較検証し、一人暮らしの視点で正直にレビューしています。</p>
</div>
'''

resp = requests.post(
    f'{WP_URL}/wp-json/wp/v2/pages/371',
    json={
        'title': new_title,
        'content': new_content,
    },
    headers=wp_auth(),
)
resp.raise_for_status()
d = resp.json()
print(f"✅ トップページ更新完了")
print(f"   タイトル: {d['title']['rendered']}")
print(f"   URL: {unquote(d.get('link', ''))}")
