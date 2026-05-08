# bousai-blog

防災アフィリエイトブログ（aoktik.online）の記事・固定ページを管理するスクリプト群。

## ディレクトリ構成

```
bousai-blog/
├── .env                    # 環境変数（gitignore対象）
├── .env.example            # サンプル
├── helpers/                # 共通ユーティリティ
│   ├── env.py              # .env loader（自動実行）
│   ├── wordpress.py        # WordPress REST API + WAF対策
│   ├── images.py           # アイキャッチ生成（JPEG固定）
│   ├── internal_links.py   # 記事マスタ + シーンマッピング
│   ├── a8.py               # A8 / 楽天 / Amazon ボタン
│   ├── rakuten.py          # 楽天検索リンク（旧API）
│   └── claude_api.py       # Gemini 記事生成
├── scripts/                # 定常運用スクリプト
│   ├── new_article.py      # 構造化データ→記事化
│   ├── update_scene_pages.py # シーンページ自動更新
│   └── upload_eyecatch.py  # アイキャッチ生成→アップロード
├── archive/                # 使い捨てスクリプト退避先
├── data/
│   ├── eyecatch/           # 生成画像
│   └── state.json          # トピックローテーション状態
├── .github/workflows/      # GitHub Actions
└── daily.py / daily_enhanced.py / keyword_research.py / publish_to_sns.py
```

## セットアップ

```bash
# 環境変数を設定
cp .env.example .env
$EDITOR .env  # WP_USER, WP_PASSWORD などを記入

# Python 依存
pip install requests pillow
```

## 運用フロー

### 既存記事のシーンページに追加

```bash
# 記事504を該当シーンページに追加（dry-run）
python3 scripts/update_scene_pages.py 504 --dry-run

# 実反映
python3 scripts/update_scene_pages.py 504
```

### 新記事を追加した場合の手順

1. 記事をWordPressで公開（または `daily_enhanced.py` で生成）
2. `helpers/internal_links.py` の `ARTICLES` に1行追加：
   ```python
   605: {
       'title': '...',
       'short': '...',
       'scenes': ['jitaku', 'stock'],   # 配置先シーン
       'desc': '...',
   },
   ```
3. シーンページに自動追加：
   ```bash
   python3 scripts/update_scene_pages.py 605
   ```
4. アイキャッチ画像を生成・設定：
   ```bash
   python3 scripts/upload_eyecatch.py 605 "記事タイトル" --emoji 📦
   ```

### アイキャッチ画像のみ単発作成

```bash
python3 scripts/upload_eyecatch.py 411 "非常食おすすめ10選" --subtitle "一人暮らし向け" --emoji 🍙
```

## シーン別固定ページ

| キー | ページID | URL |
|---|---|---|
| jitaku | 508 | 自宅で備える |
| hinan | 509 | 避難する |
| family | 510 | 家族で備える |
| mansion | 511 | 住まい別に備える |
| manabu | 512 | 知識で備える |
| stock | 513 | 備蓄する |
| - | 520 | シーン別ガイド（ハブ） |

## 日次自動化（macOS launchd）

SiteGuard WAF が GitHub Actions IP を継続的にブロックするため、日次実行は **macOS launchd** を使用します。

### セットアップ

```bash
bash scripts/install_launchd.sh
```

これで毎朝 **7:00** に `daily_enhanced.py` が実行され、`data/topic_templates.py` の ROTATION 順に下書き記事が WordPress に投稿されます（地震→台風→水害→停電→断水→火災のサイクル）。

### 確認

```bash
# 状態確認
launchctl list | grep bousai

# 手動実行（テスト用）
launchctl start com.aoktik.bousai-daily

# ログ確認
tail -f data/launchd-stdout.log
```

### 停止

```bash
bash scripts/uninstall_launchd.sh
```

### 新トピック追加

`data/topic_templates.py` の `TEMPLATES` dict に1エントリを追加し、`ROTATION` 配列にキーを加えるだけ。

### GitHub Actions（補助用・手動実行のみ）

`.github/workflows/daily.yml` は手動実行（workflow_dispatch）のみ対応。SiteGuard で GitHub IP を許可すれば自動実行も可能。

必要な Secrets（既登録）:
- `WP_URL`, `WP_USER`, `WP_PASSWORD`
- `RAKUTEN_AFFILIATE_ID`
- `A8_PRIME_VIDEO_LINK`, `A8_PRIME_VIDEO_IMG`

## helpers の主な関数

### `helpers.wordpress`

```python
from helpers import wordpress

wordpress.get_post(post_id, raw=True)    # 取得（posts→pages順）
wordpress.update_post(post_id, **fields) # 更新
wordpress.upload_image(path)             # JPEG変換+WAFリトライ
wordpress.set_featured_image(post_id, media_id)
```

### `helpers.images`

```python
from helpers.images import generate_eyecatch

path = generate_eyecatch(title, subtitle, badge, emoji)
# → data/eyecatch/<slug>-<random>.jpg
```

### `helpers.internal_links`

```python
from helpers.internal_links import link, card, articles_in_scene

link(411)                  # <a>タグ
card(411, desc='...')      # シーンページ用カード
articles_in_scene('jitaku')  # [380, 409, 411, 413, 486]
```

### `helpers.a8`

```python
from helpers.a8 import a8_button, rakuten_button, amazon_button

a8_button('prime_video')          # A8 計測タグ付き
rakuten_button('防災セット')
amazon_button('防災グッズ')
```

## トラブルシューティング

### WordPress アップロードが 403 エラー

- `helpers/wordpress.upload_image()` を使用（自動 JPEG 変換 + リトライ）
- 画像サイズが 60KB 超なら自動で品質を下げる
- 直接アップロードはしない

### 環境変数が読まれない

- `helpers.env.load_env()` は `helpers/*` の import 時に自動実行される
- スクリプトの先頭で `from helpers.env import load_env; load_env()` を呼ぶ
