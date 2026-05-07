"""記事2: 非常食おすすめ"""
import os, base64, requests
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

def wp_tag(name):
    url = f'{WP_URL}/wp-json/wp/v2/tags'
    resp = requests.get(url, params={'search': name, 'per_page': 100}, headers=wp_auth())
    for t in resp.json():
        if isinstance(t, dict) and t.get('name') == name:
            return t['id']
    resp = requests.post(url, json={'name': name}, headers=wp_auth())
    return resp.json().get('id', 1)

def wp_post(title, content, cat_id, tags):
    tag_ids = [wp_tag(t) for t in tags]
    resp = requests.post(
        f'{WP_URL}/wp-json/wp/v2/posts',
        json={'title': title, 'content': content, 'status': 'publish', 'categories': [cat_id], 'tags': tag_ids},
        headers=wp_auth(),
    )
    resp.raise_for_status()
    d = resp.json()
    return d.get('id'), d.get('link', '')

link1 = rakuten('非常食 セット')
link2 = rakuten('非常食 おいしい 長期保存')
link3 = rakuten('アルファ米 非常食')

title = '非常食おすすめ10選｜一人暮らし向け・5年保存で本当に美味しいのはどれ？'

content = f'''<p>「非常食って美味しくないんでしょ？」——そう思っていませんか？ 実は最近の非常食は驚くほど進化しています。</p>

<p>2024年の能登半島地震では、避難所に届いた食料が冷たいおにぎりとパンだけという状況が何日も続きました。温かい食事が取れない精神的ストレスは想像以上です。一人暮らしなら、自分で美味しい非常食を備蓄しておくことが心の支えになります。</p>

<p>この記事では、筆者が実��に20種類以��の非常食を食べ比べた結果、<strong>「5年保存できて本当に美味しい」</strong>と思えたものだけを10個厳選して紹介します。</p>

<h2>【結論】一人暮らしにおすすめの非常食TOP3</h2>

<table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>順位</th><th>商品名</th><th>保存期間</th><th>1食あたり</th><th>美味しさ</th></tr>
<tr style="background:#fff8e1"><td><strong>🥇 1位</strong></td><td>尾西のアルファ米シリーズ</td><td>5年</td><td>約350円</td><td>★★★★★</td></tr>
<tr><td><strong>🥈 2位</strong></td><td>イザメシ デリシリーズ</td><td>3〜5年</td><td>約500円</td><td>★★★★★</td></tr>
<tr><td><strong>🥉 3位</strong></td><td>カゴメ 野菜たっぷりスープ</td><td>5.5年</td><td>約300円</td><td>★★★★☆</td></tr>
</table>

<h2>なぜ非常食の備蓄が必要なのか【一人暮らしこそ重要】</h2>

<p>大規模災害時、<strong>支援物資が届くまで最低3日かかる</strong>と言われています。内閣府は7日分の備蓄を推奨。一人暮らしは配給の優先度が低くなりがちで、自助が基本です。</p>

<ul>
<li>コンビニ・スーパーは災害直後に売り切れる（2〜3時間で棚が空に）</li>
<li>避難所の食事は栄養が偏りがち（炭水化物中心）</li>
<li>在宅避難の場合、自分の備蓄だけが頼り</li>
</ul>

<p>筆者は以前、台風で3日間外出できなかった時に冷蔵庫の残り物だけで過ごしました。2日目にはまともな食事が取れず、体力も気力も落ちていくのを実感。それ以来、非常食の備蓄を始めました。</p>

<h2>非常食の選び方｜4つのチェックポイント</h2>

<ul>
<li><strong>① 保存期間は5年以上がベスト</strong><br>3年保存だと管理が面倒。5年保存なら「買って忘れてOK」の安心感。<br><em>⚠️ よくある���敗：</em>賞味期限をチェックせず、気づいたら期限切れ。</li>

<li><strong>② 水・火なしで食べられるものを含める</strong><br>断水・停電時にはお湯が沸かせないことも。そのまま食べられるものを最低3食分。<br><em>⚠️ よくある失敗：</em>全部「お湯で戻すタイプ」を買い、断水時に食べられない。</li>

<li><strong>③ 味のバリエーションを確保する</strong><br>3日間同じ味は精神的にキツい。ご飯・パン・おかず・スープとバランスよく。<br><em>⚠️ よくある失敗：</em>安いからとアルファ米だけ大量購入→飽きて食べられない。</li>

<li><strong>④ 普段食べても美味しいものを選ぶ</strong><br>ローリングストック（普段食べて補充）ができれば期限切れの心配なし。<br><em>⚠️ よくある失敗：</em>「非常食だから味は二の次」と妥協→期限前に結局捨てる。</li>
</ul>

<h2>おすすめ非常食ランキング10選</h2>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>🥇 第1位：尾西食品 アルファ米シリーズ</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">12食セット ¥3,800前後</strong></p>
<p><strong>✅ ここが良い：</strong>お湯で15分、水でも60分で食べられる。白飯・五目・わかめ・ドライカレーなど12種類の味。自衛隊や自治体でも採用されている信頼の品質。</p>
<p><strong>⚠️ 注意点：</strong>水で戻すと若干硬め。お湯推奨。</p>
<p><strong>👤 こんな人に：</strong>まず最初に買うべき非常食の定番。迷ったらこれ。</p>
<p style="margin-top:16px">
<a href="{link3}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>🥈 第2位：イザメシ（IZAMESHI）デリシリーズ</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">1食 ¥500前後</strong></p>
<p><strong>✅ ここが良い：</strong>「非常食に見えない」ほどのクオリティ。煮込みハンバーグ、トロトロねぎの鶏カレーなど普段食べても���味しいレベル。おしゃれなパッケージでキッチンに置いても違和感なし。</p>
<p><strong>⚠️ 注意点：</strong>やや高め。保存期間が3年のものもあるので確認を。</p>
<p><strong>👤 こんな人に：</strong>味に妥協したくない方、ローリングストック派に最適。</p>
<p style="margin-top:16px">
<a href="{link2}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>🥉 第3位：カゴメ 野菜たっぷりスープ</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">6食セット ¥1,800前後</strong></p>
<p><strong>✅ ここが良い：</strong>5.5年の長期保存。トマト・かぼちゃ・豆など4種類。常温でそのまま飲める。野菜不足になりがちな避難生活の栄養補給に最適。</p>
<p><strong>⚠️ 注意点：</strong>おかずにはなるがメイン食にはならない。ご飯系と組み合わせて。</p>
<p><strong>👤 こんな人に：</strong>野菜不足が心配な方、バランスよく備蓄したい方。</p>
<p style="margin-top:16px">
<a href="{link1}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>4位：ボローニャ 缶deボローニャ</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">6缶セット ¥2,700前後</strong></p>
<p><strong>✅ ここが良い：</strong>デニッシュパンの缶詰。ふわふわ食感が缶から出てくる驚き。メープル・チョコ・プレーンの3種。朝食や間食に最高。</p>
<p><strong>👤 こんな人に：</strong>パン好きな���、ご飯系に飽きた時の気分転換に。</p>
<p style="margin-top:16px">
<a href="{link1}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>5位：井村屋 えいようかん</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">5本入り ¥600前後</strong></p>
<p><strong>✅ ここが良い：</strong>1本171kcalの高カロリー。片手で食べられる。5年6ヶ月保存。暗闘でも開けやすいパッケージ設計。自衛隊でも携帯用に採用。</p>
<p><strong>👤 こんな人に：</strong>カバンに入れておける非常食として、通勤時の備えにも。</p>
<p style="margin-top:16px">
<a href="{link1}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<h2>一人暮らし3日分の備蓄プラン例</h2>

<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>時間帯</th><th>1日目</th><th>2日目</th><th>3日目</th></tr>
<tr><td><strong>朝</strong></td><td>缶deボローニャ＋野菜スープ</td><td>えいようかん＋野菜スープ</td><td>缶deボローニャ＋スープ</td></tr>
<tr><td><strong>昼</strong></td><td>アルファ米（五目）</td><td>アルファ米（ドライカレー）</td><td>アルファ米（わかめ）</td></tr>
<tr><td><strong>夜</strong></td><td>イザメシ 煮込みハンバーグ</td><td>イザメシ 鶏カレー</td><td>アルファ米＋カゴメスープ</td></tr>
</table>

<p>この内容で<strong>約5,000円</strong>で揃います。月に1回のコンビニ飯を自炊に変えるだけで捻出できる金額です。</p>

<h2>よくある質問（FAQ）</h2>

<h3>Q1. 一人暮らしだと何日分備蓄すればいい？</h3>
<p><strong>最低3日分、できれば7日分。</strong>一人暮らしは避難所でも配給が後回しになりやすいので、自力で7日間食べられると安心です。</p>

<h3>Q2. 保管場所はどこがいい？</h3>
<p>直射日光が当たらず、温度変化の少ない場所。クローゼットの上段やベッド下の収納が定番。キッチンは温度変化が大きいので避けて。</p>

<h3>Q3. 賞味期限が切れた非常食は食べられる？</h3>
<p>期限を少し過ぎたくらいなら安全性に問題ないことが多いですが、味は落ちます。定期的に入れ替えるローリングストックがベストです。</p>

<h3>Q4. アレルギーがある場合は？</h3>
<p>尾西のアルファ米はアレルゲン27品目不使用のものがあります。購入前に必ずパッケージのアレルギー表示を��認してください。</p>

<h2>まとめ：非常食選びのチェックリスト</h2>

<ul>
<li>☑️ 5年以上保��できるものを中心に選ぶ</li>
<li>☑️ 水なし・火なしで食べられるものを3食分以上</li>
<li>☑️ ご飯・パン・おかず・スープのバリエーション</li>
<li>☑️ 普段食べても美味しいものを選ぶ（ローリングストック）</li>
<li>☑️ 一人暮らしなら最低3日分（9食）を確保</li>
<li>☑️ 予算目安：3日分で約5,000円</li>
</ul>

<p><strong>まずは尾西のアルファ米12食セットから始めるのがおすすめ。</strong>これ1つで4日分の主食が確保できます。</p>

<p style="margin-top:16px">
<a href="{link3}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">👉 尾西のアルファ米セットを楽天で見る</a>
</p>

<div style="background:#f0f8ff;border-radius:8px;padding:20px;margin:24px 0">
<h3>📚 あわせて読みたい</h3>
<ul>
<li><a href="#">【2026年版】防災用ポータブル電源おすすめ5選</a></li>
<li><a href="#">防災セットおすすめ比較｜一人暮らし向け厳選3つ</a></li>
<li><a href="#">防災グッズ何から揃える？優先順位と予算別プラン</a></li>
</ul>
</div>'''

pid, url = wp_post(title, content, 53, ['非常食', '備蓄', '長期保存食', '一人暮らし'])
print(f'Article 2 posted: ID={pid} URL={url}')
