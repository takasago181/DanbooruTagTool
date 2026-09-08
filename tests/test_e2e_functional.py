"""Real local data -> production Tk callbacks -> Composer -> actual clipboard.

No fake engine, fake session, mocked widgets, network or image-generation calls.
On Linux run under an existing display or xvfb-run. Missing prerequisites skip
the pytest cases but the --e2e-report gate converts that outcome to BLOCKED.
"""
from dataclasses import asdict, replace
from pathlib import Path
import time
import pytest

tk = pytest.importorskip("tkinter", reason="BLOCKED: Tk is not installed")
from tkinter import ttk

from danbooru_tag_tool.ui import Stage7AApp
from danbooru_tag_tool.prompt_composer import ComposerInput, ComposerProfile
from danbooru_tag_tool.stage9c_session import ComposerVariant, WeightVariant
from danbooru_tag_tool.runtime_index import RuntimeIndex
from danbooru_tag_tool.canonical_overlay import CanonicalOverlay

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def tk_window():
    try:
        window = tk.Tk()
    except tk.TclError as exc:
        pytest.skip("BLOCKED: Tk display unavailable: " + str(exc))
    window.withdraw()
    yield window
    window.destroy()


@pytest.fixture
def app(record_property, tk_window):
    for relative in (
        "data/source/danbooru-2026-09-02.csv", "data/runtime_index/index_metadata.json",
        "data/special2788/illustrious_tag_knowledge_base_2788.csv",
        "data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv",
        "data/derived/special2788_VERIFIED_LINKAGE.csv",
        "data/derived/ruleset2/RULESET2_MANIFEST.json",
        "data/derived/ruleset2/01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv",
        "data/derived/ruleset2/37_ALIAS_SEMANTIC_RELATIONSHIP_v3.0.csv",
        "data/derived/ruleset2/38_ALIAS_STATISTICS_POLICY_v3.0.csv",
        "data/derived/ruleset2/06_SEMANTIC336_ROUTING_OVERLAY.csv",
        "data/derived/ruleset2/31_METADATA_RULESET2_MIGRATIONS_v3.0.csv",
    ):
        if not (ROOT / relative).is_file():
            pytest.skip("BLOCKED: required local protected data missing: " + relative)
    try:
        index_path = ROOT / "data/runtime_index"
        index = RuntimeIndex(index_path)
        CanonicalOverlay(index, index_path / "canonical_overlay.json")
    except (FileNotFoundError, ValueError) as exc:
        pytest.skip("BLOCKED: required statistics environment: " + str(exc))
    window = tk_window
    callback_errors = []
    window.report_callback_exception = lambda kind, value, tb: callback_errors.append(str(value))
    application = None
    try:
        application = Stage7AApp(window, root_path=ROOT)
        assert application.recommendation_controller.engine is not None, "Production index startup failed after preflight"
        record_property("tk", window.tk.call("info", "patchlevel"))
        record_property("snapshot_id", application.statistics_snapshot_id)
        yield application
        assert not callback_errors, callback_errors
    finally:
        if application is not None:
            application.close()
        # The production app normally owns its entire root. This test reuses
        # one Tcl interpreter, so remove the old app's root binding as well.
        window.unbind("<Configure>")
        for callback in window.tk.call("after", "info"):
            (application or window).after_cancel(callback)
        if application is not None:
            application.destroy()


def pump(app, condition, timeout=30):
    deadline = time.monotonic() + timeout
    while not condition() and time.monotonic() < deadline:
        app.update()
        time.sleep(.01)
    assert condition(), "Production Tk/worker path timed out"


def select_core(app):
    app.search_var.set("blindfold")
    app._on_search_key()
    pump(app, lambda: bool(app.special_rows))
    index = next(i for i, row in enumerate(app.special_rows) if row.special_id == "1816")
    app.special_list.selection_set(index)
    # Bound selection callback, real Listbox selection and production debounce.
    app._add_clicked_special()
    assert app.session.selected_special_ids == ("1816",)
    assert app.session.statistics_core_canonicals() == ("blindfold",)
    pump(app, lambda: app.recommendation_result.request_id == app.active_recommendation_request
         and app.recommendation_result.status == "ready")
    assert app.recommendation_result.common and app.recommendation_result.rare
    return app.recommendation_result


