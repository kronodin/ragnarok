"""
Ragnarok Temp-Mail Engine
Authorized red team use only.
"""
import requests, json, time, re, sys
from typing import Optional, Dict, List

class TempMailEngine:
    PROVIDERS = {
        "mailtm": "https://api.mail.tm",
        "guerrilla": "https://api.guerrillamail.com",
    }

    def __init__(self, provider: str = "mailtm"):
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")
        self.provider = provider
        self.base = self.PROVIDERS[provider]
        self.account: Optional[Dict] = None
        self.messages: List[Dict] = []

    def create_account(self) -> Dict:
        if self.provider == "mailtm":
            domain = self._get_mailtm_domain()
            addr = f"ragnarok_{int(time.time())}@{domain}"
            payload = {"address": addr, "password": "ragnarok_ops"}
            r = requests.post(f"{self.base}/accounts", json=payload, timeout=15)
            if r.status_code == 201:
                self.account = r.json()
                return self.account
            raise Exception(f"mailtm account creation failed: {r.status_code} {r.text}")
        raise NotImplementedError("Provider not implemented yet")

    def _get_mailtm_domain(self) -> str:
        r = requests.get(f"{self.base}/domains", timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "hydra:member" in data:
                return data["hydra:member"][0]["domain"]
            if isinstance(data, list):
                return data[0]["domain"]
        raise Exception("Failed to fetch mailtm domain")

    def get_messages(self) -> List[Dict]:
        if not self.account:
            return []
        if self.provider == "mailtm":
            account_id = self.account["id"]
            token = self.account.get("token") or self.account.get("@type", "")
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            r = requests.get(f"{self.base}/accounts/{account_id}/messages", headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict) and "hydra:member" in data:
                    self.messages = data["hydra:member"]
                elif isinstance(data, list):
                    self.messages = data
                return self.messages
        return []

    def get_message_detail(self, message_id: str) -> Optional[Dict]:
        if not self.account:
            return None
        token = self.account.get("token") or ""
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        r = requests.get(f"{self.base}/messages/{message_id}", headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        return None

    def wait_for_mail(self, timeout: int = 120, poll: int = 5) -> Optional[Dict]:
        start = time.time()
        while time.time() - start < timeout:
            msgs = self.get_messages()
            if msgs:
                return msgs[0]
            time.sleep(poll)
        return None

    def format_message(self, msg: Dict) -> str:
        sender = msg.get("from", {}).get("address", "unknown")
        subject = msg.get("subject", "(no subject)")
        text = msg.get("text") or msg.get("content") or ""
        text = re.sub(r"<[^>]+>", "", text)
        return f"From: {sender}\nSubject: {subject}\n\n{text[:2000]}"

    def summary(self) -> str:
        if not self.account:
            return "No account created"
        addr = self.account.get("address", "unknown")
        count = len(self.get_messages())
        return f"Provider: {self.provider}\nAddress: {addr}\nMessages: {count}"
