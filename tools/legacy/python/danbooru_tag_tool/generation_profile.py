"""Read-only static generation metadata and model observations for Special2788."""
from __future__ import annotations

import csv
from dataclasses import dataclass, fields
from pathlib import Path
from types import MappingProxyType

from .models import SpecialTag


PROMOTION_STATUSES = frozenset({
    "APPROVED_STATIC", "APPROVED_IDENTITY_ONLY", "APPROVED_SEMANTIC_ROLE",
    "APPROVED_CORRECTION_METADATA", "PROVISIONAL", "PROVISIONAL_CORRECTION",
    "REVIEW_REQUIRED",
})
APPROVED_STATUSES = frozenset(status for status in PROMOTION_STATUSES
                              if status.startswith("APPROVED_"))
AUDIT_ONLY_STATUSES = PROMOTION_STATUSES - APPROVED_STATUSES
PROMPT_USE_MODES = frozenset({
    "DIRECT", "STRUCTURED", "SUPPORT", "REFERENCE_ONLY", "ALIAS_PRESERVE",
    "MODEL_DEPENDENT",
})
OBSERVATION_TEST_TYPES = frozenset({"SINGLE", "COMBINATION", "STRESS"})
REQUIREMENT_OVERRIDE_FIELDS = (
    "ActorRequirementOverride", "BodypartRequirementOverride",
    "ImplementRequirementOverride", "PoseRequirementOverride",
    "CameraRequirementOverride", "SpatialAssignmentOverride",
)


@dataclass(frozen=True, slots=True)
class GenerationProfile:
    SpecialID: str
    Tag: str
    PromotionStatus: str
    MeaningStatus: str = ""
    MeaningConfidence: str = ""
    SourceGlossQuality: str = ""
    GenerationFamily: str = ""
    GenerationRole: str = ""
    PromptUseMode: str = ""
    FamilyRuleId: str = ""
    CompositionRoleOverride: str = ""
    ActorRequirementOverride: bool | None = None
    BodypartRequirementOverride: bool | None = None
    ImplementRequirementOverride: bool | None = None
    PoseRequirementOverride: bool | None = None
    CameraRequirementOverride: bool | None = None
    SpatialAssignmentOverride: bool | None = None
    ShapeConflictGroup: str = ""
    SpecialFlags: str = ""
    RecommendedHandling: str = ""
    EvidenceClass: str = ""
    EvidenceRefs: str = ""

    def __post_init__(self):
        if not isinstance(self.SpecialID, str) or not self.SpecialID.strip():
            raise ValueError("SpecialID is required")
        if not isinstance(self.Tag, str) or not self.Tag.strip():
            raise ValueError("Tag is required")
        if self.PromotionStatus not in PROMOTION_STATUSES:
            raise ValueError("Invalid PromotionStatus")
        if self.PromptUseMode and self.PromptUseMode not in PROMPT_USE_MODES:
            raise ValueError("Invalid PromptUseMode")
        for name in REQUIREMENT_OVERRIDE_FIELDS:
            value = getattr(self, name)
            if value is not None and type(value) is not bool:
                raise ValueError(f"{name} must be blank/true/false")
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name not in REQUIREMENT_OVERRIDE_FIELDS and not isinstance(value, str):
                raise ValueError(f"{field.name} must be text")
        if self.PromotionStatus in AUDIT_ONLY_STATUSES and any((
            self.MeaningStatus, self.MeaningConfidence, self.SourceGlossQuality,
            self.GenerationFamily, self.GenerationRole, self.PromptUseMode,
            self.FamilyRuleId, self.CompositionRoleOverride,
            *(getattr(self, name) for name in REQUIREMENT_OVERRIDE_FIELDS),
            self.ShapeConflictGroup, self.RecommendedHandling,
        )):
            raise ValueError("Audit-only profile must not promote production semantics")

    @property
    def is_approved(self) -> bool:
        return self.PromotionStatus in APPROVED_STATUSES

    @property
    def is_audit_only(self) -> bool:
        return self.PromotionStatus in AUDIT_ONLY_STATUSES


PROFILE_COLUMNS = tuple(field.name for field in fields(GenerationProfile))


