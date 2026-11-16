# Profile: Disconnected Operations

**Status:** Working Draft (experimental)
**Domain:** Autonomous agents operating in degraded, disconnected, or contested connectivity environments
**Applies to:** OT/ICS environments, defense and national security, remote field operations, critical infrastructure

---

## Status Note

This profile is a working draft. The normative specification for pre-authorization envelope evaluation, cryptographic signing requirements, and state reconciliation on reconnection is in progress. Fields marked **[WORKING DRAFT]** have defined schema and semantics but normative evaluation requirements are not yet locked.

**Experimental. Not a safety certification.** v0.1 defines no signing scheme, no envelope integrity check and no reconciliation protocol, so nothing in this profile can be relied on as a verified control. A contract conforming to this profile has not been validated for safety in any OT/ICS environment. ADC expresses authorization: what an agent is permitted to decide. It does not replace protective relays, safety instrumented systems, interlocks or any other independent safety function, and it must not be used as one.

Community contributions to this profile are explicitly invited. See `CONTRIBUTING.md` and RFC-0002 (forthcoming).

---

## Scope

This profile governs ADC usage for agents that must maintain authorized, accountable operation when they cannot reach an evaluation runtime in real time. The core problem: an agent with real-time runtime access can have every decision evaluated at execution time. An agent operating disconnected must carry its authority with it — bounded, pre-validated, and cryptographically tied to the issuing contract.

This is the machine-readable formalization of the authority models that C2 (Command and Control) doctrine has applied to human-operated systems for decades: pre-delegated authority, rules of engagement, and positive vs. procedural control — now expressed as evaluable contract semantics for autonomous agents.

---

## Connectivity States

This profile defines normative behavior for all four connectivity states:

| Mode | Definition | Authority Behavior |
|---|---|---|
| `connected` | Full real-time access to the evaluation runtime | Full contract authority; every decision evaluated by runtime |
| `degraded` | Runtime reachable with latency or intermittently | Pre-authorized subset active; non-pre-authorized decisions queue for runtime evaluation when available |
| `disconnected` | Runtime unreachable | Pre-authorization envelope governs; decisions outside envelope are denied |
| `contested` | Active disruption; communication integrity uncertain | Minimal safe actions only; all non-pre-authorized decisions denied; halt and report on reconnect |

---

## Pre-Authorization Envelope

**[WORKING DRAFT]**

The pre-authorization envelope is the bounded set of decisions an agent is cleared to execute autonomously when disconnected. It is defined at contract issuance and is intended to be validated as a strict subset of the contract's `authority` block and cryptographically signed by the issuing runtime. v0.1 specifies neither the subset check nor the signing scheme; both are open questions below.

### Design Principles

**Minimum viable envelope.** The envelope should contain only the decisions necessary for safe continued operation during the expected disconnection window. Every decision type in the envelope is one that will execute without real-time oversight.

**Time-bounded.** All envelopes must specify `envelope_ttl_seconds`. On expiry without reconnection, `on_envelope_expiry` governs behavior. `halt` is the safe default for high-criticality systems. `minimal_safe_actions_only` is appropriate for systems where complete halt is itself unsafe (e.g., active infrastructure control).

**Protective bias.** When in doubt about whether a decision should be in the envelope, exclude it. The cost of an agent halting and waiting for reconnection is almost always lower than the cost of an unauthorized autonomous decision in a disconnected state.

### Example

```json
"connectivity": {
  "assumed_mode": "connected",
  "pre_authorization_envelope": {
    "authorized_decisions": [
      "isolate_faulted_segment",
      "activate_backup_power"
    ],
    "authorized_data_domains": [
      "scada.substation_local.*",
      "ops.event_log"
    ],
    "envelope_ttl_seconds": 14400,
    "on_envelope_expiry": "minimal_safe_actions_only"
  },
  "reconnection_behavior": {
    "sync_audit_log": true,
    "await_ratification": true
  }
}
```

---

## Reconnection Behavior

On restoration of connectivity, the following sequence is recommended:

1. Agent transmits complete audit log of all decisions made during disconnected operation (`sync_audit_log: true`).
2. If `await_ratification: true`, agent pauses new non-trivial decision-making until the runtime has reviewed and acknowledged the disconnected operation log.
3. Runtime validates that all disconnected decisions were within the pre-authorization envelope.
4. Runtime issues ratification confirmation or flags violations for review.
5. Agent resumes full connected operation under standard contract authority.

---

## Required Fields

| Field | Requirement | Rationale |
|---|---|---|
| `connectivity.assumed_mode` | Must be set explicitly | Disconnected profiles must declare their connectivity assumption |
| `connectivity.pre_authorization_envelope` | Required | Disconnected operation without a defined envelope means the agent has no authorized autonomous scope |
| `connectivity.pre_authorization_envelope.envelope_ttl_seconds` | Required | Unbounded envelopes create indefinite autonomous authority |
| `connectivity.pre_authorization_envelope.on_envelope_expiry` | Required | Behavior on TTL expiry must be explicit |
| `connectivity.reconnection_behavior.sync_audit_log` | Must be `true` | Disconnected operation audit trail is required for accountability |
| `binding.audit_required` | Must be `true` | All decisions, including disconnected ones, must be logged |

---

## Recommended Constraint Patterns

**Hard prohibitions that persist in all connectivity states:**
```json
{
  "id": "no-restoration-without-authorization",
  "description": "Agent may not restore a previously isolated or halted system component without explicit human authorization, regardless of connectivity state.",
  "applies_to": "decision",
  "on_violation": "deny_and_halt"
}
```

```json
{
  "id": "no-scope-expansion-disconnected",
  "description": "Agent may not access data domains or invoke tools outside its pre-authorization envelope while operating in disconnected or contested mode.",
  "applies_to": "all_actions",
  "on_violation": "deny_and_halt"
}
```

---

## Open Questions (RFC-0002)

The following normative requirements are under active development:

- Cryptographic signing scheme for pre-authorization envelopes
- Envelope integrity verification at runtime evaluation
- State reconciliation protocol on reconnection (full replay vs. summary attestation)
- Handling of envelope violations discovered post-reconnection
- Behavior when contested mode integrity cannot be verified

Community input on these questions is explicitly invited. Open an issue labeled `profile: disconnected` or contribute to RFC-0002 when published.

---

## Example

See `examples/critical-infrastructure-grid-agent.json` for a complete example conforming to this profile.
