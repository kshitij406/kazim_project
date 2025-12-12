import sqlite3
from typing import Any, Iterable, Optional

class Store:
    def __init__(self, path: str):
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.conn:
            if exc is None:
                self.conn.commit()
            self.conn.close()

    def exec(self, sql: str, params: tuple = ()) -> None:
        assert self.conn is not None
        self.conn.execute(sql, params)

    def many(self, sql: str, params_list: Iterable[tuple]) -> None:
        assert self.conn is not None
        self.conn.executemany(sql, params_list)

    def one(self, sql: str, params: tuple = ()) -> Any:
        assert self.conn is not None
        cur = self.conn.execute(sql, params)
        return cur.fetchone()

    def all(self, sql: str, params: tuple = ()) -> list[Any]:
        assert self.conn is not None
        cur = self.conn.execute(sql, params)
        return cur.fetchall()
