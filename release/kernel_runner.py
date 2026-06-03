from __future__ import annotations
import json, os, hashlib
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Any
try:
    from . import kernel_http, kernel_parser, kernel_secret_guard
except ImportError:
    import kernel_http, kernel_parser, kernel_secret_guard

CONFIG = Path("provider_config.json")
SECRETS = Path("local_secrets.json")
OUT = Path("receipts")
RAW = OUT / "raw_response_capture_v1.json"
SUCCESS = OUT / "provider_success_receipt_v1.json"
FAILURE = OUT / "provider_failure_receipt_v1.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))

def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def fail(reason: str, details: dict[str, Any]) -> int:
    receipt = {"artifact_type": "release_provider_failure_receipt", "created_utc": now(), "receipt_status": "rejected", "failure_reason": reason, "details": details, "non_claims": {"universal_vendor_agnostic_controller_proven": False, "production_ready": False}}
    write_json(FAILURE, receipt)
    print(json.dumps(receipt, indent=2))
    return 1

def get_path(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur

def normalize(obj: dict[str, Any], paths: list[str]) -> tuple[str, dict[str, Any]]:
    trace = {"normalization_applied": False, "normalization_path": None, "normalization_errors": [], "model_text_char_length": 0}
    for path in paths:
        try:
            value = get_path(obj, path)
            if isinstance(value, str) and value.strip():
                trace.update({"normalization_applied": True, "normalization_path": path, "model_text_char_length": len(value)})
                return value, trace
        except Exception as exc:
            trace["normalization_errors"].append(f"{path}:{exc.__class__.__name__}")
    fallback = json.dumps(obj, indent=2, ensure_ascii=False)
    trace["model_text_char_length"] = len(fallback)
    return fallback, trace

def main() -> int:
    if not CONFIG.exists():
        return fail("provider_config_missing", {"path": str(CONFIG)})
    config = read_json(CONFIG)
    secrets = read_json(SECRETS) if SECRETS.exists() else {}
    endpoint = config["endpoint_url"]
    model = config["model_name"]
    key_name = config["api_key_environment_variable"]
    api_key = os.environ.get(key_name) or secrets.get(key_name)
    if not api_key or "REPLACE_WITH_REAL" in api_key:
        return fail("missing_or_placeholder_api_key", {"api_key_environment_variable": key_name})
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": config.get("system_prompt", "You are a JSON validation agent.")},
            {"role": "user", "content": "Return exactly one JSON object matching this schema. Wrapper text is allowed. Do not include secrets.\n" + json.dumps(config["required_output_schema"], indent=2)}
        ],
        "temperature": config.get("temperature", 0),
        "max_tokens": config.get("max_tokens", 512),
        "stream": False
    }
    result = kernel_http.post_json(endpoint, {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, payload, int(config.get("timeout_seconds", 30)))
    redacted_body, body_leaked = kernel_secret_guard.redact_secret(result["body"], api_key)
    try:
        response_obj = json.loads(redacted_body)
        parse_ok, parse_error = isinstance(response_obj, dict), None
    except Exception as exc:
        response_obj, parse_ok, parse_error = {}, False, f"{exc.__class__.__name__}: {exc}"
    model_text, trace = normalize(response_obj, config["response_text_paths"])
    model_text, model_leaked = kernel_secret_guard.redact_secret(model_text, api_key)
    extraction = kernel_parser.extract_one_valid_object(model_text, config["required_output_schema"])
    scan = {"secret_leak_scan_performed": True, "api_key_sha256": kernel_secret_guard.sha256_text(api_key), "raw_secret_found_in_raw_response_text": body_leaked, "raw_secret_found_in_model_text": model_leaked, "raw_api_key_logged": False, "raw_api_key_stored": False}
    raw = {"artifact_type": "release_raw_response_capture", "created_utc": now(), "provider_name": config.get("provider_name"), "endpoint_host": urlparse(endpoint).hostname, "endpoint_sha256": h(endpoint), "model_name_sha256": h(model), "http_status": result["http_status"], "latency_ms": result["latency_ms"], "network_error": result["network_error"], "response_json_parse_ok": parse_ok, "response_json_parse_error": parse_error, "normalization_trace": trace, "secret_leak_scan": scan, "deep_read_extraction": extraction}
    write_json(RAW, raw)
    if result["http_status"] != 200:
        return fail("http_status_not_200", {"http_status": result["http_status"], "raw_capture": str(RAW)})
    if not parse_ok:
        return fail("invalid_json_response_envelope", {"parse_error": parse_error, "raw_capture": str(RAW)})
    if extraction.get("accepted") is not True:
        return fail(extraction.get("rejection_reason", "extraction_failed"), {"raw_capture": str(RAW)})
    success = {"artifact_type": "release_provider_success_receipt", "created_utc": now(), "receipt_status": "accepted", "provider_name": config.get("provider_name"), "endpoint_host": urlparse(endpoint).hostname, "endpoint_sha256": h(endpoint), "model_name_sha256": h(model), "http_status": result["http_status"], "latency_ms": result["latency_ms"], "normalization_path": trace.get("normalization_path"), "candidate_count": extraction["candidate_count"], "valid_candidate_count": extraction["valid_candidate_count"], "selected_object": extraction["selected_object"], "secret_leak_scan": scan, "validated_claims": {"real_network_call_completed": True, "provider_response_normalized_to_model_text": bool(trace.get("normalization_applied")), "schema_valid_json_object_extracted": True, "secret_leak_scan_completed": True, "provider_passed_by_config_not_code": True}, "non_claims": {"universal_vendor_agnostic_controller_proven": False, "production_ready": False}}
    write_json(SUCCESS, success)
    print(json.dumps(success, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
