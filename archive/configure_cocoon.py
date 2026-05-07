"""Cocoon全設定を防災ブログ向けに最適化"""
import os, base64, json, requests

WP_URL = 'https://www.aoktik.online'
WP_USER = os.environ['WP_USER']
WP_PASSWORD = os.environ['WP_PASSWORD']

def wp_auth():
    creds = f'{WP_USER}:{WP_PASSWORD}'
    token = base64.b64encode(creds.encode()).decode()
    return {'Authorization': f'Basic {token}', 'Content-Type': 'application/json'}

API = f'{WP_URL}/wp-json/cocoon-cfg/v1'

def get_all():
    r = requests.get(f'{API}/all', headers=wp_auth())
    r.raise_for_status()
    return r.json()

def set_options(opts):
    r = requests.post(f'{API}/set', json=opts, headers=wp_auth())
    r.raise_for_status()
    return r.json()

# ============================================================
# 防災ブログ向け Cocoon 全設定
# ============================================================

# --- 1. スキン ---
# silkスキン: クリーンで信頼感のあるデザイン
SKIN = {
    'skin_url': f'{WP_URL}/wp-content/themes/cocoon-master/skins/silk/style.css',
}

# --- 2. 全体 ---
GLOBAL = {
    'site_key_color': '#1a365d',           # ダークネイビー: 信頼・安心感
    'site_key_text_color': '#ffffff',       # キーカラー上の文字: 白
    'site_text_color': '#333333',           # 本文テキスト: 読みやすいダークグレー
    'site_link_color': '#2563eb',           # リンク色: 標準的な青
    'site_background_color': '#f8fafc',     # 背景: クリーンな薄グレー
    'site_font_family': 'noto_sans_jp',     # フォント: Noto Sans JP（視認性高い）
    'site_font_size': '16px',              # フォントサイズ: 標準
    'site_font_weight': '400',             # フォントウェイト: 標準
    'site_icon_font': 'font_awesome_5',     # アイコン: Font Awesome 5
    'site_date_format': 'Y.m.d',
    'site_initiation_year': '2026',
    'align_site_width': '1',               # サイト幅を揃える
    'site_background_image_url': '',        # 背景画像なし（クリーン）
    'site_selection_background_color': '#1a365d',
    'site_selection_color': '#ffffff',
}

# --- 3. ヘッダー ---
HEADER = {
    'header_layout_type': 'center_logo_slim',  # センターロゴ（スリム）
    'header_background_color': '#ffffff',       # ヘッダー背景: 白
    'header_text_color': '#1a365d',            # ヘッダーテキスト: ネイビー
    'header_container_background_color': '',
    'header_container_text_color': '',
    'header_fixed': '1',                       # ヘッダー固定表示
    'header_area_height': '',
    'header_background_image_url': '',
    'header_background_attachment_fixed': '',
    'tagline_position': 'header_top',          # キャッチフレーズ位置
    'global_navi_background_color': '#1a365d', # グローバルナビ: ネイビー
    'global_navi_text_color': '#ffffff',       # ナビテキスト: 白
    'global_navi_menu_text_width_enable': '1',
    'global_navi_menu_width': '',
    'global_navi_sub_menu_width': '',
}

# --- 4. 広告 ---
AD = {
    'all_ads_visible': '1',
    'all_adsenses_visible': '1',
    'ad_label_caption': 'スポンサーリンク',
    'ad_shortcode_enable': '1',
    'ad_shortcode_format': 'rectangle',
    'ad_shortcode_label_visible': '1',
    # 広告配置: 記事上は非表示、記事中・記事下に表示
    'ad_pos_above_title_visible': '',
    'ad_pos_below_title_visible': '',
    'ad_pos_content_top_visible': '',
    'ad_pos_content_middle_visible': '1',      # 記事中
    'ad_pos_content_middle_count': '1',
    'ad_pos_content_middle_format': 'rectangle',
    'ad_pos_content_middle_label_visible': '1',
    'ad_pos_content_bottom_visible': '1',      # 記事下
    'ad_pos_content_bottom_format': 'rectangle',
    'ad_pos_content_bottom_label_visible': '1',
    'ad_pos_above_sns_buttons_visible': '',
    'ad_pos_below_sns_buttons_visible': '',
    'ad_pos_below_related_posts_visible': '1', # 関連記事下
    'ad_pos_below_related_posts_format': 'rectangle',
    'ad_pos_index_top_visible': '',
    'ad_pos_index_middle_visible': '',
    'ad_pos_index_bottom_visible': '',
    'ad_pos_sidebar_top_visible': '',
    'ad_pos_sidebar_bottom_visible': '',
    'adsense_display_method': '',
    # PR表記（ステマ規制対応）
    'pr_label_small_visible': '1',
    'pr_label_small_caption': 'PR',
    'pr_label_large_visible': '1',
    'pr_label_large_caption': '記事内に広告が含まれています。',
    'pr_label_single_visible': '1',
    'pr_label_page_visible': '',
    'pr_label_category_page_visible': '',
}

