"""ウィジェットを防災ブログ向けに一括設定"""
import os, base64, json, requests

WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']

def wp_auth():
    creds = f'{WP_USER}:{WP_PASSWORD}'
    token = base64.b64encode(creds.encode()).decode()
    return {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}

API = f'{WP_URL}/wp-json/wp/v2/widgets'

# 記事URL
url_start    = 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e3%82%b0%e3%83%83%e3%82%ba%e4%bd%95%e3%81%8b%e3%82%89%e6%8f%83%e3%81%88%e3%82%8b%ef%bc%9f%e5%84%aa%e5%85%88%e9%a0%86%e4%bd%8d%e3%81%a8%e4%ba%88%e7%ae%97%e5%88%a5%e3%83%97%e3%83%a9/'
url_set      = 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e3%82%bb%e3%83%83%e3%83%88%e3%81%8a%e3%81%99%e3%81%99%e3%82%81%e6%af%94%e8%bc%83%ef%bd%9c%e4%b8%80%e4%ba%ba%e6%9a%ae%e3%82%89%e3%81%97%e5%90%91%e3%81%91%e5%8e%b3%e9%81%b83%e3%81%a4/'
url_portable = 'https://www.aoktik.online/%e3%80%902026%e5%b9%b4%e7%89%88%e3%80%91%e9%98%b2%e7%81%bd%e7%94%a8%e3%83%9d%e3%83%bc%e3%82%bf%e3%83%96%e3%83%ab%e9%9b%bb%e6%ba%90%e3%81%8a%e3%81%99%e3%81%99%e3%82%815%e9%81%b8%ef%bd%9c%e5%81%9c/'
url_food     = 'https://www.aoktik.online/%e9%9d%9e%e5%b8%b8%e9%a3%9f%e3%81%8a%e3%81%99%e3%81%99%e3%82%8110%e9%81%b8%ef%bd%9c%e4%b8%80%e4%ba%ba%e6%9a%ae%e3%82%89%e3%81%97%e5%90%91%e3%81%91%e3%83%bb5%e5%b9%b4%e4%bf%9d%e5%ad%98%e3%81%a7/'
url_toilet   = 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e7%94%a8%e7%b0%a1%e6%98%93%e3%83%88%e3%82%a4%e3%83%ac%e3%81%8a%e3%81%99%e3%81%99%e3%82%815%e9%81%b8%ef%bd%9c%e5%ae%9f%e9%9a%9b%e3%81%ab%e4%bd%bf%e3%81%a3%e3%81%a6%e5%88%86%e3%81%8b/'
url_water    = 'https://www.aoktik.online/%e7%81%bd%e5%ae%b3%e7%94%a8%e4%bf%9d%e5%ad%98%e6%b0%b4%e3%81%ae%e9%81%b8%e3%81%b3%e6%96%b9%e3%81%a8%e3%81%8a%e3%81%99%e3%81%99%e3%82%81%e5%95%86%e5%93%81/'
url_prime    = 'https://www.aoktik.online/prime-video-disaster-5/'

navy = '#1a365d'
accent = '#e94560'
text = '#333333'


def create_widget(id_base, sidebar, instance_raw):
    r = requests.post(API, json={
        'id_base': id_base,
        'sidebar': sidebar,
        'instance': {'raw': instance_raw},
    }, headers=wp_auth())
    if r.status_code == 400 and 'raw' in r.text:
        # Cocoon widgets don't support raw - try encoded format
        return None, None
    r.raise_for_status()
    d = r.json()
    return d['id'], d['sidebar']


def create_block_widget(sidebar, block_content):
    r = requests.post(API, json={
        'id_base': 'block',
        'sidebar': sidebar,
        'instance': {'raw': {'content': block_content}},
    }, headers=wp_auth())
    r.raise_for_status()
    d = r.json()
    return d['id'], d['sidebar']


def html_widget(sidebar, title, content):
    return create_widget('custom_html', sidebar, {
        'title': title,
        'content': content,
    })


def clear_sidebar(sidebar_id):
    r = requests.get(f'{WP_URL}/wp-json/wp/v2/sidebars/{sidebar_id}?context=edit',
                     headers=wp_auth())
    if r.status_code != 200:
        return
    data = r.json()
    for wid in data.get('widgets', []):
        requests.post(f'{API}/{wid}', json={'sidebar': 'wp_inactive_widgets'},
                      headers=wp_auth())


