#!/usr/bin/env python3
"""Issue #30 screening-first calibration pilot runner.

This is intentionally a thin, local-only runner.  It writes generated images
and evaluator artifacts outside the repository and never writes data/**.
Human labels are not inferred; the run stops with a blinded review queue.
"""
from __future__ import annotations

import base64
import atexit
import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

requests = None
np = None
Image = None
ImageDraw = None
ImageFont = None

ROOT = Path(__file__).resolve().parents[1]
CASE_MANIFEST = ROOT / "docs/testing/ISSUE30_REAL_IMAGE_CALIBRATION_CASES_20260910.csv"
PROFILE = ROOT / "data/generation/special2788_generation_profile.csv"
FORGE_API = os.environ.get("ISSUE30_FORGE_API", "http://127.0.0.1:7860")
RUN_ROOT = Path(os.environ.get(
    "ISSUE30_PILOT_ROOT",
    r"C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_pilot_20260910",
))
KAGAMI_ROOT = Path(os.environ.get(
    "ISSUE30_KAGAMI_ROOT",
    r"C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\kagami-24k",
))
CL_ROOT = Path(os.environ.get(
    "ISSUE30_CL_ROOT",
    r"C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\cl_tagger_v2\v2_00",
))

RUN_ID = os.environ.get("ISSUE30_RUN_ID", "issue30-pilot-20260910")
NEGATIVE = "lowres, blurry, text, watermark, jpeg artifacts"
STEPS = 24
CFG = 4.5
WIDTH = 1024
HEIGHT = 1024
SAMPLER = "Euler a"
SCHEDULER = "Automatic"
CHECKPOINT = "waiIllustriousSDXL_v170.safetensors"
CHECKPOINT_HASH = "f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04"
FORGE_VERSION = "neo-2.29"
SEED_BASE = 30000
THRESHOLDS = {"WD14": 0.50, "Kagami": 0.37, "CL": 0.50}


def ensure_runtime_dependencies() -> None:
    """Load generation/evaluator dependencies only after dry-run validation."""
    global requests, np, Image, ImageDraw, ImageFont
    if requests is None:
        import requests as requests_module
        import numpy as numpy_module
        from PIL import Image as image_module
        from PIL import ImageDraw as image_draw_module
        from PIL import ImageFont as image_font_module
        requests = requests_module
        np = numpy_module
        Image = image_module
        ImageDraw = image_draw_module
        ImageFont = image_font_module


def norm(value: Any) -> str:
    value = str(value or "").strip().casefold().replace("_", " ")
    value = re.sub(r"[()\[\]{}]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_gzip_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, separators=(",", ":"))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_gzip_json(path: Path) -> Any:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def load_cases(manifest_path: Path = CASE_MANIFEST) -> list[dict[str, str]]:
    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        cases = list(csv.DictReader(handle))
    if not cases:
        raise RuntimeError(f"case manifest is empty: {manifest_path}")
    required = {"case_id", "special_ids", "canonical", "relation_binding_required", "question"}
    missing = sorted(required - set(cases[0]))
    if missing:
        raise RuntimeError(f"case manifest is missing columns: {', '.join(missing)}")
    if len({case["case_id"] for case in cases}) != len(cases):
        raise RuntimeError("case manifest contains duplicate case_id values")
    if len(cases) > 32:
        raise RuntimeError(f"case manifest exceeds 32-case safety bound: {len(cases)}")
    if len(cases) * 4 > 128:
        raise RuntimeError("hard upper bound exceeded")
    return cases


def load_profiles() -> dict[int, dict[str, str]]:
    with PROFILE.open(encoding="utf-8-sig", newline="") as handle:
        return {int(row["SpecialID"]): row for row in csv.DictReader(handle)}


def validate_cases(cases: list[dict[str, str]], profiles: dict[int, dict[str, str]]) -> None:
    for case in cases:
        try:
            special_ids = [int(value) for value in case["special_ids"].split("|")]
        except ValueError as exc:
            raise RuntimeError(f"invalid special_ids for {case['case_id']}: {case['special_ids']}") from exc
        for special_id in special_ids:
            if special_id not in profiles:
                raise RuntimeError(f"unknown current project Special ID {special_id} in {case['case_id']}")
        if not case["canonical"].strip():
            raise RuntimeError(f"empty canonical value for {case['case_id']}")


def acquire_run_lock() -> Path:
    """Prevent two pilot runners from writing the same local run root."""
    lock = RUN_ROOT / ".run.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()}\nrun_id={RUN_ID}\n")
    except FileExistsError as exc:
        raise RuntimeError(f"pilot run lock already exists: {lock}") from exc

    def release() -> None:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass

    atexit.register(release)
    return lock


