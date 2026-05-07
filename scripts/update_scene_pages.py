"""シーン別固定ページに記事カードを自動追加するスクリプト

使い方:
    # 単一記事をシーンページに追加（dry-run でプレビュー）
    python3 scripts/update_scene_pages.py 504 --dry-run

    # 実反映
    python3 scripts/update_scene_pages.py 504

    # 全記事を再構築（既存カードは「今後追加予定」プレースホルダの直前に整理）
    python3 scripts/update_scene_pages.py --rebuild-all --dry-run
"""
import sys
import argparse
import time
from pathlib import Path

# プロジェクトルートを sys.path に追加
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from helpers import wordpress
from helpers.internal_links import (
    ARTICLES, SCENE_PAGES, SCENE_NAMES, scenes_for_article,
    card, url, SCENE_PLACEHOLDER_MARKER,
)


def _already_contains(content: str, article_id: int) -> bool:
    """ページに既にこの記事のリンクがあるか"""
    return f'?p={article_id}' in content


def _insert_before_placeholder(content: str, new_card: str) -> str:
    """「今後追加予定」プレースホルダーの直前にカードを挿入"""
    if SCENE_PLACEHOLDER_MARKER in content:
        return content.replace(
            SCENE_PLACEHOLDER_MARKER,
            new_card + '\n\n' + SCENE_PLACEHOLDER_MARKER,
            1,
        )
    # プレースホルダがない場合は末尾に追加
    return content + '\n\n' + new_card


def append_to_scene(article_id: int, dry_run: bool = False) -> dict:
    """記事 article_id を該当シーンページにカードとして追加。

    既に追加済みのページはスキップ。
    Returns: {scene_key: status} （'added', 'skipped', 'error'）
    """
    if article_id not in ARTICLES:
        raise ValueError(f"Article {article_id} not in ARTICLES master")

    scenes = scenes_for_article(article_id)
    if not scenes:
        print(f"[!] Article {article_id} has no scene mapping")
        return {}

    new_card = card(article_id)
    results = {}

    for scene_key in scenes:
        page_id = SCENE_PAGES[scene_key]
        emoji, name = SCENE_NAMES[scene_key]

        try:
            page = wordpress.get_post(page_id, raw=True)
            raw_content = page.get('content', {}).get('raw', '')

            if _already_contains(raw_content, article_id):
                print(f"  [skip] {emoji} {name} (page {page_id}): 既に追加済み")
                results[scene_key] = 'skipped'
                continue

            updated = _insert_before_placeholder(raw_content, new_card)

            if dry_run:
                print(f"  [dry-run] {emoji} {name} (page {page_id}): カードを追加します")
                results[scene_key] = 'preview'
            else:
                wordpress.update_post(page_id, content=updated)
                print(f"  [✓] {emoji} {name} (page {page_id}): カードを追加しました")
                results[scene_key] = 'added'
                time.sleep(3)  # WAF 配慮
        except Exception as e:
            print(f"  [×] {emoji} {name} (page {page_id}): エラー {e}")
            results[scene_key] = 'error'

    return results


def preview_append(article_id: int) -> None:
    """dry-run でプレビュー表示"""
    print(f"\n=== Article {article_id}: {ARTICLES.get(article_id, {}).get('title', '?')} ===")
    print(f"URL: {url(article_id)}")
    print(f"配置先シーン: {scenes_for_article(article_id)}")
    print()
    append_to_scene(article_id, dry_run=True)


def main():
    p = argparse.ArgumentParser(description='シーンページへの記事カード自動追加')
    p.add_argument('article_id', nargs='?', type=int, help='記事ID')
    p.add_argument('--dry-run', action='store_true', help='実行せずプレビューのみ')
    p.add_argument('--rebuild-all', action='store_true', help='全記事をシーンページに反映')
    args = p.parse_args()

    if args.rebuild_all:
        for aid in ARTICLES:
            print(f"\n--- Article {aid} ---")
            append_to_scene(aid, dry_run=args.dry_run)
        return

    if not args.article_id:
        p.error('article_id を指定してください（または --rebuild-all）')

    if args.dry_run:
        preview_append(args.article_id)
    else:
        append_to_scene(args.article_id, dry_run=False)


if __name__ == '__main__':
    main()
