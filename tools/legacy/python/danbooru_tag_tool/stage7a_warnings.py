"""Evidence-only Stage 7A warning presentation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WarningNotice:
    code: str
    message: str
    severity: str
    special_ids: tuple[str, ...]


REQUIREMENT_MESSAGES = (
    ("ActorRequirementOverride", "needs_actor", "誰が行うかを決める必要があります"),
    ("BodypartRequirementOverride", "needs_bodypart", "対象の身体部位を決める必要があります"),
    ("ImplementRequirementOverride", "needs_implement", "使う器具・物体を決める必要があります"),
    ("PoseRequirementOverride", "needs_pose", "姿勢・体位を決める必要があります"),
    ("CameraRequirementOverride", "needs_camera", "見せ方・カメラ位置を決める必要があります"),
    ("SpatialAssignmentOverride", "needs_spatial_assignment", "どこに何を配置するか決める必要があります"),
)
AUDIT_ONLY_STATUSES = frozenset({"PROVISIONAL", "PROVISIONAL_CORRECTION", "REVIEW_REQUIRED"})


class Stage7AWarningPresenter:
    def __init__(self, knowledge, profile_store):
        self.knowledge = knowledge
        self.profile_store = profile_store

    def notices(self, selected_special_ids) -> tuple[WarningNotice, ...]:
        ids = tuple(dict.fromkeys(selected_special_ids))
        notices = []
        for special_id in ids:
            policy = self.knowledge.product_fit
            if policy.label(special_id):
                message = ("要確認：原語を保持しています。確定した意味への置換や関連候補の自動計算は行いません"
                           if not policy.allows(special_id, 'statistics') else
                           "参照用：検索・明示選択で利用できます。独立した通常候補には表示しません")
                notices.append(WarningNotice('product_fit_' + policy.verdict(special_id).lower(),
                                             message, 'information', (special_id,)))
            profile = self.profile_store.profiles.get(special_id)
            if profile is not None:
                for field, code, message in REQUIREMENT_MESSAGES:
                    if getattr(profile, field) is True:
                        notices.append(WarningNotice(code, message, "warning", (special_id,)))
                flags = {value.strip() for value in profile.SpecialFlags.replace(",", ";").split(";")
                         if value.strip()}
                if "ACTOR_SEPARATION_REQUIRED" in flags:
                    notices.append(WarningNotice(
                        "actor_separation_required",
                        "複数の人物を描き分ける必要があります",
                        "warning",
                        (special_id,),
                    ))
                if profile.PromptUseMode == "MODEL_DEPENDENT":
                    notices.append(WarningNotice(
                        "model_dependent",
                        "モデルによって出方が変わりやすいタグです",
                        "information",
                        (special_id,),
                    ))
                if profile.PromotionStatus in AUDIT_ONLY_STATUSES:
                    notices.append(WarningNotice(
                        "profile_not_final",
                        "このタグは意味・構造情報の一部が未確定です。タグ自体は使用できます",
                        "information",
                        (special_id,),
                    ))
            if self.knowledge.special[special_id].statistics_canonical is None:
                notices.append(WarningNotice(
                    "statistics_unavailable",
                    "このSpecialは関連候補の統計計算には使えません。Promptにはそのまま入ります",
                    "information",
                    (special_id,),
                ))

        by_canonical = {}
        for special_id in ids:
            canonical = self.knowledge.special[special_id].statistics_canonical
            if canonical is not None:
                by_canonical.setdefault(canonical, []).append(special_id)
        for matching_ids in by_canonical.values():
            if len(matching_ids) > 1:
                notices.append(WarningNotice(
                    "same_statistics_canonical",
                    "このSpecial同士は統計上、同じタグに対応しています。どちらも自動では削除しません",
                    "information",
                    tuple(matching_ids),
                ))
        return tuple(notices)
