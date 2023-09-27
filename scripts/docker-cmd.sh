#!/bin/sh

sh scripts/generate-opensearch.sh

exec gunicorn --workers $WORKERS --threads $THREADS __init__:app
