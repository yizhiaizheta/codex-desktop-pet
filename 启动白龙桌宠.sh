#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$APP_DIR/linux-state/config"
export XDG_CONFIG_HOME="$APP_DIR/linux-state/config"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
export PYTHONUNBUFFERED=1
if [[ -z "${BAILONG_CODEX:-}" && -x /usr/lib/chatgpt/resources/codex ]]; then
    export BAILONG_CODEX=/usr/lib/chatgpt/resources/codex
fi
cd -- "$APP_DIR"
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/app/pet.py" "$@" >> "$APP_DIR/linux-state/桌宠.log" 2>&1
