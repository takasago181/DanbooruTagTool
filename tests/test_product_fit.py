from collections import Counter
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.models import CanonicalTag, SpecialTag
from danbooru_tag_tool.product_fit import (
    COUNTS, CSV_PATH, MANIFEST_PATH, MANIFEST_SHA256, ProductFitPolicy,
    csv_bytes, expand_manifest, load_authority,
)
from danbooru_tag_tool.search import TagSearchEngine
from danbooru_tag_tool.stage7a_presenter import SpecialSearchPresenter
from danbooru_tag_tool.stage7a_session import Stage7ASession
from danbooru_tag_tool.stage7a_warnings import Stage7AWarningPresenter
from danbooru_tag_tool.stage7b_recommendations import RecommendationController
from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore
from danbooru_tag_tool.stage9c_session import Stage9ComposerSession
from danbooru_tag_tool.stage9b_runtime import Stage9BSelectionState, SelectionDecision, cooccurrence_candidate
from danbooru_tag_tool.recommendations import RecommendationCandidate, RecommendationEngine
from tools.build_product_fit_verdicts import materialize


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def production():
    return TagKnowledgeCore.load(ROOT)


@pytest.fixture
def fixture_knowledge():
    # Neutral synthetic identities make the policy tests independent of audit
    # meaning, source categories, dictionary counts, and model grammar.
    targets = ['kept', 'kept', 'reference', 'outside', 'review_target']
    verdicts = ['KEEP', 'KEEP_REFERENCE_ONLY', 'KEEP_REFERENCE_ONLY',
                'OUT_OF_SCOPE_PRODUCT', 'REVIEW']
    canonical = {tag: CanonicalTag(tag, 0, 100) for tag in {*targets, 'general'}}
    special = {}
    for i, target in enumerate(targets, 1):
        sid = str(i)
        term = 'legacy_label' if i == 2 else 'unresolved_label' if i == 5 else target
        special[sid] = SpecialTag(sid, term, f'表示{i}', '', 'Alias' if i in (2, 5) else 'Core',
                                  'unchanged', target, 'alias_unique' if i in (2, 5) else 'canonical',
                                  (target,))
    policy = ProductFitPolicy(dict(zip(special, verdicts)), special)
    return TagKnowledgeCore(canonical, {'legacy label': ('kept',), 'unresolved label': ('review_target',)},
                            special, {}, product_fit=policy)


def test_committed_csv_exactly_matches_pinned_authority(production):
    assert hashlib.sha256((ROOT / MANIFEST_PATH).read_bytes()).hexdigest() == MANIFEST_SHA256
    verdicts = load_authority(ROOT / MANIFEST_PATH)
    assert (ROOT / CSV_PATH).read_bytes() == csv_bytes(verdicts)
    assert Counter(verdicts.values()) == dict(COUNTS)
    assert list(verdicts) == [str(i) for i in range(1, 2789)]
    assert len(production.special) == 2788
    assert dict(production.product_fit.verdicts) == verdicts
    with pytest.raises(TypeError):
        production.product_fit.verdicts['1'] = 'REVIEW'


@pytest.mark.parametrize('change', ['overlap', 'duplicate', 'reverse', 'out_of_range', 'syntax', 'counts', 'unknown', 'default', 'precedence'])
def test_invalid_manifest_rejected(change):
    manifest = json.loads((ROOT / MANIFEST_PATH).read_text(encoding='utf-8'))
    sets = manifest['verdict_sets']
    if change == 'overlap': sets['REVIEW'] += ',4'
    elif change == 'duplicate': sets['REVIEW'] += ',70'
    elif change == 'reverse': sets['REVIEW'] += ',10-9'
    elif change == 'out_of_range': sets['REVIEW'] += ',2789'
    elif change == 'syntax': sets['REVIEW'] += ',01'
    elif change == 'counts': sets['REVIEW'] = sets['REVIEW'].replace('70,', '')
    elif change == 'unknown': sets['UNKNOWN'] = '1'
    elif change == 'default': manifest['default_verdict'] = 'REVIEW'
    elif change == 'precedence': manifest['expansion_contract']['precedence'].reverse()
    with pytest.raises(ValueError):
        expand_manifest(manifest)


def prepare_root(tmp_path):
    manifest = tmp_path / MANIFEST_PATH
    manifest.parent.mkdir(parents=True)
    manifest.write_bytes((ROOT / MANIFEST_PATH).read_bytes())
    return tmp_path


