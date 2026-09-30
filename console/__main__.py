"""
Start the operator console: a live simulated fleet behind the console's HTTP API (python -m
console).
"""

from __future__ import annotations

import argparse
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _secret_file(path: Path, make) -> str:  # type: ignore[no-untyped-def]
    if not path.exists():
        path.write_text(make())
        path.chmod(0o600)
    return path.read_text().strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8700)
    parser.add_argument("--data", type=Path, default=ROOT / "results" / "console")
    parser.add_argument("--devices", type=int, default=40)
    parser.add_argument("--tick-seconds", type=float, default=1.0)
    parser.add_argument("--demo-accounts", action="store_true")
    parser.add_argument(
        "--kiosk",
        choices=("admin", "operator", "auditor"),
        help="demonstration mode: this machine opens the console as that demo account",
    )
    args = parser.parse_args(argv)

    if args.kiosk and args.host not in ("127.0.0.1", "::1", "localhost"):
        print("--kiosk is loopback-only", file=sys.stderr)
        return 2
    if args.kiosk:
        args.demo_accounts = True
    args.data.mkdir(parents=True, exist_ok=True)
    if not os.environ.get("DIS_MASTER_KEY"):
        os.environ["DIS_MASTER_KEY"] = _secret_file(
            args.data / "master.key", lambda: secrets.token_hex(32)
        )

    import time

    import uvicorn

    from console import lab
    from console.accounts import Accounts
    from console.app import create_app
    from console.runtime import LiveFleet
    from shared.keys import using_development_key

    if using_development_key():
        print("refusing to start on the development master key", file=sys.stderr)
        return 1

    accounts = Accounts(args.data / "accounts.db", now=time.time)
    created = []
    wanted = [("admin", "admin")]
    if args.demo_accounts:
        wanted += [("operator", "operator"), ("auditor", "auditor")]
    existing = {u.username for u in accounts.users()}
    for username, role in wanted:
        if username not in existing:
            password = secrets.token_urlsafe(12)
            accounts.create(username, password, role)
            created.append(f"{username} ({role}): {password}")
    if created:
        credentials = args.data / "initial-credentials.txt"
        with credentials.open("a") as fh:
            fh.write("\n".join(created) + "\n")
        credentials.chmod(0o600)
        print("New console accounts (also in", credentials, "):")
        for line in created:
            print("  ", line)

    fleet = LiveFleet(n_nodes=args.devices, tick_seconds=args.tick_seconds)
    fleet.start()
    app = create_app(accounts, fleet, kiosk_user=args.kiosk)
    try:
        uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    finally:
        fleet.stop()
        lab.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
