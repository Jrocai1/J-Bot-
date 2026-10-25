"""Paid repair entitlement check against a trusted HTTPS billing service.

The desktop app does not decide that a payment succeeded. The billing server must verify
the payment provider's signed webhook and return a paid entitlement for this repair ID.
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def check_paid_repair_access(repair_id: str, *, timeout: int = 10) -> tuple[bool, str]:
    """Return (access_granted, reason). Fail closed if anything is missing or uncertain."""
    repair_id = (repair_id or "").strip()
    session_token = os.environ.get("JBOT_SESSION_TOKEN", "").strip()
    base_url = os.environ.get("JBOT_BILLING_URL", "").strip().rstrip("/")

    if not repair_id:
        return False, "A repair session ID is required."
    if not base_url:
        return False, "Checkout is not configured yet; paid repair access remains locked."
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.hostname:
        return False, "Billing URL must use HTTPS."
    if not session_token:
        return False, "Sign-in is required to verify a paid repair session."

    payload = json.dumps({"repair_id": repair_id}).encode("utf-8")
    request = Request(
        base_url + "/v1/entitlements/repair-check",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + session_token,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code in (401, 403):
            return False, "The billing service did not authorize this repair session."
        return False, f"Billing verification failed with HTTP {exc.code}; repair remains locked."
    except (URLError, TimeoutError, OSError):
        return False, "Billing service could not be reached; repair remains locked."
    except json.JSONDecodeError:
        return False, "Billing service response was invalid; repair remains locked."

    # Require explicit, matching values from the trusted HTTPS service. Never trust a
    # user-entered "paid" flag, receipt string, or local environment variable as payment.
    if (
        result.get("paid") is True
        and result.get("status") == "paid"
        and result.get("repair_id") == repair_id
    ):
        return True, "Payment verified for this repair session."
    return False, "No verified payment was found for this repair session."
