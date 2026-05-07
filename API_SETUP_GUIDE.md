# APIキー取得ガイド - 防災ブログ SNS自動投稿対応

## 📋 必要なAPIキー一覧

| プラットフォーム | 用途 | 優先度 | 所要時間 |
|---|---|---|---|
| **X (Twitter) API v2** | X自動投稿 | P0 必須 | 5-10分 |
| **Meta Business (Threads)** | Threads自動投稿 | P0 必須 | 10-15分 |
| **Google Search Console API** | キーワード自動抽出 | P1 重要 | 15-20分 |
| **Note API** | Note投稿（オプション） | P3 後回し | 10分 |

---

## 1️⃣ X (Twitter) API v2 - Bearer Token

### ステップ1: Developer Portalにアクセス
1. **https://developer.twitter.com/en/portal/dashboard** にアクセス
2. Xアカウント（@aoktik のアカウント）でログイン
3. 既存プロジェクトがあればそれを選択、なければ「Create project」

### ステップ2: API Keys を生成
1. 左メニュー → **Keys and tokens**
2. **API Key & Secret** セクション
   - 「Regenerate」をクリック（既存キーがあれば）
   - **API Key** をコピー → `X_API_KEY`
   - **API Secret Key** をコピー → `X_API_SECRET`

### ステップ3: Bearer Token を生成
1. 同じページの **Bearer Token** セクション
2. 「Regenerate」をクリック
3. **Bearer Token** をコピー → `X_BEARER_TOKEN`

### ステップ4: 権限設定を確認
1. 左メニュー → **Project settings**
2. **User authentication settings** → **Edit**
   - **OAuth 2.0** を有効化
   - **App type**: Web app, Automated app or bot
   - **Callback URIs**: `http://localhost:8000` (テスト用)
   - **Website URL**: `https://www.aoktik.online`

### ステップ5: API権限を確認
1. 左メニュー → **Permissions**
2. **Tweet creation** が `Read/Write` になっているか確認
   - なければ「Edit permissions」→ `Read/Write` に変更

### 保存先
```bash
export X_API_KEY="xxxxxxxxxxxxxxxx"
export X_API_SECRET="xxxxxxxxxxxxxxxx"
export X_BEARER_TOKEN="AAAAAxxxxxxxxxxxxxxxx"
```

---

## 2️⃣ Meta Business (Threads) API - Access Token

### ステップ1: Meta Business Accountを作成
1. **https://business.facebook.com/** にアクセス
2. Facebookアカウント（個人アカウント）でログイン
3. 「アカウントを作成」→「ビジネス」
   - 会社名: 「aoktik」または個人名
   - ビジネス目的: 「マーケティング」

### ステップ2: Threadsビジネスアカウントを接続
1. Meta Business Platform 左メニュー → **Accounts**
2. **Instagram Accounts** → **Add Account**
3. Threadsアカウント（Instagramと同じ）を接続
   - Threadsアカウントがなければ、Instagramアカウントから作成

### ステップ3: アクセストークンを生成
1. 左メニュー → **Settings** → **User**
2. **Generate token** をクリック
   - 権限: `instagram_basic`, `instagram_content_publish` を選択
   - トークンをコピー → `THREADS_ACCESS_TOKEN`

### ステップ4: ビジネスアカウントIDを取得
1. 左メニュー → **Accounts** → **Instagram Accounts**
2. 接続したThreadsアカウントをクリック
3. **Account ID** をコピー → `THREADS_BUSINESS_ACCOUNT_ID`

### 保存先
```bash
export THREADS_ACCESS_TOKEN="EAAxxxxxxxxxxxxxxxx"
export THREADS_BUSINESS_ACCOUNT_ID="17841xxxxxxxx"
```

---

## 3️⃣ Google Search Console API - Service Account JSON

### ステップ1: Google Cloud Projectを作成
1. **https://console.cloud.google.com/projectcreate** にアクセス
2. Googleアカウント（任意、GCP用）でログイン
3. **Project name**: `aoktik-blog-research`
4. 「Create」をクリック

### ステップ2: Search Console API を有効化
1. 上部検索バー → **Search Console API** を検索
2. 「有効にする」をクリック
   - 初回は有効化に1-2分待機

### ステップ3: Service Account を作成
1. 左メニュー → **IAM と管理** → **サービスアカウント**
2. 「サービスアカウントを作成」
   - **Service account name**: `aoktik-blog-seo`
   - **Service account ID**: 自動生成（変更不要）
3. 「作成して続行」

### ステップ4: サービスアカウントに権限を付与
1. **Grant this service account access to project**
   - Role: **Editor** を選択（または `webmasters.readonly`）
2. 「続行」

### ステップ5: JSON キーファイルを生成
1. 画面上の「キーを追加」 → 「新しいキーを作成」
2. **キーの種類**: JSON
3. 「作成」をクリック
4. JSON ファイルが自動ダウンロードされる
   - ファイル名例: `aoktik-blog-research-xxxxx.json`

### ステップ6: Google Search Console で権限付与
1. **https://search.google.com/search-console** にアクセス
2. 左メニュー → **設定** → **ユーザーと権限**
3. 「ユーザーを追加」
   - メールアドレス: JSON ファイルの `client_email` フィールドの値
   - 権限: **オーナー** または **フル**

