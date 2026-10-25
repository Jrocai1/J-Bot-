"""J-Bot Agent Fixer: authenticated localhost API and expansion engine."""
from __future__ import annotations
import hmac, importlib.util, json, os, secrets, smtplib, sys, threading
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any
import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent
UI_FILE = ROOT / "ui" / "index.html"
PACKS_DIR = ROOT / "expansions"
LOG_DIR = ROOT / "logs"
HISTORY_FILE = LOG_DIR / "diagnostic_history.txt"
TOKEN = os.environ.get("JBOT_ACCESS_TOKEN", "").strip()
GENERATED_TOKEN = not bool(TOKEN)
if GENERATED_TOKEN:
    TOKEN = secrets.token_urlsafe(32)
LOG_LOCK = threading.Lock()
app = FastAPI(title="J-Bot Agent Fixer", version="3.2.0", docs_url=None, redoc_url=None, openapi_url=None)


class JBotCore:
    def __init__(self):
        self.version = "3.2.0"
        self.name = "J-Bot Agent Fixer"
        self.expansions: dict[str, Any] = {}
        self.load_errors: dict[str, str] = {}
        self.lock = threading.RLock()
        PACKS_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def discover_expansions(self):
        loaded, errors = {}, {}
        with self.lock:
            for folder in sorted(PACKS_DIR.iterdir()):
                if not folder.is_dir() or folder.name.startswith((".", "_")):
                    continue
                path = folder / "plugin.py"
                if not path.is_file():
                    continue
                try:
                    spec = importlib.util.spec_from_file_location("jbot_pack_" + folder.name, path)
                    if spec is None or spec.loader is None:
                        raise RuntimeError("Could not load plugin module")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    pack_type = getattr(module, "ExpansionPack", None)
                    if pack_type is None:
                        raise TypeError("plugin.py must define ExpansionPack")
                    pack = pack_type()
                    if not callable(getattr(pack, "run_diagnostics", None)):
                        raise TypeError("ExpansionPack must define run_diagnostics(payload)")
                    loaded[folder.name] = pack
                except Exception as exc:
                    errors[folder.name] = type(exc).__name__ + ": " + str(exc)[:160]
            self.expansions, self.load_errors = loaded, errors
        return {k: str(getattr(v, "name", k)) for k, v in loaded.items()}

    @staticmethod
    def scrub(value, depth=0):
        if depth > 4:
            return "[depth-limited]"
        if isinstance(value, dict):
            output = {}
            for key, item in list(value.items())[:80]:
                low = str(key).lower()
                if any(term in low for term in ("token", "password", "secret", "authorization", "api_key", "email")):
                    output[str(key)] = "[redacted]"
                else:
                    output[str(key)] = JBotCore.scrub(item, depth + 1)
            return output
        if isinstance(value, list):
            return [JBotCore.scrub(x, depth + 1) for x in value[:80]]
        if isinstance(value, str):
            return value[:1000]
        if value is None or isinstance(value, (bool, int, float)):
            return value
        return str(value)[:400]

    @staticmethod
    def summary(result):
        for key in ("message", "summary", "jbot_action", "jbot_resolution", "jbot_remediation_protocol"):
            if isinstance(result.get(key), str):
                return result[key][:500]
        return str(result.get("status", "completed"))[:500]

    def log(self, sector, payload, result):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sector": sector,
            "status": str(result.get("status", "unknown"))[:80],
            "input": self.scrub(payload),
            "summary": self.summary(result),
        }
        with LOG_LOCK, HISTORY_FILE.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    def email_alert(self, sector, result):
        if os.getenv("JBOT_EMAIL_ALERTS", "").lower() not in {"1", "true", "yes"}:
            return
        host = os.getenv("JBOT_SMTP_SERVER", "").strip()
        sender = os.getenv("JBOT_SENDER_EMAIL", "").strip()
        password = os.getenv("JBOT_SMTP_PASSWORD", "")
        recipient = os.getenv("JBOT_RECEIVER_EMAIL", "").strip()
        try:
            port = int(os.getenv("JBOT_SMTP_PORT", "587"))
        except ValueError:
            print("[Email] Invalid SMTP port; alert skipped.")
            return
        if not all((host, sender, password, recipient)) or not 1 <= port <= 65535:
            print("[Email] SMTP configuration is incomplete; alert skipped.")
            return
        message = EmailMessage()
        message["Subject"] = "J-Bot diagnostic completed: " + sector
        message["From"], message["To"] = sender, recipient
        message.set_content("Diagnostic completed.\nSector: " + sector + "\nStatus: " +
                            str(result.get("status", "unknown")) + "\nSummary: " + self.summary(result))
        try:
            with smtplib.SMTP(host, port, timeout=8) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(message)
        except (OSError, smtplib.SMTPException, ValueError) as exc:
            print("[Email] Delivery failed:", type(exc).__name__)

    def execute_agent_fix(self, sector, payload):
        if len(json.dumps(payload, ensure_ascii=False)) > 16000:
            raise ValueError("Payload exceeds 16 KB.")
        with self.lock:
            pack = self.expansions.get(sector)
        if pack is None:
            raise KeyError("Expansion sector '" + sector + "' is missing or not loaded.")
        result = pack.run_diagnostics(payload)
        if not isinstance(result, dict):
            raise TypeError("Expansion must return a JSON object.")
        self.log(sector, payload, result)
        return result


