#!/bin/bash
# О :: встановлення автономії (macOS launchd) — запускати СВІДОМО, вручну.
# Після цього скрипт О виконує цикл кожні 15 хв без людини, навіть після перезавантаження.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$(command -v python3)"
echo "О: встановлюю автономію з $PY"
"$PY" "$ROOT/o_closed/cli.py" autonomous --every 900 --cycles 2000
echo
echo "Перевірка:  launchctl list | grep org.o.closed"
echo "Логи:       $ROOT/o_closed/state/launchd.out.log"
echo "Вимкнути:   $ROOT/o_closed/uninstall_autonomy.sh"
