from __future__ import annotations

import unittest

from scripts.issue216.harvest_danbooru_wiki_membership import canonical_source_url

try:
    from integrate_danbooru_wiki_membership_harvest import retain_or_register_source
except ModuleNotFoundError:
    from scripts.issue216.integrate_danbooru_wiki_membership_harvest import retain_or_register_source


class WikiHarvestIntegrationTests(unittest.TestCase):
    def test_source_url_normalization_is_stable_for_repeat_fetch_filter(self):
        self.assertEqual(
            canonical_source_url("HTTPS://Danbooru.Donmai.US/wiki_pages/foo///"),
            "https://danbooru.donmai.us/wiki_pages/foo",
        )

    def test_repeat_harvest_preserves_enriched_accepted_source_record(self):
        sid = "src-example"
        prior = {
            "source_id": sid,
            "copyright_canonical": "project_moon",
            "source_url": "https://example.test/list",
            "source_type": "ACCEPTED_CURATED_ROSTER",
            "authority_owner": "Danbooru Copyright wiki explicit Character/Member lists",
            "source_status": "ACCEPTED",
            "source_scope": "explicit Characters section",
            "exact_roster_available": "true",
            "reusable": "true",
            "source_claim": "Extended exact member claim",
            "provenance": "Prior reviewed provenance",
        }
        regenerated = {**prior, "source_claim": "Initial harvest claim", "provenance": "Initial harvest"}
        registry = {sid: dict(prior)}
        new_sources: set[str] = set()

        retain_or_register_source(registry, regenerated, new_sources)

        self.assertEqual(registry[sid], prior)
        self.assertEqual(new_sources, set())

    def test_repeat_harvest_rejects_scope_or_root_drift(self):
        source = {
            "source_id": "src-example",
            "copyright_canonical": "project_moon",
            "source_url": "https://example.test/list",
            "source_type": "ACCEPTED_CURATED_ROSTER",
            "authority_owner": "Danbooru Copyright wiki explicit Character/Member lists",
            "source_status": "ACCEPTED",
            "source_scope": "explicit Characters section",
            "exact_roster_available": "true",
            "reusable": "true",
        }
        prior = dict(source, copyright_canonical="sonic_(series)")
        with self.assertRaisesRegex(ValueError, "deterministic source identity collision"):
            retain_or_register_source({source["source_id"]: prior}, source, set())

    def test_new_exact_scope_is_registered(self):
        source = {"source_id": "src-new", "source_scope": "new exact scope"}
        registry: dict[str, dict[str, str]] = {}
        new_sources: set[str] = set()

        retain_or_register_source(registry, source, new_sources)

        self.assertEqual(registry["src-new"], source)
        self.assertEqual(new_sources, {"src-new"})


if __name__ == "__main__":
    unittest.main()