def assert_output(app):
    result = app.session.compose_result
    assert result.positive_prompt
    assert app.prompt_text.get("1.0", "end-1c") == result.positive_prompt
    assert ", ".join(a.text for a in result.plan.selected_atoms) == result.positive_prompt
    assert set(result.provenance_map) == {a.text for a in result.plan.selected_atoms}
    assert any("1816" in a.special_owners for a in result.plan.selected_atoms)
    return result


def test_real_tk_search_candidates_and_output(app, record_property):
    result = select_core(app)
    session = app.session
    initial = session.compose_result
    record_property("bucket_counts", {"common": len(result.common), "rare": len(result.rare)})
    all_rows = {c.canonical: c for c in (*result.common, *result.rare)}
    atoms = initial.plan.candidate_atoms
    for canonical in all_rows:
        lanes = {lane for a in atoms if a.canonical == canonical for lane in a.source_lanes}
        assert {"SEMANTIC_AUX", "COOCCURRENCE"} <= lanes
        assert session.selection_state.decision_for("cooccurrence:" + canonical) is None
    selected = []
    for tab, frame, candidates in (
        (app.common_recommendation_tab, app.common_recommendations, result.common),
        (app.rare_recommendation_tab, app.rare_recommendations, result.rare),
    ):
        app.recommendation_notebook.select(tab)
        app.update_idletasks()
        index = next(i for i, c in enumerate(candidates) if c.canonical not in selected)
        buttons = [w for w in frame.winfo_children() if isinstance(w, ttk.Button)]
        buttons[index].invoke()
        canonical = candidates[index].canonical
        selected.append(canonical)
        assert canonical in session.manual_auxiliary_canonicals
        assert session.selection_state.decision_for("cooccurrence:" + canonical).state == "INCLUDE"
        rendered = next(a for a in session.compose_result.plan.selected_atoms if a.canonical == canonical)
        assert {"USER_EXPLICIT", "COOCCURRENCE"} <= set(rendered.source_lanes)
        expected = asdict(all_rows[canonical])
        for key in ("base_count", "co_count", "conditional_rate", "runtime_global_count",
                    "global_rate", "raw_lift", "wilson_lower_bound", "shrunk_lift"):
            assert (key, expected[key]) in rendered.evidence
        assert ("snapshot_id", app.statistics_snapshot_id) in rendered.evidence
    # Remove via the actual chip's Tk command, then reorder/re-register buckets.
    chip = app.auxiliary_frame.winfo_children()[0]
    next(w for w in chip.winfo_children() if isinstance(w, ttk.Button)).invoke()
    assert session.selection_state.decision_for("cooccurrence:" + selected[0]).state == "EXCLUDE"
    reordered = replace(result, common=tuple(reversed(result.common)), rare=tuple(reversed(result.rare)))
    app._show_recommendation_result(reordered)
    assert session.selection_state.decision_for("cooccurrence:" + selected[0]).state == "EXCLUDE"
    assert session.selection_state.decision_for("cooccurrence:" + selected[1]).state == "INCLUDE"
    default = next(c for c in all_rows if c not in selected)
    assert session.selection_state.decision_for("cooccurrence:" + default) is None
    for canonical in (selected[0], default):
        atom = next(a for a in session.compose_result.plan.candidate_atoms
                    if a.atom_id == "input:cooccurrence:" + canonical)
        assert not atom.selected
    session.choose_candidate("semantic_aux:" + default, "INCLUDE")
    app._show_recommendation_result(reordered)
    atom = next(a for a in session.compose_result.plan.selected_atoms if a.canonical == default)
    assert "SEMANTIC_AUX" in atom.source_lanes and atom.provenance and atom.evidence
    assert session.selection_state.decision_for("cooccurrence:" + default) is None
    # Independent manual addition/removal via real search and selection paths.
    app.search_var.set("blue_sky")
    app._run_search()
    index = next(i for i, row in enumerate(app.general_rows) if row.canonical == "blue_sky")
    app.general_list.selection_set(index)
    app._add_clicked_general()
    assert "blue_sky" in session.manual_auxiliary_canonicals
    app._remove_auxiliary("blue_sky")
    assert "blue_sky" not in session.manual_auxiliary_canonicals
    output = assert_output(app)
    # Preserve text clipboard where possible; binary clipboard is not read.
    try:
        previous = app.clipboard_get()
    except tk.TclError:
        previous = None
    try:
        app.copy_button.invoke()
        assert app.clipboard_get() == output.positive_prompt == session.clipboard_text
    finally:
        app.clipboard_clear()
        if previous is not None:
            app.clipboard_append(previous)
    record_property("output", asdict(output))
    record_property("selection", asdict(session.selection_state))


