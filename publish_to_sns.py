"""SNS自動投稿モジュール - X、Threads、Noteへの投稿を管理"""
import os
import re
import time
import json
from typing import Optional
import requests
try:
    import tweepy
except ImportError:
    tweepy = None

from helpers import claude_api, wordpress


class SNSPublisher:
    """各SNSプラットフォームへの投稿を管理"""

    def __init__(self):
        self.x_client = self._init_x_client()
        self.threads_token = os.environ.get('THREADS_ACCESS_TOKEN')
        self.threads_account_id = os.environ.get('THREADS_BUSINESS_ACCOUNT_ID')
        self.note_token = os.environ.get('NOTE_API_KEY')

    def _init_x_client(self):
        """X API v2クライアントの初期化"""
        if not tweepy:
            print("警告: tweepyがインストールされていません。X投稿は無効です。")
            return None

        bearer_token = os.environ.get('X_BEARER_TOKEN')
        if not bearer_token:
            print("警告: X_BEARER_TOKENが設定されていません。X投稿は無効です。")
            return None

        return tweepy.Client(bearer_token=bearer_token)

    def generate_sns_copy(self, article_title: str, article_url: str, article_excerpt: str = "") -> dict:
        """Gemini APIを使用して各SNS向けのテキストを生成

        Args:
            article_title: 記事タイトル
            article_url: 記事URL
            article_excerpt: 記事の抜粋（オプション）

        Returns:
            各SNS向けのテキスト辞書
        """
        prompt = f"""以下の記事を各SNSで投稿するための最適化されたテキストを生成してください。

記事タイトル: {article_title}
記事抜粋: {article_excerpt if article_excerpt else "（抜粋なし）"}
記事URL: {article_url}

以下の形式でJSON形式で返してください（Markdown記号は不要）:
{{
    "x": "X（Twitter）向けのテキスト。140字以下。ハッシュタグは #防災 #災害対策 の形式で3個まで。URLは含めない。",
    "threads": "Threads向けのテキスト。250字程度。改行や絵文字も活用してOK。URLは含めない。",
    "note": "Note向けの説明テキスト。冒頭200字程度で記事の要点をまとめてください。URLは含めない。"
}}

各テキストは改行記号\\nを含まず、ダブルクォートは避けてください。"""

        try:
            response = claude_api._call_gemini(prompt)

            # JSONレスポンスを解析
            copy_dict = json.loads(response)
            return copy_dict
        except Exception as e:
            print(f"エラー: Gemini APIからのテキスト生成に失敗しました: {e}")
            return {
                "x": f"{article_title[:130]} 詳しくは👇 #防災 #災害対策 #防災知識",
                "threads": f"{article_title}\n\n防災・災害対策についての新しい記事を公開しました。ぜひご覧ください！",
                "note": article_title
            }

    def post_to_x(self, text: str, image_url: Optional[str] = None) -> Optional[str]:
        """X（Twitter）に投稿

        Args:
            text: 投稿テキスト（140字以下推奨）
            image_url: 画像URL（オプション）

        Returns:
            投稿ID、またはエラー時はNone
        """
        if not self.x_client:
            print("スキップ: X APIクライアントが初期化されていません")
            return None

        try:
            # テキストを140字以下に制限
            if len(text) > 140:
                text = text[:137] + "..."

            response = self.x_client.create_tweet(text=text)
            tweet_id = response.data.get('id')
            print(f"✓ X投稿成功 (ID: {tweet_id})")
            return tweet_id
        except Exception as e:
            print(f"✗ X投稿失敗: {e}")
            return None

    def post_to_threads(self, text: str, image_url: Optional[str] = None) -> Optional[str]:
        """Threads に投稿

        Args:
            text: 投稿テキスト（250字程度）
            image_url: 画像URL（オプション）

        Returns:
            投稿ID、またはエラー時はNone
        """
        if not self.threads_token or not self.threads_account_id:
            print("スキップ: Threads認証情報が設定されていません")
            return None

        try:
            url = f"https://graph.threads.net/v1.0/{self.threads_account_id}/threads"

            payload = {
                "media_type": "TEXT",
                "text": text[:500],  # Threads上限は500字
                "access_token": self.threads_token
            }

            # 画像がある場合はCARROUSEL_CONTAINERを使用
            if image_url:
                payload["media_type"] = "CAROUSEL_CONTAINER"
                # 実装簡略化のため、画像は別途処理
                pass

            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get('id'):
                print(f"✓ Threads投稿成功 (ID: {data['id']})")
                return data['id']
            else:
                print(f"✗ Threads投稿失敗: {data}")
                return None
        except Exception as e:
            print(f"✗ Threads投稿失敗: {e}")
            return None

    def post_to_note(self, title: str, excerpt: str, article_url: str) -> Optional[str]:
        """Note に記事を投稿（API経由または定期投稿リスト形式）

        Args:
            title: 記事タイトル
            excerpt: 記事抜粋
            article_url: 記事URL

        Returns:
            投稿ID、またはエラー時はNone
        """
        if not self.note_token:
            print("スキップ: Note認証情報が設定されていません")
            # フォールバック: 投稿リストをJSONに記録
            self._log_note_queue(title, excerpt, article_url)
            return None

        try:
            # Note APIの仕様に基づいて投稿を作成
            # Note公式APIが利用可能な場合のみ実装
            url = "https://api.note.com/v2/stories"

            payload = {
                "title": title,
                "body": f"{excerpt}\n\n詳しくはこちら→ {article_url}",
                "status": "open"
            }

            headers = {
                "Authorization": f"Bearer {self.note_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get('id'):
                print(f"✓ Note投稿成功 (ID: {data['id']})")
                return data['id']
            else:
                print(f"✗ Note投稿失敗: {data}")
                self._log_note_queue(title, excerpt, article_url)
                return None
        except Exception as e:
            print(f"✗ Note投稿失敗（API経由）: {e}")
            # フォールバック: キューに記録
            self._log_note_queue(title, excerpt, article_url)
            return None

    def _log_note_queue(self, title: str, excerpt: str, article_url: str):
        """Note投稿をキューに記録（手作業投稿用）"""
        from pathlib import Path

        queue_file = Path('data/note_queue.json')

        if queue_file.exists():
            queue = json.loads(queue_file.read_text(encoding='utf-8'))
        else:
            queue = []

        queue.append({
            "title": title,
            "excerpt": excerpt,
            "url": article_url,
            "timestamp": time.time()
        })

        queue_file.parent.mkdir(exist_ok=True)
        queue_file.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"→ Note投稿をキューに記録しました: {queue_file}")

    def publish_article(self, article_title: str, article_url: str, article_excerpt: str = "", image_url: Optional[str] = None) -> dict:
        """記事をすべてのSNSに投稿

        Args:
            article_title: 記事タイトル
            article_url: 記事URL
            article_excerpt: 記事の抜粋（オプション）
            image_url: OGP画像URL（オプション）

        Returns:
            各SNSの投稿結果
        """
        print(f"\n📱 SNS投稿開始: {article_title}")
        print(f"URL: {article_url}")

        # 各SNS向けのテキストを生成
        sns_copy = self.generate_sns_copy(article_title, article_url, article_excerpt)

        # 投稿実行（順序: X → Threads → Note）
        results = {
            'x': self.post_to_x(sns_copy.get('x', ''), image_url),
            'threads': self.post_to_threads(sns_copy.get('threads', ''), image_url),
            'note': self.post_to_note(article_title, sns_copy.get('note', ''), article_url)
        }

        print(f"✓ SNS投稿完了")
        return results


def publish_article_to_sns(article_title: str, article_url: str, article_excerpt: str = "", image_url: Optional[str] = None) -> dict:
    """記事をSNSに投稿するメイン関数

    daily.py から呼び出される
    """
    publisher = SNSPublisher()
    return publisher.publish_article(article_title, article_url, article_excerpt, image_url)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("使用法: python3 publish_to_sns.py <title> <url> [excerpt] [image_url]")
        sys.exit(1)

    title = sys.argv[1]
    url = sys.argv[2]
    excerpt = sys.argv[3] if len(sys.argv) > 3 else ""
    image_url = sys.argv[4] if len(sys.argv) > 4 else None

    results = publish_article_to_sns(title, url, excerpt, image_url)
    print(f"\n投稿結果: {results}")