### 保存先
```bash
# JSON ファイルはローカルに保存
cp ~/Downloads/aoktik-blog-research-xxxxx.json ~/bousai-blog/credentials/gcp-service-account.json

export GOOGLE_SERVICE_ACCOUNT_JSON="~/bousai-blog/credentials/gcp-service-account.json"
export GSC_PROPERTY_URL="https://www.aoktik.online"
```

---

## 4️⃣ Note API（オプション）- API Key

### ⚠️ 重要: Note の公式API は限定的

Note の公開APIは制限されているため、以下の選択肢があります：

#### **オプション A: Note RSS + 手作業投稿**（推奨）
- `publish_to_sns.py` が Note 投稿キューを JSON に記録
- ユーザーが週1-2回 Note にアクセスして投稿
- 📁 `/data/note_queue.json` にリストが自動保存

#### **オプション B: Note API（要申請）**
Note の API アクセスには **事前申請が必要** です：

1. **https://note.com/api** にアクセス
2. 「API アクセス申請」フォームを記入
   - 用途: 「防災情報ブログの自動投稿」
   - 予想月間API呼び出し: 「100〜1,000」

3. **承認待機**: 1-2週間

### 現在の推奨設定
```bash
# Note の手作業投稿リストを使用（オプション無視）
# publish_to_sns.py は /data/note_queue.json に記録するので
# ユーザーが週末に確認して手作業で投稿

export NOTE_API_KEY="not-configured"  # スキップ
```

---

## 🛠️ 環境変数をまとめて設定

### ステップ1: `~/.bashrc` または `~/.zshrc` に追加

```bash
# SNS API Keys
export X_API_KEY="xxxxxxxxxxxxxxxx"
export X_API_SECRET="xxxxxxxxxxxxxxxx"
export X_BEARER_TOKEN="AAAAAxxxxxxxxxxxxxxxx"

export THREADS_ACCESS_TOKEN="EAAxxxxxxxxxxxxxxxx"
export THREADS_BUSINESS_ACCOUNT_ID="17841xxxxxxxx"

# Google APIs
export GOOGLE_SERVICE_ACCOUNT_JSON="$HOME/bousai-blog/credentials/gcp-service-account.json"
export GSC_PROPERTY_URL="https://www.aoktik.online"

# WordPress（既存）
export WP_URL="https://www.aoktik.online"
export WP_USER="aoktik"
export WP_PASSWORD="AYZS 5F5X D6kL sH2N J7pg eeBn"

# Gemini API（既存）
export GEMINI_API_KEY="your-existing-key"
```

### ステップ2: 環境変数を読み込み

```bash
# ~/.zshrc の場合
source ~/.zshrc

# ~/.bashrc の場合
source ~/.bashrc
```

### ステップ3: 設定を確認

```bash
echo $X_BEARER_TOKEN
echo $THREADS_ACCESS_TOKEN
echo $GOOGLE_SERVICE_ACCOUNT_JSON
# 各キーが表示されればOK
```

---

## ✅ チェックリスト

### 取得したキー
- [ ] `X_API_KEY`
- [ ] `X_API_SECRET`
- [ ] `X_BEARER_TOKEN`
- [ ] `THREADS_ACCESS_TOKEN`
- [ ] `THREADS_BUSINESS_ACCOUNT_ID`
- [ ] `GOOGLE_SERVICE_ACCOUNT_JSON` (ファイルパス)
- [ ] `GSC_PROPERTY_URL` (設定: `https://www.aoktik.online`)

### 権限設定確認
- [ ] X API: Tweet creation = Read/Write
- [ ] Threads: instagram_content_publish 権限有
- [ ] Google Search Console: サービスアカウントをオーナー追加済み

### 環境変数設定確認
- [ ] `~/.zshrc` or `~/.bashrc` に記載
- [ ] `source` で読み込み完了
- [ ] `echo $変数名` で確認可能

---

## 🚨 トラブルシューティング

### X API 投稿失敗
**エラー**: `403 Forbidden`
- ✅ Bearer Token が正しいか確認
- ✅ Tweet creation権限が `Read/Write` か確認
- ✅ API キー再生成を試す（古いキーは機能しないことがある）

### Threads 投稿失敗
**エラー**: `401 Unauthorized`
- ✅ Access Token がまだ有効か確認（30日有効期限）
- ✅ Business Account ID が正しいか確認
- ✅ Threadsアカウントが Business Account に接続されているか確認

### Google Search Console API エラー
**エラー**: `403 Permission Denied`
- ✅ Service Account メールを Search Console の「ユーザーと権限」に追加したか確認
- ✅ 権限が「オーナー」または「フル」か確認
- ✅ JSON ファイルが正しいパスにあるか確認

---

## 次のステップ

APIキーを取得・設定したら、実行：

```bash
# OGP画像テスト
python3 generate_ogp_image.py "テスト記事"

# キーワード研究テスト
python3 keyword_research.py 1000 90

# 実際の記事投稿テスト（下書き状態）
python3 daily_enhanced.py --keyword "防災グッズ" --no-research
```

**質問がある場合は気軽に聞いてください！**
