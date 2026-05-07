"""Amazon Prime Video 災害作品紹介ページ生成・投稿"""
import os, base64, json, requests, struct, zlib, math, time

WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']
A8_LINK = os.environ.get('A8_PRIME_VIDEO_LINK', '')

if not A8_LINK:
    raise ValueError('環境変数 A8_PRIME_VIDEO_LINK が設定されていません')

def wp_auth():
    creds = f'{WP_USER}:{WP_PASSWORD}'
    token = base64.b64encode(creds.encode()).decode()
    return {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}

# === アイキャッチ画像生成 ===

W, H = 1200, 630

def create_png(width, height, pixels):
    def chunk(ct, data):
        c = ct + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    raw = b''
    for row in pixels:
        raw += b'\x00'
        for r, g, b in row:
            raw += struct.pack('BBB', max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b)))
    idat = chunk(b'IDAT', zlib.compress(raw, 9))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def blend(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def new_canvas():
    return [[(0,0,0) for _ in range(W)] for _ in range(H)]

def fill_gradient(px, c1, c2, angle_deg=135):
    rgb1, rgb2 = hex_rgb(c1), hex_rgb(c2)
    a = math.radians(angle_deg)
    cos_a, sin_a = math.cos(a), math.sin(a)
    for y in range(H):
        for x in range(W):
            t = (x * cos_a + y * sin_a) / (W * abs(cos_a) + H * abs(sin_a))
            t = max(0, min(1, t))
            px[y][x] = blend(rgb1, rgb2, t)

def draw_circle(px, cx, cy, r, color):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    r2 = r * r
    for y in range(max(0, cy-r), min(H, cy+r+1)):
        dy2 = (y - cy) ** 2
        for x in range(max(0, cx-r), min(W, cx+r+1)):
            if (x-cx)**2 + dy2 <= r2:
                px[y][x] = rgb

def draw_rect(px, x1, y1, x2, y2, color):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    for y in range(max(0, y1), min(H, y2)):
        for x in range(max(0, x1), min(W, x2)):
            px[y][x] = rgb

def draw_rounded_rect(px, x1, y1, x2, y2, r, color):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    for y in range(max(0, y1), min(H, y2)):
        for x in range(max(0, x1), min(W, x2)):
            ok = True
            if x < x1+r and y < y1+r:
                ok = (x-(x1+r))**2 + (y-(y1+r))**2 <= r*r
            elif x > x2-r and y < y1+r:
                ok = (x-(x2-r))**2 + (y-(y1+r))**2 <= r*r
            elif x < x1+r and y > y2-r:
                ok = (x-(x1+r))**2 + (y-(y2-r))**2 <= r*r
            elif x > x2-r and y > y2-r:
                ok = (x-(x2-r))**2 + (y-(y2-r))**2 <= r*r
            if ok:
                px[y][x] = rgb

def draw_polygon_points(px, points, color):
    """Simple polygon fill using scanline"""
    rgb = hex_rgb(color) if isinstance(color, str) else color
    if not points or len(points) < 3:
        return
    min_y = max(0, min(p[1] for p in points))
    max_y = min(H, max(p[1] for p in points))
    for y in range(min_y, max_y+1):
        intersects = []
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i+1) % len(points)]
            if (p1[1] <= y < p2[1]) or (p2[1] <= y < p1[1]):
                if p2[1] != p1[1]:
                    x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    intersects.append(x)
        intersects.sort()
        for i in range(0, len(intersects), 2):
            if i+1 < len(intersects):
                x1, x2 = int(intersects[i]), int(intersects[i+1])
                for x in range(max(0, x1), min(W, x2+1)):
                    px[y][x] = rgb

def blend_overlay(px, x1, y1, x2, y2, color, alpha):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    for y in range(max(0, y1), min(H, y2)):
        for x in range(max(0, x1), min(W, x2)):
            px[y][x] = blend(px[y][x], rgb, alpha)

