from __future__ import annotations

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TARGETS = [
    "/api/v1/health/live",
    "/api/v1/health/ready",
    "/openapi.json",
]


def request_once(base_url: str, path: str, timeout: float) -> tuple[str, int, float]:
    started = time.perf_counter()
    request = Request(base_url.rstrip("/") + path, headers={"X-Request-ID": "performance-smoke"})
    try:
        with urlopen(request, timeout=timeout) as response:
            response.read()
            status = response.status
    except HTTPError as exc:
        status = exc.code
    except URLError:
        status = 0
    duration_ms = (time.perf_counter() - started) * 1000
    return path, status, duration_ms


def percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * ratio))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(description="ApplyMate AI local performance smoke")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--requests", type=int, default=30)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    jobs = [TARGETS[index % len(TARGETS)] for index in range(args.requests)]
    results: list[tuple[str, int, float]] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(request_once, args.base_url, path, args.timeout) for path in jobs]
        for future in as_completed(futures):
            results.append(future.result())

    durations = [duration for _path, status, duration in results if 200 <= status < 500]
    errors = [item for item in results if item[1] >= 500 or item[1] == 0]
    print(f"requests={len(results)} concurrency={args.concurrency} errors={len(errors)}")
    print(f"p50_ms={percentile(durations, 0.50):.2f}")
    print(f"p95_ms={percentile(durations, 0.95):.2f}")
    print(f"p99_ms={percentile(durations, 0.99):.2f}")
    if durations:
        print(f"mean_ms={statistics.mean(durations):.2f}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
