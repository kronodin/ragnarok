"""
Ragnarok SSH Honeypot
Emulates weak SSH auth and logs attempts.
"""
import json, time, socket, threading, sys
from pathlib import Path

LOG_PATH = Path("/tmp/ragnarok_hp_capture.jsonl")
BANNER = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3"

def _log(record: dict):
    try:
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass

def handle_client(conn: socket.socket, addr):
    try:
        conn.sendall(f"{BANNER}\r\n".encode())
        data = conn.recv(2048).decode("utf-8", errors="ignore")
        _log({
            "type": "ssh_attempt",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "remote": addr[0],
            "banner_echo": data.strip(),
        })
        conn.sendall(b"Permission denied, please try again.\r\n")
    except Exception:
        pass
    finally:
        conn.close()

def serve(port: int = 2222, bind: str = "0.0.0.0"):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((bind, port))
    srv.listen(50)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 2222
    serve(port)
