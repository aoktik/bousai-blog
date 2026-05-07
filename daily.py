"""日次記事生成スクリプト - GitHub Actionsから毎日1回実行される"""
import json
import sys
import time
from pathlib import Path

from helpers.env import load_env  # 最初に環境変数をロード
load_env()

import helpers.wordpress as wordpress
import helpers.claude_api as claude_api
from helpers.images import generate_eyecatch
from publish_to_sns import publish_article_to_sns

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

    # WordPress に投稿（SiteGuard WAF対応のため待機が必要）
    url = wordpress.post(
        title    = article['title'],
        content  = article['content'],
        category = topic['category'],
        tags     = topic.get('tags', []),
    )
    print(f'投稿完了: {url}')

    # WAF制約対応: 次の操作まで待機
    time.sleep(5)

    # OGP画像を生成
    try:
        ogp_image_path = generate_eyecatch(
            title=article['title'],
            subtitle="防災グッズ完全ガイド",
        )
        print(f'OGP画像生成完了: {ogp_image_path}')
    except Exception as e:
        print(f'警告: OGP画像生成に失敗しました: {e}')
        ogp_image_path = None

    # SNS に投稿（Article excerpt は記事内容から自動抽出）
    try:
        from html.parser import HTMLParser

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.in_paragraph = False

            def handle_starttag(self, tag, attrs):
                if tag == 'p':
                    self.in_paragraph = True

            def handle_endtag(self, tag):
                if tag == 'p':
                    self.in_paragraph = False

            def handle_data(self, data):
                if self.in_paragraph:
                    self.text.append(data.strip())

        extractor = TextExtractor()
        extractor.feed(article['content'])
        excerpt = ' '.join(extractor.text[:2])[:200]  # 最初の200文字
        if not excerpt:
            excerpt = article['title']

        sns_results = publish_article_to_sns(
            article_title=article['title'],
            article_url=url,
            article_excerpt=excerpt,
            image_url=ogp_image_path
        )
        print(f'SNS投稿完了: {sns_results}')
    except Exception as e:
        print(f'警告: SNS投稿に失敗しました: {e}')

    state['topic_index'] = idx + 1
    save_state(state)
    print('完了')


if __name__ == '__main__':
    main()
