# Agent Delegation Contract (ADC)

**Open specification for AI agent authorization — define what agents may do, decide, and escalate.**

`v0.1 Working Draft` | Apache 2.0 | R2 Advisory

---

## What ADC Is

An **Agent Delegation Contract** is a formal, machine-readable contract that defines the authorized scope of an AI agent's actions:

- What **data** it may access, at what classification level, with what operations
- What **decisions** it may make autonomously, under what conditions and thresholds
- What **tools** it may invoke, with what permitted actions
- What **escalation conditions** route decisions to a human or higher authority
- What **authority** the agent retains when it cannot reach its evaluation runtime

ADC is a **specification**, not an implementation. Any runtime may evaluate ADCs. The language is open. Runtimes are built on top of it.

---

## The Problem ADC Solves

AI agents are making consequential decisions inside enterprise systems, critical infrastructure, and autonomous platforms today. They access data, approve transactions, trigger workflows, control physical systems, and spawn other agents. The authorization model governing those decisions is, in most deployments, absent.

Existing security infrastructure answers different questions:

| Tool | Question It Answers |
|---|---|
| IAM | Who is this human, and what resources may they access? |
| DLP | Is this data leaving the perimeter? |
| DSPM | What sensitive data exists and where? |
| SIEM | What happened, after the fact? |

None of them answer: **what is this agent authorized to decide, right now, in this context?**

ADC answers that question. It provides a contract language for expressing agent authorization that is formal enough to be machine-evaluated, human-readable enough to be auditable, and general enough to apply from enterprise SaaS to disconnected field operations.

---

## Intellectual Lineage

ADC draws from three distinct bodies of work. Each contributes a layer of the specification.

---

### Layer 1: Academic Research — Intelligent AI Delegation

