#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/issue132"))

from codex_runtime_guards import (  # noqa: E402
    allowed_forward_end,
    effective_start,
    load_authority_and_qa,
    policy_trace_required,
    validate_policy_trace,
)
from materialize_write_requests import (  # noqa: E402
    load_vocab,
    materialize_request,
    read_neutral,
)


class CodexRuntimeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authority, cls.qa, cls.errors = load_authority_and_qa(ROOT)

    def test_authority_and_policy_files_match(self):
        self.assertEqual(self.errors, [])

    def test_effective_boundaries(self):
        self.assertEqual(effective_start(self.authority, 1), 1126)
        self.assertEqual(effective_start(self.authority, 2), 1226)
        self.assertEqual(effective_start(self.authority, 3), 1201)
        self.assertFalse(policy_trace_required(self.authority, 1, 1101, 1125))
        self.assertTrue(policy_trace_required(self.authority, 1, 1126, 1150))
        with self.assertRaises(ValueError):
            policy_trace_required(self.authority, 1, 1125, 1149)

    def test_qa_watermarks(self):
        self.assertEqual(allowed_forward_end(self.qa, 1), 1225)
        self.assertEqual(allowed_forward_end(self.qa, 2), 1325)
        self.assertEqual(allowed_forward_end(self.qa, 3), 1300)

    def test_valid_policy_trace(self):
        guard = self.authority["contracts"]["semantic_guardrails"]
        policy_id = guard["current_policy_id"]
        policy_blob = guard["allowed_policies"][policy_id]["git_blob_sha"]
        obj = {
            "semantic_policy_id": policy_id,
            "semantic_policy_git_blob_sha": policy_blob,
            "decision_reason_codes": {
                "1126": ["OTHER_DIRECT_VISUAL"],
                "1127": ["CLOTHING_STATE"],
            },
        }
        self.assertEqual(
            validate_policy_trace(obj, self.authority, 1, 1126, 1127, {1126, 1127}),
            [],
        )


    def _request(self, lane: int, index: int, schema: str) -> dict:
        neutral = read_neutral(ROOT / "docs/issue132/parallel/input/luna_neutral_review_input_v2.csv")
        assigned = [
            row for row in neutral
            if ((int(row["review_seq"]) - 1) % 3) + 1 == lane
        ]
        row = assigned[index - 1]
        request = {
            "schema_version": schema,
            "lane": lane,
            "lane_local_start": index,
            "lane_local_end": index,
            "parent_neutral_sha256": self.authority["fixed"]["parent_neutral_sha256"],
            "parent_identity_order_sha256": self.authority["fixed"]["parent_identity_order_sha256"],
            "rows": [{
                "lane_local_index": index,
                "review_seq": int(row["review_seq"]),
                "discovery_mode": "SEARCH_ORIENTED",
                "routes": [],
                "local_refinement_ids": [],
                "body_site_ids": [],
                "theme_ids": [],
                "route_vocabulary_gap": "NO",
                "review_depth": "CHECKED",
                "evidence_urls": [],
            }],
            "holds": [],
        }
        if schema == "issue132-pass-a-write-request-v2":
            guard = self.authority["contracts"]["semantic_guardrails"]
            policy_id = guard["current_policy_id"]
            request["semantic_policy_id"] = policy_id
            request["semantic_policy_git_blob_sha"] = guard["allowed_policies"][policy_id]["git_blob_sha"]
            request["decision_reason_codes"] = {str(index): ["SEARCH_BY_NAME_ONLY"]}
        return request

    def test_v2_request_materializes_with_policy_trace(self):
        neutral = read_neutral(ROOT / "docs/issue132/parallel/input/luna_neutral_review_input_v2.csv")
        vocab = load_vocab(ROOT / "docs/issue132/parallel/pass_a_contract_manifest_v1.json")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request_path = root / "request_001126_001126.json"
            request_path.write_text(
                json.dumps(self._request(1, 1126, "issue132-pass-a-write-request-v2")),
                encoding="utf-8",
            )
            out_path, created = materialize_request(
                request_path, neutral, vocab, root, self.authority, self.qa
            )
            self.assertTrue(created)
            output = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(
                output["semantic_policy_id"],
                self.authority["contracts"]["semantic_guardrails"]["current_policy_id"],
            )
            self.assertEqual(output["decision_reason_codes"]["1126"], ["SEARCH_BY_NAME_ONLY"])

    def test_v1_request_rejected_after_policy_boundary(self):
        neutral = read_neutral(ROOT / "docs/issue132/parallel/input/luna_neutral_review_input_v2.csv")
        vocab = load_vocab(ROOT / "docs/issue132/parallel/pass_a_contract_manifest_v1.json")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request_path = root / "request_001126_001126.json"
            request_path.write_text(
                json.dumps(self._request(1, 1126, "issue132-pass-a-write-request-v1")),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "requires write-request v2"):
                materialize_request(
                    request_path, neutral, vocab, root, self.authority, self.qa
                )

    def test_request_rejected_beyond_qa_watermark(self):
        neutral = read_neutral(ROOT / "docs/issue132/parallel/input/luna_neutral_review_input_v2.csv")
        vocab = load_vocab(ROOT / "docs/issue132/parallel/pass_a_contract_manifest_v1.json")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request_path = root / "request_001226_001226.json"
            request_path.write_text(
                json.dumps(self._request(1, 1226, "issue132-pass-a-write-request-v2")),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "exceeds ChatGPT QA watermark"):
                materialize_request(
                    request_path, neutral, vocab, root, self.authority, self.qa
                )

    def test_invalid_reason_code_rejected(self):
        guard = self.authority["contracts"]["semantic_guardrails"]
        policy_id = guard["current_policy_id"]
        policy_blob = guard["allowed_policies"][policy_id]["git_blob_sha"]
        obj = {
            "semantic_policy_id": policy_id,
            "semantic_policy_git_blob_sha": policy_blob,
            "decision_reason_codes": {"1126": ["NOT_A_REAL_CODE"]},
        }
        errors = validate_policy_trace(obj, self.authority, 1, 1126, 1126, {1126})
        self.assertTrue(any("invalid codes" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
