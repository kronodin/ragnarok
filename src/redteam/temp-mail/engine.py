"""
Ragnarok Temp-Mail Engine
Authorized red team use only.
"""
import requests, json, time, re, sys, secrets, string
from typing import Optional, Dict, List

class TempMailEngine:
    PROVIDERS = {
        "mailtm": "https://api.mail.tm",
        "guerrilla": "https://api.guerrillamail.com",
        "dropmail": "https://dropmail.me",
    }

    def __init__(self, provider: str = "mailtm"):
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")
        self.provider = provider
        self.base = self.PROVIDERS[provider]
        self.account: Optional[Dict] = None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Ragnarok-TempMail/1.0"})

    def create_account(self, localpart: Optional[str] = None) -> Dict:
        if self.provider == "mailtm":
            return self._mailtm_create(localpart)
        if self.provider == "guerrilla":
            return self._guerrilla_create()
        if self.provider == "dropmail":
            return self._dropmail_create()
        raise NotImplementedError("Provider not implemented")

    def _mailtm_create(self, localpart: Optional[str] = None) -> Dict:
        domain = self._mailtm_domain()
        if not localpart:
            localpart = f"ragnarok_{secrets.token_hex(6)}"
        addr = f"{localpart}@{domain}"
        payload = {"address": addr, "password": secrets.token_hex(12)}
        r = self.session.post(f"{self.base}/accounts", json=payload, timeout=20)
        if r.status_code == 201:
            self.account = r.json()
            return {"address": self.account["address"], "id": self.account["id"], "provider": "mailtm"}
        raise Exception(f"mailtm create failed: {r.status_code} {r.text[:300]}")

    def _mailtm_domain(self) -> str:
        r = self.session.get(f"{self.base}/domains", timeout=20)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "hydra:member" in data:
                return data["hydra:member"][0]["domain"]
            if isinstance(data, list):
                return data[0]["domain"]
        raise Exception("mailtm domain fetch failed")

    def _mailtm_token(self) -> str:
        if not self.account:
            raise Exception("No account")
        addr = self.account["address"]
        pw = self.account.get("password", "ragnarok_ops")
        r = self.session.post(f"{self.base}/token", json={"address": addr, "password": pw}, timeout=20)
        if r.status_code == 200:
            token = r.json().get("token")
            self.account["token"] = token
            return token
        raise Exception(f"mailtm token failed: {r.status_code}")

    def _guerrilla_create(self) -> Dict:
        r = self.session.get(f"{self.base}/email.php?action=get_email_address&seq=0", timeout=20)
        if r.status_code == 200:
            data = r.json()
            self.account = {"address": data.get("email_addr"), "sid": data.get("sid_token"), "provider": "guerrilla"}
            return {"address": data.get("email_addr"), "id": data.get("sid_token"), "provider": "guerrilla"}
        raise Exception(f"guerrilla create failed: {r.status_code}")

    def _dropmail_create(self) -> Dict:
        r = self.session.get("https://api.dropmail.me/api/get_rand_mail?count=1", timeout=20)
        if r.status_code == 200:
            data = r.json()
            mail = data["mail_list"][0]
            self.account = {"address": mail["mail"], "id": mail["mail_id"], "token": mail["token"], "provider": "dropmail"}
            return {"address": mail["mail"], "id": mail["mail_id"], "provider": "dropmail"}
        raise Exception(f"dropmail create failed: {r.status_code}")

    def get_messages(self) -> List[Dict]:
        if not self.account:
            return []
        if self.provider == "mailtm":
            return self._mailtm_list()
        if self.provider == "guerrilla":
            return self._guerrilla_list()
        if self.provider == "dropmail":
            return self._dropmail_list()
        return []

    def _mailtm_list(self) -> List[Dict]:
        self._mailtm_token()
        token = self.account.get("token", "")
        headers = {"Authorization": f"Bearer {token}"}
        r = self.session.get(f"{self.base}/accounts/{self.account['id']}/messages", headers=headers, timeout=20)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "hydra:member" in data:
                return data["hydra:member"]
            if isinstance(data, list):
                return data
        return []

    def _guerrilla_list(self) -> List[Dict]:
        sid = self.account.get("sid", "")
        r = self.session.get(f"{self.base}/email.php?action=get_email_list&sid_token={sid}", timeout=20)
        if r.status_code == 200:
            return r.json().get("list", [])
        return []

    def _dropmail_list(self) -> List[Dict]:
        mail_id = self.account.get("id", "")
        r = self.session.get(f"https://api.dropmail.me/api/get_mail?mail_id={mail_id}", timeout=20)
        if r.status_code == 200:
            data = r.json()
            return data.get("mails", [])
        return []

    def get_message_detail(self, message_id: str) -> Optional[Dict]:
        if not self.account:
            return None
        if self.provider == "mailtm":
            token = self.account.get("token", "")
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            r = self.session.get(f"{self.base}/messages/{message_id}", headers=headers, timeout=20)
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
        if not sender or sender == "unknown":
            sender = msg.get("from", "unknown")
        subject = msg.get("subject", "(no subject)")
        body = msg.get("text") or msg.get("body") or msg.get("content") or ""
        body = re.sub(r"<[^>]+>", "", body)
        return f"From: {sender}\nSubject: {subject}\n\n{body[:4000]}"

    def summary(self) -> str:
        if not self.account:
            return "No account created"
        addr = self.account.get("address", "unknown")
        count = len(self.get_messages())
        return f"Provider: {self.provider}\nAddress: {addr}\nMessages: {count}"

    @staticmethod
    def generate_alias(prefix: str = "ragnarok") -> str:
        token = secrets.token_hex(6)
        return f"{prefix}_{token}"
