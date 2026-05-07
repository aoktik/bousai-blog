"""日次記事生成スクリプト - GitHub Actionsから毎日1回実行される"""
import json
import sys
from pathlib import Path

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

    idx   = state.get('topic_index', 0) % len(claude_api.TOPICS)
    topic = claude_api.TOPICS[idx]
    print(f'今日のトピック: {topic["keyword"]} (index={idx})')

    article = claude_api.generate_daily(topic)
    print(f'記事生成完了: {article["title"]}')

    url = wordpress.post(
        title    = article['title'],
        content  = article['content'],
        category = topic['category'],
        tags     = topic.get('tags', []),
    )
    print(f'投稿完了: {url}')

    state['topic_index'] = idx + 1
    save_state(state)
    print('完了')


if __name__ == '__main__':
    main()
