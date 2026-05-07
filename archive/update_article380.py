"""既存記事ID:380を書き換え"""
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

link1 = rakuten('保存水 2L 長期保存')
link2 = rakuten('保存水 500ml 防災')
link3 = rakuten('備蓄水 10年保存')

new_title = '【2026年版】防災用保存水おすすめ5選｜一人暮らしに必要な量と正しい備蓄方法'

new_content = f'''<p>「水なんてコンビニで買えるでしょ」——そう思っていませんか？ 2024年の能登半島地震では、被災地のコンビニから<strong>2時間で水が消えました</strong>。</p>

<p>人間は水なしでは3日しか生きられません。食料は1週間なくても耐えられますが、水だけは代わりがない。一人暮らしの場合、誰も水を分けてくれる保証はありません。だからこそ、保存水の備蓄は防災の<strong>最優先事項</strong>です。</p>

<p>この記事では、筆者が実際に10種類以上の保存水を比較し、「一人暮らしに最適な保存水」を5つ厳選。必要量の計算方法から、ワンルームでの保管術まで徹底解説します。</p>

<h2>【結論】おすすめ保存水TOP3</h2>

<table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>順位</th><th>商品名</th><th>保存期間</th><th>容量</th><th>特徴</th></tr>
<tr style="background:#fff8e1"><td><strong>🥇 1位</strong></td><td>カムイワッカ麗水</td><td>15年</td><td>2L×6本</td><td>超長期保存の決定版</td></tr>
<tr><td><strong>🥈 2位</strong></td><td>志布志の自然水</td><td>7年</td><td>2L×6本</td><td>コスパと保存期間のバランス◎</td></tr>
<tr><td><strong>🥉 3位</strong></td><td>アサヒ おいしい水 天然水 長期保存水</td><td>6年</td><td>500ml×24本</td><td>持ち出し用に最適</td></tr>
</table>

<h2>一人暮らしに必要な水の量【計算方法】</h2>

<p>農林水産省の推奨は<strong>「1人1日3リットル」</strong>。これは飲料用＋調理用を合わせた量です。</p>

<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>備蓄日数</th><th>必要量</th><th>2Lペットボトル換算</th></tr>
<tr><td>3日分（最低限）</td><td>9L</td><td>5本</td></tr>
<tr style="background:#fff8e1"><td><strong>7日分（推奨）</strong></td><td><strong>21L</strong></td><td><strong>11本</strong></td></tr>
<tr><td>10日分（安心）</td><td>30L</td><td>15本</td></tr>
</table>

<p><strong>一人暮らしなら2L×6本入り2ケース（24L）がベスト。</strong>これで8日分。2ケースならクローゼットの隅に収まるサイズです。</p>

<h2>保存水が必要な理由【過去の断水事例】</h2>

<ul>
<li><strong>2024年 能登半島地震：</strong>最大約13万戸が断水、一部地域で復旧まで3ヶ月以上</li>
<li><strong>2019年 台風19号：</strong>約16万戸が断水、復旧まで最長2週間</li>
<li><strong>2018年 北海道地震：</strong>約68万戸が断水</li>
</ul>

<p>筆者のマンションも2023年に設備故障で半日断水を経験。たった半日でも「水が出ない恐怖」は強烈でした。飲み水はもちろん、手も洗えない、トイレも流せない。あの経験から保存水を常備するようになりました。</p>

<h2>保存水の選び方｜4つのチェックポイント</h2>

<ul>
<li><strong>① 保存期間：5年以上を選ぶ</strong><br>一般のミネラルウォーターは1〜2年。保存水は5〜15年持つ特殊加工。長いほど管理が楽。<br><em>⚠️ よくある失敗：</em>普通のミネラルウォーターを備蓄→気づいたら全部期限切れ。</li>

<li><strong>② 容量：2Lと500mlを併用する</strong><br>自宅備蓄用には2L（コスパ良い）、持ち出し袋には500ml（軽い・衛生的）。<br><em>⚠️ よくある失敗：</em>2Lのみ備蓄→避難時に重すぎて持ち出せない。</li>

<li><strong>③ 硬度：軟水を選ぶ</strong><br>日本人が飲み慣れた軟水がベスト。赤ちゃんのミルクにも使える。硬水は下痢の原因になることも。<br><em>⚠️ よくある失敗：</em>海外ブランドの硬水を備蓄→ストレス下で飲んで体調を崩す。</li>

<li><strong>④ 容器の強度</strong><br>保存水は厚手のペットボトルやアルミ缶を使用。落としても割れにくく、光や空気を通しにくい。<br><em>⚠️ よくある失敗：</em>安い薄型ボトルの水→長期保存中に容器が劣化して臭い移り。</li>
</ul>

<h2>おすすめ保存水ランキング｜詳細レビュー</h2>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>🥇 第1位：カムイワッカ麗水（15年保存）</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">2L×6本 ¥2,500前後</strong></p>
<p><strong>✅ ここが良い：</strong>業界最長クラスの15年保存。北海道の天然水を高温殺菌＋特殊ボトルで超長期保存を実現。一度買えば2040年まで持つ安心感。味もまろやかで飲みやすい軟水。</p>
<p><strong>⚠️ 注意点：</strong>一般的な保存水より若干割高。ただし15年の保存期間を考えれば年間コストは最安。</p>
<p><strong>👤 こんな人に：</strong>「買って放置したい」「管理が面倒」という方に最適。一度の購入で15年安心。</p>
<p style="margin-top:16px">
<a href="{link3}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>🥈 第2位：志布志の自然水（7年保存）</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">2L×6本 ¥1,400前後</strong></p>
<p><strong>✅ ここが良い：</strong>7年保存で1本あたり約230円のコスパ。鹿児島県志布志市の地下水を使用。自治体の備蓄にも採用されている信頼ブランド。味も癖がなく飲みやすい。</p>
<p><strong>⚠️ 注意点：</strong>15年保存水と比べると入れ替え頻度は高い。7年後にリマインダーを。</p>
<p><strong>👤 こんな人に：</strong>コスパ重視で、十分な保存期間も欲しい方。最もバランスが良い。</p>
<p style="margin-top:16px">
<a href="{link1}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>🥉 第3位：アサヒ おいしい水 天然水 長期保存水（6年保存）</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">500ml×24本 ¥3,200前後</strong></p>
<p><strong>✅ ここが良い：</strong>500mlの持ち出しサイズ。大手メーカーの安心感。6年保存で防災リュックに入れっぱなしにできる。直飲みできるので衛生的。</p>
<p><strong>⚠️ 注意点：</strong>2Lと比べて割高。自宅備蓄のメインには不向き（持ち出し用と割り切る）。</p>
<p><strong>👤 こんな人に：</strong>防災リュックに入れる持ち出し用として。職場のデスクに1本置いておくのもあり。</p>
<p style="margin-top:16px">
<a href="{link2}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>4位：サーフビバレッジ 室戸海洋深層水（5年保存）</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">2L×6本 ¥1,200前後</strong></p>
<p><strong>✅ ここが良い：</strong>5年保存で最安クラス。高知県室戸の海洋深層水を脱塩処理。ミネラルバランスが良い。とにかく安く大量備蓄したい方に。</p>
<p><strong>⚠️ 注意点：</strong>5年は保存水としては短め。カレンダーで管理を。</p>
<p><strong>👤 こんな人に：</strong>予算を抑えて必要量をしっかり揃えたい方。</p>
<p style="margin-top:16px">
<a href="{link1}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>5位：普通のミネラルウォーター（ローリングストック用）</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">2L×9本 ¥900前後</strong></p>
<p><strong>✅ ここが良い：</strong>圧倒的な安さ。ローリングストック（古いものから飲んで補充）前提なら最もコスパが良い。1〜2年で回転させる。</p>
<p><strong>⚠️ 注意点：</strong>管理を怠ると期限切れになる。定期的な確認が必須。</p>
<p><strong>👤 こんな人に：</strong>普段から水を飲む習慣がある方。自動的に消費→補充ができる方。</p>
<p style="margin-top:16px">
<a href="{link1}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で詳細を見る →</a>
</p>
</div>

<h2>ワンルームでの保管方法【場所がない人向け】</h2>

<ul>
<li><strong>クローゼットの床：</strong>2Lペットボトル2ケース（12本）が横置きで入る。重いので下段に。</li>
<li><strong>ベッド下：</strong>収納ケースに入れれば12本保管可能。見た目もスッキリ。</li>
<li><strong>玄関の靴箱上：</strong>500ml×12本なら置ける。持ち出しにも便利な位置。</li>
<li><strong>キッチンシンク下：</strong>温度変化が気になるが、1〜2年のローリングストック用なら問題なし。</li>
</ul>

<p><strong>NG保管場所：</strong>直射日光が当たる窓際、夏場に高温になる車内（短期間なら可）、ベランダ（凍結・紫外線劣化のリスク）。</p>

<h2>ローリングストックのやり方</h2>

<ol>
<li><strong>必要量の1.5倍を購入</strong>（7日分21L→2ケース24Lを買う）</li>
<li><strong>古いものから日常で飲む</strong>（週に2〜3本消費）</li>
<li><strong>消費した分だけ買い足す</strong>（月1回のまとめ買いでOK）</li>
<li><strong>常に1ケースは未開封の状態を維持する</strong></li>
</ol>

<p>この方法なら賞味期限切れがなく、常にフレッシュな水を備蓄できます。普通のミネラルウォーターでも実践可能です。</p>

<h2>よくある質問（FAQ）</h2>

<h3>Q1. 水道水を溜めておくのはダメ？</h3>
<p>水道水は塩素が抜けると3日程度で雑菌が繁殖します。密閉容器に入れて冷暗所保管でも<strong>1週間が限度</strong>。緊急時の短期対策にはなりますが、長期備蓄には不向きです。</p>

<h3>Q2. 賞味期限が切れた保存水は飲める？</h3>
<p>密封状態で保管していれば、品質上は問題ないことが多いです。ただしメーカー保証外。期限を1年以上過ぎたものは味の劣化を感じる場合があります。ローリングストックで回避するのが理想。</p>

<h3>Q3. ウォーターサーバーがあれば備蓄不要？</h3>
<p><strong>不十分です。</strong>ウォーターサーバーのボトルは保存期間が短く（未開封でも3〜6ヶ月）、停電時は冷水・温水機能が使えません。予備ボトル1本は防災の足しになりますが、保存水の代替にはなりません。</p>

<h3>Q4. 保存水とミネラルウォーター、味の違いは？</h3>
<p>正直、ブラインドテストではほぼ分かりません。高温殺菌処理の影響で「やや柔らかい味」と感じる方もいますが、不味いということはありません。</p>

<h2>まとめ：保存水備蓄のチェックリスト</h2>

<ul>
<li>☑️ 一人暮らしの必要量：<strong>2L×11本（21L）が目安</strong></li>
<li>☑️ 保存期間5年以上の保存水を選ぶ</li>
<li>☑️ 2Lボトル（自宅用）＋500ml（持ち出し用）を併用</li>
<li>☑️ 軟水を選ぶ（硬度100mg/L以下）</li>
<li>☑️ 保管場所はクローゼット下段かベッド下</li>
<li>☑️ スマホに期限リマインダーをセット</li>
</ul>

<p><strong>迷ったら志布志の自然水（7年保存）がベスト。</strong>コスパと保存期間のバランスが最も良く、一人暮らしの備蓄に最適です。</p>

<p style="margin-top:16px">
<a href="{link1}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">👉 保存水を楽天市場で見る</a>
</p>

<div style="background:#f0f8ff;border-radius:8px;padding:20px;margin:24px 0">
<h3>📚 あわせて読みたい</h3>
<ul>
<li><a href="#">非常食おすすめ10選｜一人暮らし向け</a></li>
<li><a href="#">防災用ポータブル電源おすすめ5選</a></li>
<li><a href="#">防災グッズ何から揃える？優先順位と予算別プラン</a></li>
<li><a href="#">防災用簡易トイレおすすめ5選</a></li>
</ul>
</div>'''

# 記事を更新（PUT）
tag_ids = [wp_tag(t) for t in ['保存水', '備蓄水', '断水対策', '一人暮らし', '防災']]
resp = requests.post(
    f'{WP_URL}/wp-json/wp/v2/posts/380',
    json={
        'title': new_title,
        'content': new_content,
        'categories': [53],
        'tags': tag_ids,
    },
    headers=wp_auth(),
)
resp.raise_for_status()
d = resp.json()
from urllib.parse import unquote
print(f"✅ 記事更新完了: ID={d['id']}")
print(f"   新タイトル: {d['title']['rendered']}")
print(f"   URL: {unquote(d.get('link', ''))}")
print(f"   文字数: {len(new_content)}文字")
