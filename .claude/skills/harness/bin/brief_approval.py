"""The sole parser for a feature BRIEF.md Approval section."""
from datetime import date
from pathlib import Path
import re

_ABSENT = "BRIEF.md is absent"
_NO_SECTION = "BRIEF.md has no Approval section"
_NOT_APPROVED = "Approval status is not approved"
_BAD_DATE = "Approval date is empty or invalid"


def approval_date(feature_dir: Path) -> tuple[str | None, str | None]:
    """Return an approved BRIEF date or the precise reason it is unavailable."""
    brief = Path(feature_dir) / "BRIEF.md"
    if not brief.is_file():
        return None, _ABSENT
    section = _approval_section(brief.read_text(encoding="utf-8"))
    if section is None:
        return None, _NO_SECTION
    if _field(section, "status") != "approved":
        return None, _NOT_APPROVED
    value = _field(section, "date")
    if not _valid_date(value):
        return None, _BAD_DATE
    return value, None


def _approval_section(text: str) -> str | None:
    match = re.search(r"^## Approval\s*$([\s\S]*?)(?=^## |\Z)", text, re.MULTILINE)
    return None if match is None else match.group(1)


def _field(section: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*(.*?)\s*$", section, re.MULTILINE)
    return "" if match is None else match.group(1)


def _valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
