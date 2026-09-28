import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/issue180/claim_codex_role_v2.py"
spec = importlib.util.spec_from_file_location("issue180_role_claim_v2", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class Issue180RoleClaimV2Tests(unittest.TestCase):
    def test_exact_five_unique_roles(self):
        self.assertEqual(len(mod.ROLE_SPECS), 5)
        self.assertEqual(
            [r.role for r in mod.ROLE_SPECS],
            ["FORWARD_0", "FORWARD_1", "FORWARD_2", "FORWARD_3", "QA"],
        )
        self.assertEqual(len({r.target_branch for r in mod.ROLE_SPECS}), 5)
        self.assertEqual(len({r.claim_branch for r in mod.ROLE_SPECS}), 5)

    def test_claim_refs_do_not_match_forward_workflow_pattern(self):
        self.assertTrue(all("issue180-claim-" in r.claim_branch for r in mod.ROLE_SPECS))
        self.assertTrue(all(not r.claim_branch.startswith("research/issue180-forward-") for r in mod.ROLE_SPECS))

if __name__ == "__main__":
    unittest.main()
