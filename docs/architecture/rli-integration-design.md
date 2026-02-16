# RLI Integration Design

## Overview

This document defines the integration contract between Forge backend services and the RLI evaluation platform used by the Chainlink reputation workflow.

Goals:
- Standardize authentication and credential scope.
- Define explicit JSON schemas for create-comparison and get-result APIs.
- Standardize lifecycle transitions and polling behavior.
- Define idempotency and duplicate callback behavior for Chainlink fulfillments.

## Authentication and Credential Scope

### Mechanism
- **Transport security:** HTTPS only.
- **Authentication type:** API key in bearer token format.
- **Header:** `Authorization: Bearer <RLI_API_TOKEN>`.
- **Secondary header (recommended):** `X-Client-Id: forge-backend` for partner-level traceability.

### Credential Scope
- Token scope must be constrained to:
  - `rli.comparisons.create`
  - `rli.comparisons.read`
- Token must **not** include admin or account-management permissions.
- Use separate tokens per environment (`dev`, `staging`, `prod`).
- Rotation policy: rotate every 90 days or immediately after suspected exposure.

### Operational Requirements
- Never log raw bearer tokens.
- Persist only the last 4 characters for troubleshooting (`token_suffix`).
- Requests without authorization MUST be treated as `401 unauthorized` and non-retryable.

## API Schemas

The backend consumes two API endpoints:

1. `POST /v1/comparisons` — create comparison.
2. `GET /v1/comparisons/{comparison_id}` — retrieve status and final evaluation result.

---

## Create Comparison

### Request JSON Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "comparison_id",
    "member_address",
    "request_id",
    "task_brief",
    "ai_deliverable",
    "human_baseline",
    "callback"
  ],
  "properties": {
    "comparison_id": { "type": "string", "minLength": 1 },
    "member_address": { "type": "string", "pattern": "^0x[a-fA-F0-9]{40}$" },
    "request_id": { "type": "string", "minLength": 1 },
    "task_brief": { "type": "string", "minLength": 1 },
    "ai_deliverable": { "type": "string", "minLength": 1 },
    "human_baseline": { "type": "string", "minLength": 1 },
    "metadata": {
      "type": "object",
      "additionalProperties": { "type": ["string", "number", "boolean", "null"] }
    },
    "callback": {
      "type": "object",
      "additionalProperties": false,
      "required": ["url", "hmac_secret_ref"],
      "properties": {
        "url": { "type": "string", "format": "uri" },
        "hmac_secret_ref": { "type": "string", "minLength": 1 }
      }
    }
  }
}
```

### Response JSON Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "comparison_id",
    "state",
    "submitted_at"
  ],
  "properties": {
    "comparison_id": { "type": "string", "minLength": 1 },
    "state": { "type": "string", "enum": ["submitted"] },
    "submitted_at": { "type": "string", "format": "date-time" },
    "idempotency_key": { "type": "string" }
  }
}
```

---

## Get Result