def eyecatch_prime_video():
    """Prime Video特集用アイキャッチ画像"""
    pixels = new_canvas()
    # 背景: navy × 濃紫グラデーション（映画的）
    fill_gradient(pixels, '#0f172a', '#1e1a4d', 130)

    # 背景パターン: 微細なドットと波
    for y in range(0, H-150, 40):
        for x in range(0, W, 40):
            if (y//40 + x//40) % 3 == 0:
                draw_circle(pixels, x, y, 2, blend(hex_rgb('#0f172a'), (255,255,255), 0.1))

    # 左側: フィルムストリップ風パターン
    for i in range(5):
        strip_y = 80 + i * 110
        draw_rect(pixels, 30, strip_y, 80, strip_y+80, '#1a2644')
        # フィルムの穴
        for j in range(4):
            draw_circle(pixels, 40, strip_y+15+j*20, 3, '#0f172a')
            draw_circle(pixels, 70, strip_y+15+j*20, 3, '#0f172a')

    # 中央: 大きな再生ボタン
    play_cx, play_cy = 600, 315
    # 背景円
    draw_circle(pixels, play_cx, play_cy, 120, '#e94560')
    draw_circle(pixels, play_cx, play_cy, 105, blend(hex_rgb('#e94560'), (0,0,0), 0.3))
    # 三角形（再生マーク）
    play_points = [(play_cx-35, play_cy-45), (play_cx-35, play_cy+45), (play_cx+50, play_cy)]
    draw_polygon_points(pixels, play_points, '#ffffff')

    # 右側: 映画的な要素
    for i in range(3):
        scene_x = 900 + i * 40
        scene_y = 120 + i * 150
        draw_rounded_rect(pixels, scene_x, scene_y, scene_x+70, scene_y+100, 6,
                         blend(hex_rgb('#1a2644'), (255,255,255), 0.2))

    # 下部テキストエリア
    blend_overlay(pixels, 0, H-150, W, H, '#000000', 0.75)
    draw_rect(pixels, 0, H-150, W, H-146, '#e94560')
    # サイト名エリア
    blend_overlay(pixels, 0, H-40, W, H, '#000000', 0.3)

    return create_png(W, H, pixels)

def upload_image(filename, png_data, max_retries=5):
    for attempt in range(max_retries):
        headers = wp_auth()
        headers['Content-Type'] = 'image/png'
        headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        try:
            r = requests.post(f'{WP_URL}/wp-json/wp/v2/media', headers=headers, data=png_data, timeout=30)
            if r.status_code == 201:
                d = r.json()
                return d['id'], d['source_url']
            elif r.status_code == 403:
                wait = 30 + attempt * 30
                print(f"   ⏳ WAFブロック(403)、{wait}秒待機後リトライ ({attempt+1}/{max_retries})...")
                time.sleep(wait)
                continue
            else:
                print(f"   ❌ HTTP {r.status_code}: {r.text[:200]}")
                if attempt < max_retries - 1:
                    time.sleep(15)
                    continue
                r.raise_for_status()
        except requests.exceptions.Timeout:
            print(f"   ⏳ タイムアウト、15秒待機後リトライ...")
            time.sleep(15)
            continue
    raise Exception(f"アップロード失敗: {filename}")

def set_featured_image(post_id, media_id):
    headers = wp_auth()
    r = requests.post(f'{WP_URL}/wp-json/wp/v2/posts/{post_id}',
                      json={'featured_media': media_id}, headers=headers)
    r.raise_for_status()

# === ページコンテンツ生成 ===

def load_works():
    with open('data/prime_video_works.json', encoding='utf-8') as f:
        return json.load(f)['works']

def get_post_url(post_id):
    """記事IDからURLを取得"""
    urls = {
        409: 'https://www.aoktik.online/【2026年版】防災用ポータブル電源おすすめ5選/',
        411: 'https://www.aoktik.online/非常食おすすめ10選/',
        412: 'https://www.aoktik.online/防災セットおすすめ比較/',
        413: 'https://www.aoktik.online/防災用簡易トイレおすすめ5選/',
        414: 'https://www.aoktik.online/防災グッズ何から揃える/',
        380: 'https://www.aoktik.online/【2026年版】防災用保存水おすすめ5選/',
    }
    return urls.get(post_id, '')

def build_cta_button(text, url=None):
    """CTAボタンHTML（レスポンシブ）"""
    link_url = url or A8_LINK
    return f'''<!-- wp:html -->
<div class="cta-button">
<a href="{link_url}" target="_blank" rel="sponsored noopener">
{text}
</a>
</div>
<!-- /wp:html -->'''

def build_hero_section():
    """ヒーロー + 上部CTA"""
    content = '''<!-- wp:heading {"level":1,"align":"center"} -->
<h1 class="hero-title">震災を学ぶ | Amazon Prime Video 災害・サバイバル作品特集</h1>
<!-- /wp:heading -->

<!-- wp:paragraph {"align":"center"} -->
<p class="hero-subtitle">実際の災害を描いた映画・ドラマで防災意識を高めよう。<br>被害を知り、対策を学び、家族を守る準備をしましょう。</p>
<!-- /wp:paragraph -->

'''
    content += build_cta_button("🎬 Amazon Prime Videoで防災を学ぶ")
    return content

def build_work_card(work, a8_link):
    """作品カード - YouTube画像ギャラリー付き"""

    # YouTube サムネイル画像URLリスト
    gallery_html = ''
    if 'youtube_video_ids' in work and work['youtube_video_ids']:
        # シンプルなHTML画像スライド（Gutenberg互換・レスポンシブ）
        gallery_html = '''<!-- wp:html -->
<div class="gallery-grid">
'''
        for vid in work['youtube_video_ids']:
            thumb_url = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
            gallery_html += f'''<img src="{thumb_url}" alt="{work['title']}" loading="lazy" />
'''
        gallery_html += '''</div>
<!-- /wp:html -->
'''

    related_html = ''
    if work['related_articles']:
        related_html = '<div style="margin-top:12px;padding-top:12px;border-top:1px solid #e2e8f0;">'
        related_html += '<small style="color:#666;">関連記事:</small><br>'
        for idx, article_id in enumerate(work['related_articles'][:2]):  # 最大2つ
            url = get_post_url(article_id)
            if url:
                article_titles = {
                    414: '何から揃える',
                    380: '保存水',
                    409: 'ポータブル電源',
                    413: '簡易トイレ',
                    411: '非常食',
                    412: '防災セット',
                }
                title = article_titles.get(article_id, '記事')
                related_html += f'<a href="{url}" style="color:#2563eb;text-decoration:none;font-size:13px;">→ {title}</a> '
        related_html += '</div>'

    detailed_desc = work.get('detailed_description', work['description'])

    return f'''<!-- wp:group {{"style":{{"spacing":{{"padding":{{"top":"20px","right":"20px","bottom":"20px","left":"20px"}}}}}}, "backgroundColor":"#f8fafc", "borderColor":"#e2e8f0"}} -->
<div class="work-card">

<!-- wp:heading {{"level":3}} -->
<h3>{work['title']} <small style="color:#999;font-size:0.8em;">({work['year']})</small></h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p class="type-label">【{work['type']}】</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>{work['description']}</strong></p>
<!-- /wp:paragraph -->

{gallery_html}

<!-- wp:paragraph -->
<p>{detailed_desc}</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p class="points"><strong>防災学習ポイント:</strong><br>
{' • '.join(work['learning_points'])}</p>
<!-- /wp:paragraph -->

{related_html}

<!-- wp:html -->
<div style="margin-top:14px;text-align:center;">
<a href="{a8_link}" target="_blank" rel="sponsored noopener"
   style="display:inline-block;background:#2563eb;color:#fff;padding:12px 24px;text-decoration:none;border-radius:6px;font-size:clamp(13px,3vw,16px);font-weight:bold;transition:opacity 0.3s;white-space:nowrap;">
Prime Videoで見る
</a>
</div>
<!-- /wp:html -->

</div>
<!-- /wp:group -->'''

def build_category_section(category, works, a8_link):
    """カテゴリセクション"""
    category_jp = {'実災害': '実災害を描いた作品',
                   'サバイバル': '災害サバイバル映画',
                   '防災教育': '防災教育的なドラマ・ドキュメンタリー'}[category]

    category_desc = {
        '実災害': '東日本大震災など、実際の災害を記録・ドラマ化した作品。被害の実態から防災の重要性を学べます。',
        'サバイバル': '地震、津波、火山、隕石など、災害時の対応と人間ドラマを描いた映画。危機的状況での判断力が試されます。',
        '防災教育': '防災知識、気象情報、救助活動など、防災に必要な知識を体系的に学べるドキュメンタリー・ドラマ。',
    }

    content = f'''<!-- wp:heading {{"level":2,"textColor":"","backgroundColor":""}} -->
<h2 style="color:#1a365d;margin-top:40px;border-bottom:3px solid #e94560;padding-bottom:10px;">{category_jp}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p style="color:#1e293b;line-height:1.8;margin-bottom:20px;">{category_desc[category]}</p>
<!-- /wp:paragraph -->

<!-- wp:columns -->'''

    # 1列ずつ作品カードを配置
    for i, work in enumerate(works):
        if i > 0 and i % 2 == 0:
            content += '''<!-- /wp:columns -->

<!-- wp:columns -->'''

        content += f'''<!-- wp:column -->
{build_work_card(work, a8_link)}
<!-- /wp:column -->'''

    content += '''<!-- /wp:columns -->

'''
    return content

def build_related_articles_section():
    """関連防災記事セクション"""
    articles = [
        (414, '防災グッズ何から揃える？', 'https://www.aoktik.online/防災グッズ何から揃える/', '実災害から学ぶ優先順位。まず最低限これだけは準備するべき3つのアイテム。'),
        (380, '防災用保存水おすすめ5選', 'https://www.aoktik.online/【2026年版】防災用保存水おすすめ5選/', '人間は水なしで3日しか生きられません。備蓄水の選び方と保管術を解説。'),
        (409, 'ポータブル電源おすすめ5選', 'https://www.aoktik.online/【2026年版】防災用ポータブル電源おすすめ5選/', '停電への対策はこれ一台。スマホ充電からエアコンまで、実力派を厳選。'),
        (413, '簡易トイレおすすめ5選', 'https://www.aoktik.online/防災用簡易トイレおすすめ5選/', '災害時に最も困るのが「トイレ」。本当に使える製品を実際に使い比べました。'),
        (411, '非常食おすすめ10選', 'https://www.aoktik.online/非常食おすすめ10選/', '「非常食は美味しくない」は昔の話。本当に美味しい5年保存の逸品を厳選。'),
    ]

    content = '''<!-- wp:heading {"level":2,"textColor":"","backgroundColor":""} -->
<h2 style="color:#1a365d;margin-top:40px;border-bottom:3px solid #e94560;padding-bottom:10px;">この機会に防災を備える</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p style="color:#1e293b;line-height:1.8;margin-bottom:20px;">映画やドラマで防災の重要性を学んだら、次は実際に備えをしましょう。以下の記事では、一人暮らし向けに本当に必要な防災グッズを厳選しています。</p>
<!-- /wp:paragraph -->

<!-- wp:columns -->'''

    for i, (aid, title, url, desc) in enumerate(articles):
        if i > 0 and i % 2 == 0:
            content += '''<!-- /wp:columns -->

<!-- wp:columns -->'''

        content += f'''<!-- wp:column -->
<!-- wp:group {{"style":{{"spacing":{{"padding":{{"top":"20px","right":"20px","bottom":"20px","left":"20px"}}}}}}, "backgroundColor":"#f8fafc", "borderColor":"#e2e8f0"}} -->
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:20px;height:100%;">

<!-- wp:heading {{"level":3}} -->
<h3 style="color:#1a365d;margin:0 0 12px 0;">{title}</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p style="color:#1e293b;line-height:1.6;margin:12px 0;font-size:14px;">{desc}</p>
<!-- /wp:paragraph -->

<!-- wp:html -->
<div style="margin-top:16px;">
<a href="{url}" style="display:inline-block;background:#1a365d;color:#fff;padding:10px 16px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:14px;">詳しく読む →</a>
</div>
<!-- /wp:html -->

</div>
<!-- /wp:group -->
<!-- /wp:column -->'''

    content += '''<!-- /wp:columns -->

'''
    return content

def build_faq_section():
    """FAQ セクション"""
    return '''<!-- wp:heading {"level":2,"textColor":"","backgroundColor":""} -->
<h2 style="color:#1a365d;margin-top:40px;border-bottom:3px solid #e94560;padding-bottom:10px;">よくある質問</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3>Prime Video会員のメリットは？</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Amazon Prime Videoは、映画・ドラマ・ドキュメンタリーなど、様々なコンテンツが見放題。月額600円前後で、このような災害関連の作品も豊富に揃っています。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>オフライン視聴はできる？</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>はい、Prime Video会員は多くの作品をダウンロードしてオフライン視聴できます。災害で停電した時など、事前にダウンロードしておけば、インターネットなしで視聴可能です。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>このページの記事は本当？</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>このブログの記事は、筆者が実際に購入・使用した防災グッズの実体験に基づいています。映画で学んだ知識を、実際の製品選びに活かしてください。</p>
<!-- /wp:paragraph -->

'''

def build_page_styles():
    """ページ全体で使用するスタイルをまとめる"""
    return '''<!-- wp:html -->
<style>
/* ===== ヒーロータイトル ===== */
.hero-title {
  color: #1a365d;
  text-align: center;
  font-size: clamp(24px, 6vw, 42px);
  margin: 40px 0 20px 0;
  line-height: 1.3;
  font-weight: bold;
}
.hero-subtitle {
  color: #1e293b;
  text-align: center;
  font-size: clamp(16px, 4vw, 20px);
  margin: 20px auto 30px auto;
  line-height: 1.5;
  max-width: 800px;
}

/* ===== CTAボタン ===== */
.cta-button {
  text-align: center;
  margin: 24px 0;
}
.cta-button a {
  display: inline-block;
  background: #e94560;
  color: #fff;
  padding: clamp(12px, 3vw, 16px) clamp(24px, 5vw, 36px);
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
  font-size: clamp(14px, 3.5vw, 18px);
  transition: opacity 0.3s, transform 0.2s;
  white-space: nowrap;
}
.cta-button a:hover {
  opacity: 0.9;
  transform: scale(1.02);
}

/* ===== YouTubeギャラリー ===== */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin: 16px 0;
  width: 100%;
}
.gallery-grid img {
  width: 100%;
  border-radius: 6px;
  aspect-ratio: 16/9;
  object-fit: cover;
  display: block;
}

/* ===== 作品カード ===== */
.work-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
}
.work-card h3 {
  color: #1a365d;
  margin: 0 0 8px 0;
  font-size: clamp(18px, 5vw, 24px);
}
.work-card p {
  margin: 12px 0;
  color: #1e293b;
  line-height: 1.6;
  font-size: clamp(13px, 3.5vw, 15px);
}
.work-card .type-label {
  color: #999;
  font-size: clamp(12px, 3vw, 14px);
}
.work-card .points {
  color: #666;
  font-size: clamp(12px, 3vw, 13px);
}

/* ===== レスポンシブ調整 ===== */
@media (max-width: 768px) {
  .hero-title {
    margin: 30px 0 15px 0;
  }
  .hero-subtitle {
    margin: 15px auto 20px auto;
  }
  .gallery-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 10px;
  }
  .work-card {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    margin: 25px 0 12px 0;
  }
  .hero-subtitle {
    margin: 10px auto 15px auto;
  }
  .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  .cta-button a {
    width: 90%;
    max-width: 300px;
    display: block;
    margin: 0 auto;
  }
  .work-card {
    padding: 12px;
  }
}
</style>
<!-- /wp:html -->

'''

def build_page_content(works, a8_link):
    """ページコンテンツ全体を組み立て"""
    # ページ全体のスタイルを最上部に追加
    content = build_page_styles()
    content += build_hero_section()

    # カテゴリごとに分類
    categories = {
        '実災害': [w for w in works if w['category'] == '実災害'],
        'サバイバル': [w for w in works if w['category'] == 'サバイバル'],
        '防災教育': [w for w in works if w['category'] == '防災教育'],
    }

    for cat in ['実災害', 'サバイバル', '防災教育']:
        if categories[cat]:
            content += build_category_section(cat, categories[cat], a8_link)

    content += build_related_articles_section()
    content += build_faq_section()

    return content

def main():
    print("=" * 60)
    print("🎬 Amazon Prime Video 災害作品紹介ページ生成")
    print("=" * 60)

    # 作品リスト読み込み
    print("\n📚 作品リスト読み込み中...")
    works = load_works()
    print(f"   ✓ {len(works)}作品を読み込み")

    # ページコンテンツ生成
    print("\n📝 ページコンテンツ生成中...")
    page_content = build_page_content(works, A8_LINK)
    print(f"   ✓ {len(page_content):,} 文字のコンテンツを生成")

    # アイキャッチ画像生成
    print("\n🎨 アイキャッチ画像生成中...")
    png_data = eyecatch_prime_video()
    print(f"   📦 サイズ: {len(png_data):,} bytes")

    # 120秒待機（WAF対策）
    print("\n⏳ WAF回避のため120秒待機...")
    time.sleep(120)

    # 画像アップロード
    print("\n📤 アイキャッチ画像アップロード中...")
    media_id, media_url = upload_image('eyecatch-prime-video.png', png_data)
    print(f"   📎 Media ID: {media_id}")

    # ページ更新（既存ページを上書き）
    print("\n🌐 ページをWordPressに更新中...")
    headers = wp_auth()

    # 既存ページID 460を更新
    existing_page_id = 460

    page_data = {
        'title': '震災を学ぶ | Amazon Prime Video 災害・サバイバル作品特集',
        'content': page_content,
        'status': 'publish',
        'featured_media': media_id,
    }

    r = requests.put(f'{WP_URL}/wp-json/wp/v2/pages/{existing_page_id}', json=page_data, headers=headers, timeout=30)

    if r.status_code != 200:
        print(f"\n   ❌ エラー: {r.status_code}")
        print(f"   レスポンス: {r.text[:500]}")
        raise Exception(f"API Error {r.status_code}")

    r.raise_for_status()
    page = r.json()
    page_id = page['id']
    page_url = page['link']

    print(f"   ✅ ページID: {page_id}")
    print(f"   🔗 URL: {page_url}")

    print(f"\n{'=' * 60}")
    print("✅ ページ生成・投稿が完了しました！")
    print("=" * 60)
    print(f"\n📌 次のステップ:")
    print(f"   1. ページを確認: {page_url}")
    print(f"   2. (オプション) フロントページナビに追加")
    print(f"   3. (オプション) サイドバーウィジェットにCTA追加")
    print(f"\nコマンド:")
    print(f"   python3 update_frontpage_v2.py  # フロントページ更新")
    print(f"   python3 setup_widgets.py        # ウィジェット更新")


if __name__ == '__main__':
    main()
