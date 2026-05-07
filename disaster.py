"""災害監視スクリプト - GitHub Actionsから10分ごとに実行される"""
import json
import requests
from pathlib import Path

import helpers.rakuten as rakuten
import helpers.wordpress as wordpress
import helpers.claude_api as claude_api

STATE_FILE = Path('data/state.json')

# 地震発生時に検索する商品キーワード
EQ_KEYWORDS     = ['防災リュック 緊急', '非常食 セット', '保存水 長期保存', '懐中電灯 防災', 'モバイルバッテリー 防災']
# 台風接近時に検索する商品キーワード
TYPHOON_KEYWORDS = ['台風対策グッズ', '防水バッグ 防災', '保存水', '非常食 セット', '防災ラジオ']


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {'processed_earthquakes': [], 'processed_typhoons': [], 'topic_index': 0}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def check_earthquakes(state: dict) -> list:
    """P2P地震情報APIで震度4以上の新しい地震を検索"""
    processed = set(state.get('processed_earthquakes', []))
    try:
        resp = requests.get(
            'https://api.p2pquake.net/v2/history',
            params={'codes': 551, 'limit': 10},
            timeout=15,
        )
        resp.raise_for_status()
        events = resp.json()
    except Exception as e:
        print(f'地震API エラー: {e}')
        return []

    new_events = []
    for event in events:
        eid = event.get('id', '')
        if eid in processed:
            continue

        eq        = event.get('earthquake', {})
        max_scale = eq.get('maxScale', 0)

        # 震度4未満はスキップ（震度4 = scale値40）
        if max_scale < 40:
            continue

        # 影響を受けた都道府県を取得
        affected = []
        for point in event.get('points', []):
            pref = point.get('pref', '')
            if pref and pref not in affected:
                affected.append(pref)

        new_events.append({
            'id':            eid,
            'type':          'earthquake',
            'location':      eq.get('hypocenter', {}).get('name', '各地'),
            'magnitude':     eq.get('hypocenter', {}).get('magnitude', '-'),
            'max_intensity': max_scale / 10,
            'time':          event.get('time', ''),
            'affected_areas': affected[:5],
        })

    return new_events


def check_typhoons(state: dict) -> list:
    """気象庁APIで活発な台風を検索"""
    processed = set(state.get('processed_typhoons', []))
    try:
        resp = requests.get(
            'https://www.jma.go.jp/bosai/typhoon/data/index.json',
            timeout=15,
        )
        resp.raise_for_status()
        typhoons = resp.json()
    except Exception as e:
        print(f'台風API エラー: {e}')
        return []

    if not typhoons:
        return []

    new_events = []
    for t in typhoons:
        tid = str(t.get('id') or t.get('name', ''))
        if not tid or tid in processed:
            continue
        new_events.append({
            'id':      tid,
            'type':    'typhoon',
            'name':    t.get('name', ''),
            'name_ja': t.get('nameJa') or t.get('name_ja') or '台風',
            'status':  '日本に接近中',
            'areas':   [],
        })

    return new_events


def process_disaster(disaster: dict, state: dict):
    """災害記事を生成してWordPressに投稿し、stateを更新"""
    # 関連商品を検索
    keywords = EQ_KEYWORDS if disaster['type'] == 'earthquake' else TYPHOON_KEYWORDS
    products = []
    for kw in keywords[:3]:
        products.extend(rakuten.search(kw, hits=2))
    products = products[:5]
    print(f'商品取得: {len(products)}件')

    # 記事生成
    article = claude_api.generate_disaster(disaster, products)
    print(f'記事生成: {article["title"]}')

    # 投稿カテゴリ・タグ
    if disaster['type'] == 'earthquake':
        category = '地震対策'
        tags     = ['地震', '緊急情報', '防災対策']
    else:
        category = '台風・水害対策'
        tags     = ['台風', '緊急情報', '防災対策']

    url = wordpress.post(
        title    = article['title'],
        content  = article['content'],
        category = category,
        tags     = tags,
    )
    print(f'投稿完了: {url}')

    # 処理済みとして記録（最大200件保持）
    key = 'processed_earthquakes' if disaster['type'] == 'earthquake' else 'processed_typhoons'
    ids = state.get(key, [])
    ids.append(disaster['id'])
    state[key] = ids[-200:]


def main():
    state  = load_state()
    posted = False

    # 地震チェック
    earthquakes = check_earthquakes(state)
    print(f'新しい地震（震度4以上）: {len(earthquakes)}件')
    for eq in earthquakes:
        loc = eq['location']
        mag = eq['magnitude']
        si  = eq['max_intensity']
        print(f'  処理中: {loc} M{mag} 震度{si}')
        try:
            process_disaster(eq, state)
            posted = True
        except Exception as e:
            print(f'  エラー: {e}')
            # エラーでも記録（同じ地震で再試行しない）
            state.setdefault('processed_earthquakes', []).append(eq['id'])

    # 台風チェック
    typhoons = check_typhoons(state)
    print(f'新しい台風: {len(typhoons)}件')
    for ty in typhoons:
        print(f'  処理中: {ty["name_ja"]}')
        try:
            process_disaster(ty, state)
            posted = True
        except Exception as e:
            print(f'  エラー: {e}')
            state.setdefault('processed_typhoons', []).append(ty['id'])

    save_state(state)

    if not posted:
        print('新しい災害イベントなし')


if __name__ == '__main__':
    main()
