"""アイキャッチ画像生成モジュール（JPEG固定・WAF対策済み）

すべての画像生成は generate_eyecatch() を経由する。
"""
import secrets
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


# ブランドカラー
NAVY = (26, 54, 93)
ACCENT = (233, 69, 96)
GOLD = (255, 193, 7)
WHITE = (255, 255, 255)
LIGHT = (180, 200, 220)

# 画像仕様
WIDTH = 1200
HEIGHT = 630
PADDING = 60

# フォント候補（優先度順）
_FONT_PATHS = [
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
    '/System/Library/Fonts/ヒラギノ丸ゴ Pro W4.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    'C:\\Windows\\Fonts\\YuGothB.ttc',
]

OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'data' / 'eyecatch'


def _font(size: int) -> ImageFont.FreeTypeFont:
    """システムにある日本語フォントをロード"""
    for path in _FONT_PATHS:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _gradient_bg(img: Image.Image) -> None:
    """ナイビー → アクセント のグラデーション"""
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        r = y / HEIGHT
        c = tuple(int(NAVY[i] * (1 - r * 0.3) + ACCENT[i] * r * 0.3) for i in range(3))
        draw.line([(0, y), (WIDTH, y)], fill=c)


def _wrap(text: str, max_chars: int) -> list:
    """日本語向けの単純な折り返し（文字数ベース）"""
    if len(text) <= max_chars:
        return [text]
    lines = []
    current = ''
    for ch in text:
        if len(current) >= max_chars:
            lines.append(current)
            current = ''
        current += ch
    if current:
        lines.append(current)
    return lines


def generate_eyecatch(
    title: str,
    subtitle: str = '防災グッズ完全ガイド',
    badge: str = 'BOUSAI GUIDE',
    emoji: Optional[str] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """1200×630 のアイキャッチ画像を JPEG で生成し、保存先パスを返す。

    出力: data/eyecatch/<safe-slug>-<random>.jpg
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        safe = ''.join(c if c.isalnum() else '-' for c in title[:24]).strip('-') or 'eyecatch'
        output_path = OUTPUT_DIR / f"{safe}-{secrets.token_hex(3)}.jpg"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new('RGB', (WIDTH, HEIGHT), NAVY)
    _gradient_bg(img)
    draw = ImageDraw.Draw(img)

    # アクセントバー（上下＋左サイド）
    draw.rectangle([(0, 0), (WIDTH, 6)], fill=ACCENT)
    draw.rectangle([(0, HEIGHT - 6), (WIDTH, HEIGHT)], fill=ACCENT)
    draw.rectangle([(0, 0), (8, HEIGHT)], fill=GOLD)

    font_xl = _font(64)
    font_lg = _font(40)
    font_md = _font(28)
    font_sm = _font(22)

    # カテゴリバッジ
    bb = draw.textbbox((0, 0), badge, font=font_sm)
    bw = bb[2] - bb[0] + 32
    draw.rounded_rectangle([(PADDING, 40), (PADDING + bw, 80)], radius=4, fill=ACCENT)
    draw.text((PADDING + 16, 44), badge, font=font_sm, fill=WHITE)

    # 絵文字（オプション）
    if emoji:
        try:
            font_emoji = _font(80)
            draw.text((PADDING, 110), emoji, font=font_emoji, fill=WHITE)
            title_y = 220
        except Exception:
            title_y = 180
    else:
        title_y = 180

    # タイトル（自動折り返し）
    title_lines = _wrap(title, max_chars=14)
    line_height = 76
    y = title_y
    for line in title_lines[:3]:  # 最大3行
        draw.text((PADDING, y), line, font=font_xl, fill=WHITE)
        y += line_height

    # サブタイトル
    draw.text((PADDING, y + 16), subtitle, font=font_lg, fill=GOLD)

    # フッター
    draw.text((PADDING, HEIGHT - 60), 'aoktik.online ｜ 防災グッズ完全ガイド', font=font_sm, fill=LIGHT)

    # JPEG で保存（WAF 対策）
    img.save(str(output_path), 'JPEG', quality=70, optimize=True)
    return output_path


if __name__ == '__main__':
    import sys
    title = sys.argv[1] if len(sys.argv) > 1 else 'テスト記事タイトル'
    subtitle = sys.argv[2] if len(sys.argv) > 2 else '防災グッズ完全ガイド'
    path = generate_eyecatch(title, subtitle)
    print(f'Generated: {path} ({path.stat().st_size:,} bytes)')