# --- 5. タイトル ---
TITLE = {
    'title_separator': 'pipe',                    # タイトル区切り: |
    'front_page_title_format': 'sitename_tagline', # トップ: サイト名 | キャッチフレーズ
    'singular_page_title_format': 'pagetitle_sitename', # 個別: 記事名 | サイト名
    'category_page_title_format': 'category_sitename',
    'front_page_meta_description': '一人暮らしの防災準備を徹底ガイド。ポータブル電源・非常食・防災セット・簡易トイレなど、本当に必要な防災グッズを予算別・優先順位つきで紹介。初めてでも迷わない防災情報サイト。',
    'front_page_meta_keywords': '防災グッズ,一人暮らし,防災セット,非常食,ポータブル電源,簡易トイレ,保存水,備蓄',
    'simplified_site_name': '',
}

# --- 6. SEO ---
SEO = {
    'meta_description_to_front_page': '1',
    'meta_description_to_singular': '1',
    'meta_description_to_category': '1',
    'meta_keywords_to_front_page': '1',
    'meta_keywords_to_singular': '1',
    'meta_keywords_to_category': '1',
    'canonical_tag_enable': '1',
    'json_ld_tag_enable': '1',
    'category_page_noindex': '',          # カテゴリページはインデックス
    'tag_page_noindex': '',               # タグページもインデックス
    'other_archive_page_noindex': '1',    # その他アーカイブはnoindex
    'attachment_page_noindex': '1',
    'paged_category_page_noindex': '',
    'paged_tag_page_noindex': '1',
    'seo_date_type': 'both_date',         # 投稿日・更新日両方表示
    'prev_next_enable': '1',
    'auto_post_slug_enable': '',          # 自動スラッグ変換は無効
}

# --- 7. OGP ---
OGP = {
    'facebook_ogp_enable': '1',
    'twitter_card_enable': '1',
    'twitter_card_type': 'summary_large_image',  # 大きい画像カード
    'ogp_home_image_url': '',  # TODO: 専用OGP画像があれば設定
}

# --- 8. アクセス解析 ---
# GA4やSearch Consoleは個別に設定が必要
ANALYTICS = {
    'google_analytics_script': 'gtag.js',
    'analytics_admin_include': '',         # 管理者のアクセスは除外
}

# --- 9. カラム ---
COLUMN = {
    'main_column_contents_width': '800',   # メインカラム: 800px
    'sidebar_contents_width': '336',       # サイドバー: 336px（広告最適幅）
    'sidebar_position': 'sidebar_right',   # サイドバー右
    'sidebar_display_type': 'display_all', # 全ページでサイドバー表示
    'main_column_padding': '20',
    'sidebar_padding': '20',
    'main_sidebar_margin': '20',
    'main_column_border_color': '#e2e8f0',
    'main_column_border_width': '0',       # メインカラムの枠線なし
    'sidebar_border_color': '#e2e8f0',
    'sidebar_border_width': '0',
}

