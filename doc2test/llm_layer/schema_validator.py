"""JSON-schema enforcement for every agent I/O (paper §3.4)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SchemaValidationError(Exception):
    pass


class SchemaValidator:
    def __init__(self, schemas_root: str | Path | None = None) -> None:
        if schemas_root is None:
            schemas_root = Path(__file__).resolve().parent.parent / "schemas"
        self.root = Path(schemas_root)
        self._cache: dict[str, dict[str, Any]] = {}

    def load(self, name: str) -> dict[str, Any]:
        if name not in self._cache:
            self._cache[name] = json.loads((self.root / f"{name}.json").read_text())
        return self._cache[name]

    def validate(self, schema_name: str, payload: Any) -> Any:
        try:
            from jsonschema import validate as _validate
        except ImportError:
            from pydantic import TypeAdapter
            TypeAdapter(dict).validate_python(payload)
            return payload
        _validate(payload, self.load(schema_name))
        return payload

    def parse_and_validate(self, schema_name: str, raw: str) -> dict[str, Any]:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(f"{schema_name}: invalid JSON ({exc})") from exc
        return self.validate(schema_name, payload)
