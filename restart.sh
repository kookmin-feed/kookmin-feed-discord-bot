#!/bin/bash
cd /home/ubuntu/sw-notice-bot
source venv/bin/activate
pm2 restart sw-notice-bot 