"""Disk cache for deterministic replay of LLM calls.

Cache key = sha256(model || system || user || temperature || top_p || images_digest).
Reviewers without API keys hit cache and get the exact published numbers.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path

from .base import LLMRequest, LLMResponse


class DiskCache:
    def __init__(self, root: str | os.PathLike[str] | None = None) -> None:
        root = root or os.environ.get("DOC2TEST_CACHE_DIR", "~/.doc2test/cache")
        self.root = Path(os.path.expanduser(str(root)))
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(req: LLMRequest) -> str:
        h = hashlib.sha256()
        h.update(req.model.encode())
        h.update(b"\x00")
        h.update(req.system.encode())
        h.update(b"\x00")
        h.update(req.user.encode())
        h.update(f"\x00{req.temperature}\x00{req.top_p}".encode())
        for img in req.images:
            h.update(b"\x00")
            h.update(hashlib.sha256(img).digest())
        return h.hexdigest()

    def path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, req: LLMRequest) -> LLMResponse | None:
        p = self.path(self.key(req))
        if not p.exists():
            return None
        data = json.loads(p.read_text())
        return LLMResponse(cached=True, **{k: v for k, v in data.items() if k != "cached"})

    def put(self, req: LLMRequest, resp: LLMResponse) -> None:
        p = self.path(self.key(req))
        payload = asdict(resp)
        payload["cached"] = False
        p.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
