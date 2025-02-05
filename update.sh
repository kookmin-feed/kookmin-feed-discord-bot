#!/bin/bash
cd /home/ubuntu/kookmin-feed
source venv/bin/activate
git pull
pip install -r requirements.txt
pm2 restart kookmin-feed 