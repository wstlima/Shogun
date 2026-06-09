#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "Starting Gensui server..."

if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: No virtual environment found. Run install.sh first."
    exit 1
fi

(sleep 3 && python3 -c "import webbrowser; webbrowser.open('http://localhost:8787')") &
python3 -m gensui
