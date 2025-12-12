from __future__ import annotations
import csv
import os
from core.store import Store
from core.security import ensure_seed_folder, append_user_to_file, USERS_TXT

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  handle TEXT UNIQUE NOT NULL,
  pass_hash TEXT NOT NULL,
  access_level TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sec_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_key TEXT UNIQUE NOT NULL,
  event_kind TEXT NOT NULL,
  impact TEXT NOT NULL,
  state TEXT NOT NULL,
  raised_at TEXT NOT NULL,
  cleared_at TEXT,
  owner TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS data_assets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_name TEXT UNIQUE NOT NULL,
  steward TEXT NOT NULL,
  origin TEXT NOT NULL,
  size_mb REAL NOT NULL,
  rows_est INTEGER NOT NULL,
  created_on TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS it_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  req_key TEXT UNIQUE NOT NULL,
  topic TEXT NOT NULL,
  urgency TEXT NOT NULL,
  phase TEXT NOT NULL,
  opened_at TEXT NOT NULL,
  closed_at TEXT,
  assignee TEXT NOT NULL
);
"""

def ensure_schema(db_path: str) -> None:
    ensure_seed_folder()
    with Store(db_path) as s:
        for stmt in [x.strip() for x in SCHEMA_SQL.split(";") if x.strip()]:
            s.exec(stmt + ";")

def seed_all(db_path: str, folder: str = "seed") -> None:
    """
    Loads:
    - seed/users.txt  (handle,pass_hash,access_level)
    - seed/sec_events.csv
    - seed/data_assets.csv
    - seed/it_requests.csv
    """
    ensure_schema(db_path)

    with Store(db_path) as s:
        _seed_accounts_from_users_txt(s, os.path.join(folder, "users.txt"))
        _seed_sec_events(s, os.path.join(folder, "sec_events.csv"))
        _seed_data_assets(s, os.path.join(folder, "data_assets.csv"))
        _seed_it_requests(s, os.path.join(folder, "it_requests.csv"))

def _seed_accounts_from_users_txt(s: Store, path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 3:
                continue
            handle, pass_hash, access = parts
            s.exec(
                "INSERT OR IGNORE INTO accounts(handle, pass_hash, access_level) VALUES(?,?,?)",
                (handle, pass_hash, access),
            )

def _read_csv(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _seed_sec_events(s: Store, path: str) -> None:
    for e in _read_csv(path):
        s.exec(
            """INSERT OR IGNORE INTO sec_events(event_key,event_kind,impact,state,raised_at,cleared_at,owner,notes)
               VALUES(?,?,?,?,?,?,?,?)""",
            (
                e["event_key"], e["event_kind"], e["impact"], e["state"],
                e["raised_at"], e.get("cleared_at") or None,
                e["owner"], e.get("notes") or "",
            ),
        )

def _seed_data_assets(s: Store, path: str) -> None:
    for a in _read_csv(path):
        s.exec(
            """INSERT OR IGNORE INTO data_assets(asset_name,steward,origin,size_mb,rows_est,created_on)
               VALUES(?,?,?,?,?,?)""",
            (
                a["asset_name"], a["steward"], a["origin"],
                float(a["size_mb"]), int(a["rows_est"]), a["created_on"],
            ),
        )

def _seed_it_requests(s: Store, path: str) -> None:
    for r in _read_csv(path):
        s.exec(
            """INSERT OR IGNORE INTO it_requests(req_key,topic,urgency,phase,opened_at,closed_at,assignee)
               VALUES(?,?,?,?,?,?,?)""",
            (
                r["req_key"], r["topic"], r["urgency"], r["phase"],
                r["opened_at"], r.get("closed_at") or None, r["assignee"],
            ),
        )

if __name__ == "__main__":
    # One command to prepare a working demo:
    # 1) write default users into seed/users.txt if missing
    ensure_seed_folder()
    if not os.path.exists(USERS_TXT):
        append_user_to_file("admin", "admin123", "Owner")
        append_user_to_file("analyst", "analyst123", "Analyst")
        append_user_to_file("viewer", "viewer123", "ReadOnly")

    # 2) load everything into seed/mdip_v2.sqlite3
    from config import CFG
    seed_all(CFG.db_path, folder="seed")
    print("Seed complete.")
