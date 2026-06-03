from __future__ import annotations
import json
import time
import urllib.request
import urllib.error
from typing import Any

def post_json(endpoint: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return {"http_status": res.getcode(), "body": res.read().decode("utf-8", errors="replace"), "latency_ms": round((time.perf_counter() - start) * 1000, 3), "network_error": None}
    except urllib.error.HTTPError as exc:
        return {"http_status": exc.code, "body": exc.read().decode("utf-8", errors="replace"), "latency_ms": round((time.perf_counter() - start) * 1000, 3), "network_error": None}
    except urllib.error.URLError as exc:
        return {"http_status": 0, "body": str(exc.reason), "latency_ms": round((time.perf_counter() - start) * 1000, 3), "network_error": f"{exc.__class__.__name__}: {exc.reason}"}
