"""全記事にアイキャッチ画像を生成・設定"""
import os, base64, json, requests, struct, zlib, math

WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']

def wp_auth():
    creds = f'{WP_USER}:{WP_PASSWORD}'
    token = base64.b64encode(creds.encode()).decode()
    return {'Authorization': f'Basic {token}'}

# --- Pure Python PNG generation (no external deps needed) ---

def create_png(width, height, pixels):
    """Create PNG from pixel data (list of rows, each row is list of (r,g,b) tuples)"""
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))

    raw = b''
    for row in pixels:
        raw += b'\x00'  # filter byte
        for r, g, b in row:
            raw += struct.pack('BBB', r, g, b)

    idat = chunk(b'IDAT', zlib.compress(raw, 9))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend


def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def create_gradient_image(width, height, color1, color2, direction='diagonal'):
    """Create a gradient background image"""
    c1 = hex_to_rgb(color1)
    c2 = hex_to_rgb(color2)
    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            if direction == 'diagonal':
                t = (x / width * 0.6 + y / height * 0.4)
            elif direction == 'horizontal':
                t = x / width
            else:
                t = y / height
            t = max(0, min(1, t))
            row.append(blend(c1, c2, t))
        pixels.append(row)
    return pixels


def draw_text_bitmap(pixels, text, x, y, color, scale=1):
    """Draw text using a simple bitmap font (5x7 pixel characters)"""
    # Minimal bitmap font for key characters
    font = {
        '防': [[1,1,1,1,1,1,1],[1,0,0,1,0,0,1],[1,1,1,1,1,1,1],[1,0,0,1,0,0,1],[1,0,0,1,0,0,1],[1,1,1,1,1,1,1],[1,0,0,1,0,0,1]],
        '災': [[0,0,1,1,1,0,0],[0,1,0,0,0,1,0],[1,1,1,1,1,1,1],[0,0,0,1,0,0,0],[0,1,0,1,0,1,0],[1,0,1,0,1,0,1],[0,1,0,0,0,1,0]],
    }
    # For simplicity, we'll draw rectangles instead of actual text
    pass


def draw_circle(pixels, cx, cy, radius, color, width, height):
    """Draw a filled circle"""
    rgb = hex_to_rgb(color) if isinstance(color, str) else color
    for y in range(max(0, cy-radius), min(height, cy+radius+1)):
        for x in range(max(0, cx-radius), min(width, cx+radius+1)):
            if (x-cx)**2 + (y-cy)**2 <= radius**2:
                pixels[y][x] = rgb


def draw_rect(pixels, x1, y1, x2, y2, color, width, height):
    """Draw a filled rectangle"""
    rgb = hex_to_rgb(color) if isinstance(color, str) else color
    for y in range(max(0, y1), min(height, y2)):
        for x in range(max(0, x1), min(width, x2)):
            pixels[y][x] = rgb


def draw_rounded_rect(pixels, x1, y1, x2, y2, radius, color, width, height):
    """Draw a filled rounded rectangle"""
    rgb = hex_to_rgb(color) if isinstance(color, str) else color
    for y in range(max(0, y1), min(height, y2)):
        for x in range(max(0, x1), min(width, x2)):
            # Check corners
            in_rect = True
            # Top-left
            if x < x1 + radius and y < y1 + radius:
                if (x - (x1+radius))**2 + (y - (y1+radius))**2 > radius**2:
                    in_rect = False
            # Top-right
            if x > x2 - radius and y < y1 + radius:
                if (x - (x2-radius))**2 + (y - (y1+radius))**2 > radius**2:
                    in_rect = False
            # Bottom-left
            if x < x1 + radius and y > y2 - radius:
                if (x - (x1+radius))**2 + (y - (y2-radius))**2 > radius**2:
                    in_rect = False
            # Bottom-right
            if x > x2 - radius and y > y2 - radius:
                if (x - (x2-radius))**2 + (y - (y2-radius))**2 > radius**2:
                    in_rect = False
            if in_rect:
                pixels[y][x] = rgb


