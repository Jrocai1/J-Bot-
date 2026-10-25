# J-Bot Agent Fixer

J-Bot is a local-first contactless diagnostic assistant and modular expansion host. Current work lives on the branch `foundation/contactless-repair-mvp`; it is not yet merged into `main`.

## Included components

- `core_engine.py`: authenticated FastAPI service, local dashboard, dynamic trusted local plugin loader, redacted local diagnostic history, and opt-in SMTP alerts.
- `ui/index.html`: responsive HTML5 dashboard for desktop, tablet, and phone browsers.
- `expansions/phone_gadget_fixer/`: contactless phone/tablet triage.
- `expansions/ebike_ev_fixer/`: cautious e-bike/e-scooter fault triage.
- `expansions/usb_serial_monitor/`: serial-port inventory and explicitly confirmed, bounded read-only capture.
- `expansions/console_fixer/`: non-invasive gaming console troubleshooting.
- `jbot/`: local Ollama AI command-line foundation, payment entitlement gate, SQLite event storage, and deterministic diagnostics.
- `tests/`: regression and expansion tests.
- `docs/`: contactless safety and paid-repair access rules.

Diagnostic recommendations are not proof a device was repaired. The plugins do not open devices or replace physical components. The USB serial plugin never writes bytes to a connected controller.

## Windows 11 quick start

1. Install Python 3.12+ and Git for Windows.
2. Clone the repository and check out the working branch:

   ```powershell
   git clone https://github.com/Jrocai1/J-Bot-.git
   cd J-Bot-
   git checkout foundation/contactless-repair-mvp
   ```

3. Double-click `run_jbot.bat`, or run it in PowerShell.
4. Open `http://127.0.0.1:8080` in a browser.
5. Copy the temporary session token displayed in the terminal into the dashboard's token field.
6. Choose a module, enter diagnostic JSON, and run the diagnostic.

The launch script creates a local virtual environment and installs the listed free/open-source dependencies. It does not install a paid API or send diagnostic data to a cloud model.

## Run the tests

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Or with a preconfigured Python installation:

```powershell
py -3 -m unittest discover -s tests -v
```

## Optional local AI model

The `jbot` command-line AI uses a local Ollama server. Install Ollama and obtain a model supported by your PC:

```powershell
ollama pull qwen2.5:3b
py -3 -m jbot chat
```

The local AI command-line layer is separate from the current HTML5 diagnostic dashboard. No paid-repair entitlement is considered valid until a trusted billing service verifies it. Checkout is not live in this repository.

## Security configuration

The API binds to `127.0.0.1` by default. A temporary random access token is printed to the local terminal for that run. A configured `JBOT_ACCESS_TOKEN` is required before binding to a non-local address.

To access from another device, do not expose a plain HTTP token endpoint directly to the public internet. Use HTTPS with an authenticated reverse proxy or a secured private VPN/tunnel and firewall rules. Never commit tokens or SMTP passwords.

Optional email alerts are disabled unless `JBOT_EMAIL_ALERTS=1` is set and `JBOT_SMTP_SERVER`, `JBOT_SMTP_PORT`, `JBOT_SENDER_EMAIL`, `JBOT_SMTP_PASSWORD`, and `JBOT_RECEIVER_EMAIL` are configured in the process environment.

## Hardware and repair boundaries

- All current device work is software-based, USB, or wireless.
- No account-lock bypass, activation-lock bypass, FRP bypass, or unauthorized data access.
- No automatic firmware flashing, resets, bootloader changes, speed-limit modification, controller-wire bypass, or other destructive changes.
- Fault codes, voltage values, and symptoms submitted by a user are treated as reported data, not as independently verified measurements.
- Only trusted local plugin code should be installed; Python plugins run inside the J-Bot process.
- Fleet OTA, full enterprise IAM/SSO, and production payment checkout are not yet implemented.
