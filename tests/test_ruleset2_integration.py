import argparse
import csv
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.models import CoreTagSet
from danbooru_tag_tool.prompt_session import PromptSession
from danbooru_tag_tool.search import TagSearchEngine
from tools import model_aux_crossmatch


ROOT = Path(__file__).resolve().parents[1]
RULESET2 = ROOT / "data/derived/ruleset2"


@pytest.fixture(scope="module")
def knowledge():
    return TagKnowledgeCore.load(ROOT)


def _core(special_id: str) -> CoreTagSet:
    return CoreTagSet("ruleset2-test", "Ruleset2", (special_id,), "",
                      "2026-09-07T20:05:00+09:00")


def test_ruleset2_authorities_are_loaded_without_mutating_source(knowledge):
    assert len(knowledge.special) == 2788
    assert len(knowledge.ruleset2.alias_semantic) == 778
    assert len(knowledge.ruleset2.alias_statistics) == 778
    assert len(knowledge.semantic_routes) == 336
    assert len(knowledge.ruleset2.migration_rows) == 3076
    assert hashlib.sha256((RULESET2 / "01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv").read_bytes()).hexdigest() == (
        "12f6ccdc5d2dba33123cdfa97a636b2fdd49a519ed89d327d330471696762e02"
    )
    # Historical source bytes remain under the Stage-0 protected manifest.
    assert hashlib.sha256((ROOT / "data/special2788/illustrious_tag_knowledge_base_2788.csv").read_bytes()).hexdigest() == (
        "07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3"
    )
    package = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    assert all((ROOT / relative).is_file()
               for key, relative in package["active_audited_overlay"].items()
               if key != "ruleset")


def test_alias_two_axis_policy_controls_statistics_not_prompt(knowledge):
    allowed = [tag for tag in knowledge.special.values()
               if tag.layer == "Alias" and tag.default_full_semantic_stats_allowed]
    blocked = [tag for tag in knowledge.special.values()
               if tag.layer == "Alias" and not tag.default_full_semantic_stats_allowed]
    assert len(allowed) == 496 and len(blocked) == 282
    assert all(tag.automatic_prompt_replacement == "NEVER" for tag in allowed + blocked)

    blocked_resolved = next(tag for tag in blocked if tag.chosen_canonical)
    session = PromptSession.from_core(_core(blocked_resolved.special_id), knowledge)
    assert session.export_prompt() == blocked_resolved.term.replace("_", " ")
    assert session.statistics_canonicals == ()
    assert session.unresolved_statistics_special_ids == (blocked_resolved.special_id,)

    allowed_resolved = next(tag for tag in allowed if tag.chosen_canonical)
    allowed_session = PromptSession.from_core(_core(allowed_resolved.special_id), knowledge)
    assert allowed_session.statistics_canonicals == (allowed_resolved.chosen_canonical,)


def test_ruleset2_search_gloss_and_semantic_route_remain_separate(knowledge):
    engine = TagSearchEngine(knowledge)
    semantic = next(iter(knowledge.semantic.values()))
    result = engine.search_one(semantic.semantic_term)[0]
    assert result.canonical is None
    assert result.semantic_relations
    relation = result.semantic_relations[0]
    route = knowledge.semantic_routes[semantic.special_id]
    assert relation.semantic_subtype == route.semantic_subtype
    assert relation.anchor_kind == route.anchor_kind
    assert relation.anchor_value == route.anchor_value
    assert relation.default_prompt_mode == route.default_prompt_mode
    assert relation.candidate_canonical is None

    changed = next(tag for tag in knowledge.special.values()
                   if tag.japanese and tag.search_keys and tag.japanese in tag.search_keys)
    assert changed.special_id in knowledge.resolve_exact(changed.japanese).special_ids


def test_model_aux_local_source_rules_and_final_gate(tmp_path):
    terms = model_aux_crossmatch.read_terms(
        RULESET2 / "10_MODEL_AUX_CROSSMATCH_UNIQUE_TERMS_2811.csv"
    )
    special = RULESET2 / "01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv"
    assert model_aux_crossmatch.validate_terms_cover_special(terms, special) == {
        "special_rows": 2788,
        "special_terms_covered": 2788,
        "external_unique_terms": 23,
    }

    term = str(terms.iloc[0].term).replace(" ", "_")
    tags = tmp_path / "tags-2026-09-06.csv.gz"
    aliases = tmp_path / "tag_aliases-2026-09-06.csv.gz"
    pd.DataFrame([{"name": term, "category": 0, "post_count": 10}]).to_csv(
        tags, index=False, compression="gzip"
    )
    pd.DataFrame(columns=["antecedent_name", "consequent_name", "status"]).to_csv(
        aliases, index=False, compression="gzip"
    )
    result, _ = model_aux_crossmatch.crossmatch_e621_raw(terms, tags, aliases)
    assert len(result) == 2811
    assert result.recommended_noob_eps_form.fillna("").eq("").all()
    assert result.recommended_noob_vpred_form.fillna("").eq("").all()

    sha = model_aux_crossmatch.sha256
    args = argparse.Namespace(
        final_audit=True,
        e621_autocomplete=None,
        e621_tags=tags,
        e621_aliases=aliases,
        gelbooru=tmp_path / "gelbooru.parquet",
        allow_e621_date_mismatch=False,
        allow_unpinned_gelbooru=False,
        skip_gelbooru_row_check=False,
        e621_tags_source_url="https://e621.net/db_export/",
        e621_aliases_source_url="https://e621.net/db_export/",
        e621_tags_published_sha256=sha(tags),
        e621_aliases_published_sha256=sha(aliases),
    )
    model_aux_crossmatch.validate_final_audit_args(args)
    with pytest.raises(ValueError, match="missing provenance"):
        model_aux_crossmatch.validate_final_audit_args(
            argparse.Namespace(**(vars(args) | {"e621_tags_published_sha256": ""}))
        )


def test_model_aux_runtime_code_has_no_network_client():
    text = (ROOT / "tools/model_aux_crossmatch.py").read_text(encoding="utf-8")
    assert not any(token in text for token in ("requests.", "urllib.request", "httpx.", "aiohttp."))
    with (RULESET2 / "24_MODEL_AUX_SOURCE_POLICY_MATRIX.csv").open(
        encoding="utf-8-sig", newline=""
    ) as stream:
        assert len(tuple(csv.DictReader(stream))) == 4
