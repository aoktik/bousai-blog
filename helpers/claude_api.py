"""Claude API 記事生成モジュール"""
import os
import re
import anthropic

MODEL = 'claude-opus-4-6'

# 30日分のトピックローテーション
TOPICS = [
    {'keyword': '防災リュック',          'search': '防災リュック 一人暮らし',           'category': '防災グッズレビュー',   'tags': ['防災リュック', '一人暮らし', '避難袋']},
    {'keyword': '非常食',               'search': '非常食 長期保存 セット',             'category': '防災グッズレビュー',   'tags': ['非常食', '備蓄', '長期保存食']},
    {'keyword': '保存水',               'search': '保存水 長期保存 ミネラルウォーター',    'category': '防災グッズレビュー',   'tags': ['保存水', '備蓄水', '防災']},
    {'keyword': '防災ラジオ',            'search': '防災ラジオ 手回し 充電',             'category': '防災グッズレビュー',   'tags': ['防災ラジオ', '手回しラジオ', '停電対策']},
    {'keyword': 'ポータブル電源',         'search': 'ポータブル電源 防災 停電',           'category': '防災グッズレビュー',   'tags': ['ポータブル電源', '停電対策', '防災グッズ']},
    {'keyword': '懐中電灯',             'search': '懐中電灯 LED 防災 強力',             'category': '防災グッズレビュー',   'tags': ['懐中電灯', 'LED', '防災']},
    {'keyword': '防災セット',            'search': '防災セット おすすめ 家族',            'category': '防災グッズレビュー',   'tags': ['防災セット', '防災グッズ', '備え']},
    {'keyword': '非常用トイレ',          'search': '非常用トイレ 携帯 防災',             'category': '防災グッズレビュー',   'tags': ['非常用トイレ', '携帯トイレ', '断水対策']},
    {'keyword': '救急セット',            'search': '救急セット 防災 応急処置',            'category': '防災グッズレビュー',   'tags': ['救急セット', '応急処置', '防災']},
    {'keyword': '寝袋 防災',            'search': '寝袋 コンパクト 防災 避難',           'category': '防災グッズレビュー',   'tags': ['寝袋', 'シュラフ', '避難生活']},
    {'keyword': '耐震マット',            'search': '耐震マット 家具転倒防止',             'category': '地震対策',            'tags': ['耐震マット', '地震対策', '家具転倒防止']},
    {'keyword': 'カセットコンロ 防災',    'search': 'カセットコンロ 防災 停電',            'category': '防災グッズレビュー',   'tags': ['カセットコンロ', '停電対策', '調理']},
    {'keyword': 'アルファ米',            'search': 'アルファ米 非常食 おいしい',          'category': '防災グッズレビュー',   'tags': ['アルファ米', '非常食', '備蓄']},
    {'keyword': '保温毛布',             'search': '保温毛布 アルミ 防災 緊急',           'category': '防災グッズレビュー',   'tags': ['保温毛布', 'エマージェンシーブランケット', '防災']},
    {'keyword': '携帯浄水器',            'search': '携帯浄水器 防災 アウトドア',          'category': '防災グッズレビュー',   'tags': ['浄水器', '断水対策', '防災']},
    {'keyword': '給水袋',               'search': '給水袋 折りたたみ 防災 断水',         'category': '防災グッズレビュー',   'tags': ['給水袋', '断水対策', '備蓄']},
    {'keyword': '防水バッグ 防災',        'search': '防水バッグ 防災 水害 浸水',           'category': '台風・水害対策',       'tags': ['防水バッグ', '水害対策', '防災']},
    {'keyword': '防災ヘルメット',         'search': '防災ヘルメット 折りたたみ 地震',      'category': '地震対策',            'tags': ['防災ヘルメット', '地震対策', '防災グッズ']},
    {'keyword': '避難袋 作り方',         'search': '防災リュック 中身 セット',            'category': '防災の基礎知識',       'tags': ['避難袋', '非常用持ち出し袋', '中身']},
    {'keyword': '地震対策 一人暮らし',    'search': '地震対策グッズ 一人暮らし',           'category': '地震対策',            'tags': ['地震対策', '一人暮らし', '防災']},
    {'keyword': '台風対策 自宅',         'search': '台風対策グッズ 窓 浸水',             'category': '台風・水害対策',       'tags': ['台風対策', '自宅', '防災']},
    {'keyword': '停電対策',             'search': 'ポータブル電源 停電 備え',            'category': '防災の基礎知識',       'tags': ['停電対策', '備え', '防災']},
    {'keyword': '断水対策',             'search': '給水袋 保存水 断水',                 'category': '防災の基礎知識',       'tags': ['断水対策', '備え', '防災']},
    {'keyword': '女性 防災グッズ',        'search': '女性 防災グッズ 生理用品 衛生',       'category': '防災グッズレビュー',   'tags': ['女性', '防災グッズ', '衛生用品']},
    {'keyword': 'ペット 防災',           'search': 'ペット 防災グッズ 犬 猫',            'category': '防災グッズレビュー',   'tags': ['ペット', '防災', '犬猫']},
    {'keyword': '子ども 防災グッズ',      'search': '子ども 防災グッズ キッズ 赤ちゃん',    'category': '防災グッズレビュー',   'tags': ['子ども', '防災', 'キッズ']},
    {'keyword': 'マンション 防災',        'search': 'マンション 防災 高層 エレベーター',    'category': '防災の基礎知識',       'tags': ['マンション', '防災', '集合住宅']},
    {'keyword': 'ローリングストック',      'search': 'ローリングストック 食品 備蓄',        'category': '防災の基礎知識',       'tags': ['ローリングストック', '備蓄', '食品']},
    {'keyword': '冬 防災グッズ',         'search': '冬 防災グッズ 寒さ対策 カイロ',       'category': '防災グッズレビュー',   'tags': ['冬', '防災', '寒さ対策']},
    {'keyword': '水害対策',             'search': '水害対策 土のう 防水シート',           'category': '台風・水害対策',       'tags': ['水害対策', '洪水', '防災']},
]


