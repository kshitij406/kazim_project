import pandas as pd
from core.store import Store

class ServiceDesk:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def frame(self) -> pd.DataFrame:
        with Store(self.db_path) as s:
            rows = s.all("SELECT * FROM it_requests ORDER BY opened_at DESC")
        return pd.DataFrame([dict(r) for r in rows])

    def set_phase(self, req_key: str, phase: str) -> None:
        with Store(self.db_path) as s:
            s.exec("UPDATE it_requests SET phase=? WHERE req_key=?", (phase, req_key))

    def add_request(self, req_key: str, topic: str, urgency: str, phase: str,
                    opened_at: str, assignee: str, closed_at: str | None = None) -> None:
        with Store(self.db_path) as s:
            s.exec(
                """INSERT INTO it_requests(req_key,topic,urgency,phase,opened_at,closed_at,assignee)
                   VALUES(?,?,?,?,?,?,?)""",
                (req_key, topic, urgency, phase, opened_at, closed_at, assignee),
            )
