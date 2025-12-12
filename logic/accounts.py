from core.store import Store
from core.security import check_hash

class Accounts:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def authenticate(self, handle: str, password: str) -> dict | None:
        with Store(self.db_path) as s:
            row = s.one("SELECT id, handle, pass_hash, access_level FROM accounts WHERE handle=?", (handle,))
            if not row:
                return None
            if not check_hash(password, row["pass_hash"]):
                return None
            return {"id": row["id"], "handle": row["handle"], "access_level": row["access_level"]}
