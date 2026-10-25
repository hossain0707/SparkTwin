"""Local SQLite: scenario and user-supplied measurement history."""
import json, os, sqlite3, time, uuid
from pathlib import Path
from .model import normalize
from .calibration import validate_record


def state_dir():
    root = Path(os.environ.get("SPARKTWIN_HOME", Path.home() / ".sparktwin")).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        root.chmod(0o700)
    return root


class Store:
    def __init__(self, path=None):
        self.path = Path(path) if path else state_dir()/"sparktwin.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, check_same_thread=False, timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS scenarios (id TEXT PRIMARY KEY, data TEXT NOT NULL, created INTEGER NOT NULL, updated INTEGER NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS benchmarks (id TEXT PRIMARY KEY, data TEXT NOT NULL, created INTEGER NOT NULL)")
        self.db.commit()
        if os.name != "nt" and self.path.exists():
            self.path.chmod(0o600)

    def list_scenarios(self):
        return [{**json.loads(r["data"]), "id": r["id"], "created_at": r["created"], "updated_at": r["updated"]}
                for r in self.db.execute("SELECT * FROM scenarios ORDER BY updated DESC")]

    def save_scenario(self, raw, id=None):
        data=normalize(raw)
        now=int(time.time())
        if id is not None and not self.db.execute("SELECT 1 FROM scenarios WHERE id=?",(id,)).fetchone():
            raise KeyError("Scenario not found")
        ident=id or uuid.uuid4().hex
        created=self.db.execute("SELECT created FROM scenarios WHERE id=?",(ident,)).fetchone()
        self.db.execute("INSERT OR REPLACE INTO scenarios(id,data,created,updated) VALUES(?,?,?,?)",
                        (ident,json.dumps(data,separators=(',',':')),created[0] if created else now,now))
        self.db.commit()
        return ident

    def remove_scenario(self,id):
        cur=self.db.execute("DELETE FROM scenarios WHERE id=?",(id,))
        self.db.commit()
        return bool(cur.rowcount)

    def list_benchmarks(self):
        return [{**json.loads(r["data"]),"id":r["id"],"created_at":r["created"]}
                for r in self.db.execute("SELECT * FROM benchmarks ORDER BY created DESC")]

    def insert_benchmarks(self, raw):
        if not isinstance(raw,list) or not 1<=len(raw)<=500:
            raise ValueError("Import must contain 1–500 benchmark measurements")
        # Full upfront validation guarantees no partial accepted imports.
        data=[validate_record(r) for r in raw]
        now=int(time.time())
        with self.db:
            for r in data:
                self.db.execute("INSERT INTO benchmarks VALUES (?,?,?)",(uuid.uuid4().hex,json.dumps(r,separators=(',',':')),now))
        return len(data)

    def remove_benchmark(self,id):
        cur=self.db.execute("DELETE FROM benchmarks WHERE id=?",(id,))
        self.db.commit()
        return bool(cur.rowcount)

    def export(self):
        return {"format":"sparktwin-backup-v1","exported_at":int(time.time()),
                "scenarios":self.list_scenarios(),"benchmarks":self.list_benchmarks()}

    def close(self): self.db.close()
