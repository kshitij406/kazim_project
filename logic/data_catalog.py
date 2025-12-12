import pandas as pd
from core.store import Store

class DataCatalog:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def frame(self) -> pd.DataFrame:
        with Store(self.db_path) as s:
            rows = s.all("SELECT * FROM data_assets ORDER BY created_on DESC")
        return pd.DataFrame([dict(r) for r in rows])

    def change_steward(self, asset_name: str, steward: str) -> None:
        with Store(self.db_path) as s:
            s.exec("UPDATE data_assets SET steward=? WHERE asset_name=?", (steward, asset_name))

    def add_asset(self, asset_name: str, steward: str, origin: str,
                  size_mb: float, rows_est: int, created_on: str) -> None:
        with Store(self.db_path) as s:
            s.exec(
                """INSERT INTO data_assets(asset_name,steward,origin,size_mb,rows_est,created_on)
                   VALUES(?,?,?,?,?,?)""",
                (asset_name, steward, origin, float(size_mb), int(rows_est), created_on),
            )
