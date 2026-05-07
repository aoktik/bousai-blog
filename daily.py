"""日次記事生成スクリプト - GitHub Actionsから毎日1回実行される"""
import json
import sys
from pathlib import Path

import helpers.rakuten as rakuten
import helpers.wordpress as wordpress
import helpers.claude_api as claude_api

STATE_FILE = Path('data/state.json')


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {'processed_earthquakes': [], 'processed_typhoons': [], 'topic_index': 0}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    state = load_state()

    # トピックをローテーションで選択
    idx   = state.get('topic_index', 0) % len(claude_api.TOPICS)
    topic = claude_api.TOPICS[idx]
    print(f'今日のトピック: {topic["keyword"]} (index={idx})')

    # 楽天市場で商品を検索
    products = rakuten.search(topic['search'])
    if not products:
        products = rakuten.search(topic['keyword'] + ' 防災')
    print(f'楽天商品取得: {len(products)}件')

    if not products:
        print('商品が取得できませんでした。スキップします。')
        sys.exit(1)

    # Claude で記事を生成
    article = claude_api.generate_daily(topic, products)
    print(f'記事生成完了: {article["title"]}')

    # WordPress に投稿
    url = wordpress.post(
        title    = article['title'],
        content  = article['content'],
        category = topic['category'],
        tags     = topic.get('tags', []),
    )
    print(f'投稿完了: {url}')

    # 次のトピックに進める
    state['topic_index'] = idx + 1
    save_state(state)
    print('完了')


if __name__ == '__main__':
    main()
