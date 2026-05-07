"""強化版日次記事生成スクリプト - キーワード研究と関連記事自動挿入に対応"""
import json
import sys
import time
import re
from pathlib import Path
from typing import List, Optional

from helpers.env import load_env
load_env()

import helpers.wordpress as wordpress
import helpers.claude_api as claude_api
from helpers.images import generate_eyecatch
from publish_to_sns import publish_article_to_sns
from keyword_research import research_keywords, load_existing_titles


STATE_FILE = Path('data/state_enhanced.json')


def load_state() -> dict:
    """状態ファイルを読み込む"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {
        'last_research_date': None,
        'current_keywords': [],
        'keyword_index': 0,
        'weekly_count': 0
    }


def save_state(state: dict):
    """状態をファイルに保存"""
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def get_search_keywords(state: dict, force_research: bool = False) -> tuple:
    """検索キーワードを取得（キャッシュまたは新規研究）

    Args:
        state: 状態辞書
        force_research: キーワード研究を強制実行するか

    Returns:
        (keyword_list, updated_state)
    """
    from datetime import datetime, timedelta

    # 24時間以上経過しているか、キーワードが空か、強制実行の場合
    should_research = force_research or not state.get('current_keywords')

    if state.get('last_research_date'):
        last_date = datetime.fromisoformat(state['last_research_date'])
        if datetime.now() - last_date > timedelta(days=1):
            should_research = True

    if should_research:
        print("\n🔍 キーワード研究を実行中...")
        try:
            existing_titles = load_existing_titles()
            keywords = research_keywords(existing_titles=existing_titles, min_volume=1000, days=90)

            if keywords:
                state['current_keywords'] = [kw['query'] for kw in keywords[:50]]  # 最大50個
                state['last_research_date'] = datetime.now().isoformat()
                state['keyword_index'] = 0
                print(f"✓ {len(state['current_keywords'])}個のキーワードを取得しました")
            else:
                print("警告: キーワード研究が空の結果を返しました")
        except Exception as e:
            print(f"警告: キーワード研究に失敗しました: {e}")
            print("→ デフォルトトピックを使用します")

    # キーワードがない場合はデフォルトトピックを使用
    if not state.get('current_keywords'):
        state['current_keywords'] = [topic['keyword'] for topic in claude_api.TOPICS]
        state['keyword_index'] = 0

    return state['current_keywords'], state


def generate_related_articles_section(current_article_title: str, existing_articles: List[dict]) -> str:
    """関連記事セクションを生成（Gutenberg形式）

    Args:
        current_article_title: 現在の記事タイトル
        existing_articles: 既存記事リスト [{id, title, url, category}]

    Returns:
        関連記事セクションのGutenberg HTML
    """
    if not existing_articles:
        return ""

    # 現在の記事と関連度の高い記事を選別
    # シンプルな実装: 同じカテゴリまたはタグを含む記事を優先
    related = []
    for article in existing_articles:
        # 記事IDが409（ポータブル電源）の場合は必ず含める
        if article.get('id') == 409:
            related.insert(0, article)  # 最初に配置
        elif article.get('id') != 414:  # ハブ記事は除外
            related.append(article)

    # 最大5個に制限
    related = related[:5]

    if not related:
        return ""

    # Gutenberg形式で関連記事セクションを生成
    html_parts = [
        '<!-- wp:heading {"level":3,"align":"center"} -->',
        '<h3>こちらもおすすめ</h3>',
        '<!-- /wp:heading -->',
        '<!-- wp:columns {"verticalAlignment":"center"} -->',
        '<div class="wp-block-columns is-layout-flex wp-container-core-columns-is-layout-3" style="gap: var(--wp--style--block-gap, 2em)">',
    ]

    for article in related:
        title = article.get('title', 'タイトル')
        url_ = article.get('url', '#')
        card_html = (
            '<!-- wp:column -->\n'
            '<div class="wp-block-column">\n'
            '  <div class="wp-block-group" style="background-color:#f8fafc;padding:20px;">\n'
            f'    <h4>{title}</h4>\n'
            f'    <p><a href="{url_}" style="color:#e94560;text-decoration:none;font-weight:bold;">詳しく読む →</a></p>\n'
            '  </div>\n'
            '</div>\n'
            '<!-- /wp:column -->'
        )
        html_parts.append(card_html)

    html_parts.extend([
        '</div>',
        '<!-- /wp:columns -->',
    ])

    return '\n'.join(html_parts)


def generate_article_with_keyword(keyword: str, existing_articles: List[dict] = None) -> dict:
    """キーワードを使用して記事を生成

    Args:
        keyword: 検索キーワード
        existing_articles: 既存記事リスト（関連記事生成用）

    Returns:
        記事データ {title, content, excerpt, category}
    """
    # キーワードに基づいてカテゴリを自動判定
    if any(word in keyword for word in ['地震', '台風', '水害', '津波']):
        category = '地震対策'
    elif any(word in keyword for word in ['停電', '断水', '火災']):
        category = '防災の基礎知識'
    else:
        category = '防災グッズレビュー'

    # Gemini APIで記事を生成
    prompt = f"""あなたは防災専門のアフィリエイトブログ「防災グッズ完全ガイド」（https://www.aoktik.online）のライターです。

