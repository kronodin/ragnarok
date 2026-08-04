"""
Ragnarok HTTP Honeypot
Emulates common vulnerable web endpoints.
"""
import json, time, os, sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

LOG_PATH = Path("/tmp/ragnarok_hp_capture.jsonl")

class HoneypotHandler(BaseHTTPRequestHandler):
    FAKE_PAGES = {
        "/admin": "<html><body><h1>Admin Login</h1><form><input name='user'><input name='pass' type='password'><button>Login</button></form></body></html>",
        "/wp-login.php": "<html><body><h1>WordPress &rsaquo; Log In</h1><form><input name='log'><input name='pwd' type='password'><button>Log In</button></form></body></html>",
        "/.env": "APP_KEY=base64:ragnarok\nDB_HOST=127.0.0.1\nDB_DATABASE=honeypot\n",
        "/backup.sql": "-- MySQL dump\nCREATE TABLE users (id INT, user VARCHAR(255), pass VARCHAR(255));\nINSERT INTO users VALUES (1,'admin','ragnarok');\n",
        "/": "<html><body><h1>Welcome to Microtuff Solutions</h1><p>Under Construction</p></body></html>",
    }
    BANNER = "Apache/2.4.41 (Ubuntu)"

    def log_request(self, code="-", size="-"):
        self._log_event({
            "type": "http_request",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "remote": self.client_address[0],
            "method": self.command,
            "path": self.path,
            "version": self.request_version,
            "response": str(code),
        })

    def _log_event(self, record: dict):
        try:
            with open(LOG_PATH, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass

    def _respond(self, body: str, status: int = 200):
        self.send_response(status)
        self.send_header("Server", self.BANNER)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        path = urlparse(self.path).path
        body = self.FAKE_PAGES.get(path, self.FAKE_PAGES.get("/")) or ""
        self._respond(body, 200)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="ignore")
        params = parse_qs(raw)
        creds = {k: v[0] for k, v in params.items() if k in ("user", "log", "username", "email")}
        self._log_event({
            "type": "http_creds",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "remote": self.client_address[0],
            "path": self.path,
            "creds": creds,
        })
        self._respond("<html><body><h1>Login Failed</h1></body></html>", 401)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Server", self.BANNER)
        self.end_headers()

def serve(port: int = 8080, bind: str = "0.0.0.0"):
    HTTPServer((bind, port), HoneypotHandler).serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    serve(port)