def _format_products(products: list) -> str:
    if not products:
        return '（商品情報なし）'
    lines = ''
    for i, p in enumerate(products[:5], 1):
        lines += f"""
【商品{i}】
・商品名: {p['name']}
・価格: ¥{p['price']:,}
・評価: {p['rating']}点（{p['reviews']}件のレビュー）
・アフィリエイトURL: {p['url']}
・画像URL: {p['image']}
・販売店: {p['shop']}
・説明: {p['desc'][:150]}
"""
    return lines


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


def generate_daily(topic: dict, products: list) -> dict:
    """日次のアフィリエイト記事を生成"""
    client = anthropic.Anthropic(api_key=os.environ['CLAUDE_API_KEY'])

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
   ・例：「【2024年最新】{topic['keyword']}おすすめ5選｜選び方のポイントも解説」

2. <p>リード文</p>
   ・読者の悩みへの共感から始める
   ・この記事を読めば解決できることを明示
   ・200文字程度

3. <h2>{topic['keyword']}が必要な理由</h2>
   ・具体的な被害事例・数字・統計を含める
   ・「実は〜」「意外と知られていないのが〜」という切り口で興味を引く

4. <h2>{topic['keyword']}の選び方・チェックポイント</h2>
   ・3〜5つのポイントを<ul><li>形式で解説
   ・各ポイントに具体的な数値や基準を示す

5. <h2>おすすめ{topic['keyword']}ランキング</h2>
   ・まず比較表（必須）
   ・次に各商品を商品カード形式で詳しく紹介

6. <h2>効果的な活用方法・保管のコツ</h2>
   ・実践的なアドバイスを箇条書きで

7. <h2>よくある質問</h2>
   ・Q&A形式で3問、読者が実際に迷いそうな質問を選ぶ

8. <h2>まとめ</h2>
   ・チェックリスト形式（<ul><li>にチェック項目）
   ・最後に購入を促す一文

【比較表（必ず含める）】
<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%;margin:20px 0">
<tr style="background:#f0f0f0"><th>商品名</th><th>価格</th><th>評価</th><th>おすすめポイント</th><th>購入リンク</th></tr>
（各商品の行を追加）
</table>

【商品カード（各商品に必ず使用）】
<div style="border:2px solid #e0e0e0;border-radius:10px;padding:20px;margin:20px 0;overflow:hidden;background:#fafafa">
<img src="[画像URL]" alt="[商品名]" style="max-width:180px;float:left;margin:0 20px 10px 0;border-radius:6px">
<h3>[商品名]</h3>
<p>価格：<strong style="font-size:1.2em;color:#c00">¥[価格]</strong></p>
<p>評価：[評価]点（[レビュー数]件のレビュー）</p>
<p>[この商品ならではの特徴・読者へのコメント（2〜3文）]</p>
<a href="[アフィリエイトURL]" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#bf0000;color:#fff;padding:12px 24px;text-decoration:none;border-radius:5px;font-weight:bold;margin-top:10px">楽天市場で見る →</a>
<div style="clear:both"></div>
</div>

