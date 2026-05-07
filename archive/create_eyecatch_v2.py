"""全記事にアイキャッチ画像を生成・設定 (v2 - デザイン一新)"""
import os, base64, requests, struct, zlib, math, time

WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']

def wp_auth():
    creds = f'{WP_USER}:{WP_PASSWORD}'
    token = base64.b64encode(creds.encode()).decode()
    return {'Authorization': f'Basic {token}'}

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

def draw_ring(px, cx, cy, outer_r, inner_r, color):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    or2, ir2 = outer_r**2, inner_r**2
    for y in range(max(0, cy-outer_r), min(H, cy+outer_r+1)):
        dy2 = (y-cy)**2
        for x in range(max(0, cx-outer_r), min(W, cx+outer_r+1)):
            d2 = (x-cx)**2 + dy2
            if ir2 <= d2 <= or2:
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

def draw_ellipse(px, cx, cy, rx, ry, color):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    for y in range(max(0, cy-ry), min(H, cy+ry+1)):
        for x in range(max(0, cx-rx), min(W, cx+rx+1)):
            if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1:
                px[y][x] = rgb

def draw_triangle(px, x1, y1, x2, y2, x3, y3, color):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    min_y = max(0, min(y1, y2, y3))
    max_y = min(H, max(y1, y2, y3))
    min_x = max(0, min(x1, x2, x3))
    max_x = min(W, max(x1, x2, x3))
    def sign(px, py, ax, ay, bx, by):
        return (px-bx)*(ay-by) - (ax-bx)*(py-by)
    for y in range(min_y, max_y+1):
        for x in range(min_x, max_x+1):
            d1 = sign(x, y, x1, y1, x2, y2)
            d2 = sign(x, y, x2, y2, x3, y3)
            d3 = sign(x, y, x3, y3, x1, y1)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            if not (has_neg and has_pos):
                px[y][x] = rgb

def draw_line_h(px, x1, x2, y, thickness, color):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    for yy in range(max(0, y), min(H, y+thickness)):
        for xx in range(max(0, x1), min(W, x2)):
            px[yy][xx] = rgb

def draw_line_v(px, x, y1, y2, thickness, color):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    for yy in range(max(0, y1), min(H, y2)):
        for xx in range(max(0, x), min(W, x+thickness)):
            px[yy][xx] = rgb

def blend_overlay(px, x1, y1, x2, y2, color, alpha):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    for y in range(max(0, y1), min(H, y2)):
        for x in range(max(0, x1), min(W, x2)):
            px[y][x] = blend(px[y][x], rgb, alpha)

def add_wave_pattern(px, base_y, amplitude, freq, color, thickness=3):
    rgb = hex_rgb(color) if isinstance(color, str) else color
    for x in range(W):
        cy = int(base_y + amplitude * math.sin(x * freq * 2 * math.pi / W))
        for t in range(thickness):
            yy = cy + t
            if 0 <= yy < H and 0 <= x < W:
                px[yy][x] = blend(px[yy][x], rgb, 0.4)


# === 記事別アイキャッチ生成 ===

