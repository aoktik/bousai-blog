"""キーワード研究モジュール - Google Search Console APIから検索キーワードを自動抽出"""
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

try:
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials
    import googleapiclient.discovery
except ImportError:
    print("警告: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client がインストールされていません")
    print("インストール: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class KeywordResearcher:
    """Google Search Console API を使用してキーワード調査を実行"""

    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    MIN_VOLUME = 1000  # 最小検索ボリューム（月単位）

    def __init__(self, credentials_json_path: Optional[str] = None):
        """初期化

        Args:
            credentials_json_path: GCPサービスアカウントのJSON認証ファイルパス
        """
        self.credentials = None
        self.service = None
        self.property_url = os.environ.get('GSC_PROPERTY_URL', 'https://www.aoktik.online/')

        # 認証ファイルパスを決定
        if credentials_json_path is None:
            credentials_json_path = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')

        if credentials_json_path and Path(credentials_json_path).exists():
            self._authenticate(credentials_json_path)
        else:
            print("警告: Google Search Console認証ファイルが見つかりません")
            print(f"  GOOGLE_SERVICE_ACCOUNT_JSON={os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')}")
            print(f"  または credentials_json_path パラメータで指定してください")

    def _authenticate(self, credentials_json_path: str):
        """Google Search Console API に認証"""
        try:
            self.credentials = Credentials.from_service_account_file(
                credentials_json_path,
                scopes=self.SCOPES
            )
            self.service = googleapiclient.discovery.build(
                'webmasters',
                'v3',
                credentials=self.credentials
            )
            print(f"✓ Google Search Console認証成功: {credentials_json_path}")
        except Exception as e:
            print(f"✗ Google Search Console認証失敗: {e}")
            self.service = None

    def get_keywords(self, days: int = 90, min_impressions: int = 10) -> List[Dict]:
        """Google Search Console から検索キーワード・クエリを取得

        Args:
            days: 過去何日間のデータを取得するか
            min_impressions: 最小インプレッション数

        Returns:
            キーワードのリスト [{query, impressions, clicks, avg_ctr, avg_position}]
        """
        if not self.service:
            print("エラー: Google Search Console API が初期化されていません")
            return []

        try:
            # 日付範囲を設定
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            # Search Analytics API を呼び出し
            request = self.service.searchanalytics().query(
                siteUrl=self.property_url,
                body={
                    'startDate': start_date.isoformat(),
                    'endDate': end_date.isoformat(),
                    'dimensions': ['query'],
                    'dimensionFilterGroups': [
                        {
                            'filters': [
                                {
                                    'dimension': 'impression',
                                    'operator': 'GREATER_THAN',
                                    'expression': str(min_impressions)
                                }
                            ]
                        }
                    ],
                    'rowLimit': 1000,
                }
            )

            response = request.execute()
            rows = response.get('rows', [])

            keywords = []
            for row in rows:
                keywords.append({
                    'query': row.get('keys', [''])[0],
                    'impressions': row.get('impressions', 0),
                    'clicks': row.get('clicks', 0),
                    'avg_ctr': row.get('ctr', 0),
                    'avg_position': row.get('position', 0),
                })

            # インプレッション数でソート
            keywords.sort(key=lambda x: x['impressions'], reverse=True)

            print(f"✓ {len(keywords)}個のキーワードを取得しました（過去{days}日間）")
            return keywords

        except Exception as e:
            print(f"✗ キーワード取得に失敗しました: {e}")
            return []

    def filter_disaster_keywords(self, keywords: List[Dict], min_volume: int = 1000) -> List[Dict]:
        """防災・災害関連キーワードをフィルタリング

        Args:
            keywords: キーワードのリスト
            min_volume: 最小検索ボリューム

        Returns:
            フィルタリングされたキーワードのリスト
        """
        disaster_keywords = [
            '防災', '災害', '地震', '台風', '水害', '洪水', '津波', '火災',
            '豪雨', '落雷', '暴風', '大雨', '土砂崩れ', '崖崩れ', '停電',
            '断水', '備蓄', '避難', '非常用', '対策', '準備', '備え',
            '応急手当', '緊急', '危機', '警報', '注意報', '警戒', '警察',
            'グッズ', 'セット', 'リュック', '電源', '水', '食料', 'ラジオ',
            'ライト', 'トイレ', '毛布', 'テント', 'バッグ'
        ]

        filtered = []
        for kw in keywords:
            query = kw['query'].lower()
            # いずれかのキーワードを含む場合にフィルタリング
            if any(dk in query for dk in disaster_keywords):
                if kw['impressions'] >= min_volume:
                    filtered.append(kw)

        print(f"✓ {len(filtered)}個の防災関連キーワードをフィルタリングしました")
        return filtered

    def check_existing_articles(self, keywords: List[Dict], existing_titles: List[str]) -> List[Dict]:
        """既存記事との重複チェック

        Args:
            keywords: キーワードのリスト
            existing_titles: 既存記事のタイトルリスト

        Returns:
            重複していないキーワードのリスト
        """
        filtered = []
        for kw in keywords:
            query = kw['query'].lower()
            # どの既存記事タイトルも含まない場合にリストに追加
            if not any(title.lower() in query or query in title.lower() for title in existing_titles):
                filtered.append(kw)
            else:
                print(f"  → スキップ（既存記事との重複）: {kw['query']}")

        print(f"✓ {len(filtered)}個のキーワード（重複チェック後）")
        return filtered

    def save_keywords(self, keywords: List[Dict], output_file: str = None) -> str:
        """キーワードをJSONファイルに保存

        Args:
            keywords: キーワードのリスト
            output_file: 出力ファイルパス

        Returns:
            保存されたファイルパス
        """
        if output_file is None:
            output_file = Path(__file__).parent / 'data' / 'research_keywords.json'
        else:
            output_file = Path(output_file)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        output_file.write_text(
            json.dumps(keywords, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        print(f"✓ キーワード保存完了: {output_file}")
        return str(output_file)

    def research(self, existing_titles: List[str] = None, min_volume: int = None, days: int = 90) -> List[Dict]:
        """キーワード調査を実行（全処理）

        Args:
            existing_titles: 既存記事タイトルリスト
            min_volume: 最小検索ボリューム（デフォルト: 1000）
            days: 過去何日間のデータを取得するか

        Returns:
            フィルタリング・重複チェック済みのキーワードリスト
        """
        if min_volume is None:
            min_volume = self.MIN_VOLUME

        print(f"\n🔍 キーワード調査開始...")
        print(f"  期間: 過去 {days} 日間")
        print(f"  最小ボリューム: {min_volume}")

        # Google Search Console からキーワードを取得
        keywords = self.get_keywords(days=days, min_impressions=10)
        if not keywords:
            print("警告: キーワード取得結果が空です")
            return []

        # 防災関連キーワードをフィルタリング
        disaster_kw = self.filter_disaster_keywords(keywords, min_volume=min_volume)

        # 既存記事との重複をチェック
        if existing_titles:
            print(f"\n既存記事との重複チェック（{len(existing_titles)}件）...")
            final_kw = self.check_existing_articles(disaster_kw, existing_titles)
        else:
            final_kw = disaster_kw

        print(f"\n✓ 調査完了: {len(final_kw)}個の新規キーワードを発見")
        return final_kw


def research_keywords(existing_titles: List[str] = None, min_volume: int = 1000, days: int = 90) -> List[Dict]:
    """キーワード調査を実行するメイン関数

    Args:
        existing_titles: 既存記事タイトルリスト
        min_volume: 最小検索ボリューム
        days: 過去何日間のデータを取得するか

    Returns:
        キーワードリスト
    """
    researcher = KeywordResearcher()
    keywords = researcher.research(existing_titles=existing_titles, min_volume=min_volume, days=days)

    # JSONファイルに保存
    researcher.save_keywords(keywords)

    return keywords


def load_existing_titles() -> List[str]:
    """既存記事のタイトルを取得

    Returns:
        既存記事のタイトルリスト
    """
    # 注: 実際の実装では WordPress REST API から取得
    # ここはダミー実装
    existing_titles = [
        "防災リュック",
        "非常食おすすめ10選",
        "防災用保存水おすすめ5選",
        "防災セットおすすめ比較",
        "防災用簡易トイレおすすめ5選",
        "ポータブル電源おすすめ5選",
    ]
    return existing_titles


if __name__ == '__main__':
    import sys

    min_volume = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 90

    existing_titles = load_existing_titles()
    keywords = research_keywords(existing_titles=existing_titles, min_volume=min_volume, days=days)

    # トップ10を表示
    print("\n🏆 トップ10キーワード:")
    for i, kw in enumerate(keywords[:10], 1):
        print(f"  {i}. {kw['query']}: {kw['impressions']:.0f} impressions, {kw['avg_ctr']:.2%} CTR")
