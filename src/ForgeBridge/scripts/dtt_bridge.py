"""DanbooruTagTool local bridge for the Forge txt2img UI.

This is a companion extension: it registers only the three dtt-bridge routes
and keeps a short in-memory queue. It never calls a generation endpoint.
"""

from __future__ import annotations

import ipaddress
import json
import time
from collections import deque
from threading import Lock

from fastapi import Request
from fastapi.responses import JSONResponse
from modules import script_callbacks


PROTOCOL_VERSION = 1
MAX_BODY_BYTES = 256 * 1024
MAX_TEXT_LENGTH = 128 * 1024
MAX_QUEUE_LENGTH = 16
MAX_REQUEST_ID_LENGTH = 128

_pending: deque[dict] = deque()
_seen_ids: deque[str] = deque()
_seen_id_set: set[str] = set()
_lock = Lock()
_registered = False


def _json_error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"protocolVersion": PROTOCOL_VERSION, "accepted": False, "error": code, "message": message},
    )


def _is_loopback(request: Request) -> bool:
    host = request.client.host if request.client else "127.0.0.1"
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host.lower() == "localhost"


async def _body(request: Request) -> bytes | None:
    length = request.headers.get("content-length")
    if length:
        try:
            if int(length) > MAX_BODY_BYTES:
                return None
        except ValueError:
            return None
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > MAX_BODY_BYTES:
            return None
    return bytes(data)


def _validate(payload: object) -> tuple[dict | None, tuple[int, str, str] | None]:
    if not isinstance(payload, dict):
        return None, (400, "malformed", "payload must be an object")
    allowed = {"protocolVersion", "requestId", "positive", "negativeMode", "negative"}
    if set(payload) - allowed:
        return None, (400, "malformed", "unsupported payload field")
    version = payload.get("protocolVersion")
    if isinstance(version, bool) or not isinstance(version, int) or version != PROTOCOL_VERSION:
        return None, (426, "protocol", "unsupported protocol version")
    request_id = payload.get("requestId")
    if not isinstance(request_id, str) or not request_id or len(request_id) > MAX_REQUEST_ID_LENGTH or any(ord(c) < 32 for c in request_id):
        return None, (400, "malformed", "requestId is invalid")
    positive = payload.get("positive")
    if not isinstance(positive, str) or len(positive) > MAX_TEXT_LENGTH:
        return None, (413, "oversized", "positive is too large")
    mode = payload.get("negativeMode")
    if mode not in ("unchanged", "replace"):
        return None, (400, "malformed", "negativeMode is invalid")
    if mode == "unchanged":
        if "negative" in payload:
            return None, (400, "malformed", "negative is not allowed for unchanged mode")
        negative = None
    else:
        negative = payload.get("negative")
        if not isinstance(negative, str) or len(negative) > MAX_TEXT_LENGTH:
            return None, (413, "oversized", "negative is too large")
    return {"requestId": request_id, "positive": positive, "negativeMode": mode, "negative": negative, "createdAt": int(time.time() * 1000)}, None


async def _health(request: Request) -> JSONResponse:
    if not _is_loopback(request):
        return _json_error(403, "local_only", "loopback access required")
    return JSONResponse(content={"protocolVersion": PROTOCOL_VERSION, "ok": True, "ready": True})


async def _prompt(request: Request) -> JSONResponse:
    if not _is_loopback(request):
        return _json_error(403, "local_only", "loopback access required")
    body = await _body(request)
    if body is None:
        return _json_error(413, "oversized", "payload is too large")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _json_error(400, "malformed", "payload must be UTF-8 JSON")
    item, error = _validate(payload)
    if error:
        return _json_error(*error)
    assert item is not None
    with _lock:
        if item["requestId"] in _seen_id_set:
            return _json_error(409, "duplicate_request", "requestId was already accepted")
        if len(_pending) >= MAX_QUEUE_LENGTH:
            return _json_error(429, "queue_full", "pending queue is full")
        _pending.append(item)
        _seen_ids.append(item["requestId"])
        _seen_id_set.add(item["requestId"])
        while len(_seen_ids) > 512:
            _seen_id_set.discard(_seen_ids.popleft())
    return JSONResponse(content={"protocolVersion": PROTOCOL_VERSION, "accepted": True, "requestId": item["requestId"]})


async def _pending_request(request: Request) -> JSONResponse:
    if not _is_loopback(request):
        return _json_error(403, "local_only", "loopback access required")
    with _lock:
        item = _pending.popleft() if _pending else None
    return JSONResponse(content={"protocolVersion": PROTOCOL_VERSION, "pending": item})


def _on_app_started(_demo, app) -> None:
    global _registered
    if _registered:
        return
    app.add_api_route("/dtt-bridge/health", _health, methods=["GET"])
    app.add_api_route("/dtt-bridge/prompt", _prompt, methods=["POST"])
    app.add_api_route("/dtt-bridge/pending", _pending_request, methods=["GET"])
    _registered = True


script_callbacks.on_app_started(_on_app_started)