def eyecatch_battery(px):
    """409: ポータブル電源 - 停電時の暗闇にバッテリーが光るイメージ"""
    fill_gradient(px, '#0a0e27', '#1a2744', 150)

    # 背景に微細なグリッドパターン
    grid_color = hex_rgb('#1a2744')
    grid_light = hex_rgb('#222f4a')
    for y in range(0, H, 30):
        for x in range(W):
            if 0 <= y < H:
                px[y][x] = blend(px[y][x], grid_light, 0.15)
    for x in range(0, W, 30):
        for y in range(H):
            if 0 <= x < W:
                px[y][x] = blend(px[y][x], grid_light, 0.1)

    # 大きな電源ユニット（中央やや左）
    cx, cy = 400, 280
    # 本体 - 角丸の大きなボックス
    draw_rounded_rect(px, cx-140, cy-80, cx+140, cy+80, 12, '#2a3a5c')
    draw_rounded_rect(px, cx-135, cy-75, cx+135, cy+75, 10, '#344868')
    # 液晶ディスプレイ
    draw_rounded_rect(px, cx-100, cy-55, cx+50, cy+5, 6, '#0a1628')
    # ディスプレイ内のバッテリー表示
    for i in range(4):
        bar_x = cx - 90 + i * 35
        draw_rect(px, bar_x, cy-40, bar_x+28, cy-10, '#22c55e')
    # パーセント表示エリア
    draw_rect(px, cx+60, cy-45, cx+125, cy-15, '#0a1628')
    # コンセント穴
    for i in range(3):
        ox = cx - 80 + i * 70
        draw_rounded_rect(px, ox, cy+20, ox+50, cy+60, 6, '#1a2744')
        # プラグ穴
        draw_rect(px, ox+15, cy+30, ox+20, cy+50, '#0a0e27')
        draw_rect(px, ox+30, cy+30, ox+35, cy+50, '#0a0e27')
    # ハンドル
    draw_rounded_rect(px, cx-60, cy-95, cx+60, cy-78, 4, '#4a5a7c')

    # 右側: 充電中のデバイスたち
    # スマホ
    sx, sy = 680, 240
    draw_rounded_rect(px, sx-25, sy-45, sx+25, sy+45, 8, '#3a4a6c')
    draw_rounded_rect(px, sx-20, sy-38, sx+20, sy+32, 4, '#1a2a4c')
    # 充電マーク（雷アイコン）
    draw_triangle(px, sx-8, sy-15, sx+8, sy-15, sx, sy+5, '#fbbf24')
    draw_triangle(px, sx-5, sy-2, sx+10, sy-2, sx+2, sy+18, '#fbbf24')

    # ケーブル（電源→スマホ）
    for x in range(cx+140, sx-25):
        yy = cy + int(20 * math.sin((x - cx) * 0.02))
        for t in range(3):
            if 0 <= yy+t < H:
                px[yy+t][x] = hex_rgb('#fbbf24')

    # LEDライト（右上）
    lx, ly = 850, 180
    draw_rounded_rect(px, lx-15, ly-40, lx+15, ly+40, 8, '#4a5a7c')
    # 光の放射
    for r in range(80, 20, -5):
        alpha = 0.08 * (80 - r) / 60
        draw_circle(px, lx, ly-50, r, blend(hex_rgb('#0a0e27'), hex_rgb('#fef08a'), alpha))
    draw_circle(px, lx, ly-45, 12, '#fef08a')

    # 装飾: エネルギー波
    for wave_y in range(450, 500, 15):
        add_wave_pattern(px, wave_y, 8, 3, '#f59e0b', 2)

    # 下部テキストエリア
    blend_overlay(px, 0, H-130, W, H, '#000000', 0.7)
    draw_rect(px, 0, H-130, W, H-126, '#f59e0b')
    # カテゴリバッジ
    draw_rounded_rect(px, 50, H-110, 230, H-80, 4, '#f59e0b')
    # サイト名バー
    blend_overlay(px, 0, H-35, W, H, '#000000', 0.3)