# --- 10. インデックス ---
INDEX = {
    'entry_card_type': 'entry_card',       # 通常のエントリーカード
    'entry_card_border_visible': '1',
    'entry_card_excerpt_max_length': '120',
    'entry_card_excerpt_more': '...',
    'entry_card_snippet_visible': '1',     # 抜粋表示ON
    'entry_card_post_date_visible': '1',   # 投稿日表示
    'entry_card_post_update_visible': '1', # 更新日表示
    'entry_card_post_author_visible': '',   # 著者名は非表示
    'entry_card_post_comment_count_visible': '',
    'entry_card_post_date_or_update_visible': '',
    'smartphone_entry_card_snippet_visible': '1',
    'smartphone_entry_card_1_column': '',   # スマホ2カラム維持
    'index_sort_orderby': '',
    'all_thumbnail_visible': '1',          # サムネイル表示
    'thumbnail_image_type': 'wide',        # ワイドサムネイル
}

# --- 11. 投稿 ---
POST = {
    'post_date_visible': '1',
    'post_update_visible': '1',
    'post_author_visible': '',             # 著者名非表示
    'eyecatch_visible': '1',              # アイキャッチ表示
    'eyecatch_width_100_percent_enable': '1',  # 100%幅
    'eyecatch_center_enable': '1',
    'eyecatch_caption_visible': '',        # キャプション非表示
    'eyecatch_label_visible': '1',
    'category_tag_display_position': 'content_bottom',
    'category_tag_display_type': 'one_row',
    'single_breadcrumbs_position': 'main_top',
    'single_breadcrumbs_include_post': '1',
    'related_entries_visible': '1',        # 関連記事表示
    'related_entry_count': '6',
    'related_entry_type': 'entry_card',
    'related_entry_heading': '関連記事',
    'related_entry_sub_heading': 'あわせて読みたい',
    'related_entry_card_snippet_visible': '1',
    'related_entry_border_visible': '1',
    'related_association_type': 'category',
    'related_excerpt_max_length': '80',
    'post_navi_visible': '1',
    'post_navi_type': 'default',
    'post_navi_position': 'under_related',
    'post_navi_same_category_enable': '1', # 同カテゴリ内でナビ
}

# --- 12. 固定ページ ---
PAGE = {
    'page_breadcrumbs_position': 'main_top',
    'page_breadcrumbs_include_post': '1',
    'page_comment_visible': '',            # 固定ページのコメント非表示
    'page_toc_visible': '',                # 固定ページの目次非表示
}

# --- 13. 本文 ---
CONTENT = {
    'entry_content_line_hight': '1.9',     # 行間: ゆったり読みやすく
    'entry_content_margin_hight': '1.9',
    'content_read_time_visible': '1',      # 読了時間表示
    'content_image_center_enable': '1',    # 画像センタリング
    'external_link_icon_visible': '1',     # 外部リンクアイコン表示
    'external_link_icon': 'fa-external-link',
    'internal_link_icon_visible': '',
    'responsive_table_enable': '1',        # レスポンシブテーブル
    'responsive_table_first_column_sticky_enable': '1',
}

# --- 14. 目次 ---
TOC = {
    'toc_visible': '1',
    'single_toc_visible': '1',
    'toc_title': '目次',
    'toc_depth': '3',                      # h3まで表示（深すぎない）
    'toc_display_count': '2',              # 見出し2つ以上で表示
    'toc_number_type': 'number',           # 番号付き
    'toc_toggle_switch_enable': '1',       # 開閉スイッチ
    'toc_content_visible': '1',
    'toc_open_caption': '開く',
    'toc_close_caption': '閉じる',
    'toc_position_center': '1',
    'toc_before_ads': '1',                 # 広告の前に目次
    'toc_heading_inner_html_tag_enable': '1',
    'multi_page_toc_visible': '1',
    'category_toc_visible': '',            # カテゴリページの目次は不要
    'tag_toc_visible': '',
}

