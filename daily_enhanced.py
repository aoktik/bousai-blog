"""日次記事生成スクリプト（テンプレート主体・LLM API不要版）

仕組み:
1. data/topic_templates.py の ROTATION から今日のトピックを選択
2. helpers.article_builder で Gutenberg HTML を組み立て
3. WordPress に下書き状態で投稿
4. アイキャッチ画像を生成・アップロード・設定
5. data/state_enhanced.json でローテーション状態を保存

GitHub Actions から毎日 JST 7:00 に実行される。
ユーザーは生成された下書きをレビューして公開する。
"""
import os
import sys
import json
import time
import importlib.util
from pathlib import Path

from helpers.env import load_env
load_env()

import helpers.wordpress as wordpress
from helpers.images import generate_eyecatch
from helpers.article_builder import build_article, estimate_chars


STATE_FILE = Path('data/state_enhanced.json')


def _load_templates():
    """data/topic_templates.py を動的にロード（パッケージ化されていない場所のため）"""
    spec = importlib.util.spec_from_file_location(
        'topic_templates',
        Path(__file__).parent / 'data' / 'topic_templates.py'
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {'rotation_index': 0, 'weekly_count': 0, 'history': []}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def main(force_topic: str = None, status: str = 'draft'):
    """毎日の記事生成メインフロー

    Args:
        force_topic: 指定トピックキー（例 '地震対策'）。Noneならローテーション。
        status: 'draft'（デフォルト）または 'publish'
    """
    tt = _load_templates()
    state = load_state()

    # トピックを決定
    if force_topic and force_topic in tt.TEMPLATES:
        topic_key = force_topic
        print(f'指定トピック: {topic_key}')
    else:
        idx = state.get('rotation_index', 0)
        topic_key = tt.ROTATION[idx % len(tt.ROTATION)]
        state['rotation_index'] = idx + 1
        print(f'ローテーション: {topic_key} (index={idx})')

    template = tt.TEMPLATES[topic_key]

    # 記事HTML 生成
    print(f'\n📝 記事HTML 生成中: {template["title"]}')
    content = build_article(template)
    chars = estimate_chars(content)
    print(f'  本文: {chars}字 / HTML {len(content):,} bytes')

    if chars < 1200:
        print(f'⚠️  記事が短すぎます（{chars}字）。テンプレート見直し必須')

    # WordPress に投稿
    print(f'\n📤 WordPress に投稿中（status={status}）...')
    try:
        url = wordpress.post(
            title=template['title'],
            content=content,
            category=template.get('category', '防災の基礎知識'),
            tags=template.get('tags', []),
            status=status,
        )
        print(f'  ✓ 投稿完了: {url}')
    except Exception as e:
        print(f'✗ WordPress投稿失敗: {e}')
        return

    # ID を URL から抽出
    import re
    m = re.search(r'[?&]p=(\d+)', url) or re.search(r'/(\d+)/?$', url)
    post_id = int(m.group(1)) if m else None

    # WAF 配慮
    time.sleep(5)

    # アイキャッチ画像
    print(f'\n🖼️  アイキャッチ画像 生成中...')
    try:
        emoji_map = {
            '地震対策': '🏠', '台風対策': '🌀', '水害対策': '🌊',
            '停電対策': '⚡', '断水対策': '💧', '火災対策': '🔥',
        }
        img_path = generate_eyecatch(
            title=template['title'],
            subtitle='防災グッズ完全ガイド',
            emoji=emoji_map.get(topic_key, '🛡️'),
        )
        print(f'  生成: {img_path}')

        media_id = wordpress.upload_image(img_path)
        if media_id and post_id:
            wordpress.set_featured_image(post_id, media_id)
            print(f'  ✓ アイキャッチ設定完了 (media={media_id})')
    except Exception as e:
        print(f'  ⚠️ アイキャッチ生成/設定失敗: {e}')

    # 履歴に記録
    state.setdefault('history', []).append({
        'topic': topic_key,
        'title': template['title'],
        'url': url,
        'chars': chars,
    })
    state['weekly_count'] = state.get('weekly_count', 0) + 1
    save_state(state)

    print(f'\n✅ 完了')
    print(f'   トピック: {topic_key}')
    print(f'   URL: {url}')
    print(f'   通算記事数: {state["weekly_count"]}')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='日次記事生成（テンプレート版）')
    p.add_argument('--topic', help='指定トピック（例: 地震対策）')
    p.add_argument('--publish', action='store_true', help='下書きでなく即公開')
    # 後方互換（旧フラグは無視するだけ）
    p.add_argument('--no-research', action='store_true', help='（互換用、機能なし）')
    p.add_argument('--force-research', action='store_true', help='（互換用、機能なし）')
    args = p.parse_args()

    main(
        force_topic=args.topic,
        status='publish' if args.publish else 'draft',
    )
