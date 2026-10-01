"""Independent adapter contract tests; Forge/torch/model/network are never loaded."""
from __future__ import annotations
import asyncio
import importlib.util
import json
from pathlib import Path
import sys
from threading import Lock
from types import ModuleType, SimpleNamespace
import unittest


class Response:
    def __init__(self, content, status_code=200):
        self.content, self.status_code = content, status_code


class Request:
    def __init__(self, value, host="127.0.0.1"):
        self.client = SimpleNamespace(host=host)
        self.headers = {}
        self.data = json.dumps(value).encode()
    async def stream(self):
        yield self.data


class TokenTests(unittest.TestCase):
    def setUp(self):
        modules = ModuleType("modules")
        modules.script_callbacks = SimpleNamespace(on_app_started=lambda fn: None)
        self.lock = Lock()
        self.model = SimpleNamespace(sd_checkpoint_info=SimpleNamespace(title="owned-model", shorthash="abc"), text_processing_engine_l=SimpleNamespace(chunk_length=75, tokenizer=SimpleNamespace()))
        modules.sd_models = SimpleNamespace(model_data=SimpleNamespace(sd_model=self.model))
        self.calls = []
        def counter(text, steps, styles, **kwargs):
            self.calls.append((text, steps, styles, kwargs))
            return "<span class='gr-box gr-text-input'>80/150</span>"
        modules.ui = SimpleNamespace(update_token_counter=counter)
        sys.modules["modules"] = modules
        sys.modules["modules.call_queue"] = SimpleNamespace(queue_lock=self.lock)
        sys.modules["fastapi"] = SimpleNamespace(Request=Request)
        sys.modules["fastapi.responses"] = SimpleNamespace(JSONResponse=Response)
        spec = importlib.util.spec_from_file_location("dtt_token_test", Path(__file__).resolve().parents[2] / "src/ForgeBridge/scripts/dtt_bridge.py")
        self.bridge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.bridge)
        self.modules = modules
        self.payload = dict(protocolVersion=1, text="one BREAK two AND three", negative=False, steps=20)
    def request(self, payload=None, host="127.0.0.1"):
        return asyncio.run(self.bridge._token_count(Request(payload or self.payload, host)))
    def test_delegated_model_tokenizer_chunk_context_and_explicit_side(self):
        result = self.request(); self.assertEqual(200, result.status_code)
        self.assertEqual(2, result.content["chunks"]); self.assertEqual("owned-model", result.content["model"])
        self.assertEqual([(self.payload["text"], 20, [], {"is_positive": True})], self.calls)
        self.payload["negative"] = True; self.request(); self.assertFalse(self.calls[-1][3]["is_positive"])
        self.assertFalse(self.lock.locked())
    def test_loopback_boundary_rejects_remote_before_counter(self):
        self.assertEqual(403, self.request(host="192.168.1.10").status_code); self.assertEqual([], self.calls)
    def test_unknown_boolean_version_steps_and_fields_rejected(self):
        for change in ({"protocolVersion": True}, {"negative": 1}, {"steps": True}, {"steps": 151}, {"extra": "no"}, {"text": None}):
            with self.subTest(change=change): self.assertEqual(400, self.request(self.payload | change).status_code)
        self.assertEqual([], self.calls)
    def test_fake_initial_heuristic_and_missing_model_refused(self):
        class FakeInitialModel:
            sd_checkpoint_info = SimpleNamespace(title="fake")
        for model in (FakeInitialModel(), None, SimpleNamespace()):
            self.modules.sd_models.model_data.sd_model = model
            self.assertEqual(409, self.request().status_code)
        self.assertEqual([], self.calls); self.assertFalse(self.lock.locked())
    def test_busy_does_not_wait_or_start_generation(self):
        self.lock.acquire()
        try: self.assertEqual(409, self.request().status_code)
        finally: self.lock.release()
        self.assertEqual([], self.calls)
    def test_unknown_count_and_changed_model_refused_and_lock_released(self):
        self.modules.ui.update_token_counter = lambda *a, **k: "?/?"
        self.assertEqual(409, self.request().status_code); self.assertFalse(self.lock.locked())
        def change(*args, **kwargs):
            self.modules.sd_models.model_data.sd_model = None
            return "<span>80/150</span>"
        self.modules.ui.update_token_counter = change
        self.assertEqual(409, self.request().status_code); self.assertFalse(self.lock.locked())
    def test_non_clip_does_not_invent_chunk_contract(self):
        self.model.text_processing_engine_l = None
        result = self.request(); self.assertEqual(200, result.status_code)
        self.assertIsNone(result.content["chunkLength"]); self.assertIsNone(result.content["chunks"])


if __name__ == "__main__": unittest.main()
