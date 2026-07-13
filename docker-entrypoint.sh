#!/bin/sh
set -eu

CONFIG_DIR="${WHISPER_WEBUI_CONFIG_DIR:-/Whisper-WebUI/configs}"
DEFAULT_CONFIG_DIR="${WHISPER_WEBUI_DEFAULT_CONFIG_DIR:-/Whisper-WebUI/configs.default}"

mkdir -p "$CONFIG_DIR"

for source in "$DEFAULT_CONFIG_DIR"/*; do
    [ -e "$source" ] || continue

    target="$CONFIG_DIR/$(basename "$source")"
    if [ ! -e "$target" ]; then
        cp -R "$source" "$target"
        echo "Initialized missing config: $target"
    fi
done

exec python app.py "$@"
