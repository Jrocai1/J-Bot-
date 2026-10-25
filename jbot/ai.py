"""Local Ollama AI for J-Bot. Model output is advisory and never executed."""
from __future__ import annotations

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class OllamaUnavailable(RuntimeError):
    """Raised when the local model is unavailable or misconfigured."""


class PaymentRequired(RuntimeError):
    """Raised when a request asks for a paid repair feature."""


SYSTEM_PROMPT = """You are J-Bot, J-ROC AI's contactless troubleshooting assistant.
Help people diagnose supported connected devices using authorized USB, Wi-Fi,
Bluetooth, or manufacturer-authorized OTA interfaces. Never suggest opening devices
or internal physical repairs, bypassing passwords/account locks/encryption/security,
or using unverified firmware. Never claim a device was fixed unless a real verified
adapter reported success. Never execute or ask the host to execute shell commands.
For non-paid sessions, offer safe non-invasive triage only and explain that detailed
repair procedures are a paid service. For paid sessions, provide careful, model-specific
guidance only when the model and supported procedure are known; state uncertainty and
stop on compatibility mismatches. Destructive operations require explicit confirmation,
backups, verified compatibility, and supported recovery procedures. Prefer concise,
numbered troubleshooting instructions.
"""


# Common actionable repair requests require payment. Diagnostics and general education
# remain free; server-side entitlement verification is required to unlock these requests.
_PAID_PATTERNS = re.compile(
    r"\b(repair|fix|step[- ]by[- ]step|flash(?:ing)?|firmware|factory reset|"
    r"reset (?:my|the|this) (?:phone|device|tablet|computer)|unlock bootloader|"
    r"unbrick|bootloop|reinstall (?:the )?(?:os|operating system|firmware)|"
    r"install (?:a )?(?:rom|firmware)|restore (?:my|the|this) device|"
    r"wipe (?:my|the|this) device|ota rollout|fleet repair)\b",
    re.IGNORECASE,
)


def is_paid_repair_request(prompt: str) -> bool:
    """Conservative keyword gate for paid repair workflows."""
    return bool(_PAID_PATTERNS.search(prompt or ""))


def _local_chat_url() -> str:
    url = os.environ.get("JBOT_OLLAMA_URL", "http://127.0.0.1:11434/api/chat").strip()
    parsed = urlparse(url)
    # The MVP keeps inference local: prevent accidentally sending customer/device details
    # to a remote URL through environment configuration.
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise OllamaUnavailable(
            "J-Bot only permits a local Ollama endpoint. Use http://127.0.0.1:11434/api/chat."
        )
    return url


def ask_ollama(prompt: str, *, paid_repair: bool = False, timeout: int = 120) -> str:
    """Send one prompt to the Ollama service on this computer."""
    cleaned = (prompt or "").strip()
    if not cleaned:
        raise ValueError("Enter a question first.")
    if len(cleaned) > 12000:
        raise ValueError("Question is too long (maximum 12,000 characters).")

    model = os.environ.get("JBOT_OLLAMA_MODEL", "qwen2.5:3b").strip()
    if not model:
        raise OllamaUnavailable("JBOT_OLLAMA_MODEL is empty.")
    system = SYSTEM_PROMPT
    if not paid_repair:
        system += (
            "\nThis is a FREE diagnostic session. Do not provide a detailed repair procedure, "
            "firmware instructions, reset sequence, or state-changing operation. Provide safe "
            "preliminary checks and tell the user how to obtain paid repair access."
        )
    else:
        system += (
            "\nThe billing service has verified paid repair access for this session. "
            "Still never bypass security, use unverified firmware, or execute commands."
        )

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": cleaned},
        ],
        "options": {"temperature": 0.2},
    }
    req = Request(
        _local_chat_url(),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise OllamaUnavailable(f"Ollama returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise OllamaUnavailable(
            "Cannot reach local Ollama. Install/start Ollama and download the configured model."
        ) from exc
    except json.JSONDecodeError as exc:
        raise OllamaUnavailable("Ollama returned an invalid JSON response.") from exc

    answer = body.get("message", {}).get("content")
    if not isinstance(answer, str) or not answer.strip():
        raise OllamaUnavailable("Ollama returned no answer text.")
    return answer.strip()
