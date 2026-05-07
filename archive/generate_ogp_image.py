"""OGP画像自動生成モジュール - SNS共有用のサムネイル画像を生成"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap


class OGPImageGenerator:
    """OGP画像（1200×630px）を生成"""

    # ブランドカラー
    COLORS = {
        'navy': '#1a365d',        # メインテーマカラー
        'accent': '#e94560',      # CTA強調
        'white': '#ffffff',       # テキスト
        'light_bg': '#f8fafc',    # 背景
    }

    # 画像仕様
    WIDTH = 1200
    HEIGHT = 630
    PADDING = 60

    def __init__(self):
        self.font_dir = Path(__file__).parent / 'fonts'
        self.output_dir = Path(__file__).parent / 'data' / 'ogp_images'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # フォントの初期化（システムフォントまたはデフォルト）
        self.try_load_fonts()

    def try_load_fonts(self):
        """日本語フォントをロード"""
        self.font_large = None
        self.font_small = None

        # フォント候補（優先度順）
        font_paths = [
            '/System/Library/Fonts/ヒラギノ丸ゴ Pro W4.ttc',  # macOS
            '/System/Library/Fonts/Hiragino Sans GB.ttc',     # macOS
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',  # Linux
            'C:\\Windows\\Fonts\\YuGothB.ttc',                # Windows
        ]

        for font_path in font_paths:
            if Path(font_path).exists():
                try:
                    self.font_large = ImageFont.truetype(font_path, 72)
                    self.font_small = ImageFont.truetype(font_path, 48)
                    print(f"✓ フォント読み込み: {font_path}")
                    return
                except Exception as e:
                    print(f"✗ フォント読み込み失敗: {e}")

        # フォントが見つからない場合はデフォルトを使用
        print("警告: 日本語フォントが見つかりません。デフォルトフォントを使用します。")
        try:
            self.font_large = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
        except:
            pass

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """HEXカラーをRGBに変換"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _wrap_text(self, text: str, max_width: int = 50) -> str:
        """テキストを指定幅で折り返す"""
        wrapped = []
        for line in text.split('\n'):
            if len(line) > max_width:
                wrapped.extend(textwrap.wrap(line, width=max_width))
            else:
                wrapped.append(line)
        return '\n'.join(wrapped)

    def _get_text_bbox(self, draw: ImageDraw, text: str, font) -> tuple:
        """テキストのバウンディングボックスを取得"""
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])  # (width, height)
        except:
            # フォントが無い場合の推定サイズ
            return (len(text) * 30, 40)

    def generate(self, title: str, subtitle: str = "防災グッズ完全ガイド", output_path: str = None) -> str:
        """OGP画像を生成

        Args:
            title: 記事タイトル
            subtitle: サブタイトル（デフォルト: ブログ名）
            output_path: 出力パス（省略時は data/ogp_images に自動生成）

        Returns:
            生成された画像ファイルのパス
        """
        # 出力パスの決定
        if output_path is None:
            # タイトルからファイル名を生成
            safe_title = "".join(c if c.isalnum() or c in '-_' else '_' for c in title[:30])
            output_path = self.output_dir / f"{safe_title}.png"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # キャンバス作成
        img = Image.new(
            'RGB',
            (self.WIDTH, self.HEIGHT),
            color=self._hex_to_rgb(self.COLORS['navy'])
        )
        draw = ImageDraw.Draw(img)

        # グラデーション背景（左: navy、右: accent）
        for x in range(self.WIDTH):
            ratio = x / self.WIDTH
            navy_rgb = self._hex_to_rgb(self.COLORS['navy'])
            accent_rgb = self._hex_to_rgb(self.COLORS['accent'])
            color = tuple(int(navy_rgb[i] * (1 - ratio) + accent_rgb[i] * ratio) for i in range(3))
            draw.line([(x, 0), (x, self.HEIGHT)], fill=color)

        # サブタイトル（上）
        subtitle_text = subtitle
        subtitle_y = 40
        draw.text(
            (self.PADDING, subtitle_y),
            subtitle_text,
            font=self.font_small,
            fill=self._hex_to_rgb(self.COLORS['white'])
        )

        # タイトル（中央）
        # テキストを折り返す
        wrapped_title = self._wrap_text(title, max_width=20)
        title_lines = wrapped_title.split('\n')

        # タイトルの高さを計算
        line_height = 80
        total_title_height = len(title_lines) * line_height
        title_y_start = (self.HEIGHT - total_title_height) // 2

        # タイトルを描画
        for i, line in enumerate(title_lines):
            y = title_y_start + (i * line_height)
            draw.text(
                (self.PADDING, y),
                line,
                font=self.font_large,
                fill=self._hex_to_rgb(self.COLORS['white'])
            )

        # ブランド情報（下）
        brand_y = self.HEIGHT - 80
        draw.text(
            (self.PADDING, brand_y),
            "aoktik.online",
            font=self.font_small,
            fill=self._hex_to_rgb(self.COLORS['accent'])
        )

        # 画像を保存
        img.save(str(output_path), 'PNG')
        print(f"✓ OGP画像生成: {output_path}")
        return str(output_path)


def generate_ogp_image(title: str, subtitle: str = "防災グッズ完全ガイド", output_path: str = None) -> str:
    """OGP画像を生成するメイン関数

    Args:
        title: 記事タイトル
        subtitle: サブタイトル
        output_path: 出力パス（省略時は自動生成）

    Returns:
        生成されたファイルパス
    """
    generator = OGPImageGenerator()
    return generator.generate(title, subtitle, output_path)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("使用法: python3 generate_ogp_image.py <title> [subtitle] [output_path]")
        sys.exit(1)

    title = sys.argv[1]
    subtitle = sys.argv[2] if len(sys.argv) > 2 else "防災グッズ完全ガイド"
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    result = generate_ogp_image(title, subtitle, output_path)
    print(f"生成完了: {result}")