def forge_process_count() -> int | None:
    """Return the number of independent Forge launch trees on Windows.

    Stability Matrix can expose a normal parent/child pair with the same
    ``launch.py`` command line.  Count only roots, so that pair is accepted
    while two separately launched Forge trees are rejected.
    """
    if os.name != "nt":
        return None
    command = (
        "$ps=@(Get-CimInstance Win32_Process | Where-Object { "
        "($_.Name -eq 'python.exe') -and "
        "([string]$_.CommandLine -like '*Stable Diffusion WebUI Forge - Neo*') -and "
        "([string]$_.CommandLine -like '*launch.py*') }); "
        "$ids=@($ps | ForEach-Object { [int]$_.ProcessId }); "
        "$roots=@($ps | Where-Object { $ids -notcontains [int]$_.ParentProcessId }); "
        "$roots.Count"
    )
    result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, timeout=20)
    text = result.stdout.strip()
    return int(text) if result.returncode == 0 and text.isdigit() else None


def assert_forge_runtime(session: requests.Session, expected_checkpoint: str) -> None:
    count = forge_process_count()
    if count is not None and count != 1:
        raise RuntimeError(f"Forge process count is {count}; expected exactly one Forge Neo process")
    options = session.get(FORGE_API + "/sdapi/v1/options", timeout=30).json()
    loaded = str(options.get("sd_model_checkpoint", ""))
    if expected_checkpoint not in loaded:
        raise RuntimeError(f"Forge checkpoint changed during pilot: {loaded}")


def canonical_parts(case: dict[str, str]) -> list[str]:
    raw = case["canonical"]
    return [x.strip() for x in re.split(r"\s*\+\s*|\s*,\s*", raw) if x.strip()]


def prompts(case: dict[str, str], cell: str) -> tuple[str, str]:
    if cell.startswith("target_present") and case.get("target_prompt"):
        return case["target_prompt"], case.get("target_negative_prompt") or NEGATIVE
    if cell.startswith("contrast") and case.get("contrast_prompt"):
        return case["contrast_prompt"], case.get("contrast_negative_prompt") or NEGATIVE
    relation = case["relation_binding_required"].casefold() == "true"
    subject = "2people" if relation else "1girl, solo"
    parts = canonical_parts(case)
    target = ", ".join(parts)
    if cell.startswith("target_present"):
        return f"masterpiece, best quality, {subject}, {target}, simple background", NEGATIVE
    if len(parts) > 1:
        remaining = parts[0]
        return f"masterpiece, best quality, {subject}, {remaining}, simple background", NEGATIVE
    if relation:
        return f"masterpiece, best quality, {subject}, standing, simple background", NEGATIVE
    return "masterpiece, best quality, 1girl, solo, standing, simple background", NEGATIVE


def generation_settings(case: dict[str, str]) -> dict[str, Any]:
    """Use manifest settings when present, retaining Phase 1 defaults."""
    return {
        "sampler_name": case.get("sampler") or SAMPLER,
        "scheduler": case.get("scheduler") or SCHEDULER,
        "steps": int(case.get("steps") or STEPS),
        "cfg_scale": float(case.get("cfg") or CFG),
        "width": int(case.get("width") or WIDTH),
        "height": int(case.get("height") or HEIGHT),
    }


def seed_for(case_index: int, cell: str, case: dict[str, str] | None = None) -> int:
    # Target and contrast deliberately share the same two seeds.
    if case is not None:
        explicit = case.get("seed_a" if cell.endswith("seed_a") else "seed_b")
        if explicit:
            return int(explicit)
    offset = 0 if cell.endswith("seed_a") else 1
    return SEED_BASE + case_index * 10 + offset


