from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def get_json(url: str, timeout: float) -> tuple[int, dict]:
    request = Request(url, headers={"X-Request-ID": "release-smoke-test"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"raw": body}
    except URLError as exc:
        raise RuntimeError(f"request failed: {url}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="ApplyMate AI release smoke test")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    checks = [
        ("/api/v1/health/live", 200),
        ("/api/v1/health/ready", 200),
        ("/openapi.json", 200),
    ]
    failures: list[str] = []
    for path, expected in checks:
        url = args.base_url.rstrip("/") + path
        status, body = get_json(url, args.timeout)
        if status != expected:
            failures.append(f"{path}: expected {expected}, got {status}, body={body}")
        else:
            print(f"PASS {path} {status}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
