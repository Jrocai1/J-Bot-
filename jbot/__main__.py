"""Command-line entry point for J-Bot."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

from .access import check_paid_repair_access
from .ai import OllamaUnavailable, PaymentRequired, ask_ollama, is_paid_repair_request
from .diagnostics import recommend
from .discovery import discover
from .storage import AuditStore


def answer_prompt(prompt: str, repair_id: str | None = None, force_paid: bool = False) -> tuple[str | None, str | None]:
    """Answer a question, verifying paid access before any repair-specific response."""
    requires_payment = force_paid or is_paid_repair_request(prompt)
    paid_repair = False
    if requires_payment:
        paid_repair, reason = check_paid_repair_access(repair_id or "")
        if not paid_repair:
            return None, reason
    return ask_ollama(prompt, paid_repair=paid_repair), None


def run_chat(repair_id: str | None) -> int:
    print("J-Bot AI — local Ollama chat")
    print("Free: general questions and basic diagnostics. Paid: detailed repair guidance.")
    print("Type 'exit' or 'quit' to end the chat. Nothing is automatically executed.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nJ-Bot session ended.")
            return 0
        if question.lower() in {"exit", "quit"}:
            print("J-Bot session ended.")
            return 0
        if not question:
            continue
        try:
            answer, blocked_reason = answer_prompt(question, repair_id=repair_id)
            if blocked_reason:
                print(f"J-Bot: Paid repair access required. {blocked_reason}")
                print("Basic, non-invasive diagnostics remain available for free.\n")
            else:
                print(f"J-Bot: {answer}\n")
        except (OllamaUnavailable, ValueError) as exc:
            print(f"J-Bot: {exc}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="jbot",
        description="J-Bot: local AI assistant for contactless diagnostics and paid repair guidance",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("status", "scan", "diagnose", "chat", "ask", "repair"),
        default="status",
    )
    parser.add_argument("question", nargs="*", help="Question text for the 'ask' or 'repair' command")
    parser.add_argument("--database", default="data/jbot.sqlite3")
    parser.add_argument("--repair-id", help="Repair-session ID issued by the billing service")
    args = parser.parse_args()

    db_path = Path(args.database)
    store = AuditStore(db_path)

    if args.command == "status":
        result = {
            "app": "J-Bot",
            "version": "0.2.0",
            "mode": "local AI, read-only diagnostics, paid repair guidance",
            "host": platform.platform(),
            "database": str(db_path),
            "ai_backend": "local Ollama",
            "paid_chat_and_diagnostics": True,
            "repair_access": "locked unless trusted billing service verifies payment",
            "automatic_firmware_or_reset": False,
        }
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "scan":
        result = {"app": "J-Bot", "mode": "read-only", "devices": discover()}
        store.record("scan", {"device_count": len(result["devices"])})
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "diagnose":
        result = {"app": "J-Bot", "recommendations": recommend()}
        store.record("diagnose", {"recommendation_count": len(result["recommendations"])})
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "chat":
        return run_chat(args.repair_id)

    question = " ".join(args.question).strip()
    if not question:
        parser.error("ask/repair requires question text. Example: py -3 -m jbot ask Why is USB not detected?")
    force_paid = args.command == "repair"
    try:
        answer, blocked_reason = answer_prompt(
            question,
            repair_id=args.repair_id,
            force_paid=force_paid,
        )
    except (OllamaUnavailable, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, indent=2))
        return 2

    if blocked_reason:
        result = {
            "status": "payment_required",
            "feature": "repair_guidance",
            "message": blocked_reason,
            "repair_id": args.repair_id,
            "checkout_live": False,
        }
        store.record("repair_access_blocked", {"repair_id": args.repair_id, "reason": blocked_reason})
        print(json.dumps(result, indent=2))
        return 3

    store.record("ai_answer", {"paid_repair": force_paid or is_paid_repair_request(question)})
    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
