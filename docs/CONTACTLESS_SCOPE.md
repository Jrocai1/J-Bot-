# Contactless Repair Scope

J-Bot focuses on software diagnostics and supported USB, wireless, or manufacturer-authorized OTA workflows. It does not perform internal hardware repair.

## Contactless workflow
- Use USB, supported serial, Wi-Fi, or authorized OTA/MDM interfaces.
- Start with read-only discovery.
- Confirm customer consent and technician authorization.
- Verify model, region/variant, OS/firmware, package integrity, and supported recovery path.
- Require explicit approval for sensitive or destructive operations.
- Record the operation and verify its result.
- Stop safely on mismatches or uncertainty.

## Not implemented in this foundation
- Universal compatibility across all retail brands.
- Automatic firmware flashing, factory reset, lock removal, or data recovery.
- Fleet OTA deployment or multi-tenant administration.
- Full Apple device diagnostics; supported vendor interfaces and tested adapters are required.

A USB connection does not grant permission to access device data. Never bypass account locks, encryption, or security controls, and never use unverified firmware.
