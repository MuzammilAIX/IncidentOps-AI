#!/bin/bash
echo "BUILD START"
python3.12 -m pip install uv
uv sync --no-dev
uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput
echo "BUILD END"
