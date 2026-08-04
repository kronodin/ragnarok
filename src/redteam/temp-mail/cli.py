#!/usr/bin/env python3
"""
Ragnarok Temp-Mail CLI
Authorized testing only.
"""
import sys, json, argparse
from engine import TempMailEngine

def main():
    parser = argparse.ArgumentParser(description="Ragnarok Temp-Mail CLI")
    parser.add_argument("command", choices=["create","list","read","wait","summary","alias"])
    parser.add_argument("--provider", default="mailtm")
    parser.add_argument("--id", dest="msg_id")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    engine = TempMailEngine(provider=args.provider)
    if args.command == "create":
        alias = TempMailEngine.generate_alias() if args.msg_id is None else args.msg_id
        acc = engine.create_account(localpart=alias)
        print(json.dumps({"address": acc.get("address"), "id": acc.get("id"), "provider": acc.get("provider")}, indent=2))
    elif args.command == "list":
        msgs = engine.get_messages()
        print(json.dumps([{"id": m.get("id") or m.get("mail_id"), "from": m.get("from") or m.get("from_addr"), "subject": m.get("subject")} for m in msgs], indent=2))
    elif args.command == "read":
        if not args.msg_id:
            print("--id required")
            sys.exit(1)
        detail = engine.get_message_detail(args.msg_id)
        print(engine.format_message(detail) if detail else "Message not found")
    elif args.command == "wait":
        msg = engine.wait_for_mail(timeout=args.timeout)
        print(engine.format_message(msg) if msg else "No mail received within timeout")
    elif args.command == "summary":
        print(engine.summary())
    elif args.command == "alias":
        print(TempMailEngine.generate_alias())

if __name__ == "__main__":
    main()
