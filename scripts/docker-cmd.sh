#!/bin/sh
# This script is meant to be ran solely in a Docker container.
# Do not run it manually, it's not meant for that.

sh scripts/generate-opensearch.sh || exit $?
python3 scripts/generate-pyconfig.py || exit $?

[ "$WORKERS" ] || WORKERS=2
[ "$THREADS" ] || THREADS=8
[ "$PORT" ]    || PORT=8000

exec gunicorn --workers $WORKERS --threads $THREADS --bind="0.0.0.0:$PORT" __init__:app
