# ADC Field Reference

**ADC Specification — v0.1 Working Draft**
R2 Advisory | April 2026 | Apache 2.0

Complete field-by-field reference for the ADC JSON Schema (`spec/adc-v0.1.json`). For concept definitions and design rationale, see `docs/concepts.md`. For worked examples, see `examples/`.

---

## Top-Level Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `adc_version` | string | Yes | Spec version this contract conforms to. Must be `"0.1"` for v0.1 contracts. |
| `contract_id` | string (URI) | Yes | Globally unique identifier. URI format. Immutable once issued. Format: `urn:adc:{org}:{agent}:{date}:{version}` |
| `contract_meta` | object | No | Authorship, lifecycle, and labeling metadata. |
| `agent` | object | Yes | Identity and classification of the governed agent. |
| `principal` | object | Yes | The authorizing party accountable for the agent's actions. |
| `authority` | object | Yes | Complete enumerated scope of permitted actions. Default: deny all. |
| `constraints` | array | No | Explicit prohibitions that override permissions. Evaluated before authority. |
| `escalation` | array | No | Conditions under which the agent must route decisions to a human or higher authority. |
| `connectivity` | object | No | Authority behavior under varying connectivity conditions. Omit for fully connected enterprise deployments. |
| `binding` | object | Yes | Enforcement mode and contract lifecycle semantics. |

---

## `contract_meta`

| Field | Type | Required | Description |
|---|---|---|---|
| `issued_at` | string (date-time) | No | ISO 8601 timestamp of contract issuance. |
| `effective_from` | string (date-time) | No | Earliest time the contract is valid. Defaults to `issued_at` if omitted. |
| `expires_at` | string (date-time) | No | Expiry time. Behavior on expiry governed by `binding.on_expiry`. |
| `authored_by` | string | No | Identity of the human or system that authored this contract. |
| `description` | string | No | Human-readable description of the agent's purpose and contract intent. |
| `labels` | object | No | Arbitrary key-value string pairs for tagging, discovery, and policy grouping. |

---

