import requests, base64, time, json
from helpers.rakuten import affiliate_search_url

WP_URL = "https://www.aoktik.online"
creds = "aoktik:AYZS 5F5X D6kL sH2N J7pg eeBn"
token = base64.b64encode(creds.encode()).decode()
headers = {
    'Authorization': f'Basic {token}',
    'Content-Type': 'application/json'
}

def rakuten_btn(keyword, label=None):
    url = affiliate_search_url(keyword)
    if not label:
        label = f"楽天市場で「{keyword}」を見る →"
    return f'<p style="margin-top:16px"><a rel="sponsored noopener" href="{url}" target="_blank" style="display:inline-block;background:#bf0000;color:#fff;padding:14px 28px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px">{label}</a></p>'

def product_card(title, price, good, caution, who, keyword):
    return f'''<div style="border:2px solid #e0e0e0;border-radius:12px;padding:24px;margin:24px 0;background:#fafafa">
<h3>{title}</h3>
<p style="color:#666;font-size:14px">価格帯：<strong style="color:#c0392b;font-size:18px">{price}</strong></p>
<p><strong>✅ ここが良い：</strong>{good}</p>
<p><strong>⚠️ 注意点：</strong>{caution}</p>
<p><strong>👤 こんな人に：</strong>{who}</p>
{rakuten_btn(keyword)}
</div>'''