【紹介する商品（全て記事に組み込んでください）】
{_format_products(products)}

【出力ルール】
- HTMLのみで出力（マークダウン・コードブロック・```は一切禁止）
- 全体の文字数：2000〜3000文字
- SEOキーワード「{topic['keyword']}」をh1・リード文・最初のh2に必ず含める
- 最初の要素は必ず<h1>タイトル</h1>から始める
"""

    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{'role': 'user', 'content': prompt}],
    )
    return _parse(msg.content[0].text)


def generate_disaster(info: dict, products: list) -> dict:
    """災害発生時の緊急記事を生成"""
    client = anthropic.Anthropic(api_key=os.environ['CLAUDE_API_KEY'])

    if info['type'] == 'earthquake':
        situation = f"""
【発生した地震情報】
・発生場所：{info.get('location', '各地')}
・マグニチュード：{info.get('magnitude', '-')}
・最大震度：震度{info.get('max_intensity', '-')}
・発生時刻：{info.get('time', '-')}
・影響地域：{', '.join(info.get('affected_areas', ['各地']))}
"""
        keyword   = f"{info.get('location', '')}地震"
        category_hint = '地震'
    else:
        situation = f"""
【台風情報】
・台風名：{info.get('name_ja', '台風')}
・状況：{info.get('status', '日本に接近中')}
・影響が予想される地域：{', '.join(info.get('areas', ['広範囲']))}
"""
        keyword   = info.get('name_ja', '台風')
        category_hint = '台風'

    prompt = f"""あなたは防災専門のアフィリエイトブログ「防災グッズ完全ガイド」のライターです。
今まさに発生・接近している災害に関する緊急記事を書いてください。

{situation}

【記事の目的】
・被災地域・近隣の方が今すぐ取るべき行動を具体的に伝える
・必要な防災グッズを楽天市場で購入してもらう（緊急性を強調）
・読者の安全を第一に考えた、信頼できる情報を提供する

【記事構成】
1. <h1>緊急タイトル</h1>
   例：「{keyword}発生｜今すぐ確認すべき安全対策と準備するもの」（35文字以内）

2. <p>リード文</p>（状況説明・緊急性・この記事の目的、150文字程度）

3. <h2>現在の状況と今後の見通し</h2>
   ・{category_hint}の特性と注意点
   ・余震・二次災害への備え（地震の場合）/ 今後の予想進路・強さ（台風の場合）

4. <h2>今すぐすべき行動リスト</h2>
   ・優先順位付きで5〜7項目を<ol><li>形式で
   ・「まず〜」「次に〜」という順序で具体的に

5. <h2>緊急で揃えるべき防災グッズ</h2>
   ・「今すぐ必要な理由」を強調して商品を紹介
   ・商品カード形式で各商品を紹介

6. <h2>避難・安全確保のポイント</h2>

7. <h2>まとめ・安全のために</h2>（チェックリスト形式）

【紹介する商品（緊急性を込めて紹介してください）】
{_format_products(products)}

【商品カード（各商品に使用）】
<div style="border:2px solid #ffcccc;border-radius:10px;padding:20px;margin:20px 0;overflow:hidden;background:#fff5f5">
<img src="[画像URL]" alt="[商品名]" style="max-width:180px;float:left;margin:0 20px 10px 0;border-radius:6px">
<h3>🚨 [商品名]</h3>
<p>価格：<strong style="font-size:1.2em;color:#c00">¥[価格]</strong></p>
<p>[今なぜ必要か・緊急性を込めたコメント（2文）]</p>
<a href="[アフィリエイトURL]" target="_blank" rel="noopener sponsored" style="display:inline-block;background:#c00;color:#fff;padding:12px 24px;text-decoration:none;border-radius:5px;font-weight:bold;margin-top:10px">今すぐ楽天市場で購入 →</a>
<div style="clear:both"></div>
</div>

【出力ルール】
- HTMLのみ（マークダウン・コードブロック禁止）
- 文字数：1500〜2500文字
- 緊急性が伝わるトーン（ただし過度に不安を煽らない）
- 最初の要素は必ず<h1>タイトル</h1>から始める
"""

    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{'role': 'user', 'content': prompt}],
    )
    return _parse(msg.content[0].text)
