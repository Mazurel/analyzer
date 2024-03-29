#!/usr/bin/env bash

# Based on: https://github.com/zauberzeug/nicegui/tree/main/examples/fastapi/

set -xem

# use path of this example as working directory; enables starting this script from anywhere
cd "$(dirname "$0")"

if [ "$1" = "prod" ]; then
    echo "Starting Uvicorn server in production mode..."
    # we also use a single worker in production mode so socket.io connections are always handled by the same worker
    poetry run uvicorn main:app --workers 1 --log-level info --port 80
elif [ "$1" = "dev" ]; then
    echo "Starting Uvicorn server in development mode..."
    # reload implies workers = 1
    poetry run uvicorn main:app --reload --log-level info --port 8000 &
    sleep 5s
    python -c 'import webbrowser; webbrowser.open("http://127.0.0.1:8000/")'
    fg
else
    echo "Invalid parameter. Use 'prod' or 'dev'."
    exit 1
fi
