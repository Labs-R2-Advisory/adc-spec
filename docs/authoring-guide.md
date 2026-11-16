# ADC Authoring Guide

**ADC Specification — v0.1 Working Draft**
R2 Advisory | April 2026 | Apache 2.0

How to write an Agent Delegation Contract. This guide walks through the authoring process step by step, with decision points and examples at each stage. For field definitions, see `docs/field-reference.md`. For worked examples, see `examples/`.

---

## Before You Start

An ADC is a formal authorization contract, not a configuration file. Before writing a single field, answer four questions:

**1. Who is the agent?**
What system, model, or process is being governed? What is its stable identity in your environment? What is it trying to do?

**2. Who is the principal?**
Who is accountable for this agent's authorized actions? This is the human, role, or organizational authority that owns the decision to authorize this agent. If you cannot name a principal, the agent should not be authorized.

**3. What is the minimum authority this agent needs?**
Not what it might use. Not what would be convenient. The minimum scope required to complete its function. Every permission you add is a surface area for misuse or error.

**4. What must this agent never do?**
Identify the hard prohibitions before you enumerate permissions. Constraints override authority. Knowing your hard limits first prevents accidentally permitting them through a broadly written authority block.

---

## Step 1: Set Contract Identity

Every ADC needs a globally unique, immutable identifier and a version reference.

```json
{
  "adc_version": "0.1",
  "contract_id": "urn:adc:yourorg:cx-support-agent:2026-04-16:v1"
}
```

**URI format recommendation:** `urn:adc:{org}:{agent}:{YYYY-MM-DD}:{v1}`

The `contract_id` is immutable. If you change the contract terms, you issue a new contract with a new `contract_id`. Previous versions are retained for audit. Do not reuse or mutate a `contract_id`.

Add `contract_meta` to record authorship and lifecycle:

```json
"contract_meta": {
  "issued_at": "2026-04-16T00:00:00Z",
  "expires_at": "2026-10-16T00:00:00Z",
  "authored_by": "security-team@yourorg.com",
  "description": "Governs the customer support agent. Authorized to read support tickets and CRM records, draft responses, and escalate billing disputes to a human agent.",
  "labels": {
    "vertical": "customer-support",
    "environment": "production",
    "team": "cx-platform"
  }
}
```

Set `expires_at` for all production contracts. Short-lived contracts reduce risk from stale permissions. Renew explicitly rather than granting indefinite authority.

---

## Step 2: Define the Agent

```json
"agent": {
  "agent_id": "cx-support-agent-prod-001",
  "agent_type": "task_agent",
  "agent_version": "2.1.0"
}
```

`agent_id` must be resolvable in the evaluating runtime's agent registry. Use a stable, meaningful identifier — not a randomly generated UUID that has no operational meaning.

If this agent was spawned by a parent agent, record the lineage:

```json
"agent": {
  "agent_id": "cx-support-agent-prod-001",
  "agent_type": "task_agent",
  "spawned_by": "cx-planning-agent-prod",
  "parent_contract_id": "urn:adc:yourorg:cx-planning-agent:2026-04-16:v1"
}
```

The `parent_contract_id` links this contract to its parent. The authority in this contract must be a subset of the parent's authority. The evaluating runtime should enforce this invariant.

---

## Step 3: Name the Principal

```json
"principal": {
  "principal_id": "cx-platform-owner@yourorg.com",
  "principal_type": "human",
  "delegation_depth": 0
}
```

For agents spawned by other agents, the principal is the delegating agent:

```json
"principal": {
  "principal_id": "cx-planning-agent-prod",
  "principal_type": "agent",
  "delegation_depth": 1
}
```

`delegation_depth` tracks how many hops from the root human principal this contract is. L0 is always a human. L1 is directly authorized by a human. L2 is authorized by an L1 agent. Runtimes may enforce a maximum depth policy.

---

## Step 4: Define Authority

Authority covers three dimensions: data access, tools, and decisions. Define only what the agent needs.

### Data Access

For each data domain the agent needs to access:

```json
"authority": {
  "data_access": [
    {
      "domain": "crm.support_tickets",
      "classification_ceiling": "confidential",
      "operations": ["read", "write"]
    },
    {
      "domain": "crm.customer_profiles",
      "classification_ceiling": "confidential",
      "operations": ["read"]
    }
  ]
}
```

**Classification ceiling** is a hard limit. If a document in the domain is classified above the ceiling, access is denied regardless of the permitted operations.

