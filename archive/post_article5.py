"""記事5: 防災グッズ何から揃える"""
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

link1 = rakuten('防災グッズ 最低限')
link2 = rakuten('防災セット 一人暮らし')
link3 = rakuten('非常食 セット')

title = '防災グッズ何から揃える？優先順位と予算別プラン【一人暮らし初心者向け】'

content = f'''<p>「防災グッズ、揃えなきゃとは思ってるんだけど、何から手をつけていいか分からない…」</p>

<p>その気持ち、よく分かります。ネットで調べると「あれもこれも必要」と書いてあって、全部揃えたら数万円。結局面倒になって何も買わないまま——そんな方が大半ではないでしょうか。</p>

<p>でも安心してください。<strong>防災は「完璧」を目指す必要はありません。</strong>まずは本当に必要なものから、予算に合わせて段階的に揃えていけばOKです。</p>

<p>この記事では、防災の優先順位を<strong>3つのステップ</strong>に分けて、予算別に「今日から始める防災」のロードマップを紹介します。</p>

<h2>【結論】最低限これだけは今すぐ揃えて（予算3,000円）</h2>

<table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>優先度</th><th>アイテム</th><th>理由</th><th>目安価格</th></tr>
<tr style="background:#fff8e1"><td>★★★</td><td>水 2L×6本</td><td>人は水なしで3日しか生きられない</td><td>¥600</td></tr>
<tr style="background:#fff8e1"><td>★★★</td><td>簡易トイレ 15回分</td><td>断水時に最も困るのがトイレ</td><td>¥1,500</td></tr>
<tr style="background:#fff8e1"><td>★★★</td><td>モバイルバッテリー</td><td>スマホ＝情報・連絡の生命線</td><td>¥2,000</td></tr>
</table>

<p><strong>この3つで合計約4,000円。</strong>これだけで「何もない状態」とは天と地の差です。今日Amazonか楽天でポチれば明日届きます。</p>

<h2>なぜ「何から揃えるか」の順番が重要なのか</h2>

<p>防災グッズを優先順位なく揃えると、こうなります：</p>

<ul>
<li>ヘルメットやロープは買ったが、水と食料がない</li>
<li>高価なポータブル電源を先に買って予算がなくなった</li>
<li>「あれもこれも」と調べるうちに面倒になり、結局ゼロ</li>
</ul>

<p>大事なのは<strong>「生存に直結するもの」から順番に揃える</strong>こと。人間が生きるために必要な優先順位は明確です：</p>

<ol>
<li><strong>水</strong>（3日で死亡リスク）</li>
<li><strong>トイレ</strong>（我慢は不可能、衛生悪化で感染症リスク）</li>
<li><strong>情報・連絡手段</strong>（スマホ＝救助要請・安否確認）</li>
<li><strong>食料</strong>（1週間は生きられるが、体力・気力が落ちる）</li>
<li><strong>明かり</strong>（夜間の安全確保）</li>
<li><strong>防寒・暑さ対策</strong>（季節による）</li>
</ol>

<h2>予算別・段階的な備蓄プラン</h2>

<h3>Step 1：今すぐ編（予算5,000円以内）</h3>

<p>「今日帰りにコンビニとドラッグストアで買える」レベルの最低限。</p>

<ul>
<li>☑️ ミネラルウォーター 2L×6本（3日分）</li>
<li>☑️ 簡易トイレ 15回分</li>
<li>☑️ モバイルバッテリー 10,000mAh以上</li>
<li>☑️ 懐中電灯（100均でOK）</li>
<li>☑️ 乾電池（懐中電灯用）</li>
</ul>

<p style="margin-top:16px">
<a href="{link1}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で防災グッズを見る →</a>
</p>

<h3>Step 2：しっかり編（予算15,000円）</h3>

<p>Step 1に加えて、3日間を「快適に」過ごすための装備。</p>

<ul>
<li>☑️ 非常食 3日分（アルファ米セット等）</li>
<li>☑️ 簡易トイレ 追加で35回分（合計50回=7日分）</li>
<li>☑️ ラジオ付き手回し充電ライト</li>
<li>☑️ 救急セット</li>
<li>☑️ ウェットティッシュ・除菌シート</li>
<li>☑️ カセットコンロ＋ボンベ3本</li>
<li>☑️ ラップ・ポリ袋（食器代わり）</li>
</ul>

<p style="margin-top:16px">
<a href="{link3}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で非常食セットを見る →</a>
</p>

<h3>Step 3：万全編（予算30,000〜50,000円）</h3>

<p>1週間の在宅避難を快適に乗り切る装備。ここまで揃えばかなり安心。</p>

<ul>
<li>☑️ 防災セット（リュック型）</li>
<li>☑️ ポータブル電源 500Wh以上</li>
<li>☑️ 非常食 7日分に拡充</li>
<li>☑️ 保存水 追加（合計2L×12本）</li>
<li>☑️ 寝袋 or エアーマット</li>
<li>☑️ ソーラーパネル（ポータブル電源用）</li>
</ul>

<p style="margin-top:16px">
<a href="{link2}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">楽天市場で防災セットを見る →</a>
</p>

<h2>「面倒くさい」を乗り越えるコツ3つ</h2>

<ul>
<li><strong>① 防災セットを1つ買って終わりにする</strong><br>個別に揃えるのが面倒な方は、Defend Future等のセットを1つ買えば基本は揃います。足りないものだけ追加すればOK。</li>

<li><strong>② 給料日に1つずつ買う</strong><br>毎月1〜2アイテムずつ。3ヶ月で基本セットが完成します。一度に揃えようとしない。</li>

<li><strong>③ 「防災の日」（9/1）をリマインダーに</strong><br>年1回、備蓄の期限確認と見直し。スマホのカレンダーに入れておけば忘れない。</li>
</ul>

<h2>よくある質問（FAQ）</h2>

<h3>Q1. 100均の防災グッズでも大丈夫？</h3>
<p>懐中電灯、ホイッスル、レインコート、ポリ袋あたりは100均で十分。ただし<strong>食料・水・トイレ・バッテリーは品質重視</strong>で選んでください。命に関わるものをケチると後悔します。</p>

<h3>Q2. 賃貸ワンルームで置き場所がない</h3>
<p>クローゼットの上段、ベッド下、玄関の靴箱上が定番。防災リュック1つなら靴1足分のスペースで済みます。</p>

<h3>Q3. 防災セットを買えば個別に揃えなくていい？</h3>
<p>基本はOKですが、<strong>水・食料の追加と、モバイルバッテリー</strong>は必要。セットの水と食料だけでは3日持たないことが多いです。</p>

<h3>Q4. いつ大地震が来るか分からないのに準備する意味ある？</h3>
<p>日本では<strong>年間約2,000回</strong>の有感地震が発生。南海トラフ地震は今後30年以内に70〜80%の確率で起きると予測されています。「いつか」ではなく「必ず来る」前提で備えましょう。</p>

<h2>まとめ：今日からできる3ステップ</h2>

<ul>
<li>☑️ <strong>今日：</strong>水2L×6本、簡易トイレ15回分、モバイルバッテリーを注文</li>
<li>☑️ <strong>今月中：</strong>非常食3日分、ラジオ付きライト、カセットコンロを追加</li>
<li>☑️ <strong>3ヶ月以内：</strong>防災セット or ポータブル電源で万全に</li>
</ul>

<p><strong>完璧を目指さなくていい。今日1つ買うだけで、昨日の自分より安全になれます。</strong></p>

<p style="margin-top:16px">
<a href="{link1}" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">👉 まずは最低限の防災グッズを楽天で見る</a>
</p>

<div style="background:#f0f8ff;border-radius:8px;padding:20px;margin:24px 0">
<h3>📚 あわせて読みたい</h3>
<ul>
<li><a href="#">防災用ポータブル電源おすすめ5選</a></li>
<li><a href="#">非常食おすすめ10選｜一人暮らし向け</a></li>
<li><a href="#">防災セットおすすめ比較｜一人暮らし向け厳選3つ</a></li>
<li><a href="#">防災用簡易トイレおすすめ5選</a></li>
</ul>
</div>'''

pid, url = wp_post(title, content, 56, ['防災グッズ', '初心者', '一人暮らし', '優先順位'])
print(f'Article 5 posted: ID={pid} URL={url}')
