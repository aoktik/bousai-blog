"""フロントページ(固定ページID:371)をCocoon silk スキン対応で全面刷新"""
import os, base64, requests
from urllib.parse import quote

WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']

def wp_auth():
    creds = f'{WP_USER}:{WP_PASSWORD}'
    token = base64.b64encode(creds.encode()).decode()
    return {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}

# 記事URL
url_start   = 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e3%82%b0%e3%83%83%e3%82%ba%e4%bd%95%e3%81%8b%e3%82%89%e6%8f%83%e3%81%88%e3%82%8b%ef%bc%9f%e5%84%aa%e5%85%88%e9%a0%86%e4%bd%8d%e3%81%a8%e4%ba%88%e7%ae%97%e5%88%a5%e3%83%97%e3%83%a9/'
url_toilet  = 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e7%94%a8%e7%b0%a1%e6%98%93%e3%83%88%e3%82%a4%e3%83%ac%e3%81%8a%e3%81%99%e3%81%99%e3%82%815%e9%81%b8%ef%bd%9c%e5%ae%9f%e9%9a%9b%e3%81%ab%e4%bd%bf%e3%81%a3%e3%81%a6%e5%88%86%e3%81%8b/'
url_set     = 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e3%82%bb%e3%83%83%e3%83%88%e3%81%8a%e3%81%99%e3%81%99%e3%82%81%e6%af%94%e8%bc%83%ef%bd%9c%e4%b8%80%e4%ba%ba%e6%9a%ae%e3%82%89%e3%81%97%e5%90%91%e3%81%91%e5%8e%b3%e9%81%b83%e3%81%a4/'
url_food    = 'https://www.aoktik.online/%e9%9d%9e%e5%b8%b8%e9%a3%9f%e3%81%8a%e3%81%99%e3%81%99%e3%82%8110%e9%81%b8%ef%bd%9c%e4%b8%80%e4%ba%ba%e6%9a%ae%e3%82%89%e3%81%97%e5%90%91%e3%81%91%e3%83%bb5%e5%b9%b4%e4%bf%9d%e5%ad%98%e3%81%a7/'
url_portable= 'https://www.aoktik.online/%e3%80%902026%e5%b9%b4%e7%89%88%e3%80%91%e9%98%b2%e7%81%bd%e7%94%a8%e3%83%9d%e3%83%bc%e3%82%bf%e3%83%96%e3%83%ab%e9%9b%bb%e6%ba%90%e3%81%8a%e3%81%99%e3%81%99%e3%82%815%e9%81%b8%ef%bd%9c%e5%81%9c/'
url_water   = 'https://www.aoktik.online/%e7%81%bd%e5%ae%b3%e7%94%a8%e4%bf%9d%e5%ad%98%e6%b0%b4%e3%81%ae%e9%81%b8%e3%81%b3%e6%96%b9%e3%81%a8%e3%81%8a%e3%81%99%e3%81%99%e3%82%81%e5%95%86%e5%93%81/'
url_blog    = 'https://www.aoktik.online/blog/'
url_prime   = 'https://www.aoktik.online/prime-video-disaster-5/'

# デザインカラー（Cocoon設定と統一）
navy   = '#1a365d'
accent = '#e94560'
bg     = '#f8fafc'
text   = '#333333'
light  = '#e2e8f0'