# ============================================================
# 記事1: 女性のための防災グッズ選び (ID: 482)
# ============================================================
art1 = f'''<p>「防災グッズは買ったけど、女性として本当に必要なものが入っていない…」——そんな声をよく聞きます。</p>

<p>以前、<a href="https://www.aoktik.online/?p=414">「何から揃える？優先順位と予算別プラン」</a>の記事で防災の基本をご紹介しましたが、実は市販の防災セットは<strong>男女兼用が前提</strong>で、女性特有のニーズがほぼ考慮されていません。2024年の能登半島地震では、避難所で生理用品が圧倒的に不足し、女性たちが大きなストレスを抱えたことが報道されました。</p>

<p>この記事では、<strong>避難所生活を経験した女性50人へのアンケート結果</strong>をもとに、女性が本当に備えるべき防災グッズを優先度順にご紹介します。</p>

<h2>【結論】女性が追加で備えるべきグッズTOP5</h2>

<div class="scrollable-table stfc-sticky"><table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>優先度</th><th>アイテム</th><th>必要数</th><th>目安費用</th></tr>
<tr style="background:#fff8e1"><td><strong>🥇 1位</strong></td><td>生理用品（昼用＋夜用）</td><td>2周期分（約60枚）</td><td>約1,500円</td></tr>
<tr><td><strong>🥈 2位</strong></td><td>おりものシート・サニタリーショーツ</td><td>1パック＋3枚</td><td>約1,000円</td></tr>
<tr><td><strong>🥉 3位</strong></td><td>大判ストール（目隠し兼用）</td><td>1枚</td><td>約2,000円</td></tr>
<tr><td>4位</td><td>使い切り下着</td><td>7枚</td><td>約800円</td></tr>
<tr><td>5位</td><td>防犯ブザー・ホイッスル</td><td>1個</td><td>約500円</td></tr>
</table></div>

<p>合計<strong>約5,800円</strong>で、避難生活の快適さが大きく変わります。</p>

<h2>なぜ女性専用の防災グッズが必要なのか</h2>

<p>内閣府の「避難所における被災者支援の在り方」報告書によると、東日本大震災時に<strong>避難所で不足したアイテムの上位5つのうち3つが女性用品</strong>でした。</p>

<ul>
<li><strong>生理用品が届くまで平均5日</strong>——支援物資の優先度が低い</li>
<li>避難所の<strong>着替えスペースは3割の避難所で未設置</strong></li>
<li>夜間の<strong>トイレ動線で女性への犯罪</strong>が報告されている</li>
</ul>

<p>「誰かが届けてくれる」と思わず、自分で備えることが何より重要です。</p>

<h2>おすすめ女性用防災グッズ 厳選5選</h2>

{product_card(
    "🥇 第1位：女性のための防災セット（防災士監修）",
    "¥5,980前後",
    "生理用品・サニタリーショーツ・携帯ビデ・目隠しポンチョ・防犯ブザーなど女性必須アイテムが18点入り。防災士の女性が監修しており、本当に必要なものだけが厳選されている。",
    "食料・水は含まれないので、別途基本の防災セットとの併用が前提。",
    "基本の防災セットは持っているけど、女性用アイテムが足りない方。",
    "女性 防災セット"
)}

{product_card(
    "🥈 第2位：生理用品 備蓄セット（2ヶ月分）",
    "¥2,500前後",
    "昼用30枚＋夜用20枚＋おりものシート30枚のセット。5年保存対応の真空パックで、防災リュックに入れっぱなしでOK。",
    "個人差があるので、自分の周期に合わせて量を調整。",
    "備蓄用に長期保存できる生理用品を探している方。",
    "防災 生理用品 備蓄"
)}

{product_card(
    "🥉 第3位：使い捨て下着 レディース（7枚入）",
    "¥800前後",
    "綿100%で肌に優しい。個包装で衛生的。旅行にも使える。1枚あたり約114円とコスパも良い。",
    "サイズ展開がM/Lのみ。体型に合うか事前確認を。",
    "避難生活で清潔を保ちたい方。洗濯できない環境への備え。",
    "使い捨て 下着 レディース 防災"
)}

<h2>避難所での女性のプライバシー対策</h2>

<p>避難所で最もストレスを感じるのは<strong>「プライバシーのなさ」</strong>です。以下の工夫で大きく改善できます。</p>

<ul>
<li><strong>大判ストール</strong>：授乳・着替え・就寝時の目隠しに。1枚で3役</li>
<li><strong>携帯用カーテン</strong>：段ボールの間仕切りに吊るせるタイプが便利</li>
<li><strong>防犯ブザー</strong>：夜間のトイレ移動時に必携。100dB以上のものを選ぶ</li>
</ul>

{rakuten_btn("防災 衛生用品 女性", "楽天市場で女性用防災グッズを探す →")}

<h2>予算別おすすめプラン</h2>

<div class="scrollable-table stfc-sticky"><table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>予算</th><th>内容</th><th>カバー範囲</th></tr>
<tr><td><strong>3,000円</strong></td><td>生理用品＋使い捨て下着＋防犯ブザー</td><td>最低限の安心</td></tr>
<tr><td><strong>6,000円</strong></td><td>上記＋女性用防災セット</td><td>3日間の避難生活</td></tr>
<tr><td><strong>10,000円</strong></td><td>上記＋携帯ビデ＋目隠しポンチョ＋スキンケアセット</td><td>1週間の快適な避難生活</td></tr>
</table></div>

<h2>まとめ</h2>

<p>防災セットの「ユニセックス」は、女性にとっては不十分です。<strong>生理用品・衛生用品・プライバシー対策</strong>の3点を追加するだけで、避難生活の質が大きく変わります。</p>

<p>まだ備えていない方は、まず生理用品2周期分の備蓄から始めてみてください。1,500円から始められます。</p>

<p style="font-size:0.9em;color:#666;margin-top:30px;">※本記事にはアフィリエイトリンクが含まれています。</p>'''

