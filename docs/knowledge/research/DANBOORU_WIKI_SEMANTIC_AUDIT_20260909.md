# Danbooru Wiki — Semantic / Alias / Implication Audit

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `AUTHORITATIVE_SOURCE_PASS_V1`

## Purpose

DanbooruTagTool の Special2788 / UI-JA / generation-support audit に対して、Danbooru Wiki をどの権限で使うべきかを固定する。

結論:

**Danbooru Wiki / active tag aliases / active tag implications are the highest-priority source for Danbooru canonical tag identity and scope.**

ただし、Danbooruでの意味・分類と、各画像生成モデルがその文字列をどれだけ学習しているかは別問題である。

---

## 1. Core authority rules

### Canonical identity

`ADOPT / CANONICAL_AUTHORITY`

Danbooruの既存general tagについて、意味・適用範囲・類似タグとの差を確認する第一候補は current Danbooru Wiki。

Useful official pages:
- `help:tags`
- `howto:tag`
- tag wiki page
- relevant tag groups
- active alias / implication records

### Tag What You See

Danbooru `howto:tag` explicitly uses `Tag what you see, not what you know`.

Project implication:
- Wiki definitions are primarily **visible-image indexing semantics**.
- latent intent / creator intention / generation recipe is not automatically encoded in a Danbooru tag.
- semantic-support data must not silently add invisible assumptions to canonical meaning.

### Alias

Danbooru help defines aliases as alternate names for the **same concept**. Tagging/searching the antecedent resolves to the consequent.

Project rule:
- active alias = identity-equivalence evidence for dictionary mapping.
- preserve antecedent traceability/history where product requires it.
- do not treat implication/related/wiki-see-also as Alias.

### Implication

Danbooru help defines implications as subset / always-also relationships: using one tag automatically adds another.

Project rule:
- implication is not synonymy.
- an implied parent can be a decomposition/support candidate, but not an automatic Prompt addition.
- implication edges are strong semantic hierarchy evidence, not generation-benefit evidence.

### Deprecated tags

Danbooru marks ambiguous, redundant, invalid, subjective or obsolete tags as deprecated.

Project rule:
- deprecated status is strong evidence against using a surface as current canonical Prompt identity.
- historical/alternate trigger may still be retained as model-exposure hypothesis when training cutoff predates migration.

---

## 2. High-value semantic examples

### `anal`

Current 2026 Danbooru wiki snapshot defines `anal` as anal penetration, including sex, fingering, object insertion, tentacle penetration and other anal penetration. Penis insertion additionally warrants `sex`.

Audit consequence:
- `anal` is broader than penile anal intercourse.
- `anal sex -> anal` Alias in the project is semantically plausible as a legacy surface only if active canonical data confirms it.
- Japanese wording that narrows `anal` to only intercourse is unsafe.

### `urethral insertion` / `sounding`

Danbooru distinguishes:
- `urethral insertion`: object insertion into male or female urethra;
- `sounding`: object insertion into penile urethra;
- `urethral penetration`: finger/penis/other body part relation.

` sounding -> urethral_insertion` is implication, not Alias.

Audit consequence:
- implement type and body-site/sex specificity are intrinsic predicates.
- broad Japanese wording such as simply `尿道責め` is not sufficient canonical proof.

### `missionary`

Defined as receiver lying on back, partners face each other; several leg variations allowed.

`missionary_position` is Alias.

Audit consequence:
- `missionary` is not identical to every `face-to-face sex` posture.
- body orientation and receiver posture are intrinsic.

### `suspended congress`

Defined as receiver lifted/carried in midair while facing partner.

`stand_and_carry` is Alias.

Audit consequence:
- the carrier/lifted topology is intrinsic, not merely `standing sex`.
- useful reference case for Alias-to-canonical identity with a structurally rich relation.

### `upright straddle`

Defined as face-to-face straddling of a seated-upright partner; implicates `straddling`.

Audit consequence:
- `straddling` is broader; mapping all straddling to a sex position subtype is incorrect.
- implication / subtype must be preserved separately from synonymy.

### `bound wrists`

Both wrists bound together by restraint. Contrasted with `wrists bound apart`.

Aliases include historical surfaces such as `bound_hands`, `hands_tied`, `tied_wrists`; it implicates `bound`.

Audit consequence:
- `tied hands` wording is not proof that hands themselves are the semantic body-site; canonical target is wrist-binding relation.
- topology distinction `together` vs `apart` is intrinsic.

### `bound arms`