【今回の記事テーマ】
「{keyword}」について

【文体・スタイル】
- 「〜しましょう」「〜がおすすめです」という勧奨調
- 読者に「あなた」と呼びかける
- 専門用語は補足説明付きで使用
- 温かみのある文体で読者の不安に共感

【記事構成】
1. H1見出し: {keyword}について（タイトル形式）
2. 導入: {keyword}の重要性（2-3段落）
3. 本体: 具体的な対策・方法・商品紹介（複数のH2見出し）
4. 各セクションで商品紹介時は楽天検索アフィリエイトリンクを活用
5. 結論: 防災への取り組みの大切さ

【出力形式】
Gutenberg互換のHTML形式で出力してください。H1,H2見出し、段落、リストを適切に使用。
最小1,500字以上の記事を生成してください。

記事を生成してください："""

    try:
        response = claude_api._call_gemini(prompt)
        article = claude_api._parse(response)

        # 既存記事がある場合は関連記事セクションを追加
        if existing_articles:
            related_section = generate_related_articles_section(article['title'], existing_articles)
            if related_section:
                article['content'] = article['content'] + '\n\n' + related_section

        return {
            'title': article['title'],
            'content': article['content'],
            'excerpt': article['content'][:200],  # 最初の200文字を抜粋
            'category': category,
            'keyword': keyword
        }
    except Exception as e:
        print(f"エラー: 記事生成に失敗しました: {e}")
        return None


def main(keyword: str = None, use_research: bool = True, force_research: bool = False):
    """強化版日次記事生成メイン関数

    Args:
        keyword: 指定キーワード（Noneの場合は自動選択）
        use_research: キーワード研究を使用するか
        force_research: キーワード研究を強制実行するか
    """
    state = load_state()

    # キーワードを決定
    if keyword:
        selected_keyword = keyword
        print(f'指定キーワード: {selected_keyword}')
    elif use_research:
        keywords, state = get_search_keywords(state, force_research=force_research)
        idx = state['keyword_index'] % len(keywords)
        selected_keyword = keywords[idx]
        state['keyword_index'] = idx + 1
        print(f'選択キーワード: {selected_keyword} (index={idx})')
    else:
        # デフォルトトピックを使用
        idx = state.get('keyword_index', 0) % len(claude_api.TOPICS)
        topic = claude_api.TOPICS[idx]
        selected_keyword = topic['keyword']
        state['keyword_index'] = idx + 1
        print(f'デフォルトトピック: {selected_keyword} (index={idx})')

    # ダミー既存記事リスト（実際はWordPress REST APIから取得）
    existing_articles = [
        {'id': 414, 'title': '何から揃える？優先順位と予算別プラン', 'url': 'https://www.aoktik.online/?page_id=414', 'category': '防災の基礎知識'},
        {'id': 409, 'title': '【2026年版】防災用ポータブル電源おすすめ5選', 'url': 'https://www.aoktik.online/?page_id=409', 'category': '防災グッズレビュー'},
        {'id': 411, 'title': '非常食おすすめ10選', 'url': 'https://www.aoktik.online/?page_id=411', 'category': '防災グッズレビュー'},
        {'id': 412, 'title': '防災セットおすすめ比較', 'url': 'https://www.aoktik.online/?page_id=412', 'category': '防災グッズレビュー'},
        {'id': 413, 'title': '防災用簡易トイレおすすめ5選', 'url': 'https://www.aoktik.online/?page_id=413', 'category': '防災グッズレビュー'},
        {'id': 380, 'title': '【2026年版】防災用保存水おすすめ5選', 'url': 'https://www.aoktik.online/?page_id=380', 'category': '防災グッズレビュー'},
    ]

    # 記事を生成
    print(f'\n📝 記事生成開始: {selected_keyword}')
    article = generate_article_with_keyword(selected_keyword, existing_articles=existing_articles)

    if not article:
        print('エラー: 記事生成に失敗しました')
        return

    print(f'記事生成完了: {article["title"]}')

    # WordPress に投稿
    print(f'\n📤 WordPress投稿中...')
    try:
        url = wordpress.post(
            title=article['title'],
            content=article['content'],
            category=article['category'],
            tags=[article['keyword']],
            status='draft'  # 手作業レビュー用に下書き状態で保存
        )
        print(f'投稿完了（下書き状態）: {url}')
    except Exception as e:
        print(f'エラー: WordPress投稿に失敗しました: {e}')
        return

    # WAF制約対応
    time.sleep(5)

    # アイキャッチ画像を生成 → アップロード → 設定
    print(f'\n🖼️ アイキャッチ画像生成中...')
    try:
        img_path = generate_eyecatch(
            title=article['title'],
            subtitle="防災グッズ完全ガイド",
        )
        print(f'  生成完了: {img_path}')

        media_id = wordpress.upload_image(img_path)
        ogp_image_path = str(img_path)
        if media_id:
            # 投稿IDをURLから抽出（draft時は ?p=ID 形式）
            m = re.search(r'[?&]p=(\d+)', url)
            if m:
                wordpress.set_featured_image(int(m.group(1)), media_id)
                print(f'  ✓ アイキャッチ設定完了 (media={media_id})')
    except Exception as e:
        print(f'警告: アイキャッチ画像生成に失敗しました: {e}')
        ogp_image_path = None

    # SNS投稿（下書きのため公開URLがない場合はスキップ）
    if not url.startswith('http'):
        print('注意: 下書き状態のため SNS投稿はスキップします')
    else:
        print(f'\n📱 SNS投稿中...')
        try:
            sns_results = publish_article_to_sns(
                article_title=article['title'],
                article_url=url,
                article_excerpt=article['excerpt'],
                image_url=ogp_image_path
            )
            print(f'SNS投稿完了: {sns_results}')
        except Exception as e:
            print(f'警告: SNS投稿に失敗しました: {e}')

    # 状態を保存
    state['weekly_count'] = state.get('weekly_count', 0) + 1
    save_state(state)

    print(f'\n✓ 完了')
    print(f'  週間投稿数: {state["weekly_count"]}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='強化版日次記事生成スクリプト')
    parser.add_argument('--keyword', type=str, help='キーワードを指定')
    parser.add_argument('--no-research', action='store_true', help='キーワード研究を使用しない')
    parser.add_argument('--force-research', action='store_true', help='キーワード研究を強制実行')

    args = parser.parse_args()

    main(
        keyword=args.keyword,
        use_research=not args.no_research,
        force_research=args.force_research
    )
