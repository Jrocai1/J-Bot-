"""Command-line entry point for J-Bot."""
import argparse
import json
import platform
from pathlib import Path
from .diagnostics import recommend
from .discovery import discover
from .storage import AuditStore

def main() -> int:
    parser = argparse.ArgumentParser(prog="jbot", description="Read-only contactless diagnostics")
    parser.add_argument("command", nargs="?", choices=("status", "scan", "diagnose"), default="status")
    parser.add_argument("--database", default="data/jbot.sqlite3")
    args = parser.parse_args()
    db_path = Path(args.database)
    store = AuditStore(db_path)
    if args.command == "status":
        result = {"app": "J-Bot", "version": "0.1.0", "mode": "read-only contactless diagnostics",
                  "host": platform.platform(), "database": str(db_path),
                  "paid_services_enabled": False, "automatic_firmware_or_reset": False}
    elif args.command == "scan":
        result = {"app": "J-Bot", "mode": "read-only", "devices": discover()}
        store.record("scan", {"device_count": len(result["devices"])})
    else:
        result = {"app": "J-Bot", "recommendations": recommend()}
        store.record("diagnose", {"recommendation_count": len(result["recommendations"])})
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