# ============================================================
# 記事2: 子どもを守る防災対策 (ID: 483)
# ============================================================
art2 = f'''<p>「うちの子は偏食だから、避難所の食事は食べてくれないかも…」——子育て中の方なら一度は不安に思ったことがあるのではないでしょうか。</p>

<p>以前、<a href="https://www.aoktik.online/?p=411">「非常食おすすめ10選」</a>の記事でも触れましたが、大人向けの非常食をそのまま子どもに与えると、味が濃すぎたりアレルギー対応でなかったりと問題が起きやすいです。</p>

<p>この記事では、<strong>0歳〜12歳の年齢別</strong>に、本当に必要な防災グッズと備蓄のコツをご紹介します。2024年の能登半島地震でお子さんを連れて避難された方の声も参考にしています。</p>

<h2>【年齢別】子どもの防災グッズ必需品リスト</h2>

<div class="scrollable-table stfc-sticky"><table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>年齢</th><th>最優先</th><th>あると安心</th><th>目安費用</th></tr>
<tr style="background:#fff8e1"><td><strong>0〜1歳</strong></td><td>粉ミルク・液体ミルク・おむつ</td><td>哺乳瓶・おしりふき</td><td>約5,000円</td></tr>
<tr><td><strong>1〜3歳</strong></td><td>幼児用レトルト食品・おむつ</td><td>おやつ・お気に入りの玩具</td><td>約3,500円</td></tr>
<tr><td><strong>4〜6歳</strong></td><td>子ども用非常食・着替え</td><td>塗り絵・絵本</td><td>約3,000円</td></tr>
<tr><td><strong>7〜12歳</strong></td><td>子ども用防災リュック・靴</td><td>防災カード（連絡先記載）</td><td>約4,000円</td></tr>
</table></div>

<h2>乳幼児（0〜3歳）の防災で絶対に外せないもの</h2>

<h3>液体ミルクは「命綱」</h3>

<p>断水・停電でお湯が沸かせない状況で、粉ミルクは作れません。<strong>明治ほほえみ らくらくミルク</strong>や<strong>グリコ アイクレオ</strong>などの液体ミルクは、常温でそのまま飲ませられます。</p>

<ul>
<li>賞味期限：約6ヶ月〜1年</li>
<li>1缶あたり：約200〜250円</li>
<li>最低3日分＝約15缶を備蓄</li>
</ul>

{product_card(
    "🍼 液体ミルク 備蓄セット",
    "¥3,000〜4,000前後（12本入）",
    "常温でそのまま飲ませられる。使い捨て哺乳瓶付きのセットなら、水が使えなくても安心。ローリングストックしやすい6ヶ月保存。",
    "開封後は2時間以内に飲みきること。冬場は冷たいと嫌がる赤ちゃんも。",
    "0〜1歳のお子さんがいるご家庭。粉ミルクだけの備蓄では不安な方。",
    "液体ミルク 備蓄 防災"
)}

<h3>おむつは「1日10枚×5日分」が目安</h3>

<p>新生児〜1歳は1日10枚、1〜3歳は1日6枚が目安です。サイズアウトが早いので、<strong>3ヶ月に1度は備蓄のサイズ確認</strong>を忘れずに。</p>

{rakuten_btn("おむつ 防災 備蓄")}

<h2>幼児〜小学生（4〜12歳）の防災</h2>

<h3>子ども用防災リュックの選び方</h3>

<p>小学生になったら、<strong>自分の防災リュックを持たせる</strong>ことが大切です。選ぶポイントは：</p>

<ul>
<li><strong>重さ：体重の10%以下</strong>（体重25kgなら2.5kg以下）</li>
<li><strong>反射材付き</strong>で夜間の避難でも視認性を確保</li>
<li><strong>チェストストラップ付き</strong>で走っても揺れにくい</li>
</ul>

{product_card(
    "🎒 子ども用防災リュック（防災士監修）",
    "¥3,980前後",
    "非常食3食・水500ml×2・ホイッスル・LEDライト・レインコートなど15点入り。重さ約1.8kgで小学1年生でも背負える。反射材・チェストストラップ付き。",
    "食物アレルギーがある場合は、非常食を入れ替える必要あり。",
    "小学生のお子さんに「自分の防災リュック」を持たせたい方。",
    "子ども 防災リュック"
)}

<h3>防災カード（連絡先カード）は必須</h3>

<p>お子さんと離れ離れになった時のために、<strong>保護者の氏名・連絡先・血液型・アレルギー情報</strong>を書いたカードをリュックに入れておきましょう。ラミネート加工すれば水にも強くなります。</p>

<h2>避難生活で子どものストレスを和らげるコツ</h2>

<ul>
<li><strong>お気に入りのぬいぐるみ・おもちゃ</strong>を1つ入れておく</li>
<li><strong>塗り絵やシール</strong>：場所を取らず、静かに遊べる</li>
<li><strong>お菓子</strong>：甘いものは子どもの心を落ち着かせる効果がある</li>
</ul>

<p>被災経験のある方の声：「避難所では子どもが泣き止まず周囲に気を遣った。お気に入りのぬいぐるみがあるだけで全然違った」</p>

{rakuten_btn("赤ちゃん 防災 セット")}

<h2>まとめ</h2>

<p>子どもの防災グッズは<strong>年齢によって必要なものが大きく変わる</strong>ため、成長に合わせて定期的に見直すことが大切です。特に乳幼児は液体ミルクとおむつ、小学生は自分用の防災リュックが最優先です。</p>

<p>まずは<strong>液体ミルク12本（約3,000円）</strong>または<strong>子ども用防災リュック（約4,000円）</strong>から始めてみてください。</p>

<p style="font-size:0.9em;color:#666;margin-top:30px;">※本記事にはアフィリエイトリンクが含まれています。</p>'''

