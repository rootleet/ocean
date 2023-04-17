#!/usr/bin/bash
git pull origin main --no-ff && python3 manage.py runserver 192.168.2.60:80