def test_real_tk_variant_restoration(app, record_property):
    select_core(app)
    session = app.session
    session.add_auxiliary("blue_sky")
    app._refresh_state()
    baseline = session.comparison_snapshot()
    for family in ("NOOBAI", "WAI_ILLUSTRIOUS", "ILLUSTRIOUS", "ANIMA"):
        for count in (0, 1, 2):
            variant = ComposerVariant(
                f"e2e-{family}-{count}", ComposerProfile("e2e", family, special_slot_position=9),
                (("frontend", "withdrawn-tk"), ("runtime", "local-e2e")),
                broad_generic_support=(ComposerInput("broad:solo", canonical="solo"),
                                       ComposerInput("broad:smile", canonical="smile")),
                broad_generic_count=count, role_density_variant="explicit-pose",
                role_density_inputs=(ComposerInput("pose", canonical="sitting", block="POSE_COMPOSITION"),),
                weight_variant=(WeightVariant("sitting", 1.25, "e2e-explicit-weight"),),
                lora_inputs=(ComposerInput("lora", text="<lora:e2e:1>", block="LORA"),),
                lora_contraction_variant="explicit", lora_contraction_excluded_input_ids=("manual:blue_sky",))
            session.set_variant(variant)
            app._refresh_state()
            output = assert_output(app)
            assert output.plan.profile.model_family == family
            assert "blue sky" not in output.provenance_map
            assert output.provenance_map["e2e-explicit-weight"].weight == 1.25
            assert output.plan.selected_atoms[-1].special_owners == ("1816",)
            session.set_variant(baseline[0])
            app._refresh_state()
            assert session.comparison_snapshot() == baseline
            assert_output(app)
    record_property("variant_combinations_restored", 12)


def test_real_tk_stale_and_invalid_protection(app, record_property):
    result = select_core(app)
    session = app.session
    baseline = session.comparison_snapshot()
    app._show_recommendation_result(replace(result, request_id=result.request_id - 1, common=(), rare=()))
    assert app.recommendation_result == result
    app._show_recommendation_result(replace(result, core_canonicals=("not_current_core",)))
    assert app.recommendation_result == result
    app._on_recommendation_result(replace(result, request_id=result.request_id - 1, common=(), rare=()))
    pump(app, app.recommendation_queue.empty)
    assert app.recommendation_result == result
    app._show_recommendation_result(replace(result, status="invalid-status"))
    assert app.recommendation_result == result
    for operation in (lambda: session.add_special("invalid-e2e-special"),
                      lambda: session.add_auxiliary("invalid-e2e-canonical"),
                      lambda: session.choose_candidate("invalid-e2e-candidate", "INCLUDE")):
        with pytest.raises(KeyError):
            operation()
        assert session.comparison_snapshot() == baseline
    # Malformed current-request payload must not partially replace valid state.
    invalid = replace(result, common=(replace(result.common[0], canonical="invalid-e2e-canonical"),))
    try:
        app._show_recommendation_result(invalid)
    except (KeyError, ValueError):
        pass  # Explicit rejection is acceptable; partial state mutation is not.
    assert app.recommendation_result == result
    assert session.comparison_snapshot() == baseline
    assert_output(app)
    record_property("guards", ["stale_request", "stale_queue", "wrong_core", "invalid_status",
                               "invalid_special", "invalid_manual", "invalid_candidate", "malformed_result"])