def png_info(session: requests.Session, raw: bytes) -> dict[str, Any]:
    payload = {"image": "data:image/png;base64," + base64.b64encode(raw).decode("ascii")}
    response = session.post(FORGE_API + "/sdapi/v1/png-info", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def generate_one(session: requests.Session, case: dict[str, str], case_index: int, cell: str,
                 allow_generate: bool = True) -> dict[str, Any]:
    prompt, negative = prompts(case, cell)
    seed = seed_for(case_index, cell, case)
    settings = generation_settings(case)
    image_id = f"{case['case_id']}__{cell}"
    image_path = RUN_ROOT / "images" / f"{image_id}.png"
    artifact_base = RUN_ROOT / "generation" / image_id
    payload = {
        "prompt": prompt,
        "negative_prompt": negative,
        "seed": seed,
        **settings,
        "batch_size": 1,
        "n_iter": 1,
        "enable_hr": False,
        "restore_faces": False,
        "tiling": False,
    }
    if image_path.exists() and artifact_base.with_suffix(".request.json").exists() and artifact_base.with_suffix(".png-info.json").exists():
        with Image.open(image_path) as image:
            return {
                "image_id": image_id,
                "case": case,
                "cell": cell,
                "reused": True,
                "prompt": prompt,
                "negative_prompt": negative,
                "seed": seed,
                "image_path": str(image_path),
                "image_sha256": sha256_bytes(image_path.read_bytes()),
                "image_bytes": image_path.stat().st_size,
                "size": image.size,
                "png_metadata": {str(k): str(v) for k, v in image.info.items()},
                "png_info_artifact": str(artifact_base.with_suffix(".png-info.json")),
                "request": payload,
            }
    if not allow_generate:
        raise RuntimeError(f"screen-only mode found incomplete artifact set: {image_id}")
    assert_forge_runtime(session, "waiIllustriousSDXL_v170")
    response = None
    for attempt in range(1, 4):
        response = session.post(FORGE_API + "/sdapi/v1/txt2img", json=payload, timeout=900)
        if response.status_code < 500:
            break
        write_json(RUN_ROOT / "generation" / f"{image_id}.attempt{attempt}.error.json", {"status_code": response.status_code, "body": response.text[:4000]})
        if "same device" in response.text.casefold() or "cuda:0" in response.text.casefold():
            raise RuntimeError("Forge reported a GPU/CPU device mismatch; stop instead of retrying")
        time.sleep(5 * attempt)
    assert response is not None
    response.raise_for_status()
    result = response.json()
    encoded = result["images"][0].split(",", 1)[-1]
    raw = base64.b64decode(encoded)
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(raw)
    with Image.open(image_path) as image:
        size = image.size
        metadata = {str(k): str(v) for k, v in image.info.items()}
    info = png_info(session, raw)
    write_json(artifact_base.with_suffix(".request.json"), payload)
    write_json(artifact_base.with_suffix(".response.json"), {k: v for k, v in result.items() if k != "images"})
    write_json(artifact_base.with_suffix(".png-info.json"), info)
    return {
        "image_id": image_id,
        "case": case,
        "cell": cell,
        "reused": False,
        "prompt": prompt,
        "negative_prompt": negative,
        "seed": seed,
        "image_path": str(image_path),
        "image_sha256": sha256_bytes(raw),
        "image_bytes": len(raw),
        "size": size,
        "png_metadata": metadata,
        "png_info_artifact": str(artifact_base.with_suffix(".png-info.json")),
        "request": payload,
    }


def image_preprocess(path: Path, side: int, bgr: bool) -> np.ndarray:
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((side, side), Image.Resampling.BICUBIC)
        canvas = Image.new("RGB", (side, side), (255, 255, 255))
        canvas.paste(image, ((side - image.width) // 2, (side - image.height) // 2))
        array = np.asarray(canvas, dtype=np.float32) / 255.0
    array = (array - 0.5) / 0.5
    if bgr:
        array = array[:, :, ::-1]
    return np.ascontiguousarray(array.transpose(2, 0, 1)[None])


def normalized_pairs(value: Any) -> list[tuple[str, float]]:
    pairs: list[tuple[str, float]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (float, int)) and 0 <= float(item) <= 1:
                pairs.append((str(key), float(item)))
            elif isinstance(item, (dict, list)):
                pairs.extend(normalized_pairs(item))
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                tag = item.get("tag") or item.get("label") or item.get("name")
                score = item.get("score") or item.get("confidence") or item.get("probability")
                if tag is not None and isinstance(score, (int, float)):
                    pairs.append((str(tag), float(score)))
                else:
                    pairs.extend(normalized_pairs(item))
    elif isinstance(value, str):
        for tag, score in re.findall(r"([^,:]+):\s*(0?\.\d+|1(?:\.0+)?)", value):
            pairs.append((tag.strip(), float(score)))
    return sorted(pairs, key=lambda item: item[1], reverse=True)


def evaluator_record(name: str, version: str, vocab_revision: str, state: str,
                     score: float | None, tags: list[dict[str, Any]], basis: str,
                     observed: bool | None, artifact: Path, threshold: float | None) -> dict[str, Any]:
    return {
        "evaluator_name": name,
        "model_version": version,
        "vocabulary_revision": vocab_revision,
        "execution_state": state,
        "raw_score": score,
        "detected_tags": tags,
        "observation_basis": basis,
        "target_observed": observed,
        "threshold_used": threshold,
        "correctness": "UNASSESSABLE",
        "raw_output_artifact": str(artifact),
    }


def evaluator_artifact_path(name: str, image_id: str) -> Path:
    if name == "WD14":
        return RUN_ROOT / "raw" / "wd14" / f"{image_id}.json"
    if name == "Kagami":
        return RUN_ROOT / "raw" / "kagami" / f"{image_id}.json.gz"
    return RUN_ROOT / "raw" / "cl v2.00" / f"{image_id}.json.gz"


def target_score(pairs: list[tuple[str, float]], case: dict[str, str]) -> tuple[float | None, bool, str]:
    targets = {norm(x) for x in canonical_parts(case)}
    direct = [(score, tag) for tag, score in pairs if norm(tag) in targets]
    if direct:
        score, _ = max(direct)
        return score, True, "DIRECT"
    components = []
    for tag, score in pairs:
        nt = norm(tag)
        if any(piece in nt or nt in piece for piece in targets for piece in piece.split() if len(piece) > 2):
            components.append(score)
    if components:
        return max(components), True, "COMPONENT_PROXY"
    return None, False, "NONE"


def run_wd14(session: requests.Session, record: dict[str, Any], reuse_existing: bool = False) -> dict[str, Any]:
    raw = Path(record["image_path"]).read_bytes()
    payload = {
        "image": "data:image/png;base64," + base64.b64encode(raw).decode("ascii"),
        "model": "wd14-eva02.v3.large",
        "threshold": 0.0,
        "queue": "",
        "name_in_queue": "",
    }
    artifact = RUN_ROOT / "raw" / "wd14" / f"{record['image_id']}.json"
    if reuse_existing:
        if not artifact.exists():
            raise RuntimeError(f"missing cached WD14 artifact in screen-only mode: {artifact}")
        obj = read_json(artifact)
        if "error" in obj:
            raise RuntimeError(f"cached WD14 artifact is an error: {artifact}")
        pairs = normalized_pairs(obj)
        score, observed, basis = target_score(pairs, record["case"])
        tags = [{"tag": tag, "score": score} for tag, score in pairs[:200]]
        return evaluator_record("WD14", "wd14-eva02.v3.large", "runtime-interrogator", "OK", score, tags, basis, observed, artifact, THRESHOLDS["WD14"])
    try:
        response = session.post(FORGE_API + "/tagger/v1/interrogate", json=payload, timeout=300)
        response.raise_for_status()
        obj = response.json()
        write_json(artifact, obj)
        pairs = normalized_pairs(obj)
        score, observed, basis = target_score(pairs, record["case"])
        tags = [{"tag": tag, "score": score} for tag, score in pairs[:200]]
        return evaluator_record("WD14", "wd14-eva02.v3.large", "runtime-interrogator", "OK", score, tags, basis, observed, artifact, THRESHOLDS["WD14"])
    except Exception as exc:
        write_json(artifact, {"error": type(exc).__name__, "message": str(exc)})
        return evaluator_record("WD14", "wd14-eva02.v3.large", "runtime-interrogator", "ERROR", None, [], "UNVERIFIED", None, artifact, THRESHOLDS["WD14"])


def run_onnx(record: dict[str, Any], session: Any, tags: list[str], name: str,
             version: str, revision: str, side: int, bgr: bool, threshold: float,
             reuse_existing: bool = False) -> dict[str, Any]:
    artifact = RUN_ROOT / "raw" / name.lower() / f"{record['image_id']}.json.gz"
    if reuse_existing:
        if not artifact.exists():
            raise RuntimeError(f"missing cached {name} artifact in screen-only mode: {artifact}")
        obj = read_gzip_json(artifact)
        if "error" in obj:
            raise RuntimeError(f"cached {name} artifact is an error: {artifact}")
        pairs = [(str(tag), float(score)) for tag, score in obj["top_tags"]]
        score, observed, basis = target_score(pairs, record["case"])
        visible = [{"tag": tag, "score": score} for tag, score in pairs[:500] if score >= threshold]
        return evaluator_record(name, version, revision, "OK", score, visible, basis, observed, artifact, threshold)
    try:
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        values = session.run([output_name], {input_name: image_preprocess(Path(record["image_path"]), side, bgr)})[0][0].astype(np.float64)
        if "logit" in output_name.casefold():
            values = 1.0 / (1.0 + np.exp(-values))
        pairs = sorted(((tags[index], float(value)) for index, value in enumerate(values)), key=lambda item: item[1], reverse=True)
        score, observed, basis = target_score(pairs, record["case"])
        write_gzip_json(artifact, {"output_name": output_name, "scores": [float(x) for x in values], "top_tags": pairs[:500]})
        visible = [{"tag": tag, "score": score} for tag, score in pairs[:500] if score >= threshold]
        return evaluator_record(name, version, revision, "OK", score, visible, basis, observed, artifact, threshold)
    except Exception as exc:
        write_gzip_json(artifact, {"error": type(exc).__name__, "message": str(exc)})
        return evaluator_record(name, version, revision, "ERROR", None, [], "UNVERIFIED", None, artifact, threshold)


def score_band(results: dict[str, dict[str, Any]]) -> str:
    scores = [r["raw_score"] for r in results.values() if r["execution_state"] == "OK" and r["raw_score"] is not None]
    if len(scores) != 3:
        return "UNAVAILABLE"
    minimum = min(scores)
    if minimum >= 0.75:
        return "HIGH"
    if minimum >= 0.50:
        return "MEDIUM"
    return "LOW"


def screening(record: dict[str, Any], evaluators: dict[str, dict[str, Any]]) -> dict[str, Any]:
    case = record["case"]
    classes: list[str] = []
    relation = case["relation_binding_required"].casefold() == "true"
    states = [e["execution_state"] for e in evaluators.values()]
    votes = [e["target_observed"] for e in evaluators.values()]
    if relation:
        classes.append("RELATION_OR_BINDING")
    if any(state != "OK" for state in states):
        classes.append("BLOCKED")
    if case["desk_recommendation"] == "BLOCKED" and "BLOCKED" not in classes:
        classes.append("BLOCKED")
    if any(e["observation_basis"] == "COMPONENT_PROXY" for e in evaluators.values()) and not all(e["observation_basis"] == "DIRECT" for e in evaluators.values()):
        classes.append("COMPONENT_ONLY")
    if len(set(v for v in votes if v is not None)) > 1:
        classes.append("DISAGREEMENT")
    if any(v is None for v in votes) or any((e["raw_score"] is not None and e["threshold_used"] is not None and e["raw_score"] < e["threshold_used"]) for e in evaluators.values()):
        classes.append("LOW_CONFIDENCE")
    all_direct = all(e["execution_state"] == "OK" and e["observation_basis"] == "DIRECT" for e in evaluators.values())
    unanimous_positive = votes == [True, True, True]
    high = all_direct and unanimous_positive and not relation and case["desk_recommendation"] == "AUTO_CANDIDATE" and score_band(evaluators) == "HIGH"
    if high:
        classes.append("HIGH_CONFIDENCE_AUTO_LIKELY")
    if not classes:
        classes.append("LOW_CONFIDENCE")
    return {"classes": list(dict.fromkeys(classes)), "high": high, "band": score_band(evaluators), "relation": relation}


def routing(results: dict[str, dict[str, Any]], screen: dict[str, Any]) -> list[dict[str, str]]:
    votes = {key: value["target_observed"] is True for key, value in results.items()}
    ready = all(value["execution_state"] == "OK" for value in results.values())
    relation = screen["relation"]
    positive = list(votes.values())
    decisions: dict[str, bool] = {
        "WD14_ALONE": votes["wd14"], "KAGAMI_ALONE": votes["kagami"], "CL_ALONE": votes["cl_v2_00"],
        "OR": any(positive), "AND": all(positive), "MAJORITY": sum(positive) >= 2,
        "CL_PRIMARY_SUPPORT": votes["cl_v2_00"] and (votes["wd14"] or votes["kagami"]),
        "DISAGREEMENT_TO_HUMAN": False,
        "LIMITED_COMPONENT_PROXY": any(v["observation_basis"] == "COMPONENT_PROXY" for v in results.values()),
    }
    output = []
    for strategy, candidate in decisions.items():
        if not ready:
            decision, reason = "BLOCKED", "one or more evaluator executions failed"
        elif relation:
            decision, reason = "HUMAN_REVIEW_REQUIRED", "relation/binding is protected from AUTO"
        elif strategy == "DISAGREEMENT_TO_HUMAN" or len(set(positive)) > 1:
            decision, reason = "HUMAN_REVIEW_REQUIRED", "evaluator disagreement routes to human"
        elif strategy == "LIMITED_COMPONENT_PROXY" and candidate:
            decision, reason = "HUMAN_REVIEW_REQUIRED", "component proxy is not sufficient for this case"
        elif candidate:
            decision, reason = "AUTO_CANDIDATE", "screening candidate only; no production promotion"
        else:
            decision, reason = "ABSTAIN", "target not observed at the declared threshold"
        output.append({"strategy": strategy, "threshold_profile": "pilot-default-v1", "decision": decision, "reason": reason})
    return output


def select_review(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    by_case = defaultdict(list)
    for record in records:
        by_case[record["case"]["case_id"]].append(record)
    def choose(case_id: str, cell: str = "target_present_seed_a") -> dict[str, Any] | None:
        options = [r for r in by_case[case_id] if r["cell"] == cell]
        return sorted(options, key=lambda r: r["image_id"])[0] if options else None
    # Protected route: one deterministic anchor per relation/binding case.
    for case_id, rows in sorted(by_case.items()):
        if rows[0]["screen"]["relation"]:
            row = choose(case_id)
            if row:
                selected[row["image_id"]] = {"kind": "PROTECTED_ROUTE_ANCHOR", "reasons": ["RELATION_OR_BINDING"]}
    # Baseline non-relation blocked/rare-tail anchors and disagreement/low anchors.
    for row in sorted(records, key=lambda r: r["image_id"]):
        if len([x for x in selected.values() if x["kind"] == "REQUIRED_EXCEPTION"]) >= 6:
            break
        if row["screen"]["relation"] or row["cell"] != "target_present_seed_a":
            continue
        if "BLOCKED" in row["screen"]["classes"] or "DISAGREEMENT" in row["screen"]["classes"] or "LOW_CONFIDENCE" in row["screen"]["classes"]:
            selected.setdefault(row["image_id"], {"kind": "REQUIRED_EXCEPTION", "reasons": []})
    # All observed non-relation exceptions are safety escalations, not hidden.
    for row in records:
        if row["screen"]["relation"]:
            continue
        reasons = []
        if "DISAGREEMENT" in row["screen"]["classes"]: reasons.append("EVALUATOR_DISAGREEMENT")
        if "LOW_CONFIDENCE" in row["screen"]["classes"]: reasons.append("LOW_CONFIDENCE")
        if "COMPONENT_ONLY" in row["screen"]["classes"]: reasons.append("COMPONENT_ONLY")
        if "BLOCKED" in row["screen"]["classes"]: reasons.append("BLOCKED_OR_AMBIGUOUS")
        if reasons:
            selected.setdefault(row["image_id"], {"kind": "REQUIRED_EXCEPTION", "reasons": reasons})
            selected[row["image_id"]]["reasons"] = list(dict.fromkeys(selected[row["image_id"]]["reasons"] + reasons))
    # Six predeclared AUTO quality samples: target/contrast seed A for CAL-001..003.
    for case_id in ("CAL-001", "CAL-002", "CAL-003"):
        for cell in ("target_present_seed_a", "contrast_seed_a"):
            row = choose(case_id, cell)
            if row:
                selected.setdefault(row["image_id"], {"kind": "AUTO_QUALITY_SAMPLE", "reasons": ["AUTO_QUALITY_SAMPLE"]})
    return selected


def create_contact_sheet(records: list[dict[str, Any]]) -> Path:
    rows = [r for r in records if r["selection"]["selected_for_human_review"]]
    thumb_w, thumb_h, label_h = 256, 256, 42
    cols = 4
    sheet = Image.new("RGB", (cols * thumb_w, ((len(rows) + cols - 1) // cols) * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, record in enumerate(rows):
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        with Image.open(record["image_path"]) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb_w, thumb_h))
            sheet.paste(image, (x + (thumb_w - image.width) // 2, y + (thumb_h - image.height) // 2))
        draw.text((x + 4, y + thumb_h + 2), f"{record['image_id']}\n{record['case']['canonical'][:28]}", fill="black", font=font)
    path = RUN_ROOT / "review_queue" / "blinded_contact_sheet.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, format="PNG")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--screen-existing",
        action="store_true",
        help="never call Forge txt2img; screen only a complete existing 128-image run",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=CASE_MANIFEST,
        help="case manifest; defaults to the frozen Phase 1 32-case manifest",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate the manifest and current Special IDs without contacting Forge or writing artifacts",
    )
    args = parser.parse_args()
    cases = load_cases(args.manifest)
    profiles = load_profiles()
    validate_cases(cases, profiles)
    planned_images = len(cases) * 4
    if args.dry_run:
        print(json.dumps({
            "status": "DRY_RUN_VALID",
            "manifest": str(args.manifest),
            "case_count": len(cases),
            "planned_images": planned_images,
            "special_ids": sorted({int(value) for case in cases for value in case["special_ids"].split("|")}),
        }, ensure_ascii=False, indent=2))
        return
    ensure_runtime_dependencies()
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    acquire_run_lock()
    session = requests.Session()
    options = session.get(FORGE_API + "/sdapi/v1/options", timeout=30).json()
    loaded = str(options.get("sd_model_checkpoint", ""))
    if "waiIllustriousSDXL_v170" not in loaded:
        raise RuntimeError(f"unexpected checkpoint: {loaded}")
    count = forge_process_count()
    if count is not None and count != 1:
        raise RuntimeError(f"Forge process count is {count}; stop and leave exactly one Forge Neo process")
    settings = generation_settings(cases[0])
    write_json(RUN_ROOT / "run_manifest.json", {"run_id": RUN_ID, "case_manifest": str(args.manifest), "case_count": len(cases), "planned_images": planned_images, "forge_api": FORGE_API, "checkpoint": loaded, "checkpoint_hash": options.get("sd_checkpoint_hash", CHECKPOINT_HASH), "model_family": "Illustrious XL", "model_version": FORGE_VERSION, "negative_prompt": NEGATIVE, "steps": settings["steps"], "cfg": settings["cfg_scale"], "sampler": settings["sampler_name"], "scheduler": settings["scheduler"], "resolution": [settings["width"], settings["height"]], "lora": {"present": False, "names": [], "weights": []}, "upper_bound_enforced": True})
    records = []
    for case_index, case in enumerate(cases, start=1):
        for cell in ("target_present_seed_a", "target_present_seed_b", "contrast_seed_a", "contrast_seed_b"):
            record = generate_one(session, case, case_index, cell, allow_generate=not args.screen_existing)
            records.append(record)
            state = "REUSED" if record["reused"] else "GENERATED"
            print(f"{state} {len(records)}/{planned_images} {record['image_id']}", flush=True)
    write_json(RUN_ROOT / "generation_records.json", records)
    print("GENERATION_COMPLETE", flush=True)
    for index, record in enumerate(records, start=1):
        record["wd14"] = run_wd14(session, record, reuse_existing=args.screen_existing)
        print(f"WD14 {index}/{planned_images}", flush=True)
    import onnxruntime as ort
    kagami_session = ort.InferenceSession(str(KAGAMI_ROOT / "onnx/model_prob.onnx"), providers=["CPUExecutionProvider"])
    with (KAGAMI_ROOT / "selected_tags.csv").open(encoding="utf-8-sig", newline="") as handle:
        kagami_tags = [row["name"] for row in csv.DictReader(handle)]
    kagami_rev = "fbf04252c68c9cbf03c8b343e537e3cd7594c8a1"
    for index, record in enumerate(records, start=1):
        record["kagami"] = run_onnx(record, kagami_session, kagami_tags, "Kagami", "Kagami-24k", kagami_rev, 448, True, THRESHOLDS["Kagami"], reuse_existing=args.screen_existing)
        print(f"KAGAMI {index}/{planned_images}", flush=True)
    cl_session = ort.InferenceSession(str(CL_ROOT / "model.onnx"), providers=["CPUExecutionProvider"])
    vocab = json.loads((CL_ROOT / "model_vocabulary.json").read_text(encoding="utf-8"))
    cl_tags = [tag for tag, index in sorted(vocab["tag_to_idx"].items(), key=lambda item: item[1])]
    cl_rev = "b57909e9c63f71e208a26473e7aabdf45ed6b6"
    for index, record in enumerate(records, start=1):
        record["cl_v2_00"] = run_onnx(record, cl_session, cl_tags, "CL v2.00", "v2.00", cl_rev + ":v2_00", 384, False, THRESHOLDS["CL"], reuse_existing=args.screen_existing)
        print(f"CL {index}/{planned_images}", flush=True)
    structured = []
    for record in records:
        evaluators = {"wd14": record["wd14"], "kagami": record["kagami"], "cl_v2_00": record["cl_v2_00"]}
        for evaluator_name, evaluator in evaluators.items():
            display_name = {"wd14": "WD14", "kagami": "Kagami", "cl_v2_00": "CL v2.00"}[evaluator_name]
            evaluator["raw_output_artifact"] = str(evaluator_artifact_path(display_name, record["image_id"]))
        record["evaluators"] = evaluators
        record["screen"] = screening(record, evaluators)
        structured.append(record)
    selected = select_review(structured)
    output = []
    for record in structured:
        selection = selected.get(record["image_id"], {"kind": "NOT_SELECTED", "reasons": []})
        agreement_votes = [record["wd14"]["target_observed"], record["kagami"]["target_observed"], record["cl_v2_00"]["target_observed"]]
        if any(v is None for v in agreement_votes): agreement = "ABSTAINED"
        elif all(v is True for v in agreement_votes): agreement = "UNANIMOUS_POSITIVE"
        elif all(v is False for v in agreement_votes): agreement = "UNANIMOUS_NEGATIVE"
        else: agreement = "SPLIT"
        reasons = selection["reasons"]
        selection["reasons"] = reasons
        selected_for_review = record["image_id"] in selected
        record["selection"] = {"selected_for_human_review": selected_for_review, "selection_kind": selection["kind"], "reasons": reasons, "capability_class": record["case"]["source_stratum"], "agreement_pattern": agreement, "score_band": record["screen"]["band"], "sampled_auto_candidate": selection["kind"] == "AUTO_QUALITY_SAMPLE"}
        final = "HUMAN_REVIEW_REQUIRED" if selected_for_review else ("BLOCKED" if "BLOCKED" in record["screen"]["classes"] else ("SCREENED_AUTO_LIKELY" if record["screen"]["high"] else "NOT_REVIEWED"))
        request = record["request"]
        generation = {"model_family": "Illustrious XL", "checkpoint": CHECKPOINT, "model_version": FORGE_VERSION, "checkpoint_hash": CHECKPOINT_HASH, "forge_version": FORGE_VERSION, "prompt": record["prompt"], "negative_prompt": record["negative_prompt"], "seed": record["seed"], "sampler": request["sampler_name"], "steps": request["steps"], "cfg": request["cfg_scale"], "resolution": {"width": request["width"], "height": request["height"]}, "lora": {"present": False, "names": [], "weights": []}, "png_info_raw_artifact": record["png_info_artifact"]}
        output.append({"schema_version": "issue30.real_image_calibration.v2", "run_id": RUN_ID, "image_id": record["image_id"], "case_id": record["case"]["case_id"], "special_id": int(record["case"]["special_ids"].split("|")[0]), "special_ids": [int(x) for x in record["case"]["special_ids"].split("|")], "canonical": record["case"]["canonical"], "experiment_question": record["case"]["question"], "cell_type": record["cell"], "generation": generation, "image_artifact": {"path": record["image_path"], "sha256": record["image_sha256"], "bytes": record["image_bytes"], "width": record["size"][0], "height": record["size"][1]}, "screening": {"automatically_screened": True, "screening_classes": record["screen"]["classes"], "high_confidence_eligible": record["screen"]["high"], "provenance_complete": True, "desk_classification": record["case"]["desk_recommendation"], "desk_relation_sensitive": record["screen"]["relation"], "score_band": record["screen"]["band"]}, "human_review_selection": record["selection"], "human_reference": None, "human_effort": {"initial_viewed": False, "recheck_viewed": False, "initial_label_count": 0, "recheck_label_count": 0, "total_image_views": 0}, "evaluators": evaluators, "evaluator_agreement": {"wd14_vote": agreement_votes[0], "kagami_vote": agreement_votes[1], "cl_v2_00_vote": agreement_votes[2], "agreement_class": agreement}, "relation_binding": {"required": record["screen"]["relation"], "categories": ["ACTOR_SUBJECT", "TARGET_OBJECT", "BODYPART_SITE", "COUNT", "SPATIAL", "INSERTION", "CONTACT", "RESTRAINT", "COMPOUND", "MULTI_SPECIAL"] if record["screen"]["relation"] else [], "human_dimensions_required": ["target_concept_present", "actor_subject_correct", "target_object_correct", "body_part_ownership_site_correct", "count_correct", "spatial_relation_correct", "compound_all_elements_retained", "unwanted_extra_interpretation", "usable_for_stage10_preference_judgment"] if record["screen"]["relation"] else ["target_concept_present", "unwanted_extra_interpretation", "usable_for_stage10_preference_judgment"]}, "routing_evaluations": routing(evaluators, record["screen"]), "final_calibration_verdict": final, "final_calibration_reason": "machine screening only; human reference is pending or intentionally uncollected"})
    write_json(RUN_ROOT / "calibration_results.json", output)
    with (RUN_ROOT / "calibration_results.jsonl").open("w", encoding="utf-8") as handle:
        for row in output: handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    for row in output:
        row["image_path"] = next(r["image_path"] for r in structured if r["image_id"] == row["image_id"])
        row["case"] = next(r["case"] for r in structured if r["image_id"] == row["image_id"])
        row["selection"] = row["human_review_selection"]
        row["screen"] = row["screening"]
    contact = create_contact_sheet(output)
    counts = Counter(row["final_calibration_verdict"] for row in output)
    class_counts = Counter(cls for row in output for cls in row["screening"]["screening_classes"])
    summary = {"run_id": RUN_ID, "status": "AUTO_SCREENING_COMPLETE_HUMAN_REVIEW_PENDING", "total_images": len(output), "automatically_screened_images": sum(row["screening"]["automatically_screened"] for row in output), "three_evaluator_complete_images": sum(all(e["execution_state"] == "OK" for e in row["evaluators"].values()) for row in output), "screening_class_occurrences": dict(class_counts), "final_verdict_counts": dict(counts), "initial_review_target": len(selected), "actual_human_reviewed_images": 0, "false_positive_found_in_sampled_auto_candidates": None, "review_expanded": False, "contact_sheet": str(contact), "human_review_reduction_rate_planned": round(1 - len(selected) / planned_images, 4), "additional_generation_performed": 0, "production_auto_promotion": False, "notes": "Human labels are intentionally pending; unsampled records are NOT_REVIEWED and not ground truth."}
    write_json(RUN_ROOT / "pilot_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