def eyecatch_food(px):
    """411: 非常食 - 温かみのある食品棚のイメージ"""
    fill_gradient(px, '#3d1c02', '#1a0a00', 160)

    # 木目調の棚背景
    for y in range(80, H-150, 2):
        stripe_t = 0.03 * math.sin(y * 0.5 + 3)
        for x in range(W):
            px[y][x] = blend(px[y][x], hex_rgb('#5c3a1a'), abs(stripe_t))

    # 棚板3段
    shelf_color = '#8B6914'
    shelf_edge = '#6B4F12'
    shelves = [160, 310, 460]
    for sy in shelves:
        draw_rect(px, 60, sy, W-60, sy+12, shelf_color)
        draw_rect(px, 60, sy+12, W-60, sy+16, shelf_edge)

    # 1段目: アルファ米パック群
    for i in range(5):
        bx = 100 + i * 190
        # パウチパック
        draw_rounded_rect(px, bx, 90, bx+160, 158, 6, '#e8e0d0')
        # ラベル
        label_colors = ['#dc2626', '#ea580c', '#16a34a', '#2563eb', '#9333ea']
        draw_rect(px, bx+10, 100, bx+150, 140, label_colors[i % 5])
        # 上部シール
        draw_rect(px, bx+50, 88, bx+110, 95, '#c0b8a8')

    # 2段目: 缶詰
    can_colors = ['#b91c1c', '#1d4ed8', '#15803d', '#b45309', '#7c3aed']
    for i in range(7):
        cx = 120 + i * 140
        # 缶の胴体
        draw_ellipse(px, cx, 280, 50, 25, '#d1d5db')
        draw_rounded_rect(px, cx-50, 225, cx+50, 308, 4, can_colors[i % 5])
        # ラベルストライプ
        draw_rect(px, cx-45, 260, cx+45, 275, blend(hex_rgb(can_colors[i%5]), (255,255,255), 0.3))
        # 缶上部
        draw_ellipse(px, cx, 225, 48, 15, '#9ca3af')
        draw_ellipse(px, cx, 225, 42, 12, '#b0b5bc')

    # 3段目: ペットボトル水 + レトルトパウチ
    for i in range(4):
        bx = 120 + i * 120
        # ペットボトル
        draw_rounded_rect(px, bx-15, 380, bx+15, 458, 4, '#bfdbfe')
        draw_rect(px, bx-8, 365, bx+8, 382, '#bfdbfe')
        draw_rect(px, bx-10, 360, bx+10, 368, '#60a5fa')
        # 水
        draw_rect(px, bx-12, 410, bx+12, 455, '#93c5fd')
    for i in range(3):
        bx = 640 + i * 160
        # レトルトパウチ
        draw_rounded_rect(px, bx, 375, bx+130, 458, 6, '#fef3c7')
        draw_rect(px, bx+10, 395, bx+120, 435, '#f59e0b')

    # 装飾: 湯気エフェクト（温かさの演出）
    steam_x = [300, 500, 700]
    for sx in steam_x:
        for sy_off in range(0, 60, 8):
            wave = int(10 * math.sin(sy_off * 0.3))
            alpha = 0.15 * (1 - sy_off / 60)
            yy = 55 - sy_off
            if 0 <= yy < H:
                for dx in range(-3, 4):
                    xx = sx + wave + dx
                    if 0 <= xx < W:
                        px[yy][xx] = blend(px[yy][xx], (255,255,255), alpha)

    # 下部テキストエリア
    blend_overlay(px, 0, H-130, W, H, '#000000', 0.75)
    draw_rect(px, 0, H-130, W, H-126, '#fb923c')
    draw_rounded_rect(px, 50, H-110, 230, H-80, 4, '#fb923c')
    blend_overlay(px, 0, H-35, W, H, '#000000', 0.3)