def draw_icon(pixels, icon_type, cx, cy, size, color, width, height):
    """Draw simple geometric icons"""
    rgb = hex_to_rgb(color) if isinstance(color, str) else color

    if icon_type == 'battery':  # ポータブル電源
        # Battery body
        bw, bh = size, int(size * 0.6)
        draw_rounded_rect(pixels, cx-bw//2, cy-bh//2, cx+bw//2, cy+bh//2, 6, rgb, width, height)
        # Battery tip
        draw_rect(pixels, cx+bw//2, cy-bh//4, cx+bw//2+8, cy+bh//4, rgb, width, height)
        # Charge level bars
        inner_color = hex_to_rgb('#10b981')
        bar_w = (bw - 20) // 4
        for i in range(3):
            bx = cx - bw//2 + 10 + i * (bar_w + 4)
            draw_rect(pixels, bx, cy-bh//2+8, bx+bar_w, cy+bh//2-8, inner_color, width, height)

    elif icon_type == 'food':  # 非常食
        # Can shape
        draw_rounded_rect(pixels, cx-size//3, cy-size//2, cx+size//3, cy+size//2, 8, rgb, width, height)
        # Label stripe
        stripe = hex_to_rgb('#fbbf24')
        draw_rect(pixels, cx-size//3+4, cy-8, cx+size//3-4, cy+8, stripe, width, height)

    elif icon_type == 'backpack':  # 防災セット
        # Backpack body
        bw, bh = int(size*0.7), size
        draw_rounded_rect(pixels, cx-bw//2, cy-bh//2, cx+bw//2, cy+bh//2, 10, rgb, width, height)
        # Front pocket
        pocket = blend(rgb, (255,255,255), 0.2)
        pw, ph = int(bw*0.6), int(bh*0.3)
        draw_rounded_rect(pixels, cx-pw//2, cy+bh//4-ph, cx+pw//2, cy+bh//4, 5, pocket, width, height)

    elif icon_type == 'toilet':  # 簡易トイレ
        # Toilet seat shape
        draw_circle(pixels, cx, cy-size//6, size//3, rgb, width, height)
        # Base
        draw_rounded_rect(pixels, cx-size//3, cy, cx+size//3, cy+size//2, 6, rgb, width, height)
        # Inner circle (hole)
        inner = blend(rgb, (0,0,0), 0.3)
        draw_circle(pixels, cx, cy-size//6, size//5, inner, width, height)

    elif icon_type == 'checklist':  # 何から揃える
        # Clipboard
        draw_rounded_rect(pixels, cx-size//3, cy-size//2, cx+size//3, cy+size//2, 6, rgb, width, height)
        # Clip top
        clip = blend(rgb, (0,0,0), 0.2)
        draw_rounded_rect(pixels, cx-size//6, cy-size//2-6, cx+size//6, cy-size//2+6, 3, clip, width, height)
        # Check lines
        line_color = hex_to_rgb('#10b981')
        for i in range(3):
            ly = cy - size//4 + i * (size//4)
            draw_rect(pixels, cx-size//4, ly, cx-size//4+10, ly+3, line_color, width, height)
            draw_rect(pixels, cx-size//8, ly, cx+size//4, ly+3, (255,255,255), width, height)

    elif icon_type == 'water':  # 保存水
        # Water bottle
        bw, bh = int(size*0.4), size
        draw_rounded_rect(pixels, cx-bw//2, cy-bh//3, cx+bw//2, cy+bh//2, 6, rgb, width, height)
        # Bottle neck
        nw = bw//2
        draw_rect(pixels, cx-nw//2, cy-bh//2, cx+nw//2, cy-bh//3+4, rgb, width, height)
        # Cap
        cap = blend(rgb, (0,0,0), 0.2)
        draw_rounded_rect(pixels, cx-nw//2-2, cy-bh//2-8, cx+nw//2+2, cy-bh//2+2, 3, cap, width, height)
        # Water level
        water = hex_to_rgb('#38bdf8')
        draw_rect(pixels, cx-bw//2+4, cy, cx+bw//2-4, cy+bh//2-6, water, width, height)


def create_eyecatch(post_id, title_text, icon_type, color1, color2, accent_color):
    """Create an eyecatch image for a post"""
    W, H = 1200, 630
    pixels = create_gradient_image(W, H, color1, color2, 'diagonal')

    # Draw decorative elements
    # Top-right circle (subtle)
    circle_color = blend(hex_to_rgb(color1), (255,255,255), 0.1)
    draw_circle(pixels, W-150, 100, 180, circle_color, W, H)

    # Bottom-left circle
    draw_circle(pixels, 100, H-80, 120, circle_color, W, H)

    # Central icon area - white rounded rect
    icon_bg_w, icon_bg_h = 160, 160
    icon_cx, icon_cy = W//2, H//2 - 40
    draw_rounded_rect(pixels, icon_cx-icon_bg_w//2, icon_cy-icon_bg_h//2,
                      icon_cx+icon_bg_w//2, icon_cy+icon_bg_h//2,
                      20, (255, 255, 255), W, H)

    # Draw icon
    draw_icon(pixels, icon_type, icon_cx, icon_cy, 100, accent_color, W, H)

    # Bottom bar for text area
    bar_y = H - 180
    draw_rect(pixels, 0, bar_y, W, H, (0, 0, 0), W, H)
    # Semi-transparent overlay (simulate with dark blend)
    for y in range(bar_y, min(H, bar_y + 180)):
        for x in range(W):
            t = 0.65
            pixels[y][x] = blend(pixels[y][x], (0, 0, 0), t)

    # Accent line above text area
    draw_rect(pixels, 0, bar_y, W, bar_y + 4, accent_color, W, H)

    # Category badge
    badge_w = 180
    draw_rounded_rect(pixels, 40, bar_y + 20, 40 + badge_w, bar_y + 50, 4, accent_color, W, H)

    # Site name area at bottom
    draw_rect(pixels, 0, H-40, W, H, (0, 0, 0), W, H)
    for y in range(H-40, H):
        for x in range(W):
            pixels[y][x] = blend(pixels[y][x], (0, 0, 0), 0.3)

    # Small dots pattern (decorative)
    dot_color = blend(hex_to_rgb(color1), (255,255,255), 0.15)
    for dy in range(0, H-200, 40):
        for dx in range(0, W, 40):
            if (dy//40 + dx//40) % 3 == 0:
                draw_circle(pixels, dx, dy, 2, dot_color, W, H)

    return create_png(W, H, pixels)


def upload_image(filename, png_data, retries=3):
    """Upload image to WordPress media library"""
    import time
    for attempt in range(retries):
        headers = wp_auth()
        headers['Content-Type'] = 'image/png'
        headers['Content-Disposition'] = f'attachment; filename="{filename}"'

        r = requests.post(
            f'{WP_URL}/wp-json/wp/v2/media',
            headers=headers,
            data=png_data,
        )
        if r.status_code == 403 and attempt < retries - 1:
            wait = (attempt + 1) * 10
            print(f"   ⏳ WAFブロック、{wait}秒待機後リトライ...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        d = r.json()
        return d['id'], d['source_url']


def set_featured_image(post_id, media_id):
    """Set featured image for a post"""
    headers = wp_auth()
    headers['Content-Type'] = 'application/json'
    r = requests.post(
        f'{WP_URL}/wp-json/wp/v2/posts/{post_id}',
        json={'featured_media': media_id},
        headers=headers,
    )
    r.raise_for_status()
    return r.json()


# 記事ごとのアイキャッチ設定
POSTS = [
    {
        'id': 409,
        'title': 'ポータブル電源おすすめ5選',
        'filename': 'eyecatch-portable-battery.png',
        'icon': 'battery',
        'color1': '#0f172a',
        'color2': '#1e3a5f',
        'accent': '#f59e0b',
    },
    {
        'id': 411,
        'title': '非常食おすすめ10選',
        'filename': 'eyecatch-emergency-food.png',
        'icon': 'food',
        'color1': '#7c2d12',
        'color2': '#451a03',
        'accent': '#fb923c',
    },
    {
        'id': 412,
        'title': '防災セットおすすめ比較',
        'filename': 'eyecatch-disaster-kit.png',
        'icon': 'backpack',
        'color1': '#14532d',
        'color2': '#052e16',
        'accent': '#4ade80',
    },
    {
        'id': 413,
        'title': '簡易トイレおすすめ5選',
        'filename': 'eyecatch-portable-toilet.png',
        'icon': 'toilet',
        'color1': '#1e3a5f',
        'color2': '#0c4a6e',
        'accent': '#38bdf8',
    },
    {
        'id': 414,
        'title': '防災グッズ何から揃える？',
        'filename': 'eyecatch-getting-started.png',
        'icon': 'checklist',
        'color1': '#581c87',
        'color2': '#3b0764',
        'accent': '#e94560',
    },
    {
        'id': 380,
        'title': '防災用保存水おすすめ5選',
        'filename': 'eyecatch-water-storage.png',
        'icon': 'water',
        'color1': '#0c4a6e',
        'color2': '#164e63',
        'accent': '#22d3ee',
        'skip_if_exists': True,
    },
]


def main():
    print("=" * 60)
    print("🖼️  全記事にアイキャッチ画像を生成・設定")
    print("=" * 60)

    import time
    for i, post in enumerate(POSTS):
        post_id = post['id']
        print(f"\n📝 ID:{post_id} | {post['title']}")

        # Check if already has featured image
        r = requests.get(f'{WP_URL}/wp-json/wp/v2/posts/{post_id}',
                       headers={**wp_auth(), 'Content-Type': 'application/json'})
        if r.json().get('featured_media', 0) > 0:
            if post.get('skip_if_exists'):
                print("   ⏭️  既にアイキャッチあり、スキップ")
                continue
            else:
                current = r.json()['featured_media']
                if current >= 441:  # Our generated images
                    print(f"   ⏭️  既に設定済み (media:{current})")
                    continue

        if i > 0:
            print("   ⏳ 5秒待機...")
            time.sleep(5)

        # Generate image
        print("   🎨 画像生成中...")
        png_data = create_eyecatch(
            post_id, post['title'], post['icon'],
            post['color1'], post['color2'], post['accent']
        )
        print(f"   📦 サイズ: {len(png_data):,} bytes")

        # Upload
        print("   📤 アップロード中...")
        media_id, url = upload_image(post['filename'], png_data)
        print(f"   📎 Media ID: {media_id}")

        # Set as featured image
        set_featured_image(post_id, media_id)
        print(f"   ✅ アイキャッチ設定完了")

    print(f"\n{'=' * 60}")
    print("🎉 全記事のアイキャッチ画像設定が完了しました！")
    print("=" * 60)


if __name__ == '__main__':
    main()
