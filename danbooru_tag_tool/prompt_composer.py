"""Stage9A pure, local Prompt Composer. No candidate discovery or UI state."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from .normalization import normalize_lookup, split_prompt_input
from .prompt_formatter import PromptFormatter
from .stage8b_support import SemanticSupportRelation, SupportKnowledgeStore


BLOCK_ORDER = (
    "META_QUALITY", "COUNT", "RELATION", "IDENTITY", "SPECIAL",
    "SUPPORT_STRUCTURE", "POSE_COMPOSITION", "GENERAL_AUX", "BACKGROUND_LIGHT", "LORA",
)
MODEL_FAMILIES = frozenset({"GENERIC", "ILLUSTRIOUS", "WAI_ILLUSTRIOUS", "NOOBAI", "ANIMA"})
LANES = frozenset({"SEMANTIC_CORE", "SEMANTIC_OPTIONAL", "SEMANTIC_AUX",
                   "COOCCURRENCE", "USER_EXPLICIT"})


@dataclass(frozen=True, slots=True)
class NegativeRule:
    rule_id: str
    model_family: str
    negative_token: str = "nsfw"
    profile_id: str | None = None

    def __post_init__(self):
        if not self.rule_id or self.model_family not in MODEL_FAMILIES:
            raise ValueError("Negative rule requires an explicit supported model scope")


@dataclass(frozen=True, slots=True)
class ComposerProfile:
    profile_id: str = "stage9a_baseline"
    model_family: str = "GENERIC"
    block_order: tuple[str, ...] = BLOCK_ORDER
    special_slot_position: int = 4
    negative_rule_set: tuple[NegativeRule, ...] = ()
    validation_status: str = "STAGE9_DESIGN_CANDIDATE"
    notes: str = "Baseline ordering; not Stage10 image-validated."

    def __post_init__(self):
        if not self.profile_id or self.model_family not in MODEL_FAMILIES:
            raise ValueError("Unsupported Composer profile/model family")
        if len(self.block_order) != len(BLOCK_ORDER) or set(self.block_order) != set(BLOCK_ORDER):
            raise ValueError("block_order must contain every block exactly once")
        if not 0 <= self.special_slot_position < len(BLOCK_ORDER):
            raise ValueError("Invalid Special position")

    @property
    def effective_block_order(self) -> tuple[str, ...]:
        order = [block for block in self.block_order if block != "SPECIAL"]
        order.insert(self.special_slot_position, "SPECIAL")
        return tuple(order)


@dataclass(frozen=True, slots=True)
class SupportOverride:
    canonical: str
    state: Literal["INCLUDE", "EXCLUDE"]
    reason: str = "user explicit choice"

    def __post_init__(self):
        if self.state not in {"INCLUDE", "EXCLUDE"}:
            raise ValueError("Invalid support override")


@dataclass(frozen=True, slots=True)
class ComposerInput:
    """Explicitly classified input; later lanes keep their supplied evidence/order.

    A canonical uses the existing authority and renderer. Literal text is kept
    intact (including LoRA invocations); no role/semantic inference is performed.
    """
    input_id: str
    text: str = ""
    canonical: str | None = None
    block: str = "GENERAL_AUX"
    lane: str = "USER_EXPLICIT"
    selected: bool | None = None
    provenance: tuple[str, ...] = ()
    evidence: tuple[tuple[str, str | int | float], ...] = ()

    reason: str = "explicitly supplied selection"
    def __post_init__(self):
        if not self.input_id or (not self.text.strip() and self.canonical is None):
            raise ValueError("Input identity and text/canonical required")
        if self.block not in BLOCK_ORDER or self.block == "SPECIAL" or self.lane not in LANES:
            raise ValueError("Invalid input block/lane; Specials use selected Special IDs")

        if not self.reason:
            raise ValueError("Input reason is required")

@dataclass(frozen=True, slots=True)
class ComposerAtom:
    atom_id: str
    text: str
    canonical: str | None
    block: str
    source_lanes: tuple[str, ...]
    selected: bool
    user_override: str = "DEFAULT"
    special_owners: tuple[str, ...] = ()
    support_relations: tuple[SemanticSupportRelation, ...] = ()
    provenance: tuple[str, ...] = ()
    weight: float | None = None
    reason: str = ""
    merged_into: str | None = None
    evidence: tuple[tuple[str, str | int | float], ...] = ()


@dataclass(frozen=True, slots=True)
class ComposerWarning:
    code: str
    severity: str
    atom_ids: tuple[str, ...]
    message: str


@dataclass(frozen=True, slots=True)
class ComposerPlan:
    selected_special_ids: tuple[str, ...]
    candidate_atoms: tuple[ComposerAtom, ...]
    selected_atoms: tuple[ComposerAtom, ...]
    suppressed_atoms: tuple[ComposerAtom, ...]
    warnings: tuple[ComposerWarning, ...]
    profile: ComposerProfile


@dataclass(frozen=True, slots=True)
class ComposeResult:
    plan: ComposerPlan
    positive_blocks: tuple[tuple[str, tuple[ComposerAtom, ...]], ...]
    positive_prompt: str
    negative_prompt: str
    warnings: tuple[ComposerWarning, ...]
    provenance_map: dict[str, ComposerAtom]
    profile_id: str
    block_order: tuple[str, ...]


def _union(first, second):
    return tuple(dict.fromkeys((*first, *second)))


class PromptComposer:
    def __init__(self, knowledge, support: SupportKnowledgeStore):
        self.knowledge = knowledge
        self.support = support

    def _canonical(self, text: str) -> str:
        resolution = self.knowledge.resolve_exact(text)
        canonical = resolution.resolved_canonical
        if resolution.match_type not in {"canonical", "alias"} or canonical is None:
            raise ValueError(f"Canonical or unambiguous authority alias required: {text!r}")
        return canonical

    def _token_key(self, text: str) -> str:
        resolution = self.knowledge.resolve_exact(text)
        if resolution.match_type in {"canonical", "alias"} and resolution.resolved_canonical:
            return normalize_lookup(resolution.resolved_canonical)
        return normalize_lookup(text)

    def compose(
        self, selected_special_ids, *, inputs: tuple[ComposerInput, ...] = (),
        overrides: tuple[SupportOverride, ...] = (), negative_prompt: str = "",
        profile: ComposerProfile = ComposerProfile(), model_family: str | None = None,
        adult_intent: bool = False,
    ) -> ComposeResult:
        ids = tuple(dict.fromkeys(selected_special_ids))
        if any(sid not in self.knowledge.special for sid in ids):
            raise ValueError("Unknown selected Special identity")
        if len({item.input_id for item in inputs}) != len(inputs):
            raise ValueError("Duplicate input identity")
        warnings = []
        active_family = model_family or profile.model_family
        scope_ok = active_family == profile.model_family
        if active_family not in MODEL_FAMILIES or not scope_ok:
            warnings.append(ComposerWarning("PROFILE_SCOPE_MISMATCH", "CAUTION", (),
                                            "Selected profile does not match active model family."))
        atoms = []
        for sid in ids:
            tag = self.knowledge.special[sid]
            atoms.append(ComposerAtom(
                f"special:{sid}", PromptFormatter.format_special(tag).text, None,
                "SPECIAL", ("SPECIAL",), True, special_owners=(sid,),
                provenance=(f"special:{sid}",), reason="selected Special identity",
            ))
        candidates = self.support.candidates(ids)
        override_by_canonical = {}
        for override in overrides:
            canonical = self._canonical(override.canonical)
            if canonical in override_by_canonical:
                raise ValueError("Duplicate support override; supply one final user decision")
            override_by_canonical[canonical] = override
        if set(override_by_canonical) - {candidate.canonical for candidate in candidates}:
            raise ValueError("Override does not identify a supplied semantic support candidate")
        for candidate in candidates:
            relations = candidate.relations
            default_on = any(r.support_class == "CORE_SUPPORT" and
                             r.combination_mode == "ADDITIVE" for r in relations)
            override = override_by_canonical.get(candidate.canonical)
            selected = override.state == "INCLUDE" if override else default_on
            lanes = tuple(dict.fromkeys(
                "SEMANTIC_CORE" if r.support_class == "CORE_SUPPORT" else "SEMANTIC_OPTIONAL"
                for r in relations
            ))
            # Resolver order is authoritative, including explicit-over-Family.
            block = ("POSE_COMPOSITION" if relations[0].support_slot in
                     {"POSE", "CAMERA_COMPOSITION"} else "SUPPORT_STRUCTURE")
            atoms.append(ComposerAtom(
                f"support:{candidate.canonical}",
                PromptFormatter.format_tag(self.knowledge.canonical[candidate.canonical]).text,
                candidate.canonical, block, lanes, selected,
                override.state if override else "DEFAULT", support_relations=relations,
                provenance=tuple(r.provenance for r in relations),
                reason=(override.reason if override else
                        "CORE_SUPPORT + ADDITIVE" if default_on else "suggested; user choice required"),
            ))
        for item in inputs:
            canonical = self._canonical(item.canonical) if item.canonical is not None else None
            text = (PromptFormatter.format_tag(self.knowledge.canonical[canonical]).text
                    if canonical is not None else item.text)
            chosen = item.selected if item.selected is not None else item.lane == "USER_EXPLICIT"
            atoms.append(ComposerAtom(
                f"input:{item.input_id}", text, canonical, item.block, (item.lane,),
                chosen, ("DEFAULT" if item.selected is None else "INCLUDE" if chosen else "EXCLUDE"),
                provenance=(f"input:{item.input_id}", *item.provenance),
                reason=item.reason, evidence=item.evidence,
            ))

        # Specials are traversed first, independently of their render position.
        # Only rendered identity is compared for Specials: chosen_canonical must
        # never replace an alias/semantic Special's own text.
        emitted = {}
        suppressed = []
        for atom in atoms:
            key = ("lora", atom.text) if atom.block == "LORA" else ("tag", normalize_lookup(atom.text))
            target = emitted.get(key)
            if target is not None and (atom.selected or target.special_owners and atom.support_relations):
                reason = "satisfied_by_special" if target.special_owners else "exact rendered token dedupe"
                if atom.user_override == "EXCLUDE":
                    suppressed.append(atom)
                    continue
                emitted[key] = replace(
                    target, special_owners=_union(target.special_owners, atom.special_owners),
                    support_relations=_union(target.support_relations, atom.support_relations),
                    source_lanes=_union(target.source_lanes, atom.source_lanes),
                    provenance=_union(target.provenance, atom.provenance),
                    evidence=(*target.evidence, *atom.evidence),
                )
                suppressed.append(replace(atom, selected=False, merged_into=target.atom_id, reason=reason))
            elif atom.selected:
                emitted[key] = atom
            else:
                suppressed.append(atom)
        # A selected candidate can satisfy default-off suggestions from any
        # lane. Preserve each source's evidence/provenance on the rendered
        # atom without treating lane order or rank as a semantic score.
        for i, atom in enumerate(suppressed):
            key = ("tag", normalize_lookup(atom.text))
            target = emitted.get(key)
            if target is not None and atom.merged_into is None:
                emitted[key] = replace(
                    target, support_relations=_union(target.support_relations, atom.support_relations),
                    source_lanes=_union(target.source_lanes, atom.source_lanes),
                    provenance=_union(target.provenance, atom.provenance),
                    evidence=(*target.evidence, *atom.evidence),
                )
                suppressed[i] = replace(
                    atom, merged_into=target.atom_id,
                    reason=("satisfied_by_explicit_input" if atom.support_relations
                            else "same_canonical_selected_in_another_lane"),
                )
        order = profile.effective_block_order
        selected = tuple(atom for block in order for atom in emitted.values() if atom.block == block)
        negative_keys = {self._token_key(token) for token in split_prompt_input(negative_prompt)}
        for atom in selected:
            if self._token_key(atom.text) in negative_keys:
                warnings.append(ComposerWarning("POSITIVE_NEGATIVE_EXACT", "CONFLICT", (atom.atom_id,),
                                                f"Positive token also appears in Negative: {atom.text}"))
        for rule in profile.negative_rule_set:
            in_scope = (scope_ok and rule.model_family == active_family and
                        (rule.profile_id is None or rule.profile_id == profile.profile_id))
            if not in_scope:
                warnings.append(ComposerWarning("RULE_SCOPE_MISMATCH", "CAUTION", (),
                                                f"Negative rule not applied outside its scope: {rule.rule_id}"))
            elif adult_intent and self._token_key(rule.negative_token) in negative_keys:
                warnings.append(ComposerWarning("ADULT_NEGATIVE_CONFLICT", "CONFLICT", (),
                                                f"Adult intent conflicts with Negative ({rule.rule_id})."))
        groups = {}
        for atom in selected:
            for relation in atom.support_relations:
                if relation.choice_group:
                    # Group labels belong to the owner, not a global ontology.
                    key = (relation.owner_special_id, relation.choice_group)
                    groups[key] = _union(groups.get(key, ()), (atom.atom_id,))
        for (owner, group), members in groups.items():
            if len(members) > 1:
                warnings.append(ComposerWarning("CHOICE_GROUP_MULTIPLE", "CONFLICT", members,
                                                f"Multiple selected alternatives: {owner}/{group}"))
        plan = ComposerPlan(ids, tuple(atoms), selected, tuple(suppressed), tuple(warnings), profile)
        blocks = tuple((block, tuple(atom for atom in selected if atom.block == block)) for block in order)
        return ComposeResult(plan, blocks, ", ".join(atom.text for atom in selected), negative_prompt,
                             plan.warnings, {atom.text: atom for atom in selected}, profile.profile_id, order)