def eyecatch_kit(px):
    """412: 防災セット - リュックと中身が展開されたイメージ"""
    fill_gradient(px, '#052e16', '#1a3a2a', 130)

    # 背景パターン：微細な防災マーク的なモチーフ
    for y in range(0, H-150, 60):
        for x in range(0, W, 60):
            if (y//60 + x//60) % 4 == 0:
                draw_circle(px, x, y, 3, blend(hex_rgb('#052e16'), (255,255,255), 0.08))

    # 中央にリュック
    rcx, rcy = 350, 280
    # リュック本体
    draw_rounded_rect(px, rcx-100, rcy-140, rcx+100, rcy+140, 20, '#166534')
    draw_rounded_rect(px, rcx-90, rcy-130, rcx+90, rcy+130, 16, '#1a7a3c')
    # 上部フタ
    draw_rounded_rect(px, rcx-85, rcy-155, rcx+85, rcy-120, 12, '#15803d')
    # フロントポケット
    draw_rounded_rect(px, rcx-65, rcy+10, rcx+65, rcy+110, 10, '#14532d')
    draw_rounded_rect(px, rcx-60, rcy+15, rcx+60, rcy+105, 8, '#166534')
    # ジッパーライン
    draw_line_h(px, rcx-60, rcx+60, rcy+12, 2, '#9ca3af')
    # 肩ストラップ
    draw_rounded_rect(px, rcx-110, rcy-130, rcx-90, rcy+60, 6, '#14532d')
    draw_rounded_rect(px, rcx+90, rcy-130, rcx+110, rcy+60, 6, '#14532d')
    # 十字マーク（防災）
    cross_color = '#ef4444'
    draw_circle(px, rcx, rcy-50, 30, '#ffffff')
    draw_rect(px, rcx-20, rcy-55, rcx+20, rcy-45, cross_color)
    draw_rect(px, rcx-5, rcy-70, rcx+5, rcy-30, cross_color)

    # 右側に中身を展開表示
    items_start_x = 550
    # 懐中電灯
    fx, fy = items_start_x + 30, 120
    draw_rounded_rect(px, fx, fy, fx+100, fy+30, 6, '#fbbf24')
    draw_rounded_rect(px, fx+100, fy-5, fx+130, fy+35, 8, '#f59e0b')
    draw_circle(px, fx+125, fy+15, 18, '#fef9c3')

    # 水ボトル
    wx, wy = items_start_x + 200, 100
    draw_rounded_rect(px, wx, wy, wx+35, wy+70, 5, '#bfdbfe')
    draw_rect(px, wx+10, wy-10, wx+25, wy+5, '#bfdbfe')
    draw_rect(px, wx+8, wy-15, wx+27, wy-8, '#3b82f6')
    draw_rect(px, wx+5, wy+35, wx+30, wy+65, '#60a5fa')

    # ラジオ
    rx, ry = items_start_x + 350, 110
    draw_rounded_rect(px, rx, ry, rx+90, ry+60, 8, '#374151')
    draw_circle(px, rx+30, ry+35, 18, '#1f2937')
    draw_circle(px, rx+30, ry+35, 15, '#4b5563')
    draw_rect(px, rx+55, ry+10, rx+80, ry+20, '#6b7280')
    draw_rect(px, rx+55, ry+25, rx+80, ry+35, '#6b7280')
    # アンテナ
    draw_line_v(px, rx+45, ry-40, ry, 2, '#9ca3af')

    # ブランケット
    bx, by = items_start_x + 50, 230
    draw_rounded_rect(px, bx, by, bx+150, by+40, 4, '#a78bfa')
    draw_rounded_rect(px, bx+5, by+5, bx+145, by+35, 3, '#c4b5fd')

    # 救急キット
    kx, ky = items_start_x + 250, 220
    draw_rounded_rect(px, kx, ky, kx+80, ky+60, 6, '#ffffff')
    draw_rect(px, kx+30, ky+15, kx+50, ky+45, '#dc2626')
    draw_rect(px, kx+20, ky+25, kx+60, ky+35, '#dc2626')

    # 乾電池
    dx, dy = items_start_x + 380, 240
    for i in range(3):
        draw_rounded_rect(px, dx+i*25, dy, dx+20+i*25, dy+45, 3, '#fbbf24')
        draw_rect(px, dx+5+i*25, dy-5, dx+15+i*25, dy+2, '#d4d4d8')

    # 軍手
    gx, gy = items_start_x + 100, 330
    draw_rounded_rect(px, gx, gy, gx+70, gy+80, 8, '#fef3c7')
    # 指
    for i in range(4):
        draw_rounded_rect(px, gx+5+i*16, gy-20, gx+18+i*16, gy+10, 5, '#fef3c7')
    draw_rounded_rect(px, gx-15, gy+15, gx+5, gy+45, 5, '#fef3c7')

    # ホイッスル
    hx, hy = items_start_x + 250, 350
    draw_rounded_rect(px, hx, hy, hx+60, hy+20, 6, '#f97316')
    draw_circle(px, hx, hy+10, 12, '#f97316')

    # マスク
    mx, my = items_start_x + 350, 340
    draw_ellipse(px, mx+35, my+20, 40, 22, '#e5e7eb')
    draw_line_h(px, mx+15, mx+55, my+18, 1, '#d1d5db')
    draw_line_h(px, mx+10, mx+60, my+24, 1, '#d1d5db')

    # 下部テキストエリア
    blend_overlay(px, 0, H-130, W, H, '#000000', 0.75)
    draw_rect(px, 0, H-130, W, H-126, '#4ade80')
    draw_rounded_rect(px, 50, H-110, 230, H-80, 4, '#4ade80')
    blend_overlay(px, 0, H-35, W, H, '#000000', 0.3)


def eyecatch_toilet(px):
    """413: 簡易トイレ - 清潔感のある防災トイレ解説イメージ"""
    fill_gradient(px, '#0c2d48', '#163a5c', 120)

    # 背景: タイルパターン（清潔感）
    for y in range(0, H-150, 40):
        for x in range(0, W, 40):
            # タイルの溝
            if y % 40 < 2 or x % 40 < 2:
                blend_overlay(px, x, y, x+2, y+2, '#0a2040', 0.3)

    # 中央: 簡易トイレセットの図解
    tcx, tcy = 380, 250

    # 便座（組み立て式トイレ）
    # 脚部フレーム
    draw_rect(px, tcx-80, tcy+40, tcx-70, tcy+120, '#6b7280')
    draw_rect(px, tcx+70, tcy+40, tcx+80, tcy+120, '#6b7280')
    draw_rect(px, tcx-40, tcy+40, tcx-30, tcy+120, '#6b7280')
    draw_rect(px, tcx+30, tcy+40, tcx+40, tcy+120, '#6b7280')
    # 横フレーム
    draw_rect(px, tcx-80, tcy+110, tcx+80, tcy+120, '#6b7280')
    # 便座リング
    draw_ellipse(px, tcx, tcy+30, 75, 25, '#e5e7eb')
    draw_ellipse(px, tcx, tcy+30, 55, 15, '#0c2d48')
    # 便座フタ（半分開いた状態）
    draw_ellipse(px, tcx, tcy-10, 75, 30, '#f0f0f0')
    draw_ellipse(px, tcx, tcy-5, 70, 25, '#e5e7eb')
    # 袋（セットされた状態）
    draw_ellipse(px, tcx, tcy+35, 50, 15, '#1e3a5f')

    # 右側: 関連アイテム
    # 凝固剤パック
    gx, gy = 650, 130
    draw_rounded_rect(px, gx, gy, gx+120, gy+80, 8, '#dbeafe')
    draw_rounded_rect(px, gx+10, gy+25, gx+110, gy+70, 4, '#3b82f6')
    # 粒のイメージ
    for i in range(5):
        for j in range(3):
            draw_circle(px, gx+30+i*15, gy+35+j*12, 3, '#bfdbfe')

    # 消臭袋
    bx, by = 650, 250
    draw_rounded_rect(px, bx, by, bx+100, by+120, 6, '#fef3c7')
    # BOSロゴ風
    draw_rounded_rect(px, bx+15, by+30, bx+85, by+70, 4, '#16a34a')
    # 袋の口を結んだ形
    draw_circle(px, bx+50, by+10, 15, '#fde68a')

    # 使い方ステップ矢印
    arrow_y = 420
    for i in range(3):
        ax = 180 + i * 300
        # 丸番号
        draw_circle(px, ax, arrow_y, 20, '#38bdf8')
        # 矢印
        if i < 2:
            for xx in range(ax+30, ax+270, 3):
                if 0 <= xx < W:
                    px[arrow_y][xx] = hex_rgb('#38bdf8')
                    if arrow_y-1 >= 0:
                        px[arrow_y-1][xx] = hex_rgb('#38bdf8')
            # 矢印の先端
            draw_triangle(px, ax+260, arrow_y-8, ax+260, arrow_y+8, ax+280, arrow_y, '#38bdf8')

    # シールド（安心感の演出）
    sx, sy = 900, 200
    # 盾の形
    draw_rounded_rect(px, sx-50, sy-60, sx+50, sy+20, 12, '#38bdf8')
    draw_triangle(px, sx-50, sy+15, sx+50, sy+15, sx, sy+70, '#38bdf8')
    # チェックマーク
    inner = '#0c2d48'
    draw_rounded_rect(px, sx-35, sy-45, sx+35, sy+10, 8, inner)
    draw_triangle(px, sx-35, sy+5, sx+35, sy+5, sx, sy+55, inner)
    # チェック
    check = '#4ade80'
    draw_rect(px, sx-15, sy-10, sx-5, sy+15, check)
    draw_rect(px, sx-5, sy-25, sx+5, sy+5, check)

    # 下部テキストエリア
    blend_overlay(px, 0, H-130, W, H, '#000000', 0.75)
    draw_rect(px, 0, H-130, W, H-126, '#38bdf8')
    draw_rounded_rect(px, 50, H-110, 230, H-80, 4, '#38bdf8')
    blend_overlay(px, 0, H-35, W, H, '#000000', 0.3)


def eyecatch_checklist(px):
    """414: 何から揃える - ステップバイステップのロードマップイメージ"""
    fill_gradient(px, '#1e0a3a', '#2d1458', 140)

    # 背景: 放射状の微光
    center_x, center_y = 600, 300
    for y in range(H-130):
        for x in range(W):
            dist = math.sqrt((x-center_x)**2 + (y-center_y)**2)
            if dist < 400:
                alpha = 0.06 * (1 - dist/400)
                px[y][x] = blend(px[y][x], hex_rgb('#6d28d9'), alpha)

    # 3つのステップカード
    steps = [
        {'x': 120, 'color': '#dc2626', 'budget': '¥3,000', 'items': 3},
        {'x': 450, 'color': '#f59e0b', 'budget': '¥10,000', 'items': 5},
        {'x': 780, 'color': '#22c55e', 'budget': '¥30,000', 'items': 7},
    ]

    for i, s in enumerate(steps):
        sx = s['x']
        # カード背景
        draw_rounded_rect(px, sx, 80, sx+260, 420, 16, '#2a1a4a')
        draw_rounded_rect(px, sx+3, 83, sx+257, 417, 14, '#3a2a5a')

        # ステップ番号バッジ
        draw_circle(px, sx+130, 60, 28, s['color'])
        # 内側に数字風の装飾
        draw_circle(px, sx+130, 60, 20, blend(hex_rgb(s['color']), (0,0,0), 0.2))

        # カード上部のカラーバー
        draw_rect(px, sx+15, 95, sx+245, 100, s['color'])

        # 予算表示エリア
        draw_rounded_rect(px, sx+30, 110, sx+230, 155, 8, '#1e0a3a')
        # 予算バッジ
        draw_rounded_rect(px, sx+40, 118, sx+140, 147, 4, s['color'])

        # チェックリストアイテム
        for j in range(s['items']):
            iy = 175 + j * 32
            if iy + 25 > 415:
                break
            # チェックボックス
            draw_rounded_rect(px, sx+30, iy, sx+50, iy+20, 3, '#4a3a6a')
            if j < s['items'] - 2:
                # チェック済み
                draw_rect(px, sx+34, iy+4, sx+46, iy+16, '#22c55e')
            # アイテム名の棒（テキスト代わり）
            bar_w = 100 + (j * 17) % 60
            draw_rounded_rect(px, sx+60, iy+5, sx+60+bar_w, iy+15, 3, '#5a4a7a')

        # 矢印（カード間）
        if i < 2:
            ax = sx + 260
            for xx in range(ax+5, ax+55):
                if 0 <= xx < W:
                    for t in range(-2, 3):
                        yy = 250 + t
                        if 0 <= yy < H:
                            px[yy][xx] = hex_rgb('#a78bfa')
            # 矢印先端
            draw_triangle(px, ax+45, 240, ax+45, 260, ax+65, 250, '#a78bfa')

    # 進捗バー（下部）
    bar_y = 440
    draw_rounded_rect(px, 120, bar_y, W-120, bar_y+12, 6, '#2a1a4a')
    draw_rounded_rect(px, 120, bar_y, 120 + int((W-240)*0.33), bar_y+12, 6, '#dc2626')
    draw_rounded_rect(px, 120, bar_y, 120 + int((W-240)*0.66), bar_y+12, 6, '#f59e0b')

    # 下部テキストエリア
    blend_overlay(px, 0, H-130, W, H, '#000000', 0.75)
    draw_rect(px, 0, H-130, W, H-126, '#a78bfa')
    draw_rounded_rect(px, 50, H-110, 230, H-80, 4, '#a78bfa')
    blend_overlay(px, 0, H-35, W, H, '#000000', 0.3)


def eyecatch_water(px):
    """380: 保存水 - 水のクリスタル感と備蓄のイメージ"""
    fill_gradient(px, '#042f3d', '#0a4a5e', 110)

    # 波紋背景
    for ring in range(3):
        cx = 600 + ring * 50
        cy = 300
        for r in range(200 + ring * 80, 220 + ring * 80):
            draw_ring(px, cx, cy, r, r-2, blend(hex_rgb('#0a4a5e'), hex_rgb('#22d3ee'), 0.08))

    # 水ボトル群（メイン表示）
    bottles = [
        {'x': 200, 'h': 180, 'w': 60, 'color': '#0ea5e9', 'cap': '#0369a1', 'level': 0.8},
        {'x': 320, 'h': 200, 'w': 70, 'color': '#06b6d4', 'cap': '#0e7490', 'level': 0.9},
        {'x': 460, 'h': 220, 'w': 80, 'color': '#22d3ee', 'cap': '#0891b2', 'level': 0.85},
        {'x': 610, 'h': 200, 'w': 70, 'color': '#06b6d4', 'cap': '#0e7490', 'level': 0.75},
        {'x': 730, 'h': 180, 'w': 60, 'color': '#0ea5e9', 'cap': '#0369a1', 'level': 0.7},
    ]

    base_y = 430
    for b in bottles:
        bx, bw, bh = b['x'], b['w'], b['h']
        by = base_y - bh

        # ボトル本体
        draw_rounded_rect(px, bx-bw//2, by, bx+bw//2, base_y, 8, '#e0f2fe')
        # ネック
        nw = bw // 3
        draw_rect(px, bx-nw//2, by-30, bx+nw//2, by+5, '#e0f2fe')
        # キャップ
        draw_rounded_rect(px, bx-nw//2-3, by-40, bx+nw//2+3, by-25, 4, b['cap'])
        # 水
        water_top = by + int(bh * (1 - b['level']))
        draw_rounded_rect(px, bx-bw//2+4, water_top, bx+bw//2-4, base_y-4, 4, b['color'])

        # ラベル
        label_y = by + bh // 3
        draw_rect(px, bx-bw//2+3, label_y, bx+bw//2-3, label_y+bh//3, '#ffffff')
        draw_rect(px, bx-bw//2+8, label_y+8, bx+bw//2-8, label_y+bh//3-8, b['color'])

    # 水滴エフェクト
    drops = [(150, 100, 8), (950, 150, 10), (850, 80, 6), (100, 350, 7), (1000, 300, 9)]
    for dx, dy, dr in drops:
        draw_circle(px, dx, dy, dr, blend(hex_rgb('#22d3ee'), (255,255,255), 0.5))
        # ハイライト
        draw_circle(px, dx-dr//3, dy-dr//3, dr//3, (255,255,255))

    # 「15年保存」バッジ風
    badge_cx, badge_cy = 950, 350
    draw_circle(px, badge_cx, badge_cy, 55, '#22d3ee')
    draw_circle(px, badge_cx, badge_cy, 48, '#042f3d')
    draw_circle(px, badge_cx, badge_cy, 45, '#22d3ee')
    draw_circle(px, badge_cx, badge_cy, 40, '#042f3d')
    # 内部の装飾
    draw_rect(px, badge_cx-25, badge_cy-5, badge_cx+25, badge_cy+5, '#22d3ee')

    # 下部テキストエリア
    blend_overlay(px, 0, H-130, W, H, '#000000', 0.75)
    draw_rect(px, 0, H-130, W, H-126, '#22d3ee')
    draw_rounded_rect(px, 50, H-110, 230, H-80, 4, '#22d3ee')
    blend_overlay(px, 0, H-35, W, H, '#000000', 0.3)


POSTS = [
    {'id': 409, 'title': 'ポータブル電源おすすめ5選', 'filename': 'eyecatch-portable-battery-v2.png', 'generator': eyecatch_battery},
    {'id': 411, 'title': '非常食おすすめ10選', 'filename': 'eyecatch-emergency-food-v2.png', 'generator': eyecatch_food},
    {'id': 412, 'title': '防災セットおすすめ比較', 'filename': 'eyecatch-disaster-kit-v2.png', 'generator': eyecatch_kit},
    {'id': 413, 'title': '簡易トイレおすすめ5選', 'filename': 'eyecatch-portable-toilet-v2.png', 'generator': eyecatch_toilet},
    {'id': 414, 'title': '防災グッズ何から揃える？', 'filename': 'eyecatch-getting-started-v2.png', 'generator': eyecatch_checklist},
    {'id': 380, 'title': '防災用保存水おすすめ5選', 'filename': 'eyecatch-water-storage-v2.png', 'generator': eyecatch_water},
]


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
    raise Exception(f"アップロード失敗: {filename} ({max_retries}回リトライ)")


def set_featured_image(post_id, media_id):
    headers = wp_auth()
    headers['Content-Type'] = 'application/json'
    r = requests.post(f'{WP_URL}/wp-json/wp/v2/posts/{post_id}',
                      json={'featured_media': media_id}, headers=headers)
    r.raise_for_status()
    return r.json()


def main():
    print("=" * 60)
    print("🖼️  全記事アイキャッチ画像 v2 - デザイン一新")
    print("=" * 60)

    results = []
    for i, post in enumerate(POSTS):
        post_id = post['id']
        print(f"\n{'─' * 50}")
        print(f"📝 [{i+1}/6] ID:{post_id} | {post['title']}")

        # 画像生成
        print("   🎨 画像生成中...")
        pixels = new_canvas()
        post['generator'](pixels)
        png_data = create_png(W, H, pixels)
        print(f"   📦 サイズ: {len(png_data):,} bytes")

        # WAF回避: 2枚目以降は60秒間隔
        if i > 0:
            wait = 60
            print(f"   ⏳ WAF回避のため{wait}秒待機...")
            time.sleep(wait)

        # アップロード
        print("   📤 アップロード中...")
        try:
            media_id, url = upload_image(post['filename'], png_data)
            print(f"   📎 Media ID: {media_id}")

            # アイキャッチ設定
            set_featured_image(post_id, media_id)
            print(f"   ✅ アイキャッチ設定完了!")
            results.append((post_id, post['title'], 'OK', media_id))
        except Exception as e:
            print(f"   ❌ 失敗: {e}")
            results.append((post_id, post['title'], 'FAIL', str(e)))

    print(f"\n{'=' * 60}")
    print("📊 結果サマリー:")
    for pid, title, status, detail in results:
        icon = '✅' if status == 'OK' else '❌'
        print(f"   {icon} ID:{pid} {title} → {detail}")
    ok = sum(1 for r in results if r[2] == 'OK')
    print(f"\n🎉 完了: {ok}/6 成功")
    print("=" * 60)


if __name__ == '__main__':
    main()
