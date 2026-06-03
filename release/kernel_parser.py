from __future__ import annotations
import json
from typing import Any

def extract_candidates(text: str) -> list[str]:
    out, start, depth, in_str, esc = [], None, 0, False, False
    for i, ch in enumerate(text):
        if start is None:
            if ch == "{":
                start, depth = i, 1
            continue
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append(text[start:i + 1])
                start = None
    return out

def extract_one_valid_object(model_text: str, required_schema: dict[str, Any]) -> dict[str, Any]:
    candidates = extract_candidates(model_text)
    attempts, valid = [], []
    for idx, candidate in enumerate(candidates):
        rec = {"candidate_index": idx, "parse_passed": False, "schema_passed": False, "schema_errors": []}
        try:
            obj = json.loads(candidate)
            rec["parse_passed"] = isinstance(obj, dict)
            rec["parsed_object"] = obj
        except Exception as exc:
            rec["parse_error"] = f"{exc.__class__.__name__}: {exc}"
            attempts.append(rec)
            continue
        if not isinstance(obj, dict):
            rec["parse_error"] = "parsed_candidate_not_object"
            attempts.append(rec)
            continue
        errors = [f"{k}_mismatch" for k, v in required_schema.items() if obj.get(k) != v]
        rec["schema_errors"] = errors
        rec["schema_passed"] = not errors
        if not errors:
            valid.append((candidate, obj))
        attempts.append(rec)
    if len(valid) != 1:
        return {"accepted": False, "rejection_reason": "valid_candidate_count_not_exactly_1", "candidate_count": len(candidates), "valid_candidate_count": len(valid), "attempts": attempts}
    candidate, obj = valid[0]
    return {"accepted": True, "candidate_count": len(candidates), "valid_candidate_count": 1, "selected_candidate": candidate, "selected_object": obj, "attempts": attempts}
