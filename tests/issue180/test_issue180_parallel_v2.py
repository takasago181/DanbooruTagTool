import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts/issue180/build_parallel_campaigns_v2.py"
spec=importlib.util.spec_from_file_location("issue180_parallel_v2",SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class Issue180ParallelV2Tests(unittest.TestCase):
    def cfg(self):
        return json.loads((ROOT/"docs/issue180/parallel/PARALLEL_EXECUTION_V2.json").read_text(encoding="utf-8"))

    def test_owner_slot_stable_by_authority_key(self):
        self.assertEqual(mod.owner_slot("authority:pokemon",4),mod.owner_slot("authority:pokemon",4))
        self.assertIn(mod.owner_slot("authority:pokemon",4),range(4))

    def test_same_family_authority_is_one_campaign(self):
        cfg=self.cfg()
        units=[
            {"unit_id":"ru3-a","status":"OPEN","subject":"family:work_x","unit_type":"FAMILY_AUTHORITY","priority":"P2","member_ids/tags":json.dumps(["a","b"])},
            {"unit_id":"ru3-b","status":"OPEN","subject":"family:work_x","unit_type":"ROSTER_MEMBERSHIP","priority":"P2","member_ids/tags":json.dumps(["c"])},
        ]
        closures=[
            {"unit_id":"ru3-a","member_ids_sha256":mod.member_hash(["a","b"]),"work_bucket":"FAMILY_ROSTER_HIGH_YIELD"},
            {"unit_id":"ru3-b","member_ids_sha256":mod.member_hash(["c"]),"work_bucket":"FAMILY_ROSTER_HIGH_YIELD"},
        ]
        rows=mod.build_campaigns(units,closures,cfg)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["campaign_key"],"authority:work_x")
        self.assertEqual(rows[0]["member_count"],"3")

    def test_family_and_discovery_hint_share_authority_namespace(self):
        cfg=self.cfg()
        units=[
            {"unit_id":"ru3-f","status":"OPEN","subject":"family:work_z","unit_type":"FAMILY_AUTHORITY","priority":"P2","member_ids/tags":json.dumps(["a"])},
            {"unit_id":"ru3-rz","status":"OPEN","subject":"discovery-hint:work_z","unit_type":"DIRECT_AUTHORITY","priority":"P2","member_ids/tags":json.dumps(["b"])},
        ]
        closures=[
            {"unit_id":"ru3-f","member_ids_sha256":mod.member_hash(["a"]),"work_bucket":"FAMILY_ROSTER_HIGH_YIELD"},
            {"unit_id":"ru3-rz","member_ids_sha256":mod.member_hash(["b"]),"work_bucket":"DIRECT_AUTHORITY_RESEARCH"},
        ]
        rows=mod.build_campaigns(units,closures,cfg)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["campaign_key"],"authority:work_z")

    def test_structure_free_direct_falls_back_per_character(self):
        cfg=self.cfg()
        tags=["alpha","beta","gamma"]
        unit={"unit_id":"ru3-d","status":"OPEN","subject":"__UNGROUPED__","unit_type":"DIRECT_AUTHORITY","priority":"P3","member_ids/tags":json.dumps(tags)}
        closure={"unit_id":"ru3-d","member_ids_sha256":mod.member_hash(tags),"work_bucket":"DIRECT_AUTHORITY_RESEARCH"}
        rows=mod.build_campaigns([unit],[closure],cfg)
        self.assertEqual({r["campaign_key"] for r in rows},{"direct:alpha","direct:beta","direct:gamma"})

    def test_direct_campaign_fingerprint_survives_sibling_resolution(self):
        cfg=self.cfg()
        unit1={"unit_id":"ru3-d3","status":"OPEN","subject":"__UNGROUPED__","unit_type":"DIRECT_AUTHORITY","priority":"P3","member_ids/tags":json.dumps(["alpha","beta"])}
        closure1={"unit_id":"ru3-d3","member_ids_sha256":mod.member_hash(["alpha","beta"]),"work_bucket":"DIRECT_AUTHORITY_RESEARCH"}
        first=mod.build_campaigns([unit1],[closure1],cfg)
        alpha1=next(r for r in first if r["campaign_key"]=="direct:alpha")
        unit2={"unit_id":"ru3-d4","status":"OPEN","subject":"__UNGROUPED__","unit_type":"DIRECT_AUTHORITY","priority":"P3","member_ids/tags":json.dumps(["alpha"])}
        closure2={"unit_id":"ru3-d4","member_ids_sha256":mod.member_hash(["alpha"]),"work_bucket":"DIRECT_AUTHORITY_RESEARCH"}
        alpha2=mod.build_campaigns([unit2],[closure2],cfg)[0]
        self.assertEqual(alpha1["campaign_fingerprint"],alpha2["campaign_fingerprint"])

    def test_accepted_outcome_suppresses_exact_campaign(self):
        cfg=self.cfg()
        unit={"unit_id":"ru3-o","status":"OPEN","subject":"__UNGROUPED__","unit_type":"DIRECT_AUTHORITY","priority":"P3","member_ids/tags":json.dumps(["omega"])}
        closure={"unit_id":"ru3-o","member_ids_sha256":mod.member_hash(["omega"]),"work_bucket":"DIRECT_AUTHORITY_RESEARCH"}
        first=mod.build_campaigns([unit],[closure],cfg)
        pair={(first[0]["campaign_key"],first[0]["campaign_fingerprint"])}
        second=mod.build_campaigns([unit],[closure],cfg,pair)
        self.assertEqual(second[0]["research_state"],"EXHAUSTED_REVIEWED")

    def test_accepted_progress_keeps_campaign_open_but_marked(self):
        cfg=self.cfg()
        unit={"unit_id":"ru3-p","status":"OPEN","subject":"__UNGROUPED__","unit_type":"DIRECT_AUTHORITY","priority":"P3","member_ids/tags":json.dumps(["progress"])}
        closure={"unit_id":"ru3-p","member_ids_sha256":mod.member_hash(["progress"]),"work_bucket":"DIRECT_AUTHORITY_RESEARCH"}
        first=mod.build_campaigns([unit],[closure],cfg)
        pair={(first[0]["campaign_key"],first[0]["campaign_fingerprint"])}
        second=mod.build_campaigns([unit],[closure],cfg,set(),pair)
        self.assertEqual(second[0]["research_state"],"OPEN_WITH_PROGRESS")

    def test_all_exhausted_campaigns_make_only_accounting_terminal_candidate(self):
        cfg=self.cfg()
        unit={"unit_id":"ru3-t","status":"OPEN","subject":"__UNGROUPED__","unit_type":"DIRECT_AUTHORITY","priority":"P3","member_ids/tags":json.dumps(["a","b"])}
        closure={"unit_id":"ru3-t","member_ids_sha256":mod.member_hash(["a","b"]),"work_bucket":"DIRECT_AUTHORITY_RESEARCH"}
        first=mod.build_campaigns([unit],[closure],cfg)
        accepted={(r["campaign_key"],r["campaign_fingerprint"]) for r in first}
        rows=mod.build_campaigns([unit],[closure],cfg,accepted)
        terminal=mod.build_terminal_candidates(rows,[unit],[closure],cfg)
        self.assertEqual(terminal[0]["all_campaigns_exhausted"],"YES")

    def test_qa_bucket_remains_qa_owned(self):
        cfg=self.cfg()
        unit={"unit_id":"ru3-q","status":"OPEN","subject":"family:q","unit_type":"FAMILY_AUTHORITY","priority":"P3","member_ids/tags":json.dumps(["x"])}
        closure={"unit_id":"ru3-q","member_ids_sha256":mod.member_hash(["x"]),"work_bucket":"CONFLICT_REVIEW"}
        row=mod.build_campaigns([unit],[closure],cfg)[0]
        self.assertEqual(row["owner_role"],"QA")
        self.assertEqual(row["owner_branch"],cfg["qa_branch"])

if __name__=="__main__":
    unittest.main()