# --- 15. SNSシェア ---
SNS_SHARE = {
    # トップシェアボタン
    'sns_top_share_buttons_visible': '1',
    'sns_top_share_button_color': 'brand_color',
    'sns_top_share_column_count': '6',
    'sns_top_share_logo_caption_position': 'high_and_low_lc',
    'sns_top_share_buttons_count_visible': '',
    # 各ボタン（上）
    'top_twitter_share_button_visible': '1',
    'top_facebook_share_button_visible': '1',
    'top_hatebu_share_button_visible': '1',
    'top_pocket_share_button_visible': '1',
    'top_line_at_share_button_visible': '1',
    'top_copy_share_button_visible': '1',
    'top_pinterest_share_button_visible': '',
    'top_linkedin_share_button_visible': '',
    'top_threads_share_button_visible': '',
    'top_bluesky_share_button_visible': '',
    'top_mastodon_share_button_visible': '',
    'top_misskey_share_button_visible': '',
    'top_comment_share_button_visible': '',
    # ボトムシェアボタン
    'sns_bottom_share_buttons_visible': '1',
    'sns_bottom_share_button_color': 'brand_color',
    'sns_bottom_share_column_count': '6',
    'sns_bottom_share_logo_caption_position': 'high_and_low_lc',
    'sns_bottom_share_buttons_count_visible': '',
    'sns_bottom_share_message': 'この記事をシェアする',
    # 各ボタン（下）
    'bottom_twitter_share_button_visible': '1',
    'bottom_facebook_share_button_visible': '1',
    'bottom_hatebu_share_button_visible': '1',
    'bottom_pocket_share_button_visible': '1',
    'bottom_line_at_share_button_visible': '1',
    'bottom_copy_share_button_visible': '1',
    'bottom_pinterest_share_button_visible': '',
    'bottom_linkedin_share_button_visible': '',
    'bottom_threads_share_button_visible': '',
    'bottom_bluesky_share_button_visible': '',
    'bottom_mastodon_share_button_visible': '',
    'bottom_misskey_share_button_visible': '',
    'bottom_comment_share_button_visible': '',
    # 表示ページ設定
    'sns_single_top_share_buttons_visible': '1',
    'sns_single_bottom_share_buttons_visible': '1',
    'sns_page_top_share_buttons_visible': '',
    'sns_page_bottom_share_buttons_visible': '',
    'sns_front_page_top_share_buttons_visible': '',
    'sns_front_page_bottom_share_buttons_visible': '',
    'sns_category_top_share_buttons_visible': '',
    'sns_category_bottom_share_buttons_visible': '',
    'sns_tag_top_share_buttons_visible': '',
    'sns_tag_bottom_share_buttons_visible': '',
    # シェアカウント
    'sns_share_count_cache_enable': '1',
    'sns_share_count_cache_interval': '6',
}

# --- 16. SNSフォロー ---
SNS_FOLLOW = {
    'sns_follow_buttons_visible': '',      # フォローボタン非表示（SNSアカウント未設定のため）
    'sns_follow_button_color': 'brand_color',
    'sns_follow_message': 'フォローする',
    'sns_follow_buttons_count_visible': '',
    'sns_single_follow_buttons_visible': '',
    'sns_page_follow_buttons_visible': '',
    'sns_front_page_follow_buttons_visible': '',
    'sns_category_follow_buttons_visible': '',
    'sns_tag_follow_buttons_visible': '',
    'feedly_follow_button_visible': '',
    'rss_follow_button_visible': '',
}

# --- 17. 画像 ---
IMAGE = {
    'image_zoom_effect': 'baguettebox',    # 画像拡大エフェクト
    'image_wrap_effect': 'none',
    'retina_thumbnail_enable': '1',        # Retina対応
    'no_image_url': '',
    'eyecatch_width_100_percent_enable': '1',
}

# --- 18. ブログカード ---
BLOGCARD = {
    'internal_blogcard_enable': '1',       # 内部ブログカード有効
    'internal_blogcard_thumbnail_style': 'left',
    'internal_blogcard_date_type': 'post_date',
    'internal_blogcard_target_blank': '',   # 内部は同タブ
    'internal_blogcard_domain_style': 'domain',
    'external_blogcard_enable': '1',       # 外部ブログカード有効
    'external_blogcard_thumbnail_style': 'left',
    'external_blogcard_target_blank': '1', # 外部は別タブ
    'external_blogcard_domain_style': 'domain',
    'external_blogcard_cache_retention_period': '30',
}

# --- 19. コード ---
CODE = {
    'code_highlight_enable': '',           # コードハイライト不要（防災ブログ）
}

