"""記事生成モジュール（Google Gemini API / REST）"""
import os
import re
import requests
from helpers.rakuten import affiliate_search_url

GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'


def _call_gemini(prompt: str) -> str:
    """Gemini REST APIを呼び出してテキストを返す"""
    api_key = os.environ['GEMINI_API_KEY']
    resp = requests.post(
        GEMINI_URL,
        params={'key': api_key},
        json={
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {'maxOutputTokens': 4096, 'temperature': 0.7},
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()['candidates'][0]['content']['parts'][0]['text']

# 30日分のトピックローテーション
TOPICS = [
    {'keyword': '防災リュック',       'category': '防災グッズレビュー',  'tags': ['防災リュック', '一人暮らし', '避難袋'],            'search_kws': ['防災リュック', '防災リュック レディース', '防災セット リュック']},
    {'keyword': '非常食',            'category': '防災グッズレビュー',  'tags': ['非常食', '備蓄', '長期保存食'],                   'search_kws': ['非常食 セット', '非常食 長期保存', 'アルファ米']},
    {'keyword': '保存水',            'category': '防災グッズレビュー',  'tags': ['保存水', '備蓄水', '防災'],                      'search_kws': ['保存水 2L', '保存水 長期保存', '防災 ミネラルウォーター']},
    {'keyword': '防災ラジオ',         'category': '防災グッズレビュー',  'tags': ['防災ラジオ', '手回しラジオ', '停電対策'],           'search_kws': ['防災ラジオ 手回し', '防災ラジオ 充電', '多機能ラジオ 防災']},
    {'keyword': 'ポータブル電源',      'category': '防災グッズレビュー',  'tags': ['ポータブル電源', '停電対策', '防災グッズ'],          'search_kws': ['ポータブル電源 防災', 'ポータブル電源 大容量', 'ポータブル電源 ソーラー']},
    {'keyword': '懐中電灯',          'category': '防災グッズレビュー',  'tags': ['懐中電灯', 'LED', '防災'],                      'search_kws': ['懐中電灯 LED 防災', '懐中電灯 強力 防災', 'ヘッドライト 防災']},
    {'keyword': '防災セット',         'category': '防災グッズレビュー',  'tags': ['防災セット', '防災グッズ', '備え'],                'search_kws': ['防災セット 一人暮らし', '防災セット 家族', '防災グッズ セット']},
    {'keyword': '非常用トイレ',        'category': '防災グッズレビュー',  'tags': ['非常用トイレ', '携帯トイレ', '断水対策'],           'search_kws': ['携帯トイレ 防災', '非常用トイレ 50回分', '簡易トイレ 防災']},
    {'keyword': '救急セット',         'category': '防災グッズレビュー',  'tags': ['救急セット', '応急処置', '防災'],                  'search_kws': ['救急セット 防災', '救急箱 家庭用', '応急処置 セット']},
    {'keyword': '寝袋 防災',         'category': '防災グッズレビュー',  'tags': ['寝袋', 'シュラフ', '避難生活'],                   'search_kws': ['寝袋 コンパクト 防災', 'シュラフ 防災', '寝袋 軽量']},
    {'keyword': '耐震マット',         'category': '地震対策',          'tags': ['耐震マット', '地震対策', '家具転倒防止'],            'search_kws': ['耐震マット 家具', '耐震ジェル', '家具転倒防止 グッズ']},
    {'keyword': 'カセットコンロ 防災', 'category': '防災グッズレビュー',  'tags': ['カセットコンロ', '停電対策', '調理'],               'search_kws': ['カセットコンロ 防災', 'カセットガス まとめ買い', 'カセットコンロ アウトドア']},
    {'keyword': 'アルファ米',         'category': '防災グッズレビュー',  'tags': ['アルファ米', '非常食', '備蓄'],                   'search_kws': ['アルファ米 防災', 'アルファ米 おいしい', 'アルファ化米 非常食']},
    {'keyword': '保温毛布',          'category': '防災グッズレビュー',  'tags': ['保温毛布', 'エマージェンシーブランケット', '防災'],   'search_kws': ['保温毛布 防災', 'アルミブランケット 防災', 'エマージェンシーブランケット']},
    {'keyword': '携帯浄水器',         'category': '防災グッズレビュー',  'tags': ['浄水器', '断水対策', '防災'],                     'search_kws': ['携帯浄水器 防災', '浄水ストロー 防災', '浄水フィルター アウトドア']},
    {'keyword': '給水袋',            'category': '防災グッズレビュー',  'tags': ['給水袋', '断水対策', '備蓄'],                     'search_kws': ['給水袋 防災', '折りたたみ 給水袋', 'ウォータータンク 防災']},
    {'keyword': '防水バッグ 防災',     'category': '台風・水害対策',     'tags': ['防水バッグ', '水害対策', '防災'],                   'search_kws': ['防水バッグ 防災', '防水リュック 防災', '防水ケース 防災']},
    {'keyword': '防災ヘルメット',      'category': '地震対策',          'tags': ['防災ヘルメット', '地震対策', '防災グッズ'],           'search_kws': ['防災ヘルメット 折りたたみ', '防災ヘルメット 軽量', '防災用ヘルメット']},
    {'keyword': '避難袋 中身',        'category': '防災の基礎知識',     'tags': ['避難袋', '非常用持ち出し袋', '中身'],                'search_kws': ['防災リュック 中身', '非常用持ち出し袋 セット', '避難袋 必需品']},
    {'keyword': '地震対策 一人暮らし', 'category': '地震対策',          'tags': ['地震対策', '一人暮らし', '防災'],                   'search_kws': ['地震対策グッズ 一人暮らし', '耐震グッズ 一人暮らし', '防災グッズ 一人暮らし 女性']},
    {'keyword': '台風対策 自宅',      'category': '台風・水害対策',     'tags': ['台風対策', '自宅', '防災'],                        'search_kws': ['台風対策グッズ', '窓ガラス 台風対策', '台風 養生テープ']},
    {'keyword': '停電対策',          'category': '防災の基礎知識',     'tags': ['停電対策', '備え', '防災'],                        'search_kws': ['停電対策グッズ', 'ポータブル電源 停電', '停電 懐中電灯']},
    {'keyword': '断水対策',          'category': '防災の基礎知識',     'tags': ['断水対策', '備え', '防災'],                        'search_kws': ['断水対策グッズ', '給水袋 断水', '保存水 断水']},
    {'keyword': '女性 防災グッズ',     'category': '防災グッズレビュー',  'tags': ['女性', '防災グッズ', '衛生用品'],                   'search_kws': ['女性 防災グッズ', '防災 生理用品', '防災 衛生用品 女性']},
    {'keyword': 'ペット 防災',        'category': '防災グッズレビュー',  'tags': ['ペット', '防災', '犬猫'],                         'search_kws': ['ペット 防災グッズ', '犬 防災 キャリー', '猫 防災 避難']},
    {'keyword': '子ども 防災グッズ',   'category': '防災グッズレビュー',  'tags': ['子ども', '防災', 'キッズ'],                       'search_kws': ['子ども 防災グッズ', 'キッズ 防災リュック', '赤ちゃん 防災']},
    {'keyword': 'マンション 防災',     'category': '防災の基礎知識',     'tags': ['マンション', '防災', '集合住宅'],                   'search_kws': ['マンション 防災グッズ', '高層マンション 防災', 'マンション 地震対策']},
    {'keyword': 'ローリングストック',  'category': '防災の基礎知識',     'tags': ['ローリングストック', '備蓄', '食品'],                'search_kws': ['ローリングストック 食品', '備蓄食品 セット', '長期保存食 ローリングストック']},
    {'keyword': '冬 防災グッズ',      'category': '防災グッズレビュー',  'tags': ['冬', '防災', '寒さ対策'],                         'search_kws': ['冬 防災グッズ', 'カイロ まとめ買い 防災', '防寒 防災']},
    {'keyword': '水害対策',          'category': '台風・水害対策',     'tags': ['水害対策', '洪水', '防災'],                        'search_kws': ['水害対策グッズ', '土のう 水害対策', '防水シート 浸水対策']},
]


def _parse(text: str) -> dict:
    """応答からタイトルと本文を分離"""
    text = text.strip()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.IGNORECASE | re.DOTALL)
    if m:
        title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        body  = text[m.end():].strip()
    else:
        lines = text.split('\n')
        title = re.sub(r'^#+\s*', '', lines[0]).strip()
        body  = '\n'.join(lines[1:]).strip()
    return {'title': title, 'content': body}


def generate_daily(topic: dict, _products=None) -> dict:
    """日次のアフィリエイト記事を生成（Geminiの知識で商品推薦）"""

    # 楽天検索アフィリエイトリンクを生成
    links = {kw: affiliate_search_url(kw) for kw in topic['search_kws']}
    links_text = '\n'.join([f'・{kw}: {url}' for kw, url in links.items()])

    prompt = f"""あなたは防災専門のアフィリエイトブログ「防災グッズ完全ガイド」（https://www.aoktik.online）のライターです。
一人暮らしの方向けに、初心者でもわかりやすい防災情報を提供しています。

【今回の記事テーマ】
「{topic['keyword']}」について

【文体・スタイル】
- 「〜しましょう」「〜がおすすめです」「〜してみてください」という指示・勧奨調
- 読者に「あなた」と呼びかける
- 専門用語は使わず、必要な場合は（）内で補足説明
- 読者の不安に共感しながら具体的な解決策を示す、温かみのある文体

【必須の記事構成（この順番で）】
1. <h1>タイトル</h1>
   ・SEOを意識して「{topic['keyword']} おすすめ」などのキーワードを含める
   ・35文字以内、具体的で検索されやすいタイトル

2. <p>リード文</p>（読者の悩みへの共感 + この記事で解決できること、200文字程度）

3. <h2>{topic['keyword']}が必要な理由</h2>
   ・具体的な被害事例・数字・統計を含める

4. <h2>{topic['keyword']}の選び方・チェックポイント</h2>
   ・3〜5つのポイントを<ul><li>形式で

5. <h2>おすすめ{topic['keyword']}ランキング</h2>
   ・比較表（必須）
   ・各商品を【商品カード】形式で3〜5個紹介
   ・商品は実在する人気商品をあなたの知識で推薦（具体的なブランド・商品名を記載）

6. <h2>効果的な活用方法・保管のコツ</h2>

7. <h2>よくある質問</h2>（Q&A形式で3問）

8. <h2>まとめ</h2>（チェックリスト形式）

【楽天市場の購入リンク（必ず使用すること）】
以下のアフィリエイトリンクを商品紹介の「楽天市場で見る」ボタンに使用してください：
{links_text}

【比較表フォーマット】
<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%;margin:20px 0">
<tr style="background:#f0f0f0"><th>商品名</th><th>価格帯</th><th>特徴</th><th>こんな人におすすめ</th></tr>
（各商品の行）
</table>

【商品カードフォーマット（各商品に使用）】
<div style="border:2px solid #e0e0e0;border-radius:10px;padding:20px;margin:20px 0;background:#fafafa">
<h3>【第〇位】商品名</h3>
<p>価格帯：<strong style="color:#c00">¥〇〇〇〇前後</strong></p>
<p>✅ おすすめポイント：〜</p>
<p>⚠️ 注意点：〜</p>
<p>こんな方に：〜</p>
<a href="[上記リンクから適切なものを選んで使用]" target="_blank" rel="noopener sponsored"
   style="display:inline-block;background:#bf0000;color:#fff;padding:12px 24px;text-decoration:none;border-radius:5px;font-weight:bold;margin-top:10px">
楽天市場で見る →</a>
</div>

【出力ルール】
- HTMLのみ（マークダウン・コードブロック禁止）
- 文字数：2000〜3000文字
- SEOキーワード「{topic['keyword']}」をh1・リード文・最初のh2に必ず含める
- 最初の要素は必ず<h1>から始める
- 商品カードのリンクには必ず上記の楽天アフィリエイトリンクを使用する
"""

    return _parse(_call_gemini(prompt))


def generate_disaster(info: dict, _products=None) -> dict:
    """災害発生時の緊急記事を生成"""

    if info['type'] == 'earthquake':
        situation = f"""
【発生した地震情報】
・発生場所：{info.get('location', '各地')}
・マグニチュード：{info.get('magnitude', '-')}
・最大震度：震度{info.get('max_intensity', '-')}
・発生時刻：{info.get('time', '-')}
・影響地域：{', '.join(info.get('affected_areas', ['各地']))}
"""
        keyword = f"{info.get('location', '')}地震"
        search_kws = ['防災リュック 緊急', '非常食 セット', '保存水 2L', '懐中電灯 防災', 'モバイルバッテリー 大容量']
    else:
        situation = f"""
【台風情報】
・台風名：{info.get('name_ja', '台風')}
・状況：{info.get('status', '日本に接近中')}
・影響が予想される地域：{', '.join(info.get('areas', ['広範囲']))}
"""
        keyword = info.get('name_ja', '台風')
        search_kws = ['台風対策グッズ', '防水バッグ 防災', '保存水 2L', '非常食 セット', '防災ラジオ 手回し']

    links = {kw: affiliate_search_url(kw) for kw in search_kws}
    links_text = '\n'.join([f'・{kw}: {url}' for kw, url in links.items()])

    prompt = f"""あなたは防災専門のアフィリエイトブログ「防災グッズ完全ガイド」のライターです。
今まさに発生・接近している災害に関する緊急記事を書いてください。

{situation}

【記事の目的】
被災地域・近隣の方が今すぐ取るべき行動と、楽天市場で今すぐ買える防災グッズを紹介する。

【記事構成】
1. <h1>緊急タイトル</h1>（例：「{keyword}発生｜今すぐ確認すべき安全対策と準備するもの」、35文字以内）
2. <p>リード文</p>（状況・緊急性・この記事の目的、150文字程度）
3. <h2>現在の状況と今後の見通し</h2>
4. <h2>今すぐすべき行動リスト</h2>（<ol>形式で優先順位付き5〜7項目）
5. <h2>緊急で揃えるべき防災グッズ</h2>（商品カード形式で3〜5個、緊急性を強調）
6. <h2>避難・安全確保のポイント</h2>
7. <h2>まとめ・安全のために</h2>（チェックリスト）

【楽天市場の購入リンク（必ず使用）】
{links_text}

【商品カードフォーマット（緊急版）】
<div style="border:2px solid #ffcccc;border-radius:10px;padding:20px;margin:20px 0;background:#fff5f5">
<h3>🚨 商品名</h3>
<p>価格帯：<strong style="color:#c00">¥〇〇〇〇前後</strong></p>
<p>今すぐ必要な理由：〜</p>
<a href="[上記リンクから適切なものを使用]" target="_blank" rel="noopener sponsored"
   style="display:inline-block;background:#c00;color:#fff;padding:12px 24px;text-decoration:none;border-radius:5px;font-weight:bold;margin-top:10px">
今すぐ楽天市場で購入 →</a>
</div>

【出力ルール】
- HTMLのみ（マークダウン・コードブロック禁止）
- 文字数：1500〜2500文字
- 緊急性が伝わるトーン（過度な不安を煽らない）
- 最初の要素は必ず<h1>から始める
"""

    return _parse(_call_gemini(prompt))