new_content = f'''<!-- wp:heading {{"level":2,"style":{{"typography":{{"fontSize":"1.5rem"}}}}}} -->
<h2 class="wp-block-heading" style="font-size:1.5rem;text-align:center;margin-bottom:8px">シーン別に備える</h2>
<!-- /wp:heading -->

<!-- wp:paragraph {{"align":"center"}} -->
<p class="has-text-align-center" style="color:#64748b;margin-bottom:32px">あなたに必要な防災準備は、生活スタイルによって違います</p>
<!-- /wp:paragraph -->

<!-- wp:columns {{"style":{{"spacing":{{"blockGap":"20px"}}}}}} -->
<div class="wp-block-columns" style="margin-bottom:40px">

<!-- wp:column -->
<div class="wp-block-column" style="border:1px solid {light};border-radius:12px;padding:28px 20px;text-align:center;background:#fff">
<p style="font-size:2.5em;margin-bottom:4px;line-height:1">🎒</p>
<h3 style="color:{navy};margin-bottom:8px;font-size:1.1em">逃げる準備</h3>
<p style="font-size:0.9em;color:#64748b;margin-bottom:16px;line-height:1.6">非常用持ち出し袋の中身を完全解説。最低限これだけは揃えよう。</p>
<a href="{url_set}" style="color:{accent};font-weight:bold;text-decoration:none;font-size:0.95em">おすすめ防災セット →</a>
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column" style="border:1px solid {light};border-radius:12px;padding:28px 20px;text-align:center;background:#fff">
<p style="font-size:2.5em;margin-bottom:4px;line-height:1">🏠</p>
<h3 style="color:{navy};margin-bottom:8px;font-size:1.1em">自宅で耐える</h3>
<p style="font-size:0.9em;color:#64748b;margin-bottom:16px;line-height:1.6">在宅避難3日間を乗り切る備蓄品リスト。水・食料・電源・トイレ。</p>
<a href="{url_water}" style="color:{accent};font-weight:bold;text-decoration:none;font-size:0.95em">備蓄水の選び方 →</a>
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column" style="border:1px solid {light};border-radius:12px;padding:28px 20px;text-align:center;background:#fff">
<p style="font-size:2.5em;margin-bottom:4px;line-height:1">⚡</p>
<h3 style="color:{navy};margin-bottom:8px;font-size:1.1em">停電に備える</h3>
<p style="font-size:0.9em;color:#64748b;margin-bottom:16px;line-height:1.6">停電3日を乗り切るポータブル電源。スマホも家電も使える。</p>
<a href="{url_portable}" style="color:{accent};font-weight:bold;text-decoration:none;font-size:0.95em">ポータブル電源おすすめ →</a>
</div>
<!-- /wp:column -->

</div>
<!-- /wp:columns -->

<!-- wp:columns {{"style":{{"spacing":{{"blockGap":"20px"}}}}}} -->
<div class="wp-block-columns" style="margin-bottom:48px">

<!-- wp:column -->
<div class="wp-block-column" style="border:1px solid {light};border-radius:12px;padding:28px 20px;text-align:center;background:#fff">
<p style="font-size:2.5em;margin-bottom:4px;line-height:1">🚽</p>
<h3 style="color:{navy};margin-bottom:8px;font-size:1.1em">トイレ問題を解決</h3>
<p style="font-size:0.9em;color:#64748b;margin-bottom:16px;line-height:1.6">断水時に最も困るのがトイレ。簡易トイレの備蓄は必須です。</p>
<a href="{url_toilet}" style="color:{accent};font-weight:bold;text-decoration:none;font-size:0.95em">簡易トイレおすすめ →</a>
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column" style="border:1px solid {light};border-radius:12px;padding:28px 20px;text-align:center;background:#fff">
<p style="font-size:2.5em;margin-bottom:4px;line-height:1">🍚</p>
<h3 style="color:{navy};margin-bottom:8px;font-size:1.1em">非常食を備える</h3>
<p style="font-size:0.9em;color:#64748b;margin-bottom:16px;line-height:1.6">5年保存で本当に美味しい非常食だけを厳選。もう不味くない。</p>
<a href="{url_food}" style="color:{accent};font-weight:bold;text-decoration:none;font-size:0.95em">非常食おすすめ10選 →</a>
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column" style="border:1px solid {light};border-radius:12px;padding:28px 20px;text-align:center;background:#fff">
<p style="font-size:2.5em;margin-bottom:4px;line-height:1">💡</p>
<h3 style="color:{navy};margin-bottom:8px;font-size:1.1em">防災の知識</h3>
<p style="font-size:0.9em;color:#64748b;margin-bottom:16px;line-height:1.6">何から買う？いくらかかる？初心者の疑問にすべて答えます。</p>
<a href="{url_start}" style="color:{accent};font-weight:bold;text-decoration:none;font-size:0.95em">何から揃える？ →</a>
</div>
<!-- /wp:column -->

</div>
<!-- /wp:columns -->

<!-- wp:separator {{"className":"is-style-wide"}} -->
<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>
<!-- /wp:separator -->

<!-- wp:heading {{"level":2,"style":{{"typography":{{"fontSize":"1.5rem"}}}}}} -->
<h2 class="wp-block-heading" style="font-size:1.5rem;text-align:center;margin-top:48px;margin-bottom:24px">映画で学ぶ防災</h2>
<!-- /wp:heading -->

<!-- wp:paragraph {{"align":"center"}} -->
<p class="has-text-align-center" style="color:#64748b;margin-bottom:32px">実際の災害を描いた映画やドラマで、防災知識と危機対応を学ぼう</p>
<!-- /wp:paragraph -->

<!-- wp:group {{"style":{{"color":{{"background":"#f3e8ff"}},"border":{{"radius":"12px"}},"spacing":{{"padding":{{"top":"32px","bottom":"32px","left":"24px","right":"24px"}}}}}}}} -->
<div class="wp-block-group" style="background-color:#f3e8ff;border-radius:12px;padding:32px 24px;margin-bottom:48px">
<p style="text-align:center;font-size:2.5em;margin-bottom:12px;line-height:1">🎬</p>
<h3 style="text-align:center;color:{navy};margin-bottom:16px;font-size:1.2em">Amazon Prime Video 災害・サバイバル作品特集</h3>
<p style="text-align:center;color:#1e293b;line-height:1.6;margin-bottom:24px">東日本大震災やSan Andreasなど、実際の災害を描いた作品から、防災の本当の意味を学べます。<br>オフライン視聴で、停電時にも視聴可能。</p>
<p style="text-align:center;margin:0">
<a href="{url_prime}" style="display:inline-block;background:{accent};color:#fff;padding:14px 36px;border-radius:25px;font-weight:bold;font-size:1em;text-decoration:none">Prime Video作品特集を見る →</a>
</p>
</div>
<!-- /wp:group -->

<!-- wp:separator {{"className":"is-style-wide"}} -->
<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>
<!-- /wp:separator -->

<!-- wp:heading {{"level":2,"style":{{"typography":{{"fontSize":"1.5rem"}}}}}} -->
<h2 class="wp-block-heading" style="font-size:1.5rem;text-align:center;margin-top:48px;margin-bottom:24px">まず読むべき記事 TOP3</h2>
<!-- /wp:heading -->

<!-- wp:columns {{"style":{{"spacing":{{"blockGap":"16px"}}}}}} -->
<div class="wp-block-columns" style="margin-bottom:48px">

<!-- wp:column -->
<div class="wp-block-column" style="background:#fff;border-radius:10px;padding:24px;box-shadow:0 1px 6px rgba(0,0,0,0.06)">
<span style="background:{accent};color:#fff;font-size:0.75em;padding:3px 10px;border-radius:4px;font-weight:bold">人気 No.1</span>
<h4 style="margin-top:12px;font-size:0.95em;line-height:1.5"><a href="{url_start}" style="color:{navy};text-decoration:none">防災グッズ何から揃える？<br>優先順位と予算別プラン</a></h4>
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column" style="background:#fff;border-radius:10px;padding:24px;box-shadow:0 1px 6px rgba(0,0,0,0.06)">
<span style="background:{navy};color:#fff;font-size:0.75em;padding:3px 10px;border-radius:4px;font-weight:bold">高単価</span>
<h4 style="margin-top:12px;font-size:0.95em;line-height:1.5"><a href="{url_portable}" style="color:{navy};text-decoration:none">防災用ポータブル電源<br>おすすめ5選【2026年版】</a></h4>
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column" style="background:#fff;border-radius:10px;padding:24px;box-shadow:0 1px 6px rgba(0,0,0,0.06)">
<span style="background:#059669;color:#fff;font-size:0.75em;padding:3px 10px;border-radius:4px;font-weight:bold">コスパ◎</span>
<h4 style="margin-top:12px;font-size:0.95em;line-height:1.5"><a href="{url_set}" style="color:{navy};text-decoration:none">防災セットおすすめ比較<br>一人暮らし向け厳選3つ</a></h4>
</div>
<!-- /wp:column -->

</div>
<!-- /wp:columns -->

<!-- wp:separator {{"className":"is-style-wide"}} -->
<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>
<!-- /wp:separator -->

<!-- wp:heading {{"level":2,"style":{{"typography":{{"fontSize":"1.5rem"}}}}}} -->
<h2 class="wp-block-heading" style="font-size:1.5rem;text-align:center;margin-top:48px;margin-bottom:8px">予算別・おすすめスタートプラン</h2>
<!-- /wp:heading -->

<!-- wp:paragraph {{"align":"center"}} -->
<p class="has-text-align-center" style="color:#64748b;margin-bottom:28px">完璧を目指さなくてOK。今日1つ買うだけで昨日より安全に。</p>
<!-- /wp:paragraph -->

<!-- wp:table {{"hasFixedLayout":true,"className":"is-style-stripes"}} -->
<figure class="wp-block-table is-style-stripes" style="margin-bottom:48px"><table style="border-collapse:collapse;width:100%;font-size:0.95em"><thead><tr style="background:{navy};color:#fff"><th style="padding:14px 16px">予算</th><th style="padding:14px 16px">買うもの</th><th style="padding:14px 16px">備えレベル</th></tr></thead><tbody><tr style="background:#fffbeb"><td style="padding:12px 16px;font-weight:bold">5,000円</td><td style="padding:12px 16px">水2L×6本 + 簡易トイレ15回分 + モバイルバッテリー</td><td style="padding:12px 16px">★ 最低限クリア</td></tr><tr><td style="padding:12px 16px;font-weight:bold">15,000円</td><td style="padding:12px 16px">上記 + 非常食3日分 + ラジオライト + カセットコンロ</td><td style="padding:12px 16px">★★ しっかり備え</td></tr><tr><td style="padding:12px 16px;font-weight:bold">50,000円</td><td style="padding:12px 16px">上記 + 防災セット + ポータブル電源</td><td style="padding:12px 16px">★★★ 万全</td></tr></tbody></table></figure>
<!-- /wp:table -->

<!-- wp:group {{"style":{{"color":{{"background":"{navy}"}},"border":{{"radius":"12px"}},"spacing":{{"padding":{{"top":"40px","bottom":"40px","left":"24px","right":"24px"}}}}}}}} -->
<div class="wp-block-group" style="background-color:{navy};border-radius:12px;padding:40px 24px;text-align:center;margin-bottom:48px">
<h2 style="color:#fff;margin-bottom:12px;font-size:1.4em">まず何から買えばいい？</h2>
<p style="color:rgba(255,255,255,0.8);margin-bottom:24px;font-size:0.95em">予算5,000円から始める防災。優先順位つきで解説します。</p>
<a href="{url_start}" style="display:inline-block;background:{accent};color:#fff;padding:14px 36px;border-radius:25px;font-weight:bold;font-size:1em;text-decoration:none">予算別おすすめプランを見る →</a>
</div>
<!-- /wp:group -->

<!-- wp:separator {{"className":"is-style-wide"}} -->
<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>
<!-- /wp:separator -->

<!-- wp:group {{"style":{{"color":{{"background":"#f0f9ff"}},"border":{{"radius":"12px"}},"spacing":{{"padding":{{"top":"32px","bottom":"32px","left":"24px","right":"24px"}}}}}}}} -->
<div class="wp-block-group" style="background-color:#f0f9ff;border-radius:12px;padding:32px 24px;margin-bottom:24px">
<h2 style="margin-bottom:16px;font-size:1.3em">このサイトについて</h2>
<p style="line-height:1.8;margin-bottom:8px">「防災グッズ完全ガイド」は、一人暮らしの20〜30代に向けた防災情報サイトです。</p>
<p style="line-height:1.8;margin-bottom:8px">「何を買えばいいか分からない」「面倒で後回しにしてしまう」——そんな方のために、本当に必要なものだけを、予算と優先順位をつけて紹介しています。</p>
<p style="line-height:1.8">すべての記事で実際に商品を比較検証し、一人暮らしの視点で正直にレビューしています。</p>
</div>
<!-- /wp:group -->

<!-- wp:paragraph {{"align":"center"}} -->
<p class="has-text-align-center" style="margin-top:16px"><a href="{url_blog}" style="color:{accent};font-weight:bold;text-decoration:none">すべての記事を見る →</a></p>
<!-- /wp:paragraph -->
'''