jbot_instance = JBotCore()


def require_token(x_jbot_token: str | None = Header(default=None, alias="X-JBot-Token")):
    if not x_jbot_token or not hmac.compare_digest(x_jbot_token, TOKEN):
        raise HTTPException(status_code=401, detail="Access denied. Enter a valid J-Bot token.")


@app.on_event("startup")
def startup():
    packs = jbot_instance.discover_expansions()
    print("[J-Bot] Loaded packs:", ", ".join(packs) if packs else "(none)")
    if jbot_instance.load_errors:
        print("[J-Bot] Plugin errors:", jbot_instance.load_errors)
    if GENERATED_TOKEN:
        print("[Security] Temporary dashboard token for this run:")
        print(TOKEN)
        print("Do not share this token. It changes when the app restarts.")


@app.get("/")
def root():
    if not UI_FILE.is_file():
        raise HTTPException(status_code=500, detail="Dashboard file is missing.")
    return FileResponse(UI_FILE)


@app.get("/health")
def health():
    return {"agent": jbot_instance.name, "status": "online", "version": jbot_instance.version}


@app.get("/sectors", dependencies=[Depends(require_token)])
def sectors():
    return {
        "sectors": [{"id": k, "name": str(getattr(v, "name", k))}
                    for k, v in sorted(jbot_instance.expansions.items())],
        "load_errors": jbot_instance.load_errors,
    }


@app.post("/fix/{sector}", dependencies=[Depends(require_token)])
def fix(sector: str, data: dict[str, Any], background_tasks: BackgroundTasks):
    if not sector.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid sector.")
    try:
        result = jbot_instance.execute_agent_fix(sector, data)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except Exception as exc:
        print("[J-Bot] Pack failure:", sector, type(exc).__name__, str(exc)[:160])
        raise HTTPException(status_code=500, detail="Diagnostic failed. Check local terminal.") from exc
    background_tasks.add_task(jbot_instance.email_alert, sector, result)
    return result


@app.get("/history", dependencies=[Depends(require_token)])
def history(limit: int = Query(default=50, ge=1, le=200)):
    if not HISTORY_FILE.exists():
        return {"entries": []}
    try:
        lines = HISTORY_FILE.read_text(encoding="utf-8").splitlines()[-limit:]
        return {"entries": [json.loads(line) for line in lines if line.strip()]}
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=500, detail="Could not read local history.") from exc


def main():
    host = os.getenv("JBOT_HOST", "127.0.0.1").strip()
    try:
        port = int(os.getenv("JBOT_PORT", "8080"))
    except ValueError:
        print("JBOT_PORT must be an integer.")
        return 2
    if not 1 <= port <= 65535:
        print("JBOT_PORT must be between 1 and 65535.")
        return 2
    if host not in {"127.0.0.1", "localhost", "::1"} and GENERATED_TOKEN:
        print("Refusing network binding without a configured JBOT_ACCESS_TOKEN.")
        return 2
    print("=" * 58)
    print(jbot_instance.name, "v" + jbot_instance.version)
    print("Local-first diagnostics | localhost default | no hard-coded passwords")
    print("Dashboard: http://" + ("127.0.0.1" if host in {"0.0.0.0", "::"} else host) + ":" + str(port))
    uvicorn.run(app, host=host, port=port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
