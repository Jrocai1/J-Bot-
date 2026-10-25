# Paid repair access contract

J-Bot allows free general chat, read-only device discovery, and basic diagnostics. Detailed repair procedures, firmware/OTA workflows, and fleet repair are paid features.

## Trust boundary

The desktop client must never treat a user-entered price, receipt text, environment flag, or locally edited database row as proof of payment. Repair access is granted only when the trusted billing service verifies the signed payment-provider event and confirms an entitlement for the exact repair session.

## Billing API contract

Configure the desktop environment with:
- `JBOT_BILLING_URL`: base HTTPS URL for the owner's billing service.
- `JBOT_SESSION_TOKEN`: signed-in user's session token issued by the authentication service.
- `JBOT_OLLAMA_MODEL`: optional installed local Ollama model name.
- `JBOT_OLLAMA_URL`: optional local Ollama API URL; remote inference URLs are rejected.

The endpoint expected by this MVP is `POST /v1/entitlements/repair-check` with a JSON body `{"repair_id":"..." }` and a session bearer token. The billing service must return a JSON object containing `paid: true`, `status: "paid"`, and the exact same `repair_id` only after verified payment. Any missing configuration, network error, mismatch, pending payment, refund, or invalid response keeps repair access locked.

## Important: checkout is not live yet

The local gate is implemented; a payment provider checkout, signed webhook verifier, customer account/session service, price catalog, refunds, and billing backend still need to be configured and tested. Do not advertise that customers can pay or unlock paid repair until those components are deployed and verified. Never store payment card numbers in J-Bot.
