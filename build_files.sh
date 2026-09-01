#!/bin/bash
# Build script for Vercel deployment
pip install --break-system-packages -r requirements.txt
python manage.py collectstatic --noinput