@dataclass(frozen=True, slots=True)
class GenerationFamilyRule:
    FamilyRuleId: str
    GenerationFamily: str
    DefaultPromptUseMode: str
    DefaultNeedsActor: bool | None
    DefaultNeedsBodypart: bool | None
    DefaultNeedsImplement: bool | None
    DefaultNeedsPose: bool | None
    DefaultNeedsCamera: bool | None
    DefaultNeedsSpatialAssignment: bool | None
    DefaultCompositionRole: str
    Notes: str

    def __post_init__(self):
        if not self.FamilyRuleId or not self.GenerationFamily:
            raise ValueError("Family rule ID/family required")
        if self.DefaultPromptUseMode not in PROMPT_USE_MODES:
            raise ValueError("Invalid family DefaultPromptUseMode")
        for name in (
            "DefaultNeedsActor", "DefaultNeedsBodypart", "DefaultNeedsImplement",
            "DefaultNeedsPose", "DefaultNeedsCamera", "DefaultNeedsSpatialAssignment",
        ):
            value = getattr(self, name)
            if value is not None and type(value) is not bool:
                raise ValueError(f"{name} must be blank/true/false")


FAMILY_RULE_COLUMNS = tuple(field.name for field in fields(GenerationFamilyRule))


@dataclass(frozen=True, slots=True)
class GenerationModelObservation:
    ObservationID: str
    ModelProfile: str
    Checkpoint: str
    Seed: str
    Steps: str
    CFG: str
    Size: str
    Sampler: str
    Scheduler: str
    TestType: str
    SpecialIDs: tuple[str, ...]
    SupportTags: str
    StandaloneRecognition: str
    ActorSeparation: str
    SpatialAssignment: str
    CompositionRetention: str
    PlacementMode: str
    Result: str
    FailureModes: str
    Notes: str
    EvidenceImagePaths: str

    def __post_init__(self):
        if not self.ObservationID or not self.ModelProfile or not self.Checkpoint:
            raise ValueError("Observation identity/model/checkpoint required")
        if self.TestType not in OBSERVATION_TEST_TYPES:
            raise ValueError("Invalid observation TestType")
        if (not isinstance(self.SpecialIDs, tuple) or not self.SpecialIDs
                or any(not isinstance(sid, str) or not sid for sid in self.SpecialIDs)
                or len(set(self.SpecialIDs)) != len(self.SpecialIDs)):
            raise ValueError("SpecialIDs must be a nonempty unique tuple")
        for field in fields(self):
            if field.name != "SpecialIDs" and not isinstance(getattr(self, field.name), str):
                raise ValueError(f"{field.name} must be text")


OBSERVATION_COLUMNS = tuple(field.name for field in fields(GenerationModelObservation))


@dataclass(frozen=True, slots=True)
class EffectiveGenerationProfile:
    SpecialID: str
    PromotionStatus: str
    PromptUseMode: str | None
    NeedsActor: bool | None
    NeedsBodypart: bool | None
    NeedsImplement: bool | None
    NeedsPose: bool | None
    NeedsCamera: bool | None
    NeedsSpatialAssignment: bool | None
    CompositionRole: str | None
    AllowsAutomaticExpansion: bool = False


@dataclass(frozen=True, slots=True)
class ProfiledSpecial:
    special: SpecialTag
    generation_profile: GenerationProfile | None


def _read_rows(path: Path | None, columns: tuple[str, ...]):
    if path is None:
        return ()
    try:
        stream = Path(path).open(encoding="utf-8-sig", newline="")
    except FileNotFoundError:
        return ()
    with stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(columns):
            raise ValueError("Unexpected columns/order")
        rows = []
        for line, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Invalid CSV row width at line {line}")
            rows.append((line, row))
        return tuple(rows)


def _optional_bool(value: str) -> bool | None:
    try:
        return {"": None, "true": True, "false": False}[value]
    except KeyError as exc:
        raise ValueError("Boolean must be blank/true/false") from exc


def load_generation_profiles(path: Path | None):
    result = {}
    for line, row in _read_rows(path, PROFILE_COLUMNS):
        try:
            for name in REQUIREMENT_OVERRIDE_FIELDS:
                row[name] = _optional_bool(row[name])
            profile = GenerationProfile(**row)
            if profile.SpecialID in result:
                raise ValueError("Duplicate SpecialID")
            result[profile.SpecialID] = profile
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Generation profile line {line}: {exc}") from exc
    return MappingProxyType(result)


