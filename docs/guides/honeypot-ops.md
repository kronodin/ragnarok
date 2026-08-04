# Honeypot Operations Guide

## Start services
python src/redteam/honeypot/http/server.py 8080
python src/redteam/honeypot/ssh/server.py 2222

## View captures
python src/redteam/honeypot/logs/capture.py
python src/redteam/honeypot/logs/capture.py alerts
python src/redteam/honeypot/logs/capture.py csv /tmp/alerts.csv
