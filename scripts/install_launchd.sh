#!/bin/bash
# launchd 自動化のインストーラ
# 毎朝 7:00 に daily_enhanced.py を実行する

set -e

PLIST_NAME="com.aoktik.bousai-daily"
PLIST_SRC="$(dirname "$0")/${PLIST_NAME}.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/${PLIST_NAME}.plist"

echo "=== bousai-blog 日次自動化セットアップ ==="

# 既存をアンロード
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "→ 既存 LaunchAgent をアンロード"
    launchctl unload "$PLIST_DST" 2>/dev/null || true
fi

# コピーしてロード
cp "$PLIST_SRC" "$PLIST_DST"
echo "→ ${PLIST_DST} にコピー"

launchctl load "$PLIST_DST"
echo "→ ロード完了"

echo
echo "✓ 毎朝 7:00 に daily_enhanced.py が実行されます"
echo
echo "ログ確認:"
echo "  tail -f /Users/aokitaiki/bousai-blog/data/launchd-stdout.log"
echo
echo "手動実行:"
echo "  launchctl start ${PLIST_NAME}"
echo
echo "停止:"
echo "  bash $(dirname "$0")/uninstall_launchd.sh"