Both arms bound together; aliases include `arms_tied`, `tied_arms`; implicates `bound`.

Audit consequence:
- `bound arms` and `arms behind back` are related but not synonymous.
- support must not collapse restraint state into pose.

### `gag`

An object in/over the mouth restricting speech. Character state `gagged` should also be tagged when worn; not the same as `gagging`.

Audit consequence:
- object identity (`gag`) and wearer state (`gagged`) are distinct semantic predicates.
- high-value false-positive guard for Japanese translation and generation evaluator.

### `dildo`

Artificial penis replica designed as sex toy; not equivalent to generic phallic object. Implicates `sex_toy`.

Audit consequence:
- purpose/design distinction matters.
- `phallic object` or arbitrary cylindrical object is not sufficient canonical evidence.

### `rope`

Generic rope object; may be used for bondage or unrelated purposes.

Audit consequence:
- rope presence does not imply bondage/restraint.
- generation evaluator must not certify BDSM topology from `rope` detection.

### Body parts tag group

Danbooru's body-parts group distinguishes `anus`, `ass`, `groin`, `pussy`, `penis`, `perineum`, `prostate`, `uterus/cervix`, appendages, etc.

Audit consequence:
- body-site is a first-class semantic axis.
- body-site-specific Special must not be approved from broad anatomy wording.

---

## 3. Tag-group use

Tag groups are useful discovery/index structures, not proof that every item is synonymous or that parent should be added to Prompt.

High-value groups for current project:
- body parts
- breasts tags
- groups / participant counts
- sex acts
- sexual positions
- sex objects
- BDSM and torture
- posture
- viewpoint / framing related groups.

Project use:
1. inventory recall
2. sibling/subtype discovery
3. semantic contrast cases
4. generation-decomposition hypotheses

Do not use group membership as Alias equivalence.

---

## 4. Semantic audit rules derived from Danbooru

For every high-risk Special, explicitly answer:

1. What visible state/action does canonical require?
2. Which actor/receiver/owner matters?
3. Which body-site matters?
4. Does exact count matter?
5. Is an object merely present, worn, inserted, held, attached, or acting?
6. Is relation orientation intrinsic?
7. Is the candidate surface Alias, implication child/parent, merely related, or free phrase?
8. Does the wiki distinguish a nearby concept that Japanese wording may collapse?

### Automatic risk escalation

Escalate translation/generation audit when:
- wiki uses `not to be confused with`;
- `see X for ...` splits body-site/implement/action;
- sibling tags differ only by count/orientation/site;
- Alias target differs lexically from surface;
- implication parent is much broader;
- canonical concept is topology/relation, not unary object.

---

## 5. Generation boundary

Danbooru canonical authority does **not** prove:
- exact model token exposure;
- exact model trigger spelling;
- prompt-order benefit;
- broad+specific generation benefit;
- relation success rate;
- minimum support set;
- Negative interaction.

For these, use exact model author evidence / controlled image tests.

A current Danbooru rename may postdate a model cutoff. Therefore:

`canonical identity != historical training token != best current model trigger`

All three may need to be stored separately.

---

## 6. Sources

Primary/current pages consulted:
- https://safebooru.donmai.us/wiki_pages/help%3Atags
- https://safebooru.donmai.us/wiki_pages/howto%3Atag
- https://safebooru.donmai.us/wiki_pages/howto%3Atag_checklist
- https://safebooru.donmai.us/wiki_pages/help%3Afrequently_asked_questions
- https://safebooru.donmai.us/wiki_pages/tag_group%3Abody_parts
- https://safebooru.donmai.us/wiki_pages/urethral_insertion
- https://safebooru.donmai.us/wiki_pages/sounding
- https://safebooru.donmai.us/wiki_pages/missionary
- https://safebooru.donmai.us/wiki_pages/suspended_congress
- https://safebooru.donmai.us/wiki_pages/upright_straddle
- https://safebooru.donmai.us/wiki_pages/bound_wrists
- https://safebooru.donmai.us/wiki_pages/bound_arms
- https://safebooru.donmai.us/wiki_pages/gag
- https://safebooru.donmai.us/wiki_pages/dildo
- https://safebooru.donmai.us/wiki_pages/rope

Supplementary 2026 wiki snapshot:
- https://huggingface.co/datasets/lylogummy/danbooru_wikis_2026

## Final decision

**Danbooru Wiki + active Alias/Implication is the canonical semantic reference lane for Danbooru-origin Special identities.**

It should be used aggressively for scope and contradiction audits, while generation-response claims remain separately versioned/model-scoped.
