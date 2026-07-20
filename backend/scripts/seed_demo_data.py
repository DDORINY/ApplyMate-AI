from __future__ import annotations

import argparse
import json
import os

from app.seeds.demo import build_demo_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ApplyMate AI demo seed payload")
    parser.add_argument("--email", default=os.getenv("DEMO_USER_EMAIL", "demo@example.com"))
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    payload = build_demo_payload(args.email)
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(content)
            file.write("\n")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
