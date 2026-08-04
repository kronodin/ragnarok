import unittest, json, tempfile, os
from src.redteam.honeypot.logs.capture import load, summarize, alerts

class TestHoneypotLogs(unittest.TestCase):
    def setUp(self):
        self.path = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl")
        self.path.close()
        os.environ["RAGNAROK_HP_LOG"] = self.path.name

    def tearDown(self):
        os.unlink(self.path.name)

    def test_summary_empty(self):
        s = summarize([])
        self.assertEqual(s["total_events"], 0)

    def test_alerts_threshold(self):
        records = [
            {"type": "http_request", "remote": "1.2.3.4", "path": "/admin", "response": "200"},
            {"type": "http_request", "remote": "1.2.3.4", "path": "/.env", "response": "200"},
        ]
        a = alerts(records, threshold=2)
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0]["ip"], "1.2.3.4")

if __name__ == "__main__":
    unittest.main()