resp = requests.post(
    f'{WP_URL}/wp-json/wp/v2/pages/371',
    json={
        'title': '防災グッズ完全ガイド｜一人暮らしのための備えと対策',
        'content': new_content,
    },
    headers=wp_auth(),
)
resp.raise_for_status()
d = resp.json()
print(f"✅ フロントページ更新完了")
print(f"   タイトル: {d['title']['rendered']}")

# Update Cocoon front page settings via theme_mods
print("\n⚙️  Cocoon フロントページ設定を更新...")

API_URL = f'{WP_URL}/wp-json/cocoon-cfg/v1'

r = requests.get(
    f'{API_URL}/get/theme_mods_cocoon-child-master',
    headers=wp_auth()
)
r.raise_for_status()
theme_mods = r.json().get('value', {})

# フロントページ関連のCocoon設定
front_settings = {
    'front_page_type': 'index',
    'front_page_title_format': 'sitename_tagline',
    'free_front_page_title': '',
    # アピールエリア: トップページのみ表示（Cocoon設定で管理）
    'appeal_area_display_type': 'front_page_only',
    'appeal_area_title': '一人暮らしの防災、何から始める？',
    'appeal_area_message': '初めてでも迷わない。シーン別の防災準備ガイド',
    'appeal_area_button_message': '何から揃える？ 優先順位を見る →',
    'appeal_area_button_url': url_start,
    'appeal_area_button_target': '_self',
    'appeal_area_background_color': navy,
    'appeal_area_button_background_color': accent,
    'appeal_area_height': '280',
    'appeal_area_content_visible': '1',
    # カルーセル: トップページのみ
    'carousel_display_type': 'front_page_only',
    'carousel_max_count': '12',
    'carousel_orderby': 'rand',
    'carousel_autoplay_enable': '1',
    'carousel_autoplay_interval': '5',
    'carousel_card_border_visible': '1',
    'carousel_smartphone_visible': '1',
    # おすすめカード: トップページのみ
    'recommended_cards_display_type': 'front_page_only',
    'recommended_cards_style': 'center_white_title',
    'recommended_cards_margin_enable': '1',
    'recommended_cards_both_sides_margin_enable': '1',
    # 通知エリア
    'notice_area_visible': '1',
    'notice_type': 'notice',
    'notice_area_message': '防災グッズの準備は万全ですか？ まずは何から揃えるかチェック！',
    'notice_area_url': url_start,
    'notice_area_background_color': '#fef3c7',
    'notice_area_text_color': '#92400e',
    # メタ情報
    'front_page_meta_description': '一人暮らしの防災準備を徹底ガイド。ポータブル電源・非常食・防災セット・簡易トイレなど、本当に必要な防災グッズを予算別・優先順位つきで紹介。初めてでも迷わない防災情報サイト。',
    'front_page_meta_keywords': '防災グッズ,一人暮らし,防災セット,非常食,ポータブル電源,簡易トイレ,保存水,備蓄',
}

theme_mods.update(front_settings)

result = requests.post(
    f'{API_URL}/set',
    json={'theme_mods_cocoon-child-master': theme_mods},
    headers=wp_auth()
)
result.raise_for_status()
print(f"   theme_mods更新: {result.json()}")

print("\n🎉 フロントページ設定の全面更新が完了しました！")
print("   - 固定ページ(ID:371): コンテンツ刷新")
print("   - 投稿一覧ページ(ID:439): /blog/ に設定")
print("   - Cocoonアピールエリア: 防災ガイドCTA")
print("   - Cocoonカルーセル: 記事自動スライド")
print("   - Cocoon通知バー: 防災グッズCTA")
print("   - SEOメタ情報: 防災キーワード最適化")