def test_materialization_is_deterministic_and_never_overwrites(tmp_path):
    prepare_root(tmp_path)
    a = materialize(tmp_path)
    first = (tmp_path / CSV_PATH).read_bytes()
    timestamp = (tmp_path / CSV_PATH).stat().st_mtime_ns
    assert materialize(tmp_path, check=True) == a == materialize(tmp_path)
    assert (tmp_path / CSV_PATH).stat().st_mtime_ns == timestamp
    assert first == (ROOT / CSV_PATH).read_bytes()
    (tmp_path / CSV_PATH).write_bytes(b'existing user content')
    with pytest.raises(ValueError, match='refusing overwrite'):
        materialize(tmp_path)
    assert (tmp_path / CSV_PATH).read_bytes() == b'existing user content'


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'gap', 'unknown', 'columns', 'swapped', 'authority'])
def test_runtime_rejects_missing_or_corrupt_sidecar(tmp_path, production, change):
    prepare_root(tmp_path)
    if change != 'missing':
        materialize(tmp_path)
        path = tmp_path / CSV_PATH
        lines = path.read_text(encoding='utf-8').splitlines()
        if change == 'duplicate': lines.append(lines[1])
        elif change == 'gap': lines.pop(1)
        elif change == 'unknown': lines[1] = '1,UNKNOWN'
        elif change == 'columns': lines[0] += ',unexpected'
        elif change == 'swapped':
            lines[1], lines[4] = '1,KEEP_REFERENCE_ONLY', '4,KEEP'
        elif change == 'authority':
            manifest = tmp_path / MANIFEST_PATH
            manifest.write_bytes(manifest.read_bytes() + b' ')
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    with pytest.raises((ValueError, FileNotFoundError)):
        ProductFitPolicy.load(tmp_path, production.special)


@pytest.mark.parametrize('sid,browse,search,statistics', [
    ('1', True, True, True), ('2', False, True, True),
    ('3', False, True, True), ('4', False, False, False), ('5', False, True, False)])
def test_four_classes_share_one_policy(fixture_knowledge, sid, browse, search, statistics):
    policy = fixture_knowledge.product_fit
    assert policy.allows(sid, 'browse') is browse
    assert policy.allows(sid, 'recommendation') is browse
    assert policy.allows(sid, 'search') is search
    assert policy.allows(sid, 'statistics') is statistics
    assert policy.allows(sid, 'inspect')
    with pytest.raises(KeyError): policy.allows(sid, 'typo')
    with pytest.raises(KeyError): policy.verdict('9999')


def test_browse_search_and_reference_alias_preserve_identity(fixture_knowledge):
    knowledge = fixture_knowledge
    before = deepcopy(knowledge.special)
    presenter = SpecialSearchPresenter(knowledge, TagSearchEngine(knowledge), SimpleNamespace(profiles={}))
    assert [item.special_id for item in presenter.browse()] == ['1']
    for query in ('legacy_label', '表示2'):
        card = next(item for item in presenter.search(query).special if item.special_id == '2')
        assert card.original_term == 'legacy_label'
        assert card.product_fit_label == '参照用'
        assert card.matched_canonical == 'kept'
    assert knowledge.resolve_exact('legacy_label').resolved_canonical == 'kept'
    assert knowledge.special == before
    assert not presenter.search('outside').special
    assert not presenter.search('outside').general  # no General fallback leak
    assert knowledge.resolve_exact('outside').resolved_canonical == 'outside'
    review = next(item for item in presenter.search('unresolved_label').special if item.special_id == '5')
    assert review.product_fit_label == '要確認'
    assert review.matched_canonical is None
    assert presenter.search('general').general[0].canonical == 'general'


def test_product_eligibility_runs_before_top_k(fixture_knowledge):
    engine = TagSearchEngine(fixture_knowledge)
    # The exact excluded hit outranks this prefix in the unchanged Stage4 order.
    fixture_knowledge.canonical['outside_visible'] = CanonicalTag('outside_visible', 0, 1)
    engine = TagSearchEngine(fixture_knowledge)
    assert engine.search_one('outside', limit=1)[0].canonical == 'outside'
    assert engine.search_one('outside', limit=1, product_facing=True)[0].canonical == 'outside_visible'


def candidate(canonical):
    return RecommendationCandidate(canonical, 'other', 20, 5, .25, 10, .1, 2.5, .1, 1.5)


def test_recommendations_filter_before_limits_keep_raw_statistics(fixture_knowledge):
    raw = tuple(candidate(c) for c in ['outside', 'reference', 'review_target', 'kept', 'general'])
    engine = SimpleNamespace(knowledge=fixture_knowledge, candidates=lambda core: raw)
    controller = RecommendationController(engine, max_common=2, max_rare=2)
    try:
        result = controller._calculate(1, ('general',))
        expected = RecommendationEngine.rank(raw[-2:], 'conditional_rate')
        assert result.common == expected
        assert result.rare == expected
        assert result.base_count == 20
        assert raw[0].canonical == 'outside'  # raw source objects are untouched
    finally:
        controller.close()


