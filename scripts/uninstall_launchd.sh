#!/bin/bash
# launchd 自動化の停止
set -e

PLIST_NAME="com.aoktik.bousai-daily"
PLIST_DST="${HOME}/Library/LaunchAgents/${PLIST_NAME}.plist"

if launchctl list | grep -q "$PLIST_NAME"; then
    launchctl unload "$PLIST_DST"
    echo "✓ ${PLIST_NAME} をアンロードしました"
fi

if [ -f "$PLIST_DST" ]; then
    rm "$PLIST_DST"
    echo "✓ ${PLIST_DST} を削除しました"
fi