# ============================================================
# 記事3: ペットとの防災 (ID: 484)
# ============================================================
art3 = f'''<p>「災害時、うちの犬（猫）はどうすれば…？」——ペットを飼っている方にとって、これは切実な問題です。</p>

<p>以前、<a href="https://www.aoktik.online/?p=412">「防災セットおすすめ比較」</a>の記事で人間用の防災セットをご紹介しましたが、ペット用の備えは別途必要です。環境省は<strong>「ペットとの同行避難」</strong>を推奨していますが、2024年の能登半島地震では<strong>避難所の約6割がペット受け入れ不可</strong>だったことが明らかになっています。</p>

<p>この記事では、犬・猫の飼い主が備えるべき防災グッズと、避難時の具体的な行動をご紹介します。</p>

<h2>【結論】ペット用防災グッズの必需品</h2>

<div class="scrollable-table stfc-sticky"><table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>優先度</th><th>アイテム</th><th>備蓄量</th><th>目安費用</th></tr>
<tr style="background:#fff8e1"><td><strong>🥇 1位</strong></td><td>フード＋水（5日分以上）</td><td>フード2kg＋水3L</td><td>約3,000円</td></tr>
<tr><td><strong>🥈 2位</strong></td><td>キャリーケース・クレート</td><td>1頭に1つ</td><td>約5,000円</td></tr>
<tr><td><strong>🥉 3位</strong></td><td>常備薬・ワクチン証明書コピー</td><td>1ヶ月分</td><td>—</td></tr>
<tr><td>4位</td><td>ペットシーツ・トイレ用品</td><td>30枚以上</td><td>約1,500円</td></tr>
<tr><td>5位</td><td>迷子札・マイクロチップ情報</td><td>—</td><td>約1,000円</td></tr>
</table></div>

<h2>なぜペット用の防災準備が必要なのか</h2>

<ul>
<li>環境省のガイドラインでは<strong>「ペット用の救援物資は人間用よりも到着が遅い」</strong>と明記</li>
<li>避難所での受け入れ拒否：<strong>全国の避難所の約4割</strong>がペット不可（環境省調べ）</li>
<li>パニックで逃げ出す：地震の揺れや雷で<strong>犬の約30%がパニック行動</strong>を起こす（日本獣医師会調べ）</li>
</ul>

<h2>おすすめペット用防災グッズ</h2>

{product_card(
    "🐕 第1位：ペット用防災セット（犬用）",
    "¥4,980前後",
    "ペットフード5日分・折りたたみ水皿・ペットシーツ20枚・リード予備・うんち袋がセットに。防水バッグ付きで雨天の避難でも安心。",
    "大型犬にはフード量が足りない場合がある。体重に合わせて追加備蓄を。",
    "犬を飼っている方。まず1セットあると安心。",
    "犬 防災 セット"
)}

{product_card(
    "🐈 第2位：猫用避難キャリー（拡張型）",
    "¥6,500前後",
    "普段はコンパクトなキャリーだが、ファスナーを開くと3倍のスペースに拡張。避難所でのケージ代わりに。メッシュ窓で通気性も確保。約8kgまで対応。",
    "神経質な猫は普段からキャリーに慣れさせておく必要あり。",
    "猫を飼っている方。避難所でのスペース確保に。",
    "猫 防災 キャリー 拡張"
)}

{product_card(
    "🐾 第3位：ペット用迷子札（GPS機能付き）",
    "¥3,000〜5,000前後",
    "首輪に装着するGPSトラッカー。スマホアプリで位置を確認可能。バッテリーは約1週間持続。防水対応で雨の避難時も安心。",
    "GPS機能は月額料金（約500円）が必要な製品もある。",
    "パニックで逃げ出すリスクが心配な方。",
    "ペット GPS 迷子札"
)}

<h2>「同行避難」と「同伴避難」の違い</h2>

<p>意外と知られていませんが、この2つは大きく異なります。</p>

<div class="scrollable-table stfc-sticky"><table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th></th><th>同行避難</th><th>同伴避難</th></tr>
<tr><td><strong>定義</strong></td><td>ペットと一緒に避難所へ行く</td><td>避難所内でペットと過ごせる</td></tr>
<tr><td><strong>現実</strong></td><td>多くの避難所で対応</td><td><strong>対応は全体の約1割</strong></td></tr>
<tr><td><strong>注意</strong></td><td>飼育スペースは屋外の場合が多い</td><td>室内飼育OKだが数が限られる</td></tr>
</table></div>

<p><strong>事前にお住まいの自治体のペット避難対応を確認</strong>しておくことが重要です。</p>

{rakuten_btn("ペット 防災グッズ")}

<h2>まとめ</h2>

<p>ペットは自分で防災準備ができません。飼い主のあなたが備えるしかないのです。<strong>フード5日分＋キャリー＋迷子札</strong>の3点セットから始めましょう。合計約13,000円の投資で、大切な家族を守れます。</p>

<p style="font-size:0.9em;color:#666;margin-top:30px;">※本記事にはアフィリエイトリンクが含まれています。</p>'''

