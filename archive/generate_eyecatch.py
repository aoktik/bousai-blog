"""アイキャッチ画像生成 - 読みたくなるデザイン・統一テンプレート"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap

OUTPUT_DIR = Path(__file__).parent / "data" / "eyecatch"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1200, 630
NAVY   = (26, 54, 93)
ACCENT = (233, 69, 96)
WHITE  = (255, 255, 255)
LIGHT  = (248, 250, 252)
DARK   = (30, 41, 59)
GOLD   = (255, 193, 7)

# フォントロード
def load_font(size):
    paths = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]
    for p in paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

font_title  = load_font(56)
font_sub    = load_font(30)
font_cat    = load_font(24)
font_brand  = load_font(22)
font_icon   = load_font(100)

def wrap_text(text, max_chars=18):
    lines = []
    for line in text.split('\n'):
        while len(line) > max_chars:
            lines.append(line[:max_chars])
            line = line[max_chars:]
        lines.append(line)
    return lines

def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0+radius, y0, x1-radius, y1], fill=fill)
    draw.rectangle([x0, y0+radius, x1, y1-radius], fill=fill)
    draw.pieslice([x0, y0, x0+2*radius, y0+2*radius], 180, 270, fill=fill)
    draw.pieslice([x1-2*radius, y0, x1, y0+2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1-2*radius, x0+2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1-2*radius, y1-2*radius, x1, y1], 0, 90, fill=fill)

def generate(title, subtitle, category, icon, filename):
    img = Image.new('RGB', (W, H), color=NAVY)
    draw = ImageDraw.Draw(img)

    # 下部のアクセントライン
    draw.rectangle([0, H-8, W, H], fill=ACCENT)

    # 左の縦アクセントバー
    draw.rectangle([0, 0, 8, H], fill=ACCENT)

    # アイコン（右上に大きく、半透明風）
    icon_color = (40, 70, 120)  # NAVYよりやや明るい
    try:
        bbox = draw.textbbox((0,0), icon, font=font_icon)
        iw = bbox[2] - bbox[0]
        ih = bbox[3] - bbox[1]
        draw.text((W - iw - 60, 40), icon, font=font_icon, fill=icon_color)
    except:
        pass

    # カテゴリバッジ
    cat_text = f"  {category}  "
    try:
        cat_bbox = draw.textbbox((0,0), cat_text, font=font_cat)
        cat_w = cat_bbox[2] - cat_bbox[0]
        cat_h = cat_bbox[3] - cat_bbox[1]
    except:
        cat_w, cat_h = 200, 30
    badge_x, badge_y = 40, 40
    draw_rounded_rect(draw, (badge_x, badge_y, badge_x+cat_w+20, badge_y+cat_h+14), 6, ACCENT)
    draw.text((badge_x+10, badge_y+7), cat_text, font=font_cat, fill=WHITE)

    # タイトル（中央左寄せ）
    title_lines = wrap_text(title, max_chars=18)
    line_h = 68
    total_h = len(title_lines) * line_h
    start_y = max(120, (H - total_h) // 2 - 20)

    for i, line in enumerate(title_lines):
        y = start_y + i * line_h
        # テキストシャドウ
        draw.text((42, y+2), line, font=font_title, fill=(10, 30, 60))
        draw.text((40, y), line, font=font_title, fill=WHITE)

    # サブタイトル（タイトル下）
    sub_y = start_y + len(title_lines) * line_h + 15
    draw.text((42, sub_y), subtitle, font=font_sub, fill=GOLD)

    # ブランド（下部）
    draw.text((40, H-50), "防災グッズ完全ガイド  |  aoktik.online", font=font_brand, fill=(140, 160, 190))

    # 保存
    out = OUTPUT_DIR / filename
    img.save(str(out), 'PNG', quality=95)
    print(f"✓ {filename}")
    return str(out)


# ============================================================
# 全11記事のアイキャッチ画像を生成
# ============================================================
articles = [
    # 既存6記事
    {
        "id": 414,
        "title": "防災グッズ\n何から揃える？",
        "subtitle": "優先順位と予算別プラン｜一人暮らし初心者向け",
        "category": "防災の基礎知識",
        "icon": "📋",
        "file": "eyecatch_414.png"
    },
    {
        "id": 409,
        "title": "防災用ポータブル電源\nおすすめ5選",
        "subtitle": "停電3日を乗り切る実力派を徹底比較【2026年版】",
        "category": "防災グッズレビュー",
        "icon": "🔋",
        "file": "eyecatch_409.png"
    },
    {
        "id": 411,
        "title": "非常食おすすめ10選",
        "subtitle": "5年保存で本当に美味しいのはどれ？",
        "category": "防災グッズレビュー",
        "icon": "🍚",
        "file": "eyecatch_411.png"
    },
    {
        "id": 412,
        "title": "防災セット\nおすすめ比較",
        "subtitle": "一人暮らし向け厳選3つを徹底レビュー",
        "category": "防災グッズレビュー",
        "icon": "🎒",
        "file": "eyecatch_412.png"
    },
    {
        "id": 413,
        "title": "防災用簡易トイレ\nおすすめ5選",
        "subtitle": "実際に使って分かった選び方のコツ",
        "category": "防災グッズレビュー",
        "icon": "🚽",
        "file": "eyecatch_413.png"
    },
    {
        "id": 380,
        "title": "防災用保存水\nおすすめ5選",
        "subtitle": "長期保存できる安心の備蓄水【2026年版】",
        "category": "防災グッズレビュー",
        "icon": "💧",
        "file": "eyecatch_380.png"
    },
    # 新規5記事
    {
        "id": 482,
        "title": "女性のための\n防災グッズ選び",
        "subtitle": "避難所で本当に必要なもの完全ガイド",
        "category": "防災グッズレビュー",
        "icon": "👩",
        "file": "eyecatch_482.png"
    },
    {
        "id": 483,
        "title": "子どもを守る\n防災対策",
        "subtitle": "年齢別おすすめグッズと備蓄のコツ",
        "category": "防災グッズレビュー",
        "icon": "👶",
        "file": "eyecatch_483.png"
    },
    {
        "id": 484,
        "title": "ペットとの防災",
        "subtitle": "犬・猫の飼い主が備えるべきグッズと避難の知識",
        "category": "防災グッズレビュー",
        "icon": "🐾",
        "file": "eyecatch_484.png"
    },
    {
        "id": 485,
        "title": "マンションの\n防災対策",
        "subtitle": "集合住宅特有のリスクと対処法",
        "category": "防災の基礎知識",
        "icon": "🏢",
        "file": "eyecatch_485.png"
    },
    {
        "id": 486,
        "title": "ローリングストック\n入門",
        "subtitle": "月+500円で始める「期限切れゼロ」の備蓄術",
        "category": "防災の基礎知識",
        "icon": "🔄",
        "file": "eyecatch_486.png"
    },
]

print("🎨 アイキャッチ画像を生成中...\n")
for a in articles:
    generate(a["title"], a["subtitle"], a["category"], a["icon"], a["file"])

print(f"\n✓ {len(articles)}枚の生成完了！")