### Response JSON Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["comparison_id", "state"],
  "properties": {
    "comparison_id": { "type": "string", "minLength": 1 },
    "state": {
      "type": "string",
      "enum": ["pending", "submitted", "processing", "completed", "failed", "timed_out"]
    },
    "updated_at": { "type": "string", "format": "date-time" },
    "result": {
      "type": "object",
      "additionalProperties": false,
      "required": ["automation_rate", "elo_score", "economic_value", "comparison_url"],
      "properties": {
        "automation_rate": { "type": "number", "minimum": 0, "maximum": 1 },
        "elo_score": { "type": "integer", "minimum": 0 },
        "economic_value": { "type": "number" },
        "comparison_url": { "type": "string", "format": "uri" }
      }
    },
    "error": {
      "type": "object",
      "additionalProperties": false,
      "required": ["code", "message"],
      "properties": {
        "code": { "type": "string", "minLength": 1 },
        "message": { "type": "string", "minLength": 1 },
        "retryable": { "type": "boolean" }
      }
    }
  },
  "allOf": [
    {
      "if": { "properties": { "state": { "const": "completed" } } },
      "then": { "required": ["result"] }
    },
    {
      "if": { "properties": { "state": { "enum": ["failed", "timed_out"] } } },
      "then": { "required": ["error"] }
    }
  ]
}
```

## Evaluation Lifecycle

Canonical lifecycle:

`pending -> submitted -> processing -> completed | failed | timed_out`

Rules:
- `pending`: locally registered; outbound submit not yet acknowledged.
- `submitted`: RLI accepted the comparison request.
- `processing`: evaluator actively processing artifacts.
- Terminal states:
  - `completed`: numeric evaluation result available.
  - `failed`: unrecoverable processing error in RLI.
  - `timed_out`: processing exceeded timeout budget.

State constraints:
- No transition from any terminal state to non-terminal state.
- `completed`, `failed`, and `timed_out` are terminal and immutable.

## Polling Algorithm

For integrations that poll `GET /v1/comparisons/{comparison_id}`:

- **Initial delay:** `2s` after successful create response.
- **Base interval:** `2s`.
- **Backoff:** exponential, `next = min(current * 2, 30s)`.
- **Max retries:** `8` poll attempts after initial delay.
- **Total timeout budget:** `120s` from create timestamp.
- **Jitter:** add random jitter in range `[0, 250ms]` to reduce synchronized bursts.

Polling stop conditions:
1. State is terminal (`completed`, `failed`, `timed_out`).
2. Retry limit reached.
3. Total timeout exceeded.

On stop due to retries/timeout without terminal state, integration sets local status to `timed_out`.

## Error Taxonomy

### 4xx Client Errors
- `400 invalid_request`: malformed JSON, missing required fields.
- `401 unauthorized`: missing/invalid token.
- `403 forbidden`: token lacks required scope.
- `404 not_found`: unknown `comparison_id`.
- `409 conflict`: duplicate create with mismatched payload for same idempotency key.
- `422 invalid_payload`: semantic validation failed (e.g., bad address format).

Handling:
- Non-retryable by default except explicit `429` rate limits.

### 5xx Server Errors
- `500 internal_error`
- `502 bad_gateway`
- `503 unavailable`
- `504 gateway_timeout`

Handling:
- Retryable with backoff, bounded by `max_retries` and total timeout.

### Timeout Conditions
- Network timeout from client HTTP layer.
- Polling timeout before terminal state.

Handling:
- Retry network timeout if budget remains.
- Mark as `timed_out` when total timeout budget is exhausted.

### Invalid Payload / Contract Violations
- Any response violating schema (missing required fields, wrong types, invalid state transitions) is treated as `invalid_payload`.

Handling:
- Fail request, mark local status as `failed`, and log response sample for investigation.

## Idempotency and Duplicate Callback Handling (Chainlink Fulfillment)

### Idempotency Keys
- The `create comparison` call uses deterministic idempotency key:
  - `idempotency_key = sha256(request_id + ":" + member_address + ":" + deliverable_ipfs)`
- Send with header: `Idempotency-Key: <idempotency_key>`.

Behavior:
- Same key + same payload: server returns existing comparison resource.
- Same key + different payload: server returns `409 conflict` and the request is rejected.

### Duplicate Chainlink Fulfillment Events

A fulfillment is uniquely identified by `(request_id, comparison_id)`.

Processing policy:
1. If no prior fulfillment recorded, persist result and mark request terminal.
2. If duplicate fulfillment arrives with identical terminal payload, acknowledge and no-op.
3. If duplicate fulfillment arrives with different payload, treat as integrity violation:
   - keep first accepted terminal result,
   - emit alert,
   - store conflicting payload for audit,
   - return success acknowledgement to avoid repeated retries from oracle network.

### Exactly-Once Local Effects
- Persist a local dedupe record keyed by `request_id` with:
  - final state,
  - result hash,
  - processed timestamp.
- All state updates and reputation writes must be in one transaction boundary where possible.