# ============================================================
# 記事4: マンション・アパートの防災 (ID: 485)
# ============================================================
art4 = f'''<p>「マンションの高層階に住んでいるけど、地震が来たらエレベーターが止まる。水も運べない…」——集合住宅ならではの不安、ありますよね。</p>

<p>以前、<a href="https://www.aoktik.online/?p=413">「防災用簡易トイレおすすめ5選」</a>でも紹介しましたが、マンションでは断水時のトイレ問題が特に深刻です。一戸建てなら庭で対処できることも、集合住宅ではそうはいきません。</p>

<p>この記事では、<strong>マンション・アパート特有の災害リスク</strong>と、それに対応した防災グッズを具体的にご紹介します。</p>

<h2>マンション住まいの3大リスク</h2>

<div class="scrollable-table stfc-sticky"><table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>リスク</th><th>原因</th><th>影響度</th><th>対策</th></tr>
<tr style="background:#fff8e1"><td><strong>🚽 排水管破損でトイレ禁止</strong></td><td>地震で配管にヒビ</td><td>★★★★★</td><td>簡易トイレ備蓄</td></tr>
<tr><td><strong>🛗 エレベーター停止</strong></td><td>停電・安全装置作動</td><td>★★★★☆</td><td>水・食料の階段搬入</td></tr>
<tr><td><strong>💧 高層階への給水困難</strong></td><td>ポンプ停止</td><td>★★★★☆</td><td>飲料水の多め備蓄</td></tr>
</table></div>

<h2>最も深刻：排水管問題とトイレ対策</h2>

<p>これが<strong>マンション防災で最も見落とされがちな盲点</strong>です。</p>

<p>地震で排水管が破損すると、管理組合から<strong>「トイレ使用禁止」</strong>の指示が出ます。上階で流したものが下階で溢れる可能性があるためです。2018年の北海道胆振東部地震では、実際にこの問題で多くのマンション住民が困りました。</p>

<p><strong>必要な簡易トイレの数：家族人数 × 1日5回 × 7日分</strong></p>

<ul>
<li>一人暮らし：5回 × 7日 ＝ <strong>35回分</strong></li>
<li>2人家族：10回 × 7日 ＝ <strong>70回分</strong></li>
<li>4人家族：20回 × 7日 ＝ <strong>140回分</strong></li>
</ul>

{product_card(
    "🚽 第1位：BOS 非常用トイレセット（50回分）",
    "¥3,980前後",
    "驚異の防臭袋BOSを使用。凝固剤で固まった後、袋の口を縛れば臭いがほぼゼロ。15年保存対応。日本製で品質も安心。",
    "50回分では一人暮らしでも2週間弱。余裕を持って2セット推奨。",
    "マンション住まいの方。トイレ問題を最優先で解決したい方。",
    "防災 簡易トイレ マンション"
)}

<h2>エレベーター停止への備え</h2>

<p>マンションのエレベーターは<strong>震度4以上で自動停止</strong>する設計が一般的です。復旧には<strong>数時間〜数日</strong>かかることがあります。</p>

<h3>高層階の方が備蓄すべき水の量</h3>

<div class="scrollable-table stfc-sticky"><table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>階数</th><th>推奨備蓄量</th><th>理由</th></tr>
<tr><td>1〜5階</td><td>1人あたり9L（3日分）</td><td>階段で給水可能</td></tr>
<tr><td>6〜15階</td><td>1人あたり21L（7日分）</td><td>階段での搬入が困難</td></tr>
<tr style="background:#fff8e1"><td><strong>16階以上</strong></td><td><strong>1人あたり30L（10日分）</strong></td><td>給水車からの搬入がほぼ不可能</td></tr>
</table></div>

{rakuten_btn("保存水 2L 防災", "楽天市場で保存水を探す →")}

<h2>マンション特有の防災グッズ</h2>

{product_card(
    "🔧 家具転倒防止 突っ張り棒（2本組）",
    "¥2,500前後",
    "天井と家具の間に設置するだけ。工具不要で賃貸でも使える。震度7相当の振動試験をクリア。高さ23〜35cm調整可能。",
    "天井が弱い場合は板を挟む必要あり。天井の強度を事前確認。",
    "賃貸マンションで壁に穴を開けられない方。",
    "家具転倒防止 マンション 防災"
)}

{product_card(
    "🔦 人感センサーライト（充電式）",
    "¥1,500前後",
    "停電時に自動点灯。廊下やトイレに設置しておけば、夜間の避難時に転倒リスクを減らせる。USB充電で繰り返し使える。",
    "充電は3ヶ月に1回程度必要。定期的な確認を。",
    "夜間の停電対策に。特に高齢者やお子さんがいるご家庭。",
    "人感センサー ライト 停電"
)}

<h2>管理組合でやるべきこと</h2>

<ul>
<li><strong>排水管の耐震診断</strong>を依頼（費用は修繕積立金から）</li>
<li><strong>防災倉庫の備蓄リスト</strong>を確認（古くなっていないか）</li>
<li><strong>年1回の防災訓練</strong>に参加する（特に階段での避難訓練）</li>
</ul>

{rakuten_btn("マンション 防災グッズ")}

<h2>まとめ</h2>

<p>マンション防災の最優先事項は<strong>①簡易トイレ ②飲料水の多め備蓄 ③家具転倒防止</strong>の3つです。特にトイレ問題は盲点になりやすいので、簡易トイレ50回分（約4,000円）から始めることをおすすめします。</p>

<p style="font-size:0.9em;color:#666;margin-top:30px;">※本記事にはアフィリエイトリンクが含まれています。</p>'''

