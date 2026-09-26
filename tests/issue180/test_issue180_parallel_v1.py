import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts/issue180/build_parallel_assignment_v1.py"
spec=importlib.util.spec_from_file_location("issue180_parallel",SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class Issue180ParallelTests(unittest.TestCase):
    def test_owner_slot_is_stable(self):
        self.assertEqual(mod.owner_slot("family:pokemon",4),mod.owner_slot("family:pokemon",4))
        self.assertIn(mod.owner_slot("family:pokemon",4),range(4))

    def test_direct_ungrouped_is_split_by_character(self):
        cfg=json.loads((ROOT/"docs/issue180/parallel/PARALLEL_EXECUTION_V1.json").read_text(encoding="utf-8"))
        tags=["alpha","beta","gamma"]
        unit={"unit_id":"ru3-test","status":"OPEN","subject":"__UNGROUPED__","unit_type":"DIRECT_AUTHORITY",
              "priority":"P3","member_ids/tags":json.dumps(tags)}
        closure={"unit_id":"ru3-test","member_ids_sha256":mod.member_hash(tags),
                 "work_bucket":"DIRECT_AUTHORITY_RESEARCH"}
        rows=mod.build_assignments([unit],[closure],cfg,"a"*40)
        self.assertEqual(len(rows),3)
        self.assertEqual({r["ownership_key"] for r in rows},{"direct:alpha","direct:beta","direct:gamma"})

    def test_qa_bucket_is_not_forward_sharded(self):
        cfg=json.loads((ROOT/"docs/issue180/parallel/PARALLEL_EXECUTION_V1.json").read_text(encoding="utf-8"))
        tags=["x"]
        unit={"unit_id":"ru3-q","status":"OPEN","subject":"family:q","unit_type":"FAMILY_AUTHORITY",
              "priority":"P3","member_ids/tags":json.dumps(tags)}
        closure={"unit_id":"ru3-q","member_ids_sha256":mod.member_hash(tags),"work_bucket":"CONFLICT_REVIEW"}
        row=mod.build_assignments([unit],[closure],cfg,"b"*40)[0]
        self.assertEqual(row["owner_role"],"QA")
        self.assertEqual(row["owner_branch"],cfg["qa_branch"])

if __name__=="__main__":
    unittest.main()
