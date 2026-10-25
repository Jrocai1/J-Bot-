# J-Bot — J-ROC AI Contactless Repair Agent

J-Bot is the J-ROC AI contactless diagnostic and troubleshooting agent. It is intended for Windows 11 and Linux hosts, with read-only USB/device discovery, local AI chat, modular diagnostic expansions, and an audit trail.

> **Repository status:** The working contactless-repair implementation and its test suite currently live on `foundation/contactless-repair-mvp`. The default `main` branch is still the original Builder.io starter and is not the working repair application. Do not treat the starter UI on `main` as a complete J-Bot release.

## Open the working implementation

- [Working branch: foundation/contactless-repair-mvp](https://github.com/Jrocai1/J-Bot-/tree/foundation/contactless-repair-mvp)
- [Working-branch README and setup instructions](https://github.com/Jrocai1/J-Bot-/blob/foundation/contactless-repair-mvp/README.md)
- [Latest J-Bot CI workflow runs](https://github.com/Jrocai1/J-Bot-/actions/workflows/tests.yml)

## Windows 11 quick start

Install Python 3.12 or newer. Then open PowerShell and run:

```powershell
git clone https://github.com/Jrocai1/J-Bot-.git
cd J-Bot-
git checkout foundation/contactless-repair-mvp
```

Follow the exact setup instructions in the working-branch README before launching the app. The current implementation includes a local dashboard/API and a separate local-Ollama chat foundation; these are not yet one unified production-ready hosted chat service.

## Safety and honest status

- Repair work is software-based and contactless: USB or authorized wireless interfaces only.
- Device discovery is read-only; AI output is advisory and must not be treated as proof of a successful repair.
- No account-lock/security bypass, unverified firmware, or automatic destructive operation.
- Local AI requires Ollama and a compatible model installed on the host.
- Payment checkout, production enterprise SSO/RBAC, fleet OTA orchestration, and a signed Windows installer must not be considered implemented unless verified in code and tested.

## Development and tests

Use the working branch, preserve existing source, and run the test suite before claiming a fix:

```powershell
py -3 -m unittest discover -s tests -v
```

Track any failed test or missing feature as an explicit blocker. Never report a successful build, installation, repair, or deployment without a corresponding verification result.
