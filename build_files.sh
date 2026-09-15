#!/bin/bash
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt --system
else
    python3 -m pip install --break-system-packages -r requirements.txt || pip install --break-system-packages -r requirements.txt
fi

python3 manage.py collectstatic --no-input || python manage.py collectstatic --no-input || true
