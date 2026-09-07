"""Deterministic Stage 7A acceptance scenarios over the production UI adapters."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.search import TagSearchEngine
from danbooru_tag_tool.stage7a_presenter import SpecialSearchPresenter
from danbooru_tag_tool.stage7a_session import Stage7ASession
from danbooru_tag_tool.stage7a_warnings import Stage7AWarningPresenter


OUTPUT = ROOT / "benchmarks/stage7a/ui_smoke.json"


def main():
    knowledge = TagKnowledgeCore.load(ROOT)
    profiles = knowledge.load_generation_profile_store(ROOT)
    presenter = SpecialSearchPresenter(knowledge, TagSearchEngine(knowledge), profiles)
    warnings = Stage7AWarningPresenter(knowledge, profiles)

    def state():
        return Stage7ASession(knowledge, warnings)

    restraint = presenter.search("拘束")
    restraint_state = state()
    restraint_state.add_special(restraint.special[0].special_id)

    cross_section = presenter.search("断面")
    cross_card = next(item for item in cross_section.special if item.special_id == "2003")
    cross_state = state()
    cross_state.add_special(cross_card.special_id)

    machine = presenter.search("機械")
    machine_state = state()
    machine_state.add_special(machine.special[0].special_id)

    semantic = next(item for item in knowledge.special.values()
                    if item.match_type == "semantic_unmapped")
    semantic_card = next(item for item in presenter.search(semantic.term).special
                         if item.special_id == semantic.special_id)
    semantic_state = state()
    semantic_state.add_special(semantic_card.special_id)

    alias = next(item for item in knowledge.special.values() if item.layer == "Alias")
    alias_card = next(item for item in presenter.search(alias.term).special
                      if item.special_id == alias.special_id)
    alias_state = state()
    alias_state.add_special(alias_card.special_id)

    general = presenter.search("青い空")
    general_card = next(item for item in general.general if item.canonical == "blue_sky")
    general_state = state()
    general_state.add_auxiliary(general_card.canonical)

    document = {
        "format_version": 1,
        "runtime_external_calls": 0,
        "recommendation_engine_connected": False,
        "representative_click_count": {
            "search_input_excluded": True,
            "special_add": 1,
            "prompt_copy_after_add": 1,
            "total_after_search_input": 2,
        },
        "scenarios": {
            "restraint": {
                "query": "拘束",
                "special_result_count": len(restraint.special),
                "selected_special_id": restraint_state.selected_special_ids[0],
                "prompt": restraint_state.prompt_preview,
                "clipboard_equals_preview": restraint_state.clipboard_text == restraint_state.prompt_preview,
            },
            "cross_section": {
                "query": "断面",
                "selected_special_id": cross_card.special_id,
                "prompt": cross_state.prompt_preview,
                "warning_codes": [notice.code for notice in cross_state.warnings],
            },
            "machine": {
                "query": "機械",
                "special_result_count": len(machine.special),
                "selected_special_id": machine_state.selected_special_ids[0],
                "prompt": machine_state.prompt_preview,
            },
            "semantic_unmapped": {
                "selected_special_id": semantic_card.special_id,
                "matched_canonical": semantic_card.matched_canonical,
                "prompt": semantic_state.prompt_preview,
                "warning_codes": [notice.code for notice in semantic_state.warnings],
            },
            "alias": {
                "selected_special_id": alias_card.special_id,
                "original_term": alias.term,
                "prompt": alias_state.prompt_preview,
            },
            "general_japanese": {
                "query": "青い空",
                "selected_auxiliary": general_state.manual_auxiliary_canonicals[0],
                "selected_special_ids": list(general_state.selected_special_ids),
                "prompt": general_state.prompt_preview,
            },
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(json.dumps(document, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

