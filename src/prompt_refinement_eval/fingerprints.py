"""Cross-platform fingerprint policies for text-backed evidence artifacts."""

from __future__ import annotations

import hashlib

CANONICAL_JSON_SHA256_POLICY = "canonical-json-sort-keys-compact-utf8-sha256-v1"
CANONICAL_TEXT_SHA256_POLICY = "utf8-bom-strip-newlines-lf-sha256-v1"


def canonical_text_sha256(raw_bytes: bytes) -> str:
    """Hash UTF-8 text after removing a BOM and canonicalizing newlines to LF."""

    text = raw_bytes.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
