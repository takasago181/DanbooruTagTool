from __future__ import annotations
import importlib.util, json, os, sqlite3, tempfile, unittest
from contextlib import closing
from pathlib import Path

MODULE_PATH=Path(__file__).with_name("catalog_structural_health.py")
spec=importlib.util.spec_from_file_location("catalog_structural_health",MODULE_PATH)
health=importlib.util.module_from_spec(spec); spec.loader.exec_module(health)

def make_catalog(path: Path, entries: list[tuple[str,str,int,str]]):
    with closing(sqlite3.connect(path)) as db:
        db.executescript("PRAGMA user_version=1; CREATE TABLE entries(id TEXT PRIMARY KEY,canonical TEXT,ordinal INTEGER NOT NULL,payload TEXT NOT NULL); CREATE INDEX canonical_lookup ON entries(canonical); CREATE TABLE metadata(provenance TEXT NOT NULL);")
        db.execute("INSERT INTO metadata VALUES('{}')")
        db.executemany("INSERT INTO entries VALUES(?,?,?,?)",entries)
        db.commit()

def row(entry_id: str, ordinal: int, *, payload: str|None=None):
    value={"Id":entry_id,"Canonical":entry_id,"English":entry_id,"Aliases":[],"TagCategory":"General","IsSpecial":False}
    return (entry_id,entry_id,ordinal,payload if payload is not None else json.dumps(value))

class StructuralHealthTests(unittest.TestCase):
    def test_count_drift_alone_is_valid(self):
        with tempfile.TemporaryDirectory(dir=MODULE_PATH.parent) as d:
            p=Path(d)/"catalog.db"; make_catalog(p,[row("one",0),row("two",1),row("three",2)])
            self.assertEqual(3,health.validate(p)["total"])
    def test_invalid_payload_json_fails(self): self.assert_invalid([row("one",0,payload="{")])
    def test_duplicate_id_fails(self):
        with tempfile.TemporaryDirectory(dir=MODULE_PATH.parent) as d:
            p=Path(d)/"catalog.db"
            with closing(sqlite3.connect(p)) as db:
                db.executescript("PRAGMA user_version=1; CREATE TABLE entries(id TEXT,canonical TEXT,ordinal INTEGER NOT NULL,payload TEXT NOT NULL); CREATE TABLE metadata(provenance TEXT NOT NULL); INSERT INTO metadata VALUES('{}');")
                db.executemany("INSERT INTO entries VALUES(?,?,?,?)",[row("same",0),row("same",1)])
                db.commit()
            with self.assertRaises(ValueError): health.validate(p)
    def test_invalid_ordinal_fails(self): self.assert_invalid([row("one",2)])
    def test_missing_schema_fails(self):
        with tempfile.TemporaryDirectory(dir=MODULE_PATH.parent) as d:
            p=Path(d)/"catalog.db"
            with closing(sqlite3.connect(p)) as db: db.execute("CREATE TABLE nope(x)")
            with self.assertRaises((ValueError,sqlite3.Error)): health.validate(p)
    def test_broken_sqlite_fails(self):
        with tempfile.TemporaryDirectory(dir=MODULE_PATH.parent) as d:
            p=Path(d)/"catalog.db"; p.write_bytes(b"not a sqlite database")
            with self.assertRaises(sqlite3.Error): health.validate(p)
    def test_current_production_catalog_when_explicitly_available(self):
        value=os.environ.get("DTT_PRODUCTION_CATALOG")
        if not value: self.skipTest("DTT_PRODUCTION_CATALOG not set")
        result=health.validate(Path(value)); self.assertEqual(124895,result["total"])
    def assert_invalid(self, rows):
        with tempfile.TemporaryDirectory(dir=MODULE_PATH.parent) as d:
            p=Path(d)/"catalog.db"; make_catalog(p,rows)
            with self.assertRaises(ValueError): health.validate(p)

if __name__ == "__main__": unittest.main()
