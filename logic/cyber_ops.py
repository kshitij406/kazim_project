import pandas as pd
from core.store import Store

class CyberOps:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def frame(self) -> pd.DataFrame:
        with Store(self.db_path) as s:
            rows = s.all("SELECT * FROM sec_events ORDER BY raised_at DESC")
        return pd.DataFrame([dict(r) for r in rows])

    def update_state(self, event_key: str, new_state: str) -> None:
        with Store(self.db_path) as s:
            s.exec("UPDATE sec_events SET state=? WHERE event_key=?", (new_state, event_key))

    def add_event(self, event_key: str, event_kind: str, impact: str, state: str,
                  raised_at: str, owner: str, notes: str = "", cleared_at: str | None = None) -> None:
        with Store(self.db_path) as s:
            s.exec(
                """INSERT INTO sec_events(event_key,event_kind,impact,state,raised_at,cleared_at,owner,notes)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (event_key, event_kind, impact, state, raised_at, cleared_at, owner, notes),
            )
