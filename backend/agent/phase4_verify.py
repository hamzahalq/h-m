from __future__ import annotations


def verify_text_content(text: str) -> dict:
    issues = []
    if len(text) < 40:
        issues.append("Text too short.")
    if "CTA" not in text:
        issues.append("Missing CTA.")
    return {"ok": len(issues) == 0, "issues": issues}