The foundational conceptual framework for ADC derives from **Tomasev, Franklin & Osindero (2026), "Intelligent AI Delegation," Google DeepMind** ([arXiv:2602.11865](https://arxiv.org/abs/2602.11865)).

That paper defines intelligent delegation as a sequence of decisions involving task allocation that incorporates transfer of authority, responsibility, accountability, clarity of roles and boundaries, clarity of intent, and trust mechanisms between parties. It establishes the theoretical basis for why ad-hoc, heuristic-based delegation frameworks fail at scale and what properties a rigorous delegation system must possess.

Key concepts from that work that directly shape ADC:

| Concept (Tomasev et al.) | ADC Implementation |
|---|---|
| Principal-agent problem: misaligned incentives between delegator and delegatee | `principal` block: explicit accountability ownership; authority is scoped, not presumed |
| Span of control: limits on how many agents a delegator can supervise reliably | `authority.delegation.max_delegation_depth`: bounded delegation chains; runtime span-of-control enforcement |
| Authority gradient: capability/authority disparities that impede communication and cause errors | `agent.agent_type` classification + `constraints` block: challenge rights, clarification triggers, sycophancy mitigation |
| Zone of indifference: range of instructions executed without critical scrutiny | `constraints` as hard overrides; `escalation` conditions that fire before zone-of-indifference compliance |
| Permission handling via privilege attenuation: sub-delegatees receive strict subsets only | Delegation invariant: authority can only be constrained downward, never amplified |
| Trust calibration: trust is contextual, not global; must be earned per task class | `binding.enforcement_mode` + audit trail: trust is evaluated per contract instance, not per agent globally |
| Verifiable task completion: outcomes must be formally closeable, not assumed | `binding.audit_required` + immutable contract IDs: every evaluation event creates a non-repudiable record |
| Adaptive coordination: static execution plans are insufficient for high-uncertainty environments | `escalation` with `on_timeout` behavior + `connectivity` model: defined fallback for every failure mode |

---

### Layer 2: Operational Doctrine — Command and Control

ADC's **connectivity model and disconnected authority semantics** derive from **C2 (Command and Control) doctrine** developed across decades of defense and national security systems design.

C2 doctrine has long addressed the problem ADC's connectivity model formalizes: how does an autonomous actor maintain effective, accountable operation when it cannot reach the authoritative command element? The answers, developed through operational necessity, translate directly to machine-readable contract semantics.

| C2 Concept | ADC Implementation |
|---|---|
| Delegation of Authority | Delegation chain: authority flows downward and can only be constrained, never amplified |
| Rules of Engagement | `constraints` block: explicit prohibitions that override permissions regardless of authority scope |
| Commander's Intent | Root intent contract: the principal's stated objective that bounds the entire delegation chain |
| PACE (Primary/Alternate/Contingency/Emergency) communications | `connectivity.assumed_mode`: connected, degraded, disconnected, contested |
| Pre-Delegated Authority | `connectivity.pre_authorization_envelope`: decisions cleared for autonomous execution before contact loss |
| Positive Control vs. Procedural Control | Connected mode (runtime evaluates every decision) vs. disconnected mode (agent operates within pre-cleared envelope) |
| Reconstitution and ratification on reconnection | `connectivity.reconnection_behavior.await_ratification`: post-reconnection review of disconnected operation log |

These are not analogies. The problems are structurally identical at different layers of abstraction. C2 doctrine developed these authority models through operational necessity in human-operated systems. ADC brings machine-readable precision to the same models for autonomous agents.

---

### Layer 3: Applied Security Research — OWASP GenAI Data Security

ADC's **constraint semantics, data access control model, and violation behavior** are informed by the **OWASP GenAI Data Security Risks and Mitigations 2026** (v1.0, March 2026), which catalogs the attack surface created by AI agents operating against enterprise data systems.

That document identifies the systematic ways AI agents break existing data protection assumptions: agents access data at volumes and velocities that exceed human-auditable thresholds; agent identity is ephemeral and difficult to bind to accountability chains; and agents operating through MCP or API integrations can invoke data operations far beyond any single session's stated purpose.

Key threat patterns from OWASP GenAI that ADC directly addresses:

| OWASP GenAI Threat | ADC Mitigation |
|---|---|
| Agents accessing data beyond task scope | `authority.data_access[].domain` with explicit classification ceiling and permitted operations per domain |
| Absence of authorization model for MCP tool invocations | `authority.tools[].permitted_actions`: explicit allowlist of permitted operations per tool, not binary access |
| Agent identity is ephemeral; audit trail is operationally infeasible at AI event volume | `binding.audit_required` + immutable `contract_id`: every evaluation event captures agent identity, contract version, and decision |
| Indirect prompt injection enabling agents to exceed authorized scope | `constraints` block as hard overrides evaluated before authority; `on_violation: deny_and_halt` for critical constraints |
| Sub-agent authority inheritance: spawned agents inherit more access than the task requires | Delegation invariant: authority is constrained downward at every level; `agent.parent_contract_id` links lineage |
| Data access leaving an unmanageable audit trail at AI event velocity | `binding.audit_required` + SIEM-compatible JSON Lines export: structured audit at enforcement-layer rather than log-review layer |
| Retrieval-augmented agents accessing high-classification data without policy gates | `data_access[].classification_ceiling`: hard ceiling per domain enforced at contract evaluation time |

OWASP GenAI establishes the threat model. ADC provides the contract language for expressing and enforcing mitigations at the agent authorization layer, upstream of where existing DLP, DSPM, and IAM controls operate.

---

## Scope

ADC is designed for any environment where autonomous agents make consequential decisions. The specification defines a **domain-invariant core** with **normative profiles** for specific operational contexts.

| Domain | Profile Status |
|---|---|
| Enterprise AI Governance | Normative (v0.1) |
| Critical Infrastructure (OT/ICS) | Working Draft — contributors needed |
| Defense / National Security | Working Draft — contributors needed |
| Autonomous Field Operations | Placeholder — RFC open |
| High-Latency Autonomous (Space) | Placeholder — RFC open |

---

## Repository Structure

```
spec/
  adc-v0.1.json          # JSON Schema — the normative specification
examples/
  enterprise-procurement-agent.json    # Enterprise AI governance pattern
  critical-infrastructure-grid-agent.json  # Disconnected/OT operations pattern
docs/
  concepts.md            # Primitives, design rationale, consumption patterns
  field-reference.md     # Field-by-field reference (forthcoming)
  authoring-guide.md     # How to write an ADC (forthcoming)
  profiles/              # Domain-specific normative profiles (forthcoming)
  rfcs/                  # RFC archive
CONTRIBUTING.md          # How to contribute
CHANGELOG.md             # Version history
LICENSE                  # Apache 2.0
```

---

## Core Primitives

| Primitive | Definition |
|---|---|
| **Agent** | An entity with decision authority: capacity to evaluate context and take consequential action |
| **Principal** | The authorizing party accountable for the agent's authorized actions |
| **Authority** | The complete enumerated scope of what an agent is permitted to do. Default: deny. |
| **Constraint** | An explicit prohibition that overrides permissions. Evaluated before authority. |
| **Delegation** | Transfer of a bounded authority subset to a sub-agent. Can only be constrained downward, never amplified. |
| **Escalation** | Condition under which the agent suspends autonomous action and routes to a human or higher authority |
| **Binding** | Enforcement mode and lifecycle semantics for the contract |
| **Connectivity Mode** | The agent's relationship to its evaluation runtime: connected, degraded, disconnected, contested |
| **Pre-Authorization Envelope** | Decisions cleared for autonomous execution when the agent cannot reach its runtime |

Full definitions: [`docs/concepts.md`](docs/concepts.md)

---

## Minimal Example

```json
{
  "adc_version": "0.1",
  "contract_id": "urn:adc:example:procurement-agent:2026-04-16:v1",
  "agent": {
    "agent_id": "procurement-agent-001",
    "agent_type": "task_agent"
  },
  "principal": {
    "principal_id": "cfo@example.com",
    "principal_type": "human"
  },
  "authority": {
    "decisions": [
      {
        "decision_type": "approve_purchase_order",
        "autonomous": true,
        "thresholds": [
          { "field": "purchase_order.amount_usd", "operator": "lte", "value": 10000 },
          { "field": "purchase_order.vendor_id", "operator": "in", "value": ["{{finance.approved_vendor_list}}"] }
        ]
      }
    ]
  },
  "escalation": [
    {
      "trigger": "purchase_order.amount_usd > 10000",
      "escalate_to": "cfo@example.com",
      "timeout": { "seconds": 86400, "on_timeout": "deny" },
      "priority": "routine"
    }
  ],
  "binding": {
    "enforcement_mode": "native",
    "on_violation": "deny_and_escalate",
    "audit_required": true
  }
}
```

Full examples: [`examples/`](examples/)

---

## Enforcement Modes

ADC defines three enforcement modes. The contract format is identical across all three. What differs is where evaluation happens and whether the agent participates.

**Pattern 1 — Native Consumption**
The agent reads its ADC, self-governs, and calls the evaluation runtime to validate decisions. The agent is ADC-aware.

**Pattern 2 — Overseer Validation**
Sub-agents execute without ADC awareness. An overseer agent validates outputs against the governing ADC before propagation. Bridge pattern for non-ADC-native agents.

**Pattern 3 — Infrastructure Enforcement**
The evaluation runtime intercepts agent actions at the infrastructure boundary. Enforcement operates regardless of agent awareness.

---

## Connectivity Model

ADC specifies agent authority behavior under four connectivity states. Enterprise deployments operating in fully connected environments may omit the `connectivity` block entirely. Disconnected and contested profiles are required for field, OT/ICS, and defense deployments.

| Mode | Authority Behavior |
|---|---|
| `connected` | Full contract authority, real-time evaluation |
| `degraded` | Pre-authorized subset, escalations queued |
| `disconnected` | Pre-authorization envelope governs; deny on ambiguity |
| `contested` | Minimal safe actions only; halt and report on reconnect |

---

## Relationship to Existing Standards

ADC is complementary to, not a replacement for:

- **NIST AI RMF**: ADC provides the machine-readable contract layer for operationalizing AI RMF governance controls at the agent level
- **EU AI Act**: ADC contract terms can express and enforce AI Act obligations (human oversight, prohibited practices) at the agent authorization layer
- **ISO 42001**: ADC supports AI management system controls by formalizing agent authorization as auditable policy
- **OpenAPI / AsyncAPI**: ADC governs what an agent is authorized to do with APIs it can invoke; it does not describe the APIs themselves
- **SAML / OAuth**: ADC extends identity and access concepts to agent-level decision authorization; it assumes identity is established by existing IAM

---

## Contributing

ADC needs practitioners from enterprise AI governance, defense/national security, critical infrastructure, and autonomous systems. The spec is stronger with domain expertise from each community.

**Where contributions are most needed right now:**

- `disconnected-operations` profile: defense/C2 practitioners and OT/ICS engineers
- `critical-infrastructure` profile: power, pipeline, water, transportation operators
- Example ADCs: any domain, any agent pattern
- Field reference documentation

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the RFC process, issue labels, and how to get started.

---

## Versioning

| Version | Status | Date |
|---|---|---|
| v0.1 | Working Draft | April 2026 |
| v1.0 | Target: Q4 2026 | — |

v0.1 is a working draft. Fields marked `WORKING DRAFT` in the schema have defined semantics but normative evaluation requirements are in progress. Schema changes are possible before v1.0. v1.0 will be the first locked release.

Breaking changes to v0.1 follow the RFC process. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## License

Apache 2.0. See [`LICENSE`](LICENSE).

The ADC specification is open. Runtimes built on ADC may be open or proprietary.

---

## Maintainer

**R2 Advisory**
Michael Ruiz, Founder and Managing Director
[r2advisory.ai](https://r2advisory.ai)

R2 Advisory maintains the ADC specification.
