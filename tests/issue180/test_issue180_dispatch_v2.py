import csv
import importlib.util
import io
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts/issue180/refresh_dispatch_snapshot_v2.py"
spec=importlib.util.spec_from_file_location("issue180_dispatch_v2",SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class Issue180DispatchV2Tests(unittest.TestCase):
    def campaigns(self):
        return [
            {
                "queue_id":"q2-x","campaign_id":"pc2-a","owner_role":"FORWARD","owner_slot":"0",
                "owner_branch":"research/issue180-forward-0","campaign_key":"authority:work_x",
                "campaign_fingerprint":"a"*64,"research_state":"OPEN",
                "work_buckets":json.dumps(["FAMILY_ROSTER_HIGH_YIELD"]),
                "source_units":"[]","member_count":"2","member_ids/tags":json.dumps(["a","b"]),"priority":"P1",
            },
            {
                "queue_id":"q2-x","campaign_id":"pc2-q","owner_role":"QA","owner_slot":"",
                "owner_branch":"research/issue180-qa-integrator","campaign_key":"qa:CONFLICT_REVIEW:ru3-x",
                "campaign_fingerprint":"b"*64,"research_state":"QA_OWNED",
                "work_buckets":json.dumps(["CONFLICT_REVIEW"]),
                "source_units":"[]","member_count":"1","member_ids/tags":json.dumps(["z"]),"priority":"P1",
            },
        ]

    def sources(self):
        return [{
            "source_review_id":"src1","source_url":"https://example.invalid/roster",
            "authority_type":"OFFICIAL_ROSTER","proved_scope":"named roster","home_root":"work_x",
            "campaign_keys":json.dumps(["authority:work_x"]),"mapping_rule":"exact named member -> direct home",
            "review_status":"ACCEPTED","reviewed_on":"2026-09-26","last_verified_commit":"deadbeef","notes":"",
        }]

    def test_dispatch_excludes_qa_and_embeds_source_hint(self):
        rows=mod.build_rows(self.campaigns(),self.sources(),[])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["campaign_key"],"authority:work_x")
        self.assertEqual(json.loads(rows[0]["source_hint_urls"]),["https://example.invalid/roster"])

    def test_progress_routes_are_carried_forward(self):
        campaigns=self.campaigns()
        campaigns[0]["research_state"]="OPEN_WITH_PROGRESS"
        qa=[{
            "campaign_key":"authority:work_x","campaign_fingerprint":"a"*64,
            "decision":"ACCEPT_PROGRESS",
            "research_routes_json":json.dumps([{"route_type":"OFFICIAL_ROSTER","url_or_query":"https://old.example/","result":"no exact match"}]),
        }]
        rows=mod.build_rows(campaigns,self.sources(),qa)
        self.assertEqual(rows[0]["research_state"],"OPEN_WITH_PROGRESS")
        routes=json.loads(rows[0]["prior_checked_routes"])
        self.assertEqual(routes[0]["url_or_query"],"https://old.example/")

    def test_lane_files_only_contain_owned_slot(self):
        rows=mod.build_rows(self.campaigns(),self.sources(),[])
        files=mod.expected_files(rows, packet_limit=200)
        parsed=list(csv.DictReader(io.StringIO(files["fwd-0.csv"])))
        self.assertEqual(len(parsed),1)
        self.assertEqual(parsed[0]["owner_slot"],"0")
        parsed1=list(csv.DictReader(io.StringIO(files["fwd-1.csv"])))
        self.assertEqual(parsed1,[])

    def test_packet_limit_caps_lane_context(self):
        campaigns=[]
        for i in range(5):
            campaigns.append({
                "queue_id":"q2-x","campaign_id":f"pc2-{i}","owner_role":"FORWARD","owner_slot":"0",
                "owner_branch":"research/issue180-forward-0","campaign_key":f"direct:tag{i}",
                "campaign_fingerprint":str(i)*64,"research_state":"OPEN","work_buckets":"[]",
                "source_units":"[]","member_count":"1","member_ids/tags":json.dumps([f"tag{i}"]),"priority":"P3",
            })
        rows=mod.build_rows(campaigns,[],[])
        files=mod.expected_files(rows,packet_limit=2)
        parsed=list(csv.DictReader(io.StringIO(files["fwd-0.csv"])))
        self.assertEqual(len(parsed),2)
        summary=json.loads(files["DISPATCH_SUMMARY_V2.json"])
        self.assertEqual(summary["lanes"]["0"]["open_campaigns"],5)
        self.assertEqual(summary["lanes"]["0"]["dispatched_open_campaigns"],2)

if __name__=="__main__":
    unittest.main()
