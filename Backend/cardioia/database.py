import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class EventConflict(Exception):
    pass


class Database:
    def __init__(self, path):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL, event_id TEXT NOT NULL,
                payload TEXT NOT NULL, result TEXT NOT NULL,
                captured_at TEXT NOT NULL, received_at TEXT NOT NULL,
                UNIQUE(device_id, event_id)
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS readings_captured ON readings(captured_at DESC, id DESC)")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            db.row_factory = sqlite3.Row
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def store(self, payload, result):
        canonical = json.dumps(payload, sort_keys=True)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM readings WHERE device_id=? AND event_id=?", (payload["device_id"], payload["event_id"])).fetchone()
            if row:
                if row["payload"] != canonical:
                    raise EventConflict()
                return {**json.loads(row["result"]), "duplicate": True}
            db.execute("INSERT INTO readings(device_id,event_id,payload,result,captured_at,received_at) VALUES(?,?,?,?,?,?)", (
                payload["device_id"], payload["event_id"], canonical,
                json.dumps(result), result["captured_at"], result["received_at"],
            ))
        return result

    def history(self, limit=30):
        with self.connect() as db:
            rows = db.execute("SELECT result FROM readings ORDER BY captured_at DESC, id DESC LIMIT ?", (limit,)).fetchall()
        return [json.loads(row["result"]) for row in rows]


