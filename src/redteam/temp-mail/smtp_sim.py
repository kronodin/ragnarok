"""
SMTP send wrapper for phishing simulation emails.
Authorized campaigns only. Requires relay server or local SMTP credentials.
"""
import smtplib, json, os
from email.message import EmailMessage
from typing import List, Dict

class SmtpSim:
    def __init__(self, host: str, port: int, username: str = "", password: str = "", use_tls: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send(self, frm: str, to: List[str], subject: str, body: str, html: str = "") -> Dict:
        msg = EmailMessage()
        msg["From"] = frm
        msg["To"] = ", ".join(to)
        msg["Subject"] = subject
        msg.set_content(body)
        if html:
            msg.add_alternative(html, subtype="html")
        with smtplib.SMTP(self.host, self.port) as s:
            if self.use_tls:
                s.starttls()
            if self.username:
                s.login(self.username, self.password)
            s.send_message(msg)
        return {"status": "sent", "from": frm, "to": to, "subject": subject}

    def batch_send(self, frm: str, targets: List[Dict], subject: str, body: str, html: str = "") -> List[Dict]:
        results = []
        for t in targets:
            to = t.get("email")
            if not to:
                continue
            try:
                results.append(self.send(frm, [to], subject, body, html))
            except Exception as e:
                results.append({"status": "error", "to": to, "error": str(e)})
        return results