def load_generation_family_rules(path: Path | None):
    result = {}
    bool_fields = (
        "DefaultNeedsActor", "DefaultNeedsBodypart", "DefaultNeedsImplement",
        "DefaultNeedsPose", "DefaultNeedsCamera", "DefaultNeedsSpatialAssignment",
    )
    for line, row in _read_rows(path, FAMILY_RULE_COLUMNS):
        try:
            for name in bool_fields:
                row[name] = _optional_bool(row[name])
            rule = GenerationFamilyRule(**row)
            if rule.FamilyRuleId in result:
                raise ValueError("Duplicate FamilyRuleId")
            result[rule.FamilyRuleId] = rule
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Generation family rule line {line}: {exc}") from exc
    return MappingProxyType(result)


def load_generation_model_observations(path: Path | None):
    result = {}
    for line, row in _read_rows(path, OBSERVATION_COLUMNS):
        try:
            row["SpecialIDs"] = tuple(filter(None, row["SpecialIDs"].split(";")))
            observation = GenerationModelObservation(**row)
            if observation.ObservationID in result:
                raise ValueError("Duplicate ObservationID")
            result[observation.ObservationID] = observation
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Generation observation line {line}: {exc}") from exc
    return MappingProxyType(result)


def join_generation_profiles(special, profiles):
    """Left join by existing ID; Tag is a drift guard, never a fallback key."""
    result = {}
    for sid, tag in special.items():
        profile = profiles.get(sid)
        if profile is not None and (profile.SpecialID != sid or profile.Tag != tag.term):
            raise ValueError(f"Generation profile ID/Tag mismatch: {sid}")
        result[sid] = ProfiledSpecial(tag, profile)
    return MappingProxyType(result)


class GenerationProfileStore:
    """Inspection-only view; no prompt support is inserted by this class."""

    def __init__(self, special, profiles, family_rules=None, observations=None):
        self.special = special
        self.profiles = MappingProxyType(dict(profiles))
        self.family_rules = MappingProxyType(dict(family_rules or {}))
        self.observations = MappingProxyType(dict(observations or {}))
        self.joined = join_generation_profiles(special, self.profiles)
        for profile in self.profiles.values():
            if profile.SpecialID not in special:
                continue
            if profile.FamilyRuleId:
                rule = self.family_rules.get(profile.FamilyRuleId)
                if rule is None or rule.GenerationFamily != profile.GenerationFamily:
                    raise ValueError("Unknown/mismatched generation family rule")
        for observation in self.observations.values():
            if not set(observation.SpecialIDs) <= set(special):
                raise ValueError("Observation references unknown SpecialID")

    @classmethod
    def load(cls, root: Path, special):
        directory = Path(root) / "data/generation"
        return cls(
            special,
            load_generation_profiles(directory / "special2788_generation_profile.csv"),
            load_generation_family_rules(directory / "generation_family_rules.csv"),
            load_generation_model_observations(directory / "generation_model_observations.csv"),
        )

    def effective_profile(self, special_id: str) -> EffectiveGenerationProfile:
        profile = self.profiles[special_id]
        rule = self.family_rules.get(profile.FamilyRuleId) if profile.FamilyRuleId else None

        def requirement(override_name: str, default_name: str):
            override = getattr(profile, override_name)
            return override if override is not None else (getattr(rule, default_name) if rule else None)

        return EffectiveGenerationProfile(
            SpecialID=special_id,
            PromotionStatus=profile.PromotionStatus,
            PromptUseMode=profile.PromptUseMode or (rule.DefaultPromptUseMode if rule else None),
            NeedsActor=requirement("ActorRequirementOverride", "DefaultNeedsActor"),
            NeedsBodypart=requirement("BodypartRequirementOverride", "DefaultNeedsBodypart"),
            NeedsImplement=requirement("ImplementRequirementOverride", "DefaultNeedsImplement"),
            NeedsPose=requirement("PoseRequirementOverride", "DefaultNeedsPose"),
            NeedsCamera=requirement("CameraRequirementOverride", "DefaultNeedsCamera"),
            NeedsSpatialAssignment=requirement(
                "SpatialAssignmentOverride", "DefaultNeedsSpatialAssignment"
            ),
            CompositionRole=(profile.CompositionRoleOverride
                             or (rule.DefaultCompositionRole if rule else None)
                             or None),
            AllowsAutomaticExpansion=False,
        )
