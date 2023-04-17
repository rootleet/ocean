#!/usr/bin/bash
git pull origin main --no-ff -m'$(date)' && python3 manage.py runserver 192.168.2.60:80