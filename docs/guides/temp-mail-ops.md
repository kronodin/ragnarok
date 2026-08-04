# Temp-Mail Operations Guide

## Quickstart
python src/redteam/temp-mail/cli.py create --provider mailtm
python src/redteam/temp-mail/cli.py list --provider mailtm
python src/redteam/temp-mail/cli.py wait --provider mailtm --timeout 60

## Relay Server
python src/redteam/temp-mail/relay.py 7777 /tmp/ragnarok_capture.jsonl

## SMTP Simulation
from src.redteam.temp-mail.smtp_sim import SmtpSim
sim = SmtpSim("localhost", 25, username="", password="", use_tls=False)
sim.send("redteam@microtuff.com", ["target@example.com"], "Subject", "Body")
