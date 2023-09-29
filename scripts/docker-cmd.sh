#!/bin/sh
# This script is meant to be ran solely in a Docker container.
# Do not run it manually, it's not meant for that.

sh scripts/generate-opensearch.sh || exit $?
python3 scripts/generate-pyconfig.py || exit $?

exec gunicorn --workers $WORKERS --threads $THREADS __init__:app
