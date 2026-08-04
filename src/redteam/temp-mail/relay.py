"""
Inbound webhook relay for temp-mail captures.
Writes received mail to JSONL for downstream tooling.
"""
import json, os, sys
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

DEFAULT_LOG = Path("/tmp/ragnarok_temp_mail_capture.jsonl")

class RelayHandler(BaseHTTPRequestHandler):
    log_path = DEFAULT_LOG

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except Exception:
            data = {"raw": body.decode("utf-8", errors="ignore")}
        record = {"timestamp": datetime.utcnow().isoformat()+"Z", "path": self.path, "data": data}
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def log_message(self, format, *args):
        return

def serve(port: int = 7777, log_path: str = ""):
    if log_path:
        RelayHandler.log_path = Path(log_path)
    HTTPServer(("127.0.0.1", port), RelayHandler).serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7777
    serve(port)
