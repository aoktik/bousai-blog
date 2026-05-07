"""環境変数ローダー - .env ファイルから os.environ に注入（標準ライブラリのみ）"""
import os
from pathlib import Path

_loaded = False


def load_env(path: str = None) -> None:
    """.env を読み込んで os.environ に展開する。

    - 既にセット済みの環境変数は上書きしない（setdefault）
    - 行頭 # はコメント
    - 値のクォートは外す
    - 1度ロードしたら以降のコールはスキップ（冪等）
    """
    global _loaded
    if _loaded:
        return

    if path is None:
        # プロジェクトルート（このファイルの2階層上）の .env を探す
        path = Path(__file__).resolve().parent.parent / '.env'
    else:
        path = Path(path)

    if not path.exists():
        _loaded = True
        return

    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip()
        # クォート除去
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        os.environ.setdefault(key, value)

    _loaded = True


# モジュール import時に自動でロード
load_env()