## `agent`

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_id` | string | Yes | Unique identifier for this agent instance. Must be resolvable in the evaluating runtime's agent registry. |
| `agent_type` | string (enum) | Yes | Classification of the agent. See agent types below. |
| `agent_version` | string | No | Version identifier of the agent implementation bound to this contract. |
| `spawned_by` | string | No | `agent_id` of the parent agent that spawned this agent. Establishes delegation lineage. |
| `parent_contract_id` | string (URI) | No | `contract_id` of the parent ADC under which this agent was spawned. Authority in this contract must be a subset of the parent. |

### Agent Types

| Value | Description |
|---|---|
| `ai_assistant` | Conversational or task-completion AI operating under human direction |
| `planning_agent` | Agent that decomposes goals and generates sub-agent ADCs |
| `task_agent` | Agent executing a specific bounded task |
| `data_agent` | Agent whose primary function is data access, transformation, or analysis |
| `infrastructure_agent` | Agent managing infrastructure resources or configuration |
| `autonomous_system` | Autonomous platform operating with limited real-time human oversight |
| `composite_agent` | Agent coordinating multiple sub-components or sub-agents |
| `human_node` | A human participant in the multi-agent graph with a defined authorization profile |

---

## `principal`

| Field | Type | Required | Description |
|---|---|---|---|
| `principal_id` | string | Yes | Unique identifier for the principal. For humans: IAM-resolvable identity. For agents: the delegating agent's `agent_id`. |
| `principal_type` | string (enum) | Yes | Classification of the principal: `human`, `agent`, `organization`, `system`. |
| `delegation_depth` | integer | No | Number of delegation hops from the root human principal. L0 = human principal. Minimum: 0. |

---

## `authority`

### `authority.data_access[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `domain` | string | Yes | Data domain identifier. Glob patterns supported (e.g., `client.*`, `finance.payroll`). |
| `classification_ceiling` | string (enum) | Yes | Maximum classification level accessible in this domain: `public`, `internal`, `confidential`, `restricted`, `secret`, `top_secret`. |
| `operations` | array of string | Yes | Permitted operations: `read`, `write`, `delete`, `aggregate`, `export`, `execute`. |
| `conditions` | array of condition | No | Additional conditions that must be satisfied for access. See `condition` definition below. |

### `authority.tools[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `tool_id` | string | Yes | Tool or API identifier. Should match the tool registry of the execution environment. |
| `permitted_actions` | array of string | Yes | Specific actions or methods within this tool the agent may invoke. |
| `rate_limit` | object | No | Optional rate limiting on tool invocation. |
| `rate_limit.max_calls` | integer | No | Maximum number of invocations permitted. |
| `rate_limit.window_seconds` | integer | No | Time window in seconds for the rate limit. |
| `conditions` | array of condition | No | Conditions that must be satisfied for tool access. |

### `authority.decisions[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `decision_type` | string | Yes | Identifier for the class of decision (e.g., `approve_purchase_order`, `deploy_configuration`). |
| `autonomous` | boolean | Yes | Whether the agent may execute this decision without human review. |
| `thresholds` | array of threshold | No | Numeric or categorical bounds on autonomous authority for this decision type. |
| `thresholds[].field` | string | Yes | The field being evaluated (e.g., `purchase_order.amount_usd`). |
| `thresholds[].operator` | string (enum) | Yes | Comparison operator: `lt`, `lte`, `gt`, `gte`, `eq`, `neq`, `in`, `not_in`. |
| `thresholds[].value` | any | Yes | The value to compare against. |
| `conditions` | array of condition | No | Additional conditions for this decision type. |

### `authority.delegation`

| Field | Type | Required | Description |
|---|---|---|---|
| `may_delegate` | boolean | No | Whether this agent may spawn sub-agents and issue them ADCs. Default: `false`. |
| `max_delegation_depth` | integer | No | Maximum further delegation hops permitted below this agent. Minimum: 1. |
| `delegation_constraints` | string | No | Narrative constraints that apply to any ADCs this agent issues. Sub-agent ADCs must be a strict subset of this contract's authority. |

---

## `constraints[]`

Constraints are evaluated before permissions. A constraint violation overrides any otherwise-applicable permission.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique identifier for this constraint within the contract. |
| `description` | string | Yes | Human-readable statement of the prohibition. |
| `applies_to` | string (enum) | Yes | Category of agent action governed: `all_actions`, `data_access`, `tool_invocation`, `decision`, `delegation`. |
| `rule` | string | No | Machine-evaluable expression of the constraint. Syntax is runtime-defined. |
| `on_violation` | string (enum) | No | Action on violation: `deny`, `deny_and_escalate`, `deny_and_halt`, `log_only`. Overrides `binding.on_violation` for this constraint. |

---

## `escalation[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `trigger` | string | Yes | Condition that activates this escalation rule. May reference decision type, data domain, threshold breach, or explicit flag. |
| `escalate_to` | string | Yes | `principal_id` or role identifier of the human node or authority to receive this escalation. |
| `timeout` | object | Yes | Response timeout and fallback behavior. |
| `timeout.seconds` | integer | Yes | Maximum wait time in seconds before timeout behavior applies. |
| `timeout.on_timeout` | string (enum) | Yes | Action if escalation is not resolved: `deny`, `approve`, `escalate_further`, `halt`. |
| `priority` | string (enum) | No | Urgency: `routine`, `urgent`, `immediate`. |

---

## `connectivity`

Omit this block for fully connected enterprise deployments. Required for OT/ICS, field operations, defense, and any scenario where the agent may operate without reliable runtime access.

| Field | Type | Required | Description |
|---|---|---|---|
| `assumed_mode` | string (enum) | No | Connectivity state at runtime: `connected` (default), `degraded`, `disconnected`, `contested`. |
| `pre_authorization_envelope` | object | No | Decisions and data domains pre-authorized for autonomous operation during disconnection. **WORKING DRAFT.** |
| `pre_authorization_envelope.authorized_decisions` | array of string | No | `decision_type` values from `authority.decisions` that remain authorized in disconnected mode. |
| `pre_authorization_envelope.authorized_data_domains` | array of string | No | Data domains from `authority.data_access` that remain accessible in disconnected mode. |
| `pre_authorization_envelope.envelope_ttl_seconds` | integer | No | Maximum validity period of the envelope without re-validation from the authoritative runtime. |
| `pre_authorization_envelope.on_envelope_expiry` | string (enum) | No | Behavior on TTL expiry: `halt`, `minimal_safe_actions_only`, `deny_new_decisions`. |
| `reconnection_behavior` | object | No | State reconciliation behavior on connectivity restoration. |
| `reconnection_behavior.sync_audit_log` | boolean | No | Transmit complete audit log of disconnected-operation decisions on reconnection. Default: `true`. |
| `reconnection_behavior.await_ratification` | boolean | No | Pause new decision-making on reconnection until the runtime has reviewed and ratified the disconnected operation log. Default: `false`. |

---

## `binding`

| Field | Type | Required | Description |
|---|---|---|---|
| `enforcement_mode` | string (enum) | Yes | How this contract is enforced: `native`, `overseer`, `infrastructure`. See enforcement modes below. |
| `on_violation` | string (enum) | No | Default action on contract violation: `deny`, `deny_and_escalate`, `deny_and_halt`, `log_only`. Default: `deny`. |
| `on_expiry` | string (enum) | No | Behavior when `contract_meta.expires_at` is reached: `deny_all`, `escalate`, `renew_request`. Default: `deny_all`. |
| `immutable` | boolean | No | Whether this contract is immutable once effective. Recommended: `true`. Default: `true`. |
| `audit_required` | boolean | No | Whether every evaluation event must be recorded in the audit log. Default: `true`. |

### Enforcement Modes

| Value | Description |
|---|---|
| `native` | Agent is ADC-aware, self-governs, and calls the evaluation runtime to validate decisions. |
| `overseer` | An overseer agent validates sub-agent outputs against this contract before propagation. |
| `infrastructure` | Contract is enforced at the infrastructure boundary regardless of agent awareness. |

---

## Shared Definitions

### `condition`

Used in `authority.data_access[].conditions`, `authority.tools[].conditions`, and `authority.decisions[].conditions`.

| Field | Type | Required | Description |
|---|---|---|---|
| `field` | string | Yes | Context field being evaluated (e.g., `request.time_of_day`, `agent.session_duration_seconds`). |
| `operator` | string (enum) | Yes | `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `in`, `not_in`, `matches`. |
| `value` | any | Yes | Value to evaluate the field against. |