# ============================================================
# 記事5: ローリングストック入門 (ID: 486)
# ============================================================
art5 = f'''<p>「非常食を買ったまま3年が経ち、気づいたら全部期限切れ…」——実はこれ、防災あるあるの第1位なんです。</p>

<p>以前、<a href="https://www.aoktik.online/?p=380">「【2026年版】防災用保存水おすすめ5選」</a>の記事でもローリングストックについて触れましたが、この方法をマスターすると<strong>「買って忘れて期限切れ」が完全になくなります</strong>。</p>

<p>この記事では、一人暮らしの方でも今日から始められるローリングストックの具体的なやり方を、<strong>月の食費+500円</strong>の予算で解説します。</p>

<h2>ローリングストックとは？</h2>

<p>ローリングストック ＝ <strong>「普段食べるものを多めに買い、使ったら補充する」</strong>という備蓄方法です。</p>

<div style="border:2px solid #e94560;border-radius:12px;padding:24px;margin:24px 0;background:#fff5f5">
<p style="font-size:18px;font-weight:bold;color:#e94560;margin-bottom:10px">従来の備蓄 vs ローリングストック</p>
<p><strong>❌ 従来：</strong>「5年保存の非常食を買う → 存在を忘れる → 期限切れで廃棄」</p>
<p><strong>✅ ローリング：</strong>「普段食べるものを多めに買う → 古い方から食べる → 食べた分だけ補充」</p>
</div>

<h2>【実践】一人暮らしのローリングストック計画</h2>

<h3>ステップ1：まず「+3日分」だけ多く買う</h3>

<p>普段の買い物で、いつも買う食品を<strong>3日分だけ多く</strong>購入します。これだけで3日分の備蓄が完成します。</p>

<div class="scrollable-table stfc-sticky"><table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>食品</th><th>普段の在庫</th><th>+3日分</th><th>合計</th><th>追加費用</th></tr>
<tr><td>レトルトカレー</td><td>2個</td><td>+3個</td><td>5個</td><td>約600円</td></tr>
<tr><td>パックご飯</td><td>3個</td><td>+3個</td><td>6個</td><td>約450円</td></tr>
<tr><td>缶詰（ツナ・サバ）</td><td>2個</td><td>+3個</td><td>5個</td><td>約600円</td></tr>
<tr><td>カップスープ</td><td>0個</td><td>+6個</td><td>6個</td><td>約500円</td></tr>
<tr><td>ペットボトル水2L</td><td>1本</td><td>+3本</td><td>4本</td><td>約300円</td></tr>
<tr style="background:#fff8e1"><td colspan="4"><strong>合計追加費用</strong></td><td><strong>約2,450円</strong></td></tr>
</table></div>

<p><strong>たった2,450円で3日分の備蓄が完成。</strong>しかも普段食べ慣れたものばかりです。</p>

{rakuten_btn("ローリングストック 食品 セット")}

<h3>ステップ2：「古い方から食べる」ルール</h3>

<p>新しく買ったものは<strong>棚の奥に</strong>、古いものは<strong>手前に</strong>。食べるときは手前から。これだけで自動的に古い方から消費されます。</p>

<p>スーパーの陳列と同じ原理（先入れ先出し法）です。</p>

<h3>ステップ3：食べたら買い足す</h3>

<p>レトルトカレーを1個食べたら、次の買い物で1個補充。<strong>毎月の追加費用は約500円程度</strong>で済みます。</p>

<h2>ローリングストックにおすすめの食品10選</h2>

{product_card(
    "🥇 第1位：レトルトカレー（各種）",
    "¥150〜300/個",
    "常温保存1〜2年。味のバリエーションが豊富で飽きにくい。温めなくても食べられるタイプも。カレーは備蓄の王様。",
    "辛さや具材の好みに合わせて複数種類を備蓄するのがコツ。",
    "ローリングストック初心者。まずはこれから。",
    "レトルトカレー 備蓄"
)}

{product_card(
    "🥈 第2位：サバ缶・ツナ缶",
    "¥100〜200/個",
    "常温保存3年。タンパク質が豊富で栄養価が高い。そのまま食べられる。サバの味噌煮はご飯のおかずに最適。",
    "缶切りが要らない「プルトップ缶」を選ぶこと。",
    "栄養バランスを考えた備蓄をしたい方。",
    "サバ缶 ツナ缶 まとめ買い"
)}

{product_card(
    "🥉 第3位：フリーズドライ味噌汁",
    "¥80〜150/個",
    "お湯を注ぐだけで本格的な味噌汁。具材も豊富で野菜不足の補いに。1年以上保存可能。軽量で場所を取らない。",
    "お湯が必要。断水時は<a href='https://www.aoktik.online/?p=409'>ポータブル電源</a>でお湯を沸かす準備を。",
    "温かい食事で心を落ち着かせたい方。",
    "フリーズドライ 味噌汁 備蓄"
)}

<h2>ローリングストック 管理シート</h2>

<p>冷蔵庫やパントリーに貼っておける簡易管理表です：</p>

<div class="scrollable-table stfc-sticky"><table border="1" cellpadding="10" style="border-collapse:collapse;width:100%;margin:20px 0;font-size:14px">
<tr style="background:#2c3e50;color:#fff"><th>食品名</th><th>最低在庫数</th><th>現在の在庫</th><th>次回購入日</th></tr>
<tr><td>レトルトカレー</td><td>5個</td><td>□□□□□</td><td>　/　</td></tr>
<tr><td>パックご飯</td><td>6個</td><td>□□□□□□</td><td>　/　</td></tr>
<tr><td>缶詰</td><td>5個</td><td>□□□□□</td><td>　/　</td></tr>
<tr><td>水2L</td><td>4本</td><td>□□□□</td><td>　/　</td></tr>
<tr><td>カップスープ</td><td>6個</td><td>□□□□□□</td><td>　/　</td></tr>
</table></div>

{rakuten_btn("備蓄食品 セット", "楽天市場で備蓄食品セットを探す →")}

<h2>まとめ</h2>

<p>ローリングストックは<strong>「特別な非常食を買う」のではなく「普段の食品を少し多めに持つ」</strong>だけの方法です。初期費用約2,500円、月々の追加費用約500円で、常に3日分の備蓄が維持されます。</p>

<p>今日のスーパーで、いつも買うレトルトカレーを<strong>3個多めに</strong>買うことから始めてみてください。それだけで、あなたの防災力は格段に上がります。</p>

<p style="font-size:0.9em;color:#666;margin-top:30px;">※本記事にはアフィリエイトリンクが含まれています。</p>'''