**Operations** are an allowlist. If you omit `write`, the agent cannot write — even if the domain's ACL would otherwise permit it.

Use **conditions** to add context-dependent restrictions:

```json
{
  "domain": "crm.billing_records",
  "classification_ceiling": "restricted",
  "operations": ["read"],
  "conditions": [
    {
      "field": "ticket.category",
      "operator": "eq",
      "value": "billing_dispute"
    }
  ]
}
```

This agent can only read billing records when the ticket category is `billing_dispute`. Outside that context, access is denied.

### Tools

```json
"tools": [
  {
    "tool_id": "crm.ticket_api",
    "permitted_actions": ["get_ticket", "update_status", "add_note"]
  },
  {
    "tool_id": "email.send",
    "permitted_actions": ["send"],
    "conditions": [
      {
        "field": "email.recipient_domain",
        "operator": "in",
        "value": ["yourorg.com", "support.yourorg.com"]
      }
    ]
  }
]
```

`permitted_actions` is an allowlist of specific methods within the tool. Do not grant access to a tool and expect the agent to self-limit to a subset — specify the subset explicitly.

### Decisions

```json
"decisions": [
  {
    "decision_type": "close_support_ticket",
    "autonomous": true,
    "thresholds": [
      {
        "field": "ticket.resolution_confirmed_by_customer",
        "operator": "eq",
        "value": true
      }
    ]
  },
  {
    "decision_type": "issue_refund",
    "autonomous": true,
    "thresholds": [
      {
        "field": "refund.amount_usd",
        "operator": "lte",
        "value": 50
      }
    ]
  },
  {
    "decision_type": "escalate_to_specialist",
    "autonomous": false
  }
]
```

`autonomous: false` means this decision type always routes to escalation. The agent may not execute it autonomously under any condition.

---

## Step 5: Write the Constraints

Constraints are the hard limits. Write them before finalizing the authority block. If you find that a constraint conflicts with something you wrote in authority, the constraint wins — revise the authority, not the constraint.

```json
"constraints": [
  {
    "id": "no-external-email",
    "description": "Agent may not send email to any recipient outside yourorg.com or support.yourorg.com.",
    "applies_to": "tool_invocation",
    "on_violation": "deny_and_escalate"
  },
  {
    "id": "no-financial-data-write",
    "description": "Agent may not write to any financial data domain.",
    "applies_to": "data_access",
    "on_violation": "deny_and_halt"
  },
  {
    "id": "no-pii-export",
    "description": "Agent may not export any data classified confidential or above.",
    "applies_to": "data_access",
    "on_violation": "deny_and_halt"
  }
]
```

**Choose `on_violation` deliberately:**
- `deny`: block and log. Suitable for routine boundary enforcement.
- `deny_and_escalate`: block, log, and route to a human. Suitable for violations that require review.
- `deny_and_halt`: block, log, and stop all agent activity. Suitable for high-severity violations where continued operation is unsafe.
- `log_only`: permit but record. Use only for monitoring during initial deployment. Not appropriate for production enforcement.

---

## Step 6: Define Escalation Conditions

Escalation is not an error state. It is a designed control path for decisions that exceed autonomous authority or that the principal has reserved for human judgment.

```json
"escalation": [
  {
    "trigger": "refund.amount_usd > 50",
    "escalate_to": "cx-supervisor@yourorg.com",
    "timeout": {
      "seconds": 14400,
      "on_timeout": "deny"
    },
    "priority": "routine"
  },
  {
    "trigger": "customer.account_status == 'enterprise'",
    "escalate_to": "enterprise-success@yourorg.com",
    "timeout": {
      "seconds": 3600,
      "on_timeout": "escalate_further"
    },
    "priority": "urgent"
  },
  {
    "trigger": "constraint_violation",
    "escalate_to": "security-ops@yourorg.com",
    "timeout": {
      "seconds": 1800,
      "on_timeout": "halt"
    },
    "priority": "immediate"
  }
]
```

**Every escalation rule must specify `on_timeout`.** There is no system default. `deny` is the safe default for most cases. `approve` is appropriate only when the action is low-risk and inaction is the correct response to non-engagement. `halt` is appropriate when continued operation pending a response is unsafe.

