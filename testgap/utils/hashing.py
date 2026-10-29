"""Content hashing utilities for duplicate detection."""
import hashlib


def compute_content_hash(requirements: str, source_code: str, test_suite: str) -> str:
    """Compute deterministic SHA-256 hash of core content fields.
    
    Normalizes whitespace and joins with delimiters to avoid collisions.
    """
    req_norm = (requirements or "").strip()
    src_norm = (source_code or "").strip()
    test_norm = (test_suite or "").strip()
    
    raw = f"{req_norm}|{src_norm}|{test_norm}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