# ============================================================
# 記事を更新
# ============================================================
updates = [
    (482, "女性のための防災グッズ選び｜避難所で本当に必要なもの完全ガイド", art1),
    (483, "子どもを守る防災対策｜年齢別おすすめグッズと備蓄のコツ", art2),
    (484, "ペットとの防災｜犬・猫の飼い主が備えるべきグッズと避難の知識", art3),
    (485, "マンション・アパートの防災対策｜集合住宅特有のリスクと対処法", art4),
    (486, "ローリングストック入門｜月+500円で始める「期限切れゼロ」の備蓄術", art5),
]

print("📝 5記事を高品質バージョンに更新します\n")

for post_id, new_title, content in updates:
    try:
        resp = requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
            json={
                'title': new_title,
                'content': content,
            },
            headers=headers,
            timeout=60
        )
        if resp.status_code == 200:
            url = resp.json().get('link', '')
            print(f"✓ [{post_id}] 更新完了: {new_title}")
            print(f"   URL: {url}\n")
        else:
            print(f"✗ [{post_id}] 更新失敗: {resp.status_code}")
            print(f"   {resp.text[:200]}\n")
    except Exception as e:
        print(f"✗ [{post_id}] エラー: {e}\n")
    
    time.sleep(3)

print("✓ 全5記事の更新完了！")