# --- 20. コメント ---
COMMENT = {
    'comment_display_type': 'default',
    'comment_heading': 'コメント',
    'comment_form_heading': 'コメントをどうぞ',
    'comment_submit_label': 'コメントを送信',
    'comment_form_display_type': 'toggle_button', # トグルボタンで開閉
    'comment_website_visible': '',         # URL欄非表示（スパム防止）
    'comment_internal_blogcard_enable': '1',
    'comment_external_blogcard_enable': '1',
    'single_comment_visible': '1',
}

# --- 21. 通知エリア ---
NOTIFICATION = {
    'notice_area_visible': '1',
    'notice_type': 'notice',
    'notice_area_message': '🔔 防災グッズの準備は万全ですか？ まずは何から揃えるかチェック！',
    'notice_area_url': 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e3%82%b0%e3%83%83%e3%82%ba%e4%bd%95%e3%81%8b%e3%82%89%e6%8f%83%e3%81%88%e3%82%8b%ef%bc%9f%e5%84%aa%e5%85%88%e9%a0%86%e4%bd%8d%e3%81%a8%e4%ba%88%e7%ae%97%e5%88%a5%e3%83%97%e3%83%a9/',
    'notice_area_background_color': '#fef3c7',  # 暖かい黄色
    'notice_area_text_color': '#92400e',        # ブラウン
    'notice_link_target_blank': '',
}

# --- 22. アピールエリア ---
APPEAL = {
    'appeal_area_display_type': 'front_page_only',  # トップページのみ表示
    'appeal_area_title': '一人暮らしの防災、何から始める？',
    'appeal_area_message': '初めてでも迷わない。シーン別の防災準備ガイド',
    'appeal_area_button_message': '何から揃える？ 優先順位を見る →',
    'appeal_area_button_url': 'https://www.aoktik.online/%e9%98%b2%e7%81%bd%e3%82%b0%e3%83%83%e3%82%ba%e4%bd%95%e3%81%8b%e3%82%89%e6%8f%83%e3%81%88%e3%82%8b%ef%bc%9f%e5%84%aa%e5%85%88%e9%a0%86%e4%bd%8d%e3%81%a8%e4%ba%88%e7%ae%97%e5%88%a5%e3%83%97%e3%83%a9/',
    'appeal_area_button_target': '_self',
    'appeal_area_background_color': '#1e3a5f',
    'appeal_area_button_background_color': '#e94560',
    'appeal_area_height': '300',
    'appeal_area_content_visible': '1',
}

# --- 23. おすすめカード ---
RECOMMEND = {
    'recommended_cards_display_type': 'front_page_only',  # トップページのみ
    'recommended_cards_style': 'center_white_title',
    'recommended_cards_margin_enable': '1',
    'recommended_cards_both_sides_margin_enable': '1',
    'recommended_cards_menu_name': '',  # メニュー名は手動設定が必要
}

# --- 24. カルーセル ---
CAROUSEL = {
    'carousel_display_type': 'front_page_only',  # トップページのみ
    'carousel_max_count': '12',
    'carousel_orderby': 'rand',            # ランダム表示
    'carousel_autoplay_enable': '1',       # 自動再生
    'carousel_autoplay_interval': '5',     # 5秒間隔
    'carousel_card_border_visible': '1',
    'carousel_smartphone_visible': '1',
    'carousel_popular_posts_enable': '',
}

# --- 25. フッター ---
FOOTER = {
    'footer_display_type': 'left_and_right',
    'footer_background_color': '#1a365d',  # ネイビー
    'footer_text_color': '#ffffff',
    'footer_navi_menu_text_width_enable': '1',
    'credit_notation': 'user_credit',
    'copyright_name': '防災グッズ完全ガイド',
}

# --- 26. モバイル ---
MOBILE = {
    'mobile_site_font_size': '16px',
    'mobile_header_logo_visible': '1',
    'mobile_adsense_width_wide': '1',
    'mobile_button_layout_type': 'header_mobile_buttons',
    'fixed_mobile_buttons_enable': '',
}

# --- 27. 404ページ ---
PAGE_404 = {
    '404_page_title': 'ページが見つかりません',
    '404_page_message': 'お探しのページは見つかりませんでした。\nトップページから目的の記事をお探しください。',
}

