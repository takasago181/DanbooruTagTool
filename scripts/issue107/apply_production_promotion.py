#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

BASE_COUNT=2983
NEW_COUNT=105
FINAL_COUNT=3088
FIRST_NEW=2984
LAST_NEW=3088
EXPECTED_METADATA_SHA='84a31353d438001985b76793570417b6501f8ada220466c8508bf989544f26f5'
ISSUE104_MERGE='0e165d02c4715fedbd28b49525276294d0cd8ee3'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_csv(path: Path):
    with path.open('r',encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def write_csv(path: Path, rows, fields):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)

def exact_replace(text: str, old: str, new: str, label: str) -> str:
    n=text.count(old)
    if n!=1: raise ValueError(f'{label}: expected exactly one match, got {n}')
    return text.replace(old,new,1)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--metadata',default='docs/issue107/promotion_metadata_v1.csv'); ap.add_argument('--summary-out',default='docs/issue107/production_apply_summary_v1.json'); args=ap.parse_args()
    root=Path(args.repo_root)
    metadata_path=root/args.metadata
    if sha(metadata_path)!=EXPECTED_METADATA_SHA: raise ValueError('Issue #107 metadata hash drift')
    meta=read_csv(metadata_path)
    if len(meta)!=NEW_COUNT or [int(r['proposed_special_id']) for r in meta]!=list(range(FIRST_NEW,LAST_NEW+1)): raise ValueError('Issue #107 metadata ID/count drift')
    if any(r['metadata_status']!='HUMAN_BOUNDED_RESOLVED' for r in meta): raise ValueError('unresolved Issue #107 metadata row')

    profile_path=root/'data/generation/special2788_generation_profile.csv'
    fit_path=root/'data/special2788/product_fit_verdicts.csv'
    importer_path=root/'src/DanbooruTagTool.Data/AcceptedAssetImporter.cs'
    browse_path=root/'src/DanbooruTagTool.Data/SpecialBrowseV2Overlay.cs'

    before={p.as_posix():sha(p) for p in (profile_path,fit_path,importer_path,browse_path)}

    profile=read_csv(profile_path); profile_fields=list(profile[0].keys())
    if len(profile) not in (BASE_COUNT,FINAL_COUNT): raise ValueError(f'unexpected generation profile count {len(profile)}')
    if [int(r['SpecialID']) for r in profile[:BASE_COUNT]]!=list(range(1,BASE_COUNT+1)): raise ValueError('existing profile IDs 1..2983 drift')
    original_profile_prefix=[dict(r) for r in profile[:BASE_COUNT]]
    expected_new=[]
    for m in meta:
        expected_new.append({
            'SpecialID':m['proposed_special_id'],'Tag':m['canonical_tag'],'PromotionStatus':'APPROVED_STATIC','MeaningStatus':'SOURCE_CLEAR','MeaningConfidence':'HIGH','SourceGlossQuality':'GOOD',
            'GenerationFamily':m['generation_family'],'GenerationRole':m['generation_role'],'PromptUseMode':m['prompt_use_mode'],'FamilyRuleId':m['family_rule_id'],
            'CompositionRoleOverride':'','ActorRequirementOverride':'','BodypartRequirementOverride':'','ImplementRequirementOverride':'','PoseRequirementOverride':'','CameraRequirementOverride':'','SpatialAssignmentOverride':'','ShapeConflictGroup':'','SpecialFlags':'',
            'RecommendedHandling':'Accepted Issue #107 metadata; use as structural inspection data only; do not auto-add support tags.',
            'EvidenceClass':'ISSUE107_ACCEPTED_SPECIAL_EXPANSION','EvidenceRefs':f"ISSUE107:{m['proposed_special_id']};ISSUE104:{ISSUE104_MERGE}"
        })
    if len(profile)==BASE_COUNT:
        profile=profile+expected_new
    elif profile[BASE_COUNT:]!=expected_new:
        raise ValueError('existing Issue #107 generation profile suffix differs from deterministic expectation')
    if profile[:BASE_COUNT]!=original_profile_prefix: raise AssertionError('existing profile prefix changed in memory')
    write_csv(profile_path,profile,profile_fields)

    fit=read_csv(fit_path); fit_fields=list(fit[0].keys())
    if len(fit) not in (BASE_COUNT,FINAL_COUNT): raise ValueError(f'unexpected product-fit count {len(fit)}')
    if [int(r['special_id']) for r in fit[:BASE_COUNT]]!=list(range(1,BASE_COUNT+1)): raise ValueError('existing product-fit IDs 1..2983 drift')
    fit_prefix=[dict(r) for r in fit[:BASE_COUNT]]
    expected_fit=[{'special_id':str(i),'product_fit_verdict':'KEEP'} for i in range(FIRST_NEW,LAST_NEW+1)]
    if len(fit)==BASE_COUNT: fit=fit+expected_fit
    elif fit[BASE_COUNT:]!=expected_fit: raise ValueError('existing Issue #107 product-fit suffix differs')
    if fit[:BASE_COUNT]!=fit_prefix: raise AssertionError('existing fit prefix changed in memory')
    write_csv(fit_path,fit,fit_fields)

    importer=importer_path.read_text(encoding='utf-8')
    if 'Issue107PromotionRelativePath' not in importer:
        importer=exact_replace(importer,
            '    public const int ExpandedSpecialCount = 2983;\n    public const string PromotionRelativePath = "docs/issue96/special_expansion_promotion_proposal_v1.csv";\n    private const string PromotionHash = "cdeef93802f8b1ebf0e70b2fe82211e2fd8955b064b063f10093a3ff0642dc1f";',
            '    public const int Issue96ExpandedSpecialCount = 2983;\n    public const int ExpandedSpecialCount = 3088;\n    public const string PromotionRelativePath = "docs/issue96/special_expansion_promotion_proposal_v1.csv";\n    public const string Issue107PromotionRelativePath = "docs/issue107/promotion_metadata_v1.csv";\n    private const string PromotionHash = "cdeef93802f8b1ebf0e70b2fe82211e2fd8955b064b063f10093a3ff0642dc1f";\n    private const string Issue107PromotionHash = "84a31353d438001985b76793570417b6501f8ada220466c8508bf989544f26f5";',
            'importer constants')
        importer=exact_replace(importer,
            '        var promotion = Csv(promotionPath).OrderBy(row => int.Parse(row["proposed_special_id"], CultureInfo.InvariantCulture)).ToArray();\n        ValidatePromotion(source, canonical, promotion);',
            '        var promotion = Csv(promotionPath).OrderBy(row => int.Parse(row["proposed_special_id"], CultureInfo.InvariantCulture)).ToArray();\n        ValidatePromotion(source, canonical, promotion);\n        var issue107PromotionPath = Authority(Issue107PromotionRelativePath);\n        if (Hash(issue107PromotionPath) != Issue107PromotionHash) throw new InvalidDataException("Issue #107 promotion metadata hash mismatch");\n        var issue107Promotion = Csv(issue107PromotionPath).OrderBy(row => int.Parse(row["proposed_special_id"], CultureInfo.InvariantCulture)).ToArray();\n        ValidateIssue107Promotion(source, canonical, promotion, issue107Promotion);',
            'load Issue107 promotion')
        importer=exact_replace(importer,
            '        // #63 canonical eligibility must also prevent General duplicates from bypassing exclusion.',
            '        foreach (var row in issue107Promotion)\n        {\n            var id = row["proposed_special_id"];\n            var canonicalTag = row["canonical_tag"];\n            var bodySites = SplitPipe(row["body_site_ids"]);\n            var themes = SplitPipe(row["theme_ids"]);\n            ValidatePromotionFacets(id, row["kind_id"], bodySites, themes);\n            entries.Add(new("S:" + id, canonicalTag, canonicalTag, row["display_ja"], true,\n                canonical[canonicalTag], aliases.GetValueOrDefault(canonicalTag)?.ToArray() ?? [],\n                SplitPipe(row["search_ja"]), [], fit[id], "",\n                BrowseClassificationStatus.NotApplicable,\n                new SpecialBrowseV2Classification(row["kind_id"], bodySites, themes, SpecialBrowseV2Status.HumanResolved)));\n        }\n        // #63 canonical eligibility must also prevent General duplicates from bypassing exclusion.',
            'import Issue107 entries')
        importer=exact_replace(importer,
            '        if (promotion.Count != ExpandedSpecialCount - BaseSpecialCount || !ids.SequenceEqual(Enumerable.Range(BaseSpecialCount + 1, ExpandedSpecialCount - BaseSpecialCount)))\n            throw new InvalidDataException("Issue #96 promotion IDs must be contiguous 2789..2983");',
            '        if (promotion.Count != Issue96ExpandedSpecialCount - BaseSpecialCount || !ids.SequenceEqual(Enumerable.Range(BaseSpecialCount + 1, Issue96ExpandedSpecialCount - BaseSpecialCount)))\n            throw new InvalidDataException("Issue #96 promotion IDs must be contiguous 2789..2983");',
            'freeze Issue96 promotion count')
        importer=exact_replace(importer,
            '    private static void ValidatePromotionFacets(string id, string kind, string[] bodySites, string[] themes)',
            '    private static void ValidateIssue107Promotion(\n        IReadOnlyDictionary<string, Dictionary<string, string>> source,\n        IReadOnlyDictionary<string, long> canonical,\n        IReadOnlyList<Dictionary<string, string>> issue96Promotion,\n        IReadOnlyList<Dictionary<string, string>> issue107Promotion)\n    {\n        var ids = issue107Promotion.Select(row => int.Parse(row["proposed_special_id"], CultureInfo.InvariantCulture)).ToArray();\n        if (issue107Promotion.Count != ExpandedSpecialCount - Issue96ExpandedSpecialCount ||\n            !ids.SequenceEqual(Enumerable.Range(Issue96ExpandedSpecialCount + 1, ExpandedSpecialCount - Issue96ExpandedSpecialCount)))\n            throw new InvalidDataException("Issue #107 promotion IDs must be contiguous 2984..3088");\n        var existing = source.Values.Select(row => row["Tag"]).Concat(issue96Promotion.Select(row => row["canonical_tag"])).ToHashSet(StringComparer.Ordinal);\n        var seen = new HashSet<string>(StringComparer.Ordinal);\n        foreach (var row in issue107Promotion)\n        {\n            var tag = row["canonical_tag"];\n            if (!seen.Add(tag)) throw new InvalidDataException("Duplicate Issue #107 promotion canonical: " + tag);\n            if (!canonical.TryGetValue(tag, out var postCount)) throw new InvalidDataException("Issue #107 promotion is not a current General canonical: " + tag);\n            if (existing.Contains(tag)) throw new InvalidDataException("Issue #107 promotion overlaps existing Special identity: " + tag);\n            if (long.Parse(row["frozen_post_count_2026_09_02"], CultureInfo.InvariantCulture) != postCount)\n                throw new InvalidDataException("Issue #107 frozen post_count drift: " + tag);\n            if (row["metadata_status"] != "HUMAN_BOUNDED_RESOLVED" || string.IsNullOrWhiteSpace(row["display_ja"]) || string.IsNullOrWhiteSpace(row["search_ja"]))\n                throw new InvalidDataException("Issue #107 product metadata incomplete: " + tag);\n            if (string.IsNullOrWhiteSpace(row["generation_family"]) || string.IsNullOrWhiteSpace(row["generation_role"]) ||\n                string.IsNullOrWhiteSpace(row["prompt_use_mode"]) || string.IsNullOrWhiteSpace(row["family_rule_id"]))\n                throw new InvalidDataException("Issue #107 generation metadata incomplete: " + tag);\n            ValidatePromotionFacets(row["proposed_special_id"], row["kind_id"], SplitPipe(row["body_site_ids"]), SplitPipe(row["theme_ids"]));\n        }\n    }\n\n    private static void ValidatePromotionFacets(string id, string kind, string[] bodySites, string[] themes)',
            'add Issue107 validation')
        importer_path.write_text(importer,encoding='utf-8')
    else:
        if 'public const int ExpandedSpecialCount = 3088;' not in importer: raise ValueError('partially applied importer state')

    browse=browse_path.read_text(encoding='utf-8')
    if 'SpecialBrowseV2Status.HumanResolved, 210' in browse:
        browse=exact_replace(browse,'        Expect(counts, SpecialBrowseV2Status.HumanResolved, 210);','        Expect(counts, SpecialBrowseV2Status.HumanResolved, 315);','Browse HumanResolved count')
        browse_path.write_text(browse,encoding='utf-8')
    elif 'SpecialBrowseV2Status.HumanResolved, 315' not in browse: raise ValueError('unexpected Browse HumanResolved contract')

    after={p.as_posix():sha(p) for p in (profile_path,fit_path,importer_path,browse_path)}
    summary={
        'before_sha256':before,'after_sha256':after,
        'special_before':BASE_COUNT,'special_after':FINAL_COUNT,'added':NEW_COUNT,'id_range':[FIRST_NEW,LAST_NEW],
        'metadata_sha256':EXPECTED_METADATA_SHA,'issue96_authority_mutated':'NO','issue70_mutated':'NO','userdata_mutated':'NO',
        'existing_id_prefix_preserved':'YES','hidden_prompt_insertion':'NO','content_filter_used':'NO'
    }
    summary_path=root/args.summary_out; summary_path.parent.mkdir(parents=True,exist_ok=True); summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
