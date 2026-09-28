#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv-podcast"

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$ROOT/tools/requirements-podcast.txt"

cat <<EOF
Podcast environment ready.

Internet Archive CLI:
  $VENV/bin/ia

Existing IA config expected at:
  $HOME/.config/internetarchive/ia.ini

Run publication with:
  cd "$ROOT"
  python3 tools/podcast_publish.py "https://www.youtube.com/watch?v=VIDEO_ID"

The publisher automatically uses $VENV/bin/ia if ia is not available in PATH.
EOF
