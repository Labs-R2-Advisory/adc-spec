# ADC Concepts and Primitives

**ADC Specification — v0.1 Working Draft**
R2 Advisory | April 2026 | Apache 2.0

---

## 1. What ADC Is

An **Agent Delegation Contract (ADC)** is a formal, machine-readable contract that defines the authorized scope of an AI agent's actions: what data it may access, what decisions it may make autonomously, what tools it may invoke, under what conditions, and what escalation conditions route decisions to a human or higher authority.

ADC is a **specification**, not an implementation. Any runtime may evaluate ADCs. The spec defines the contract language and semantics. Runtimes implement evaluation.

ADC is not:
- A configuration file (it expresses business-level authorization, not system parameters)
- An orchestration framework (it defines authority, not execution order)
- A monitoring or observability spec (it governs decisions before they execute, not after)
- A general control system protocol (it coordinates decision authority, not mechanical actuation)

---

## 2. Intellectual Lineage

ADC draws from two distinct bodies of work. Understanding the lineage explains why the spec is structured the way it is.

---

### 2.1 Academic Research: Intelligent AI Delegation

The foundational conceptual framework derives from **Tomasev, Franklin & Osindero (2026), "Intelligent AI Delegation," Google DeepMind** ([arXiv:2602.11865](https://arxiv.org/abs/2602.11865)).

That work defines intelligent delegation as a sequence of decisions involving task allocation that incorporates transfer of authority, responsibility, accountability, clarity of roles and boundaries, and trust mechanisms between parties. It identifies why heuristic-based delegation fails at scale and what properties a rigorous delegation system must possess — specifically: the principal-agent problem in AI systems, span-of-control limits on delegators, authority gradient risks, zone-of-indifference compliance failures, privilege attenuation in delegation chains, and the requirement for verifiable, auditable task completion.

ADC is the machine-readable contract language that operationalizes these properties at the per-agent, per-action level.

---

### 2.2 Operational Doctrine: Command and Control

ADC's connectivity model and disconnected authority semantics derive from **C2 (Command and Control) doctrine** developed across decades of defense and national security systems design.

C2 doctrine has long addressed the core problem ADC formalizes: how does an autonomous actor maintain effective, accountable operation when it cannot reach the authoritative command element? The answers, developed through operational necessity, translate directly to machine-readable contract semantics.

| C2 Concept | ADC Implementation |
|---|---|
| Delegation of Authority | Delegation chain: authority flows downward, can only be constrained, never amplified |
| Rules of Engagement | `constraints` block: explicit prohibitions that override all permissions |
| Commander's Intent | Root intent contract: the principal's objective bounding the entire delegation chain |
| PACE (Primary/Alternate/Contingency/Emergency) | `connectivity.assumed_mode`: connected, degraded, disconnected, contested |
| Pre-Delegated Authority | `connectivity.pre_authorization_envelope`: decisions cleared before contact loss |
| Positive Control vs. Procedural Control | Connected mode (runtime evaluates real-time) vs. disconnected mode (pre-cleared envelope governs) |
| Reconstitution and ratification | `connectivity.reconnection_behavior.await_ratification`: post-reconnection review |
| Mission-Type Orders | Pattern 1 (native consumption): agent self-governs within its full authority envelope |

These are not analogies. The problems are structurally identical at different layers of abstraction. ADC brings machine-readable precision to authority models C2 doctrine has long handled through human interpretation.

---

## 3. Core Primitives

### 3.1 Agent

An **agent** is an entity that possesses decision authority: the capacity to evaluate context and take action based on that evaluation. An agent may be an AI system, an autonomous subsystem, or a composite system coordinating multiple components.

**What qualifies as an agent for ADC purposes:**
- It makes context-dependent decisions (not just executes pre-specified instructions)
- Its decisions have consequential effects on data, systems, resources, or other agents
- It can be assigned a stable identity for the purposes of authorization and audit

**What does not qualify:**
- Sensors and actuators that receive commands but do not independently decide
- Rule-execution engines with no contextual judgment
- API endpoints that respond deterministically to inputs

A `human_node` is a valid agent type in ADC. Humans in a multi-agent system have authorization profiles: what decisions are routed to them, through which channel, with what response time expectation, and what happens if they do not respond.

---

### 3.2 Principal

A **principal** is the authorizing party whose intent the contract expresses. The principal is accountable for the agent's authorized actions.

Principals may be:
- **Human**: a named individual or role in the organization's identity system
- **Agent**: a parent agent delegating to a sub-agent
- **Organization**: an institutional authority (e.g., operations center, command authority)
- **System**: an automated system with defined governance authority

Every ADC has exactly one principal. The principal is the answer to: who authorized this agent to act this way?

---

### 3.3 Authority

**Authority** is the complete enumerated scope of what an agent is permitted to do. Authority is defined across three dimensions:

- **Data Access**: which data domains the agent may access, at what classification level, and with which operations
- **Tools**: which tools and APIs the agent may invoke, with what permitted actions and under what conditions
- **Decisions**: which decision types the agent may execute autonomously, with what thresholds

**The default is deny.** Everything not explicitly permitted in the authority block is denied. Authority is not a description of what the agent might do. It is a complete specification of what it is allowed to do.

---

### 3.4 Constraint

A **constraint** is an explicit prohibition that applies across the entire contract, regardless of what is permitted in the authority block. Constraints are evaluated before permissions. A constraint violation overrides any otherwise-applicable permission.

Constraints answer the question: what is this agent never permitted to do, even if its authority would otherwise allow it?

Example: An agent may have write access to `finance.purchase_orders` in its authority block, but a constraint may prohibit any write operation that would result in a transaction exceeding $10,000 without human approval. The constraint governs regardless of the permission.

---

### 3.5 Delegation

**Delegation** is the act of a principal or agent issuing an ADC to a sub-agent, transferring a bounded subset of its own authority.

The invariant rule of delegation: **authority can only be constrained downward, never amplified.** A sub-agent ADC may authorize actions that are a subset of the parent ADC's authority. It may not authorize anything the parent ADC does not authorize.

The delegation chain records every hop from the root principal to the executing agent:

```
L0: Human Principal (root authority, maximum scope for the project)
L1: Planning Agent  (delegated by L0, subset of L0 authority)
L2: Task Agent      (delegated by L1, subset of L1 authority)
L3: Sub-task Agent  (delegated by L2, if L2 ADC permits delegation)
```

An agent may only delegate if its ADC explicitly sets `authority.delegation.may_delegate: true`. Delegation depth is bounded by `authority.delegation.max_delegation_depth`.

---

### 3.6 Escalation

**Escalation** is the condition under which an agent suspends autonomous action and routes a decision to a human node or higher-authority principal for resolution.

An escalation rule defines:
- The **trigger**: the condition that activates escalation
- The **target**: who receives the escalation
- The **timeout**: how long to wait for a response, and what to do if none arrives
- The **priority**: urgency classification for delivery

Escalation is not an error state. It is a designed-in control path for decisions that exceed the agent's autonomous authority or that the contract explicitly reserves for human judgment.

**Timeout behavior is explicit, not a system default.** Each escalation rule declares its own `on_timeout` action. `deny` is the safe default for high-risk decisions. `approve` may be appropriate for low-risk notifications where inaction is the correct response to non-engagement.

---

### 3.7 Binding

**Binding** defines how the contract is enforced and its lifecycle behavior. Three enforcement modes are defined:

| Mode | Description | Primary Use |
|---|---|---|
| `native` | Agent is ADC-aware, self-governs, and calls the evaluation runtime for decisions | ADC-native agents, planning agents, mature integrations |
| `overseer` | An overseer agent validates sub-agent outputs against the ADC before propagation | Bridge pattern for non-ADC-aware agents |
| `infrastructure` | Contract is enforced at the infrastructure boundary regardless of agent awareness | Data protection enforcement, network-path interception |

Agent ADC awareness improves operational efficiency and enables graceful constraint handling. It is not required for enforcement. Infrastructure-mode enforcement operates regardless of whether the agent knows its ADC exists.

---

### 3.8 Connectivity Mode

**Connectivity mode** defines the state of the agent's relationship to the authoritative evaluation runtime. Four states are defined:

| Mode | Description | Authority Behavior |
|---|---|---|
| `connected` | Full real-time access to the evaluation runtime | Full contract authority, real-time evaluation |
| `degraded` | Runtime reachable with latency or intermittently | Pre-authorized subset, escalations queued |
| `disconnected` | Runtime unreachable | Pre-authorization envelope governs; deny on ambiguity |
| `contested` | Active disruption; communication integrity uncertain | Minimal safe actions only; halt and report on reconnect |

For enterprise deployments operating in fully connected environments, the `connectivity` block may be omitted or set to `assumed_mode: connected`. The connectivity model is required for deployments in OT/ICS environments, field operations, defense/national security contexts, and any scenario where the agent may operate outside reliable network coverage.

---

### 3.9 Pre-Authorization Envelope

A **pre-authorization envelope** is the bounded set of decisions an agent is cleared to make autonomously when it cannot reach the evaluation runtime. The envelope is defined at contract issuance, validated against the contract's authority block, and cryptographically signed.

The envelope answers: if this agent loses contact with its authoritative runtime, exactly which decisions may it continue to make, for how long, and what must it do when contact is restored?

An empty envelope means the agent must halt all non-trivial decision-making upon disconnection. A populated envelope means the agent has pre-cleared operational authority for a defined scope and duration.

> **WORKING DRAFT:** The normative specification for pre-authorization envelope evaluation, cryptographic signing requirements, and state reconciliation on reconnection is in progress. See `docs/profiles/disconnected-operations.md` when available. Community contributions to this section are explicitly invited. See `CONTRIBUTING.md`.

---

## 4. Consumption Patterns

Three patterns define how ADCs are consumed at runtime:

**Pattern 1 — Native Consumption**
The agent reads its ADC, understands its authorized scope, and self-governs before acting. The agent calls the evaluation runtime to validate decisions before execution. This is the mature pattern and the long-term default as ADC adoption grows.

**Pattern 2 — Overseer Validation**
Sub-agents execute without ADC awareness. An overseer agent validates their outputs against the governing ADC before those outputs propagate or trigger downstream actions. This is the bridge pattern for non-ADC-native agents and the current default for most deployed systems.

**Pattern 3 — Infrastructure Enforcement**
The evaluation runtime sits in the infrastructure path. Agent action requests are intercepted and evaluated before reaching their target. The agent may or may not be aware that an ADC governs it. Agent ADC awareness is an optimization, not a requirement for enforcement.

---

## 5. Domain Applicability

ADC is designed for any environment where autonomous agents make consequential decisions. The specification defines a core that is domain-invariant. Normative profiles for specific operational contexts are maintained as extensions to the core.

| Domain | Connectivity Profile | Key ADC Features |
|---|---|---|
| Enterprise AI Governance | Connected | Data access control, decision thresholds, tool scope, audit |
| Critical Infrastructure (OT/ICS) | Degraded / Disconnected | Pre-authorization envelope, protective action constraints, ratification on reconnect |
| Defense / National Security | Disconnected / Contested | Minimal safe actions, pre-delegated authority envelopes, PACE-aligned connectivity model |
| Autonomous Field Operations | Degraded / Intermittent | Time-bounded envelopes, mission scope constraints, sync on reconnect |
| Space-Based Autonomous Systems | High-latency / Periodic contact | Extended envelope TTL, mission-type order equivalents, post-mission ratification |

Profiles for Critical Infrastructure and Defense/National Security are open for community contribution. See `CONTRIBUTING.md`.

---

## 6. What ADC Does Not Define

ADC defines the contract language and enforcement semantics. The following are explicitly out of scope for the specification:

- **Runtime implementation**: How a runtime evaluates ADCs (OPA, custom engine, embedded logic) is implementation-defined.
- **Agent communication protocols**: How agents communicate with each other or with runtimes is not specified by ADC.
- **Interface channels for escalation**: How a human node receives an escalation (email, UI, messaging) is an implementation detail of the runtime.
- **Cryptographic signing schemes**: The spec notes where signatures are relevant but does not mandate a specific scheme.
- **Agent capability definitions**: ADC governs what an agent is authorized to do, not what it is capable of doing.
