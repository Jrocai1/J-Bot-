# J-Bot — Contactless Repair Intelligence

J-Bot is a local-first AI assistant for contactless device diagnostics. General chat and initial non-invasive diagnostics are free. **Detailed repair guidance and paid repair workflows require a verified payment entitlement.** J-Bot never opens devices, solders components, bypasses security, or executes AI-generated commands.

## What is implemented
- Read-only Windows Plug-and-Play discovery.
- Optional Android discovery through ADB.
- Deterministic connection troubleshooting.
- Local SQLite audit log.
- Local Ollama chat using Python's standard library; no paid AI API is required.
- Server-verified paid repair entitlement gate; it fails closed when billing is not configured.
- Unit tests and Windows/Linux GitHub Actions checks.

This is an implementation foundation, not a claim that every brand/model is supported or that a repair has been completed. Device support depends on the model, drivers, OS, permissions, cable, and manufacturer interfaces.

## Run on Windows 11

### 1. Install prerequisites
Install Python 3.12 or newer and [Ollama for Windows](https://ollama.com/download/windows). Ollama runs local models on your computer; local performance depends on memory and hardware.

Open PowerShell and download a small model:

    ollama pull qwen2.5:3b

The model download is about 1.9 GB. The official model page is [Ollama Qwen2.5](https://ollama.com/library/qwen2.5).

### 2. Get the J-Bot branch

    git clone https://github.com/Jrocai1/J-Bot-.git
    cd J-Bot-
    git checkout foundation/contactless-repair-mvp

### 3. Run J-Bot

    py -3 -m jbot status
    py -3 -m jbot chat

Ask a one-off question:

    py -3 -m jbot ask "Why is my Android device not detected over USB?"

Run a read-only scan:

    py -3 -m jbot scan

Print the free diagnostic checklist:

    py -3 -m jbot diagnose

Request a repair (locked until a trusted billing server confirms payment):

    py -3 -m jbot repair --repair-id YOUR_REPAIR_SESSION_ID "Help me repair this device"

Tests:

    py -3 -m unittest discover -s tests -v

If the repository is private, sign in to GitHub or use GitHub Desktop and confirm you have access. Never paste a personal access token into chat or commit it to source files.

## Paid repair rule

Free users can ask general questions and run safe, read-only diagnostics. Repair-specific prompts, detailed repair guidance, firmware work, resets, and fleet repair are treated as paid features. The AI module itself checks entitlement; a caller-supplied "paid" flag cannot unlock it.

The gate expects a trusted HTTPS billing service configured with `JBOT_BILLING_URL` and an authenticated `JBOT_SESSION_TOKEN`. Its endpoint `POST /v1/entitlements/repair-check` must verify a real payment and return the exact repair session ID and paid status. The app does not accept a typed receipt or local flag as proof of payment.

**Checkout is not live yet.** A payment provider, signed-webhook verifier, login/session backend, price catalog, refunds, and billing deployment must be configured and tested before collecting real customer payments or promising paid unlocks. Never store card numbers inside J-Bot.

## Safety boundaries

Inference is local to Ollama at `127.0.0.1`; remote inference endpoints are rejected by this MVP. No model-generated command is executed. Automatic firmware flashing, factory reset, bootloader changes, data erasure, and fleet OTA execution are not implemented. Only service devices you own or are explicitly authorized to repair.