The `on_timeout` values are `deny`, `approve`, `escalate_further` and `halt`. `deny_and_halt` and `deny_and_escalate` are `on_violation` values only; they are not valid timeout actions in v0.1. For a constraint-violation escalation, the violating action is already denied by `on_violation`, so `halt` expresses "stop if nobody answers."

**Triggers are free text in v0.1.** The `trigger` field has no normative grammar. Expressions such as `refund.amount_usd > 50` are readable conventions, not a defined language, and two runtimes may interpret the same string differently. A normative trigger grammar is on the RFC backlog.

---

## Step 7: Set Binding

```json
"binding": {
  "enforcement_mode": "native",
  "on_violation": "deny_and_escalate",
  "on_expiry": "deny_all",
  "immutable": true,
  "audit_required": true
}
```

**Choose `enforcement_mode`:**
- `native`: the agent reads its ADC, self-governs, and calls the runtime for validation. Use when the agent is ADC-aware.
- `overseer`: an overseer agent validates outputs before propagation. Use as a bridge for agents that are not ADC-aware.
- `infrastructure`: the runtime intercepts actions at the infrastructure boundary. Use for data-path or gateway enforcement, or when agent awareness cannot be assumed.

Do not set `audit_required: false` in production. The audit log is the foundation of accountability.

---

## Step 8: Add Connectivity (If Applicable)

For fully connected enterprise deployments, omit the `connectivity` block entirely. For OT/ICS, field operations, defense, or any environment where the agent may lose contact with the evaluation runtime:

```json
"connectivity": {
  "assumed_mode": "connected",
  "pre_authorization_envelope": {
    "authorized_decisions": ["close_support_ticket"],
    "authorized_data_domains": ["crm.support_tickets"],
    "envelope_ttl_seconds": 3600,
    "on_envelope_expiry": "deny_new_decisions"
  },
  "reconnection_behavior": {
    "sync_audit_log": true,
    "await_ratification": false
  }
}
```

The `pre_authorization_envelope` defines what the agent may do autonomously if it loses contact with the runtime. Keep this envelope as narrow as possible. Every decision type in the envelope is one that will execute without real-time oversight.

> **WORKING DRAFT:** Normative evaluation requirements for the pre-authorization envelope are in progress. See `docs/profiles/disconnected-operations.md` when available.

---

## Common Mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Broad domain patterns without classification ceiling (`*.*`) | Agent can access any data in any domain up to any classification | Enumerate domains explicitly; always set `classification_ceiling` |
| `permitted_actions: ["*"]` on a tool | Agent can invoke any method on the tool | List specific permitted methods |
| No `expires_at` on production contracts | Stale permissions accumulate; credentials outlive their purpose | Set expiry; build renewal into operational procedures |
| No escalation rule for constraint violations | Security violations are blocked but not reviewed | Always add an escalation rule with `trigger: "constraint_violation"` |
| `on_timeout: "approve"` on high-risk escalations | Unreviewed high-risk decisions execute if the human does not respond | Use `deny` or `halt` as default for anything consequential |
| `audit_required: false` | No record of decisions; accountability chain broken | Never disable audit in production |
| Missing `parent_contract_id` on spawned agents | Delegation lineage is broken; parent authority invariant cannot be enforced | Always set `parent_contract_id` for sub-agent contracts |

---

## Validation

Before committing an ADC to a runtime registry, validate it against the JSON Schema:

```bash
# Using ajv-cli
npx ajv validate -s spec/adc-v0.1.json -d your-adc.json

# Using Python jsonschema
python3 -c "
import json, jsonschema
schema = json.load(open('spec/adc-v0.1.json'))
instance = json.load(open('your-adc.json'))
jsonschema.validate(instance, schema)
print('Valid')
"
```

Schema validation confirms structure. It does not validate that your authority scope is appropriate, that your escalation targets are reachable, or that your constraints are sufficient. Those are authoring decisions that require human review.

Three v0.1 limits to keep in mind when reading a "Valid" result:

- **Valid is not enforceable.** A constraint with only a `description` and no `rule` is schema-valid, but no runtime can evaluate it as written. Add a `rule` in your runtime's syntax for any constraint you expect a machine to enforce.
- **Unknown fields pass.** The v0.1 schema does not set `additionalProperties: false`, so a misspelled field such as `decisons` is accepted and silently ignored. Check field names against `docs/field-reference.md`.
- **Valid is not in force.** Schema validation does not check `expires_at` against the current time. An expired contract still validates.

To check this repository's own examples and documentation snippets, run `python3 tests/validate.py`.