def main():
    print("=" * 60)
    print("🧩 ウィジェットを防災ブログ向けに一括設定")
    print("=" * 60)

    # まず既存ウィジェットをすべてクリア
    sidebars_to_clear = [
        'sidebar', 'sidebar-scroll', 'content-top', 'content-bottom',
        'single-content-bottom', 'below-single-sns-buttons',
        'footer-left', 'footer-center', 'footer-right',
        'footer-mobile', '404-page', 'index-top',
    ]
    print("\n🗑️  既存ウィジェットをクリア...")
    for sb in sidebars_to_clear:
        clear_sidebar(sb)
    print("   完了")

    created = []

    # ============================================================
    # 1. サイドバー（メイン）
    # ============================================================
    print("\n📋 サイドバー（メイン）")

    # 1-1. 検索
    wid, sb = create_widget('search', 'sidebar', {'title': '記事を検索'})
    print(f"   ✅ {wid} | 検索")
    created.append(wid)

    # 1-2. プロフィール（カスタムHTML）
    profile_html = f'''<div style="text-align:center;padding:20px 16px;background:#fff;border-radius:8px">
<div style="width:80px;height:80px;border-radius:50%;background:{navy};margin:0 auto 12px;display:flex;align-items:center;justify-content:center">
<span style="color:#fff;font-size:2em">🛡️</span>
</div>
<p style="font-weight:bold;font-size:1em;margin-bottom:6px;color:{navy}">防災グッズ完全ガイド</p>
<p style="font-size:0.82em;color:#64748b;line-height:1.6">一人暮らしの20〜30代に向けた防災情報サイト。本当に必要なものだけを予算と優先順位つきで紹介します。</p>
</div>'''
    wid, sb = html_widget('sidebar', '', profile_html)
    print(f"   ✅ {wid} | プロフィール")
    created.append(wid)

    # 1-3. 新着記事（標準WordPress）
    wid, sb = create_widget('recent-posts', 'sidebar', {
        'title': '新着記事',
        'number': 5,
        'show_date': True,
    })
    print(f"   ✅ {wid} | 新着記事")
    created.append(wid)

    # 1-4. カテゴリー
    wid, sb = create_widget('categories', 'sidebar', {
        'title': 'カテゴリー',
        'count': 1,
        'hierarchical': 1,
        'dropdown': 0,
    })
    print(f"   ✅ {wid} | カテゴリー")
    created.append(wid)

    # 1-5. おすすめ記事リンク（カスタムHTML）
    recommend_html = f'''<div style="background:#fff;border-radius:8px;padding:16px">
<ul style="list-style:none;padding:0;margin:0">
<li style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #f1f5f9">
<a href="{url_start}" style="color:{text};text-decoration:none;font-size:0.9em;font-weight:500;display:block;line-height:1.5">
<span style="color:{accent};font-weight:bold">1.</span> 防災グッズ何から揃える？
</a></li>
<li style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #f1f5f9">
<a href="{url_portable}" style="color:{text};text-decoration:none;font-size:0.9em;font-weight:500;display:block;line-height:1.5">
<span style="color:{accent};font-weight:bold">2.</span> ポータブル電源おすすめ5選
</a></li>
<li style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #f1f5f9">
<a href="{url_set}" style="color:{text};text-decoration:none;font-size:0.9em;font-weight:500;display:block;line-height:1.5">
<span style="color:{accent};font-weight:bold">3.</span> 防災セットおすすめ比較
</a></li>
<li style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #f1f5f9">
<a href="{url_food}" style="color:{text};text-decoration:none;font-size:0.9em;font-weight:500;display:block;line-height:1.5">
<span style="color:{accent};font-weight:bold">4.</span> 非常食おすすめ10選
</a></li>
<li>
<a href="{url_toilet}" style="color:{text};text-decoration:none;font-size:0.9em;font-weight:500;display:block;line-height:1.5">
<span style="color:{accent};font-weight:bold">5.</span> 簡易トイレおすすめ5選
</a></li>
</ul>
</div>'''
    wid, sb = html_widget('sidebar', 'おすすめ記事', recommend_html)
    print(f"   ✅ {wid} | おすすめ記事")
    created.append(wid)

    # 1-6. 防災CTA
    cta_html = f'''<div style="background:linear-gradient(135deg,{navy},#0f3460);border-radius:10px;padding:24px;text-align:center">
<p style="color:#fff;font-weight:bold;font-size:1.05em;margin-bottom:8px">まず何から揃える？</p>
<p style="color:rgba(255,255,255,0.8);font-size:0.85em;margin-bottom:16px">予算5,000円から始める防災</p>
<a href="{url_start}" style="display:inline-block;background:{accent};color:#fff;padding:10px 24px;border-radius:20px;font-weight:bold;font-size:0.9em;text-decoration:none">優先順位を見る →</a>
</div>'''
    wid, sb = html_widget('sidebar', '', cta_html)
    print(f"   ✅ {wid} | 防災CTA")
    created.append(wid)

    # 1-7. Prime Video CTA
    prime_cta_html = f'''<style>
    .prime-widget {{
        background: linear-gradient(135deg, #0f172a, #1e1a4d);
        border-radius: 10px;
        padding: 24px;
        text-align: center;
        border: 1px solid #2d2955;
    }}
    .prime-widget p {{
        color: #fff;
        font-weight: bold;
        font-size: 1.05em;
        margin-bottom: 8px;
    }}
    .prime-widget .subtitle {{
        color: rgba(255,255,255,0.8);
        font-size: 0.85em;
        margin-bottom: 12px;
    }}
    .prime-widget .play-icon {{
        font-size: 2.5em;
        margin-bottom: 8px;
    }}
    .prime-widget a {{
        display: inline-block;
        background: {accent};
        color: #fff;
        padding: 10px 24px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
        text-decoration: none;
        transition: opacity 0.3s;
    }}
    .prime-widget a:hover {{
        opacity: 0.9;
    }}
    </style>
    <div class="prime-widget">
    <div class="play-icon">🎬</div>
    <p>映画で学ぶ防災</p>
    <p class="subtitle">Amazon Prime Video災害作品特集</p>
    <a href="{url_prime}">作品を見る →</a>
    </div>'''
    wid, sb = html_widget('sidebar', '', prime_cta_html)
    print(f"   ✅ {wid} | Prime Video CTA")
    created.append(wid)

    # ============================================================
    # 2. サイドバースクロール追従
    # ============================================================
    print("\n📋 サイドバースクロール追従")

    # 目次（Cocoon toc ウィジェット非対応のため、ブロックで代替）
    toc_block = '<!-- wp:cocoon-blocks/toc {"title":"目次","depth":3} /-->'
    wid, sb = create_block_widget('sidebar-scroll', toc_block)
    print(f"   ✅ {wid} | 目次ブロック")
    created.append(wid)

    # ============================================================
    # 3. 投稿本文下
    # ============================================================
    print("\n📋 投稿本文下")

    cta_bottom_html = f'''<div style="background:#f0f9ff;border:2px solid {navy};border-radius:10px;padding:24px;text-align:center;margin:24px 0">
<p style="font-weight:bold;font-size:1.1em;color:{navy};margin-bottom:8px">防災セットを比較するなら</p>
<p style="font-size:0.9em;color:#64748b;margin-bottom:16px">一人暮らし向け厳選3つを徹底レビュー</p>
<a href="{url_set}" style="display:inline-block;background:{accent};color:#fff;padding:12px 28px;border-radius:25px;font-weight:bold;font-size:0.95em;text-decoration:none">防災セットおすすめ比較 →</a>
</div>'''
    wid, sb = html_widget('single-content-bottom', '', cta_bottom_html)
    print(f"   ✅ {wid} | 記事下CTA")
    created.append(wid)

    # ============================================================
    # 4. フッター左
    # ============================================================
    print("\n📋 フッター左")

    footer_about_html = f'''<div style="color:#cbd5e1">
<p style="font-weight:bold;font-size:1.05em;color:#fff;margin-bottom:10px">防災グッズ完全ガイド</p>
<p style="font-size:0.85em;line-height:1.7">一人暮らしの20〜30代に向けた防災情報サイト。本当に必要なものだけを、予算と優先順位をつけて紹介しています。</p>
</div>'''
    wid, sb = html_widget('footer-left', '', footer_about_html)
    print(f"   ✅ {wid} | フッターAbout")
    created.append(wid)

    # ============================================================
    # 5. フッター中央
    # ============================================================
    print("\n📋 フッター中央")

    wid, sb = create_widget('categories', 'footer-center', {
        'title': 'カテゴリー',
        'count': 1,
        'hierarchical': 1,
        'dropdown': 0,
    })
    print(f"   ✅ {wid} | フッターカテゴリー")
    created.append(wid)

    # ============================================================
    # 6. フッター右
    # ============================================================
    print("\n📋 フッター右")

    wid, sb = create_widget('recent-posts', 'footer-right', {
        'title': '新着記事',
        'number': 3,
        'show_date': True,
    })
    print(f"   ✅ {wid} | フッター新着記事")
    created.append(wid)

    # ============================================================
    # 7. フッター（モバイル用）
    # ============================================================
    print("\n📋 フッター（モバイル用）")

    wid, sb = create_widget('recent-posts', 'footer-mobile', {
        'title': '新着記事',
        'number': 3,
        'show_date': True,
    })
    print(f"   ✅ {wid} | モバイルフッター新着")
    created.append(wid)

    mobile_cta_html = f'''<div style="text-align:center;padding:16px">
<a href="{url_start}" style="display:inline-block;background:{accent};color:#fff;padding:12px 24px;border-radius:20px;font-weight:bold;font-size:0.9em;text-decoration:none;width:100%;box-sizing:border-box">防災グッズ 何から揃える？ →</a>
</div>'''
    wid, sb = html_widget('footer-mobile', '', mobile_cta_html)
    print(f"   ✅ {wid} | モバイルCTA")
    created.append(wid)

    # ============================================================
    # 8. 404ページ
    # ============================================================
    print("\n📋 404ページ")

    wid, sb = create_widget('search', '404-page', {'title': '記事を検索'})
    print(f"   ✅ {wid} | 404検索")
    created.append(wid)

    page404_html = f'''<div style="margin:20px 0">
<h3 style="font-size:1em;margin-bottom:16px;color:{navy}">おすすめ記事</h3>
<ul style="list-style:none;padding:0">
<li style="margin-bottom:10px"><a href="{url_start}" style="color:{accent};text-decoration:none;font-weight:500">防災グッズ何から揃える？優先順位ガイド</a></li>
<li style="margin-bottom:10px"><a href="{url_portable}" style="color:{accent};text-decoration:none;font-weight:500">ポータブル電源おすすめ5選</a></li>
<li style="margin-bottom:10px"><a href="{url_set}" style="color:{accent};text-decoration:none;font-weight:500">防災セットおすすめ比較</a></li>
<li style="margin-bottom:10px"><a href="{url_food}" style="color:{accent};text-decoration:none;font-weight:500">非常食おすすめ10選</a></li>
<li style="margin-bottom:10px"><a href="{url_toilet}" style="color:{accent};text-decoration:none;font-weight:500">簡易トイレおすすめ5選</a></li>
<li><a href="{url_water}" style="color:{accent};text-decoration:none;font-weight:500">保存水おすすめ5選</a></li>
</ul>
</div>'''
    wid, sb = html_widget('404-page', '', page404_html)
    print(f"   ✅ {wid} | 404おすすめ記事")
    created.append(wid)

    wid, sb = create_widget('categories', '404-page', {
        'title': 'カテゴリーから探す',
        'count': 1,
        'hierarchical': 1,
        'dropdown': 0,
    })
    print(f"   ✅ {wid} | 404カテゴリー")
    created.append(wid)

    # ============================================================
    # 9. インデックスリストトップ
    # ============================================================
    print("\n📋 インデックスリストトップ")

    index_cta_html = f'''<div style="background:#fffbeb;border:1px solid #fbbf24;border-radius:8px;padding:16px;text-align:center;margin-bottom:20px">
<p style="font-size:0.95em;margin:0"><strong>初めての方へ：</strong> <a href="{url_start}" style="color:{accent};font-weight:bold;text-decoration:none">防災グッズ何から揃える？ 優先順位ガイド →</a></p>
</div>'''
    wid, sb = html_widget('index-top', '', index_cta_html)
    print(f"   ✅ {wid} | インデックス上部CTA")
    created.append(wid)

    # ============================================================
    print(f"\n{'=' * 60}")
    print(f"🎉 合計 {len(created)} 個のウィジェットを設定完了！")
    print("=" * 60)
    print("\n配置サマリー:")
    print("  📌 サイドバー: 検索 / プロフィール / 人気記事 / 新着記事 / カテゴリー / 防災CTA")
    print("  📌 サイドバー追従: 目次")
    print("  📌 投稿本文下: 防災セットCTA")
    print("  📌 投稿SNSボタン下: ナビカード")
    print("  📌 フッター左: サイト紹介")
    print("  📌 フッター中央: カテゴリー")
    print("  📌 フッター右: 新着記事")
    print("  📌 フッターモバイル: 新着記事 / CTA")
    print("  📌 404ページ: 検索 / 人気記事 / カテゴリー")
    print("  📌 インデックストップ: 初心者向けCTA")


if __name__ == '__main__':
    main()
