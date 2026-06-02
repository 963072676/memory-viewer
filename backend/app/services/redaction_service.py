"""PII Redaction service (F-41) — Detect and mask sensitive data in memory content.

Detects API keys, emails, phone numbers, IP addresses, passwords, and other PII.
Masking is non-destructive — original data is never modified.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class PIIMatch:
    """A single PII match found in text."""
    pii_type: str        # e.g. "api_key", "email", "phone", "ip_address", "password"
    original: str        # The original matched text
    masked: str          # The masked version
    start: int           # Start index in text
    end: int             # End index in text
    confidence: float    # 0.0-1.0


@dataclass
class ScanResult:
    """Result of scanning a single memory for PII."""
    memory_id: str
    memory_title: str
    pii_count: int
    pii_types: list[str]
    matches: list[PIIMatch]


@dataclass
class PIIReport:
    """Aggregate PII scan report across all memories."""
    total_memories: int
    memories_with_pii: int
    total_pii_count: int
    by_type: dict[str, int] = field(default_factory=dict)
    by_memory: list[ScanResult] = field(default_factory=list)


# --- Regex patterns for PII detection ---

_PATTERNS: list[tuple[str, str, float]] = [
    # API keys (OpenAI sk-..., AWS AKIA..., GitHub ghp_/gho_, generic long hex keys)
    ("api_key", r"\b(sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|[a-zA-Z0-9]{32,})\b", 0.85),
    # Email addresses
    ("email", r"\b[a-zA-Z0-9._%+\-]{1,64}@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b", 0.95),
    # Phone numbers (US/international formats)
    ("phone", r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b", 0.7),
    # IP addresses (IPv4)
    ("ip_address", r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b", 0.8),
    # Password patterns (password=, passwd=, pwd=, secret=)
    ("password", r"(?:password|passwd|pwd|secret|token)\s*[:=]\s*\S+", 0.9),
    # AWS Secret keys
    ("aws_secret", r"(?:aws_secret_access_key|aws_secret)\s*[:=]\s*[A-Za-z0-9/+=]{40}", 0.95),
    # Private keys (PEM format)
    ("private_key", r"-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----", 0.99),
    # Credit card numbers (basic pattern)
    ("credit_card", r"\b(?:4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}|5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}|3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5})\b", 0.75),
    # SSN (US Social Security Numbers)
    ("ssn", r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", 0.5),
]

# Compiled patterns
_COMPILED_PATTERNS: list[tuple[str, re.Pattern, float]] = [
    (name, re.compile(pattern, re.IGNORECASE), confidence)
    for name, pattern, confidence in _PATTERNS
]

# Detector enable/disable state
_enabled_detectors: dict[str, bool] = {
    name: True for name, _, _ in _PATTERNS
}


def get_detector_config() -> dict[str, bool]:
    """Get current detector enabled/disabled state."""
    return dict(_enabled_detectors)


def set_detector_enabled(detector: str, enabled: bool) -> bool:
    """Enable or disable a specific detector. Returns True if detector exists."""
    if detector in _enabled_detectors:
        _enabled_detectors[detector] = enabled
        return True
    return False


def _mask_api_key(text: str) -> str:
    """Mask API key: sk-abc123...xyz -> sk-****...****"""
    if len(text) <= 8:
        return "*" * len(text)
    return text[:3] + "*" * (len(text) - 6) + text[-3:]


def _mask_email(text: str) -> str:
    """Mask email: user@example.com -> u***@***.com"""
    parts = text.split("@")
    if len(parts) != 2:
        return "***@" + "***"
    local = parts[0][0] + "***" if parts[0] else "***"
    domain_parts = parts[1].split(".")
    if len(domain_parts) >= 2:
        domain = "***." + domain_parts[-1]
    else:
        domain = "***"
    return f"{local}@{domain}"


def _mask_phone(text: str) -> str:
    """Mask phone: keep last 4 digits."""
    digits = re.sub(r"\D", "", text)
    if len(digits) >= 4:
        return "***-***-" + digits[-4:]
    return "***"


def _mask_ip(text: str) -> str:
    """Mask IP: 192.168.1.1 -> ***.***.*.1"""
    parts = text.split(".")
    if len(parts) == 4:
        return f"***.***.*.{parts[3]}"
    return "***"


def _mask_password(text: str) -> str:
    """Mask password field: keep key, mask value."""
    match = re.match(r"((?:password|passwd|pwd|secret|token)\s*[:=]\s*)\S+", text, re.IGNORECASE)
    if match:
        prefix = match.group(1)
        return prefix + "****"
    return "****"


def _mask_generic(text: str) -> str:
    """Generic masking: keep first and last 3 chars."""
    if len(text) <= 6:
        return "*" * len(text)
    return text[:3] + "*" * (len(text) - 6) + text[-3:]


_MASKERS: dict[str, callable] = {
    "api_key": _mask_api_key,
    "email": _mask_email,
    "phone": _mask_phone,
    "ip_address": _mask_ip,
    "password": _mask_password,
    "aws_secret": _mask_generic,
    "private_key": lambda t: "-----BEGIN PRIVATE KEY-----",
    "credit_card": lambda t: "****-****-****-" + re.sub(r"\D", "", t)[-4:] if len(re.sub(r"\D", "", t)) >= 4 else "****",
    "ssn": lambda t: "***-**-" + re.sub(r"\D", "", t)[-4:] if len(re.sub(r"\D", "", t)) >= 4 else "***",
}


def detect_pii(text: str) -> list[PIIMatch]:
    """Detect all PII patterns in the given text.
    
    Returns list of PIIMatch with positions, types, and masked versions.
    """
    matches: list[PIIMatch] = []

    for name, pattern, confidence in _COMPILED_PATTERNS:
        if not _enabled_detectors.get(name, True):
            continue

        for m in pattern.finditer(text):
            original = m.group()
            # Skip false positives for low-confidence patterns
            if name == "phone" and len(re.sub(r"\D", "", original)) < 7:
                continue
            if name == "ssn" and len(re.sub(r"\D", "", original)) != 9:
                continue
            if name == "credit_card":
                digits = re.sub(r"\D", "", original)
                if len(digits) < 13:
                    continue

            masker = _MASKERS.get(name, _mask_generic)
            masked = masker(original)

            matches.append(PIIMatch(
                pii_type=name,
                original=original,
                masked=masked,
                start=m.start(),
                end=m.end(),
                confidence=confidence,
            ))

    # Sort by position; remove overlapping matches (keep higher confidence)
    matches.sort(key=lambda x: (x.start, -x.confidence))
    filtered: list[PIIMatch] = []
    for match in matches:
        if filtered and match.start < filtered[-1].end:
            continue  # Skip overlapping
        filtered.append(match)

    return filtered


def mask_text(text: str, matches: Optional[list[PIIMatch]] = None) -> str:
    """Apply masking to text using detected PII matches.
    
    If matches not provided, will detect them first.
    Returns the masked text.
    """
    if matches is None:
        matches = detect_pii(text)

    if not matches:
        return text

    # Apply masking from end to start to preserve indices
    result = text
    for match in reversed(matches):
        result = result[:match.start] + match.masked + result[match.end:]

    return result


def scan_memories(memories: list[dict]) -> PIIReport:
    """Scan a list of memories for PII. Returns aggregate report."""
    by_type: dict[str, int] = {}
    by_memory: list[ScanResult] = []
    total_pii = 0

    for mem in memories:
        text = f"{mem.get('title', '')} {mem.get('content', '')}"
        matches = detect_pii(text)

        if matches:
            pii_types = list(set(m.pii_type for m in matches))
            by_memory.append(ScanResult(
                memory_id=mem.get("id", ""),
                memory_title=mem.get("title", ""),
                pii_count=len(matches),
                pii_types=pii_types,
                matches=matches,
            ))
            total_pii += len(matches)
            for m in matches:
                by_type[m.pii_type] = by_type.get(m.pii_type, 0) + 1

    return PIIReport(
        total_memories=len(memories),
        memories_with_pii=len(by_memory),
        total_pii_count=total_pii,
        by_type=by_type,
        by_memory=by_memory,
    )


def has_pii(text: str) -> bool:
    """Quick check if text contains any PII."""
    for name, pattern, _ in _COMPILED_PATTERNS:
        if not _enabled_detectors.get(name, True):
            continue
        if pattern.search(text):
            return True
    return False
