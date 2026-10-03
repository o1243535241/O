#!/bin/bash
# О :: вимкнення автономії
set -euo pipefail
PLIST="$HOME/Library/LaunchAgents/org.o.closed.loop.plist"
launchctl unload -w "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "О: автономію вимкнено, plist видалено."