@pytest.mark.parametrize('session_type', [Stage7ASession, Stage9ComposerSession])
def test_manual_review_preserves_literal_and_blocks_statistics(fixture_knowledge, session_type):
    profiles = SimpleNamespace(profiles={})
    warning = Stage7AWarningPresenter(fixture_knowledge, profiles)
    args = [fixture_knowledge, warning]
    if session_type is Stage9ComposerSession:
        args.append(SupportKnowledgeStore((), (), profiles, fixture_knowledge.product_fit))
    session = session_type(*args)
    session.add_special('5')
    assert session.statistics_core_canonicals() is None
    assert session.prompt_preview == 'unresolved label'
    assert any(n.code == 'product_fit_review' for n in session.warnings)
    with pytest.raises(ValueError): session.add_special('4')
    assert session.selected_special_ids == ('5',)
    session.remove_special('5')
    session.add_special('2')
    assert session.prompt_preview == 'legacy label'
    assert session.statistics_core_canonicals() == ('kept',)


def test_stage9_runtime_cannot_promote_excluded_lanes(fixture_knowledge):
    profiles = SimpleNamespace(profiles={})
    support = SupportKnowledgeStore((), (), profiles, fixture_knowledge.product_fit)
    session = Stage9ComposerSession(fixture_knowledge, Stage7AWarningPresenter(fixture_knowledge, profiles), support)
    lanes = tuple(cooccurrence_candidate(candidate(c)) for c in ['outside', 'reference', 'review_target', 'kept'])
    choices = Stage9BSelectionState(tuple(SelectionDecision(item.candidate_id, 'INCLUDE') for item in lanes))
    result = session.runtime.compose(('1',), cooccurrence=lanes, selection_state=choices)
    assert {atom.canonical for atom in result.plan.candidate_atoms if atom.canonical} == {'kept'}
    review = session.runtime.compose(('5',))
    assert review.positive_prompt == 'unresolved label'
    assert any(w.code == 'PRODUCT_FIT_REVIEW' for w in review.warnings)
    with pytest.raises(ValueError): session.runtime.compose(('4',))


def test_production_browse_counts_and_reference_lookup(production):
    profiles = production.load_generation_profile_store(ROOT)
    presenter = SpecialSearchPresenter(production, TagSearchEngine(production), profiles)
    browse = presenter.browse(limit=2788)
    assert len(browse) == 1618
    assert {item.product_fit_verdict for item in browse} == {'KEEP'}
    alias = next(s for s in production.special.values() if s.layer == 'Alias'
                 and production.product_fit.verdict(s.special_id) == 'KEEP_REFERENCE_ONLY')
    for query in (alias.term, alias.japanese):
        assert any(item.special_id == alias.special_id for item in presenter.search(query, limit=2788).special)
    for sid in ('70', '1577', '2770'):
        assert production.product_fit.verdict(sid) == 'REVIEW'
        items = presenter.search(production.special[sid].term, limit=2788).special
        assert any(item.special_id == sid and item.matched_canonical is None for item in items)


def test_support_does_not_infer_from_review_owner(production):
    profiles = production.load_generation_profile_store(ROOT)
    store = SupportKnowledgeStore.load(ROOT, production, profiles)
    template = next(row for row in store.special_rows if row.enabled)
    review_row = replace(template, owner_id='70')
    isolated = SupportKnowledgeStore((review_row,), (), profiles, production.product_fit)
    assert isolated.candidates(('70',)) == ()


def test_real_tk_search_labels_and_review_session(production):
    import tkinter as tk
    from danbooru_tag_tool.ui import Stage7AApp
    window = tk.Tk()
    window.withdraw()
    app = None
    try:
        app = Stage7AApp(window, root_path=ROOT)
        for sid, label in [('70', '要確認'), ('4', '参照用')]:
            app.search_var.set(app.knowledge.special[sid].term)
            app._run_search()
            index = next(i for i, item in enumerate(app.special_rows) if item.special_id == sid)
            assert app.special_list.get(index).startswith('[' + label + '] ')
        app.search_var.set(app.knowledge.special['70'].term)
        app._run_search()
        index = next(i for i, item in enumerate(app.special_rows) if item.special_id == '70')
        app._add_special_index(index)
        assert app.session.statistics_core_canonicals() is None
        assert app.knowledge.special['70'].term.replace('_', ' ') == app.session.prompt_preview
        assert any(w.code == 'PRODUCT_FIT_REVIEW' for w in app.session.composer_warnings)
    finally:
        if app is not None: app.close()
        window.destroy()
