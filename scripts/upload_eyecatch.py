"""アイキャッチ画像生成 → アップロード → 記事/ページに紐付け

使い方:
    python3 scripts/upload_eyecatch.py 504 "記事タイトル" --emoji 🎬
    python3 scripts/upload_eyecatch.py 504 "記事タイトル" --subtitle "サブ" --badge "GUIDE"
"""
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from helpers import wordpress
from helpers.images import generate_eyecatch


def main():
    p = argparse.ArgumentParser()
    p.add_argument('post_id', type=int)
    p.add_argument('title', type=str)
    p.add_argument('--subtitle', default='防災グッズ完全ガイド')
    p.add_argument('--badge', default='BOUSAI GUIDE')
    p.add_argument('--emoji', default=None)
    p.add_argument('--no-set', action='store_true', help='アップロードのみ（記事に紐付けない）')
    args = p.parse_args()

    print(f'画像生成中: {args.title}')
    img_path = generate_eyecatch(args.title, args.subtitle, args.badge, args.emoji)
    print(f'  → {img_path} ({img_path.stat().st_size:,} bytes)')

    print('アップロード中...')
    media_id = wordpress.upload_image(img_path)
    if not media_id:
        print('✗ アップロード失敗')
        sys.exit(1)
    print(f'  → media_id = {media_id}')

    if not args.no_set:
        print(f'記事 {args.post_id} のアイキャッチに設定中...')
        ok = wordpress.set_featured_image(args.post_id, media_id)
        if ok:
            print('  ✓ 完了')
        else:
            print('  ✗ 設定失敗')
            sys.exit(1)


if __name__ == '__main__':
    main()
