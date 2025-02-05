#!/bin/bash
cd /home/ubuntu/sw-notice-bot
source venv/bin/activate
git pull
pip install -r requirements.txt
pm2 restart sw-notice-bot 