import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/issue223'


def read(name):
    return list(csv.DictReader((OUT/name).open(encoding='utf-8')))


def test_frozen_reproduction_and_input_integrity():
    spec = importlib.util.spec_from_file_location('issue223', ROOT/'scripts/issue223/build_browse_groups.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    outputs, manifest = module.build()
    for name, content in outputs.items():
        assert (OUT/name).read_bytes() == content
    for name, expected in manifest['inputs'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected


def test_population_partition_and_primary_group_uniqueness():
    homes = {r['character']: r['formal_home'] or r['reviewed_home'] for r in csv.DictReader((ROOT/'docs/issue216/BROWSE_HOME_RUNTIME_V1.csv').open(encoding='utf-8'))}
    groups = {(r['home_copyright'], r['group_id']) for r in read('BROWSE_GROUPS_V1.csv')}
    members = read('BROWSE_GROUP_MEMBERS_V1.csv')
    assert len({r['character_canonical'] for r in members}) == len(members)
    for row in members:
        assert homes[row['character_canonical']] == row['home_copyright']
        assert (row['home_copyright'], row['group_id']) in groups
        assert row['review_status'] == 'REVIEWED'
        assert row['evidence_ref'] and row['evidence_kind']
    census = read('HOME_CENSUS_V1.csv')
    assert sum(int(r['character_count']) for r in census) == 32942
    selected = [r for r in census if r['selected'] == 'true']
    assert len(selected) == 7
    assert sum(int(r['grouped']) for r in selected) == len(members)
    assert sum(int(r['unclassified'])+int(r['grouped']) for r in selected) == sum(int(r['character_count']) for r in selected)
    assert all(int(r['character_count']) >= 100 for r in selected)


def test_ambiguous_and_guest_rosters_do_not_force_groups():
    members = {r['character_canonical']: r for r in read('BROWSE_GROUP_MEMBERS_V1.csv')}
    holds = read('HOLD_V1.csv')
    assert len(holds) == 21
    assert not set(r['character_canonical'] for r in holds) & members.keys()
    for character in ['anna_(fire_emblem)', 'tamamo_no_mae_(fate)', 'bahamut_(final_fantasy)', 'dio_brando']:
        assert character not in members
    assert members['pikachu']['group_id'] == 'generation_1'
    assert members['bulbasaur']['group_id'] == 'generation_1'
    assert 'captain_pikachu' not in members
    assert 'archetype_earth' not in members
    assert all('AMBIGUOUS_TERMINALS' not in r['evidence_ref'] and 'LEGACY_NO_SAFE' not in r['evidence_ref'] for r in members.values())
