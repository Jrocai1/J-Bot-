# J-Bot — Contactless Repair Intelligence

J-Bot is a local-first contactless repair assistant. It starts with read-only discovery and deterministic troubleshooting. It does not open devices, solder, bypass account locks, or automatically flash firmware.

## Current foundation
- Read-only Windows Plug-and-Play discovery.
- Optional Android discovery through Android Debug Bridge (ADB), if installed.
- Deterministic connection troubleshooting.
- Local SQLite audit log.
- No paid APIs or third-party Python packages required.
- Unit tests using Python's standard library.

This is a working foundation, not a claim that every brand/model is supported or that a repair has been completed. Device support depends on model, drivers, OS, permissions, cable, and manufacturer interfaces.

## Run on Windows 11
Install Python 3.12 or newer, extract the repository ZIP, open PowerShell in the project folder, and run:

    py -3 -m jbot

Read-only scan: `py -3 -m jbot scan`

Troubleshooting checklist: `py -3 -m jbot diagnose`

Tests: `py -3 -m unittest discover -s tests -v`

Or double-click run-jbot.bat.

## Run with Git
Install Git for Windows, then use PowerShell:

    git clone https://github.com/Jrocai1/J-Bot-.git
    cd J-Bot-
    py -3 -m jbot

If the repository is private, sign in to GitHub or use GitHub Desktop and ensure you have repository access. Never paste access tokens into chat or commit them to source files.

## Optional Android discovery
Install Android Platform Tools from the official Android developer site. Enable USB debugging only on devices you own or are explicitly authorized to service, connect the device, and approve its prompt. Then run the scan command. If ADB is missing, J-Bot reports that Android discovery is unavailable instead of pretending a device was found.

## Safety and boundaries
Discovery and recommendations are read-only. No model-generated shell commands are executed. Firmware, factory reset, bootloader changes, and data erasure are not implemented. Real repair workflows require model-specific adapters, verified manufacturer procedures, compatibility data, and hardware testing before support is advertised.
