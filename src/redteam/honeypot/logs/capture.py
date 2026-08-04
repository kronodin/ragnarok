"""
Honeypot log processor: read JSONL, summarize, export alerts.
"""
import json, sys, csv
from pathlib import Path
from collections import Counter, defaultdict

LOG_PATH = Path("/tmp/ragnarok_hp_capture.jsonl")

def load(path: str = "") -> list:
    p = Path(path) if path else LOG_PATH
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]

def summarize(records: list) -> dict:
    by_type = Counter(r.get("type") for r in records)
    by_ip = Counter(r.get("remote") for r in records)
    paths = Counter(r.get("path") for r in records if r.get("type") == "http_request")
    return {
        "total_events": len(records),
        "by_type": dict(by_type),
        "top_ips": by_ip.most_common(20),
        "top_paths": paths.most_common(20),
    }

def alerts(records: list, threshold: int = 5) -> list:
    hits = defaultdict(int)
    for r in records:
        ip = r.get("remote")
        if ip:
            hits[ip] += 1
    return [{"ip": ip, "count": count} for ip, count in hits.items() if count >= threshold]

def export_csv(records: list, out: str = "/tmp/ragnarok_hp_alerts.csv"):
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp","type","remote","path","response"])
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k, "") for k in ["timestamp","type","remote","path","response"]})

def main():
    records = load()
    if not records:
        print("No records")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "alerts":
        for a in alerts(records):
            print(a)
    elif len(sys.argv) > 1 and sys.argv[1] == "csv":
        out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/ragnarok_hp_alerts.csv"
        export_csv(records, out)
        print(f"Exported {len(records)} records to {out}")
    else:
        print(json.dumps(summarize(records), indent=2))

if __name__ == "__main__":
    main()