# --- 28. 管理者画面 ---
ADMIN = {
    'admin_panel_display_type': 'pc_only',
    'admin_panel_edit_area_visible': '1',
    'admin_panel_pv_area_visible': '1',
    'admin_panel_check_tools_area_visible': '1',
    'admin_panel_responsive_tools_area_visible': '1',
    'admin_tool_menu_visible': '1',
    'admin_pagespeed_insights_visible': '1',
    'admin_nu_html_checker_visible': '1',
    'admin_gtmetrix_visible': '1',
    'admin_seocheki_visible': '1',
    'admin_list_eyecatch_visible': '1',
    'admin_list_categories_visible': '1',
    'admin_list_tags_visible': '1',
    'admin_list_date_visible': '1',
    'admin_editor_counter_visible': '1',
    'confirmation_before_publish': '1',
    'editor_tag_check_list_enable': '1',
}

# --- 29. エディター ---
EDITOR = {
    'gutenberg_editor_enable': '1',
    'visual_editor_style_enable': '1',
    'block_editor_style_block_option_visible': '1',
    'block_editor_marker_style_dropdown_visible': '1',
    'block_editor_font_size_style_dropdown_visible': '1',
    'block_editor_letter_style_dropdown_visible': '1',
    'block_editor_badge_style_dropdown_visible': '1',
    'block_editor_general_shortcode_dropdown_visible': '1',
    'block_editor_template_shortcode_dropdown_visible': '1',
    'block_editor_affiliate_shortcode_dropdown_visible': '1',
    'block_editor_ranking_shortcode_dropdown_visible': '1',
    'block_editor_ruby_button_visible': '1',
    'block_editor_clear_format_button_visible': '1',
}

# --- 30. API ---
API_SETTINGS = {
    'api_cache_retention_period': '30',    # APIキャッシュ30日
    'api_error_mail_enable': '1',
}

# --- 31. その他 ---
OTHER = {
    'jquery_version': '3',
    'jquery_migrate_version': '3',
    'meta_referrer_content': 'no-referrer-when-downgrade',
    'easy_ssl_enable': '',
    'featured_image_from_title_enable': '1',
    'featured_image_from_title': '0',
    'external_target_blank_link_noopener_enable': '1',
    'external_target_blank_link_noreferrer_enable': '',
}

# --- 32. 楽天/Amazon商品リンク設定 ---
PRODUCT_LINK = {
    'rakuten_search_button_text': '楽天市場',
    'rakuten_search_button_visible': '1',
    'rakuten_item_logo_visible': '1',
    'rakuten_item_description_visible': '',
    'rakuten_item_price_visible': '1',
    'amazon_search_button_text': 'Amazon',
    'amazon_search_button_visible': '1',
    'amazon_item_logo_visible': '1',
    'amazon_item_customer_reviews_visible': '1',
    'amazon_item_customer_reviews_text': 'Amazonの商品レビュー・口コミを見る',
    'yahoo_search_button_text': 'Yahoo!ショッピング',
    'yahoo_search_button_visible': '1',
    'mercari_search_button_text': 'メルカリ',
    'mercari_search_button_visible': '',
    'product_block_auto_update_enable': '1',
    'product_block_auto_update_interval': 'cocoon_every_3_days',
    'product_block_auto_update_batch_size': '30',
}

# --- 33. PWA ---
PWA = {
    'pwa_enable': '',  # PWA無効（まだ不要）
}

# ============================================================

