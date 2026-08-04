#!/usr/bin/env python3
"""
Ragnarok Temp-Mail CLI
Authorized testing only.
"""
import sys, json
from engine import TempMailEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <create|list|read|wait> [args]")
        sys.exit(1)
    cmd = sys.argv[1]
    engine = TempMailEngine()
    if cmd == "create":
        acc = engine.create_account()
        print(json.dumps({"address": acc.get("address"), "id": acc.get("id")}, indent=2))
    elif cmd == "list":
        msgs = engine.get_messages()
        print(json.dumps([{"id": m.get("id"), "from": m.get("from", {}).get("address"), "subject": m.get("subject")} for m in msgs], indent=2))
    elif cmd == "read" and len(sys.argv) > 2:
        detail = engine.get_message_detail(sys.argv[2])
        if detail:
            print(engine.format_message(detail))
        else:
            print("Message not found")
    elif cmd == "wait":
        msg = engine.wait_for_mail()
        if msg:
            print(engine.format_message(msg))
        else:
            print("No mail received within timeout")
    else:
        print("Unknown command")
        sys.exit(1)

if __name__ == "__main__":
    main()