ALL_SETTINGS = {}
categories = [
    ('スキン', SKIN),
    ('全体', GLOBAL),
    ('ヘッダー', HEADER),
    ('広告', AD),
    ('タイトル', TITLE),
    ('SEO', SEO),
    ('OGP', OGP),
    ('アクセス解析', ANALYTICS),
    ('カラム', COLUMN),
    ('インデックス', INDEX),
    ('投稿', POST),
    ('固定ページ', PAGE),
    ('本文', CONTENT),
    ('目次', TOC),
    ('SNSシェア', SNS_SHARE),
    ('SNSフォロー', SNS_FOLLOW),
    ('画像', IMAGE),
    ('ブログカード', BLOGCARD),
    ('コード', CODE),
    ('コメント', COMMENT),
    ('通知エリア', NOTIFICATION),
    ('アピールエリア', APPEAL),
    ('おすすめカード', RECOMMEND),
    ('カルーセル', CAROUSEL),
    ('フッター', FOOTER),
    ('モバイル', MOBILE),
    ('404ページ', PAGE_404),
    ('管理者画面', ADMIN),
    ('エディター', EDITOR),
    ('API', API_SETTINGS),
    ('その他', OTHER),
    ('商品リンク', PRODUCT_LINK),
    ('PWA', PWA),
]


def main():
    print("=" * 60)
    print("⚙️  Cocoon全設定を防災ブログ向けに最適化")
    print("=" * 60)

    # 現在の設定を取得して差分表示
    current = {}
    try:
        r = requests.get(f'{WP_URL}/wp-json/cocoon-cfg/v1/all', headers=wp_auth())
        if r.status_code == 200:
            current = r.json()
    except:
        pass

    # theme_modsから現在値を取得
    r2 = requests.get(
        f'{WP_URL}/wp-json/cocoon-cfg/v1/get/theme_mods_cocoon-child-master',
        headers=wp_auth()
    )
    if r2.status_code == 200:
        mods = r2.json().get('value', {})
        if isinstance(mods, dict):
            current.update(mods)

    total_changes = 0
    all_updates = {}

    for cat_name, settings in categories:
        changes = []
        for key, new_val in settings.items():
            old_val = str(current.get(key, ''))
            if old_val != str(new_val):
                changes.append((key, old_val, new_val))
                all_updates[key] = new_val
            else:
                all_updates[key] = new_val  # 同じ値でも送信

        if changes:
            print(f"\n📋 {cat_name} ({len(changes)}件変更)")
            for key, old, new in changes[:5]:
                old_short = str(old)[:40] or '(空)'
                new_short = str(new)[:40] or '(空)'
                print(f"   {key}: {old_short} → {new_short}")
            if len(changes) > 5:
                print(f"   ... 他{len(changes)-5}件")
            total_changes += len(changes)
        else:
            print(f"\n✅ {cat_name} (変更なし)")

    print(f"\n{'=' * 60}")
    print(f"📊 合計 {total_changes} 件の設定を変更")
    print("=" * 60)

    # theme_modsとして一括更新
    # Cocoonはtheme_modsに設定を保存するため、既存のtheme_modsを取得して更新
    r3 = requests.get(
        f'{WP_URL}/wp-json/cocoon-cfg/v1/get/theme_mods_cocoon-child-master',
        headers=wp_auth()
    )
    r3.raise_for_status()
    theme_mods = r3.json().get('value', {})
    if not isinstance(theme_mods, dict):
        theme_mods = {}

    # 設定を更新
    theme_mods.update(all_updates)

    # 保存
    result = set_options({'theme_mods_cocoon-child-master': theme_mods})
    print(f"\n🔧 theme_mods更新: {result}")

    print(f"\n{'=' * 60}")
    print("🎉 Cocoon全設定の最適化が完了しました！")
    print("=" * 60)
    print("\n📝 変更のサマリー:")
    print("  ・スキン: silk（クリーン＆モダン）")
    print("  ・カラー: ネイビー(#1a365d)ベース＋アクセント赤(#e94560)")
    print("  ・フォント: Noto Sans JP 16px")
    print("  ・SEO: メタ情報・構造化データ・OGP全有効")
    print("  ・SNS: Twitter/Facebook/はてブ/Pocket/LINE/コピー")
    print("  ・目次: 有効（h3まで・番号付き・開閉可能）")
    print("  ・通知バー: 防災グッズCTA表示")
    print("  ・アピールエリア: トップページに防災ガイドCTA")
    print("  ・カルーセル: トップページに記事カルーセル")
    print("  ・コメント: URL欄非表示（スパム対策）")
    print("  ・PR表記: ステマ規制対応済み")
    print("  ・404ページ: カスタムメッセージ設定")


if __name__ == '__main__':
    main()
