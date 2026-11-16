# Contributing to ADC

**Agent Delegation Contract Specification — v0.1 Working Draft**

ADC is an open specification. The goal is a standard that is credible across enterprise AI governance, defense and national security, critical infrastructure, and autonomous systems — built by practitioners from each domain, not by a single vendor.

This document defines how to contribute.

---

## Who Should Contribute

ADC needs domain expertise that no single organization possesses. If you work in any of the following areas, your contributions directly shape the spec:

**Enterprise AI Governance**
Practitioners defining AI agent policies in regulated industries (financial services, healthcare, government). You understand what authorization contracts need to express to satisfy real compliance requirements. Your contribution: example ADCs, vertical-specific constraint patterns, integration with existing governance frameworks (NIST AI RMF, EU AI Act, ISO 42001).

**Defense / National Security / C2 Systems**
Engineers building autonomous systems in contested, denied, or intermittent (CDI) environments. You have operationally-proven models for pre-delegated authority, rules of engagement enforcement, and authority behavior under degraded communications. ADC's disconnected operations profile is informed by C2 doctrine and needs your validation. Your contribution: the `disconnected-operations` and `contested-environment` profiles.

**Critical Infrastructure**
Engineers operating autonomous systems in OT/ICS environments: power grids, pipeline control, water treatment, transportation. You understand what happens when an autonomous agent loses contact with its control plane and must continue operating safely. Your contribution: the critical infrastructure profile, safety constraint patterns, and protective action envelope definitions.

**Robotics and Autonomous Field Systems**
Developers building agents that operate in degraded-connectivity field environments. Your contribution: field operations profile, mission envelope patterns, and example ADCs for autonomous field agents.

**Standards and Governance**
Architects with experience in open standard development (IETF, IEEE, NIST, OpenAPI, SAML, etc.). Your contribution: spec structure, RFC process, conformance testing requirements, and governance model.

---

## Contribution Types

### Spec Contributions (High Impact)

Changes to `spec/adc-v0.1.json` or the core concepts in `docs/concepts.md`.

These require an RFC. See the RFC Process below.

**What makes a good spec contribution:**
- Fills a documented gap (see open issues labeled `spec-gap`)
- Adds a field that is domain-invariant or clearly profiled to a specific domain
- Does not break existing valid ADC instances
- Includes a rationale for why the field belongs in core vs. a profile
- Includes at least one example ADC demonstrating the field in use

### Profile Contributions

ADC profiles extend the core spec for specific operational domains. The following profiles are open for contribution:

| Profile | Status | RFC |
|---|---|---|
| `enterprise-ai-governance` | Working Draft (v0.1) | N/A |
| `disconnected-operations` | Working Draft (experimental) | RFC-0002 (forthcoming; not yet published) |
| `critical-infrastructure` | Placeholder | Open — start here |
| `defense-national-security` | Placeholder | Open — start here |
| `autonomous-field-operations` | Placeholder | Open — start here |
| `high-latency-autonomous` | Placeholder | Open — start here |

To initiate a profile: open an issue with the label `new-profile`, describe the domain, the key ADC primitives that need extension or profiling, and your credentials/context in the domain.

### Example ADCs

The `examples/` directory is the most accessible entry point for new contributors. A well-authored example ADC:
- Covers a real agent pattern from your domain
- Exercises ADC fields that are not already covered by existing examples
- Includes comments (use `"_comment"` keys) explaining non-obvious decisions
- Is accompanied by a brief description in the PR

### Documentation

Improvements to `docs/concepts.md`, the field reference, the authoring guide, or profile documentation. No RFC required for documentation-only changes. Open a PR with a clear description of what was unclear and what your revision fixes.

---

## RFC Process

Spec changes follow a lightweight RFC process modeled on successful open standards.

### When an RFC Is Required

- Adding, removing, or renaming a field in `spec/adc-v0.1.json`
- Changing the semantics of an existing field
- Adding a new agent type, principal type, or connectivity mode enum value
- Adding a new enforcement mode
- Any change that would cause a previously valid ADC to be invalid, or a previously invalid ADC to become valid

### RFC Format

Create a file at `docs/rfcs/RFC-XXXX-short-title.md` using this structure:

```markdown
# RFC-XXXX: [Short Title]

**Status:** Draft | Under Review | Accepted | Rejected
**Author:** [Name / GitHub handle]
**Domain:** [Enterprise | Defense/NS | Critical Infrastructure | Robotics | Space | Cross-domain]
**Date:** YYYY-MM-DD

## Problem Statement
What is missing or broken in the current spec?

## Proposed Change
What field, type, or semantic change are you proposing?

## Rationale
Why does this belong in the core spec (or a profile)?
What operational scenario requires it?

## Schema Delta
Show the exact JSON Schema change.

## Examples
At least one example ADC demonstrating the change.

## Backward Compatibility
Does this change break any existing valid ADC instances?
If yes: migration path.

## Alternatives Considered
What other approaches were considered and why were they rejected?
```

### RFC Lifecycle

1. Open a PR with your RFC file. Label it `rfc`.
2. Discussion period: minimum 14 days for minor changes, 30 days for breaking changes.
3. Maintainer review and decision: Accept, Reject, or Return for Revision.
4. Accepted RFCs are merged. Schema changes are implemented in the next working draft.

---

## Issue Labels

| Label | Meaning |
|---|---|
| `spec-gap` | Identified gap in the spec that needs a contribution |
| `rfc` | Pull request containing an RFC |
| `new-profile` | Proposal for a new domain profile |
| `example` | New or improved example ADC |
| `question` | Question about the spec — no change proposed |
| `docs` | Documentation improvement |
| `breaking` | Change that would affect existing valid ADCs |
| `profile: defense-ns` | Related to the defense/national security profile |
| `profile: critical-infra` | Related to the critical infrastructure profile |
| `profile: disconnected` | Related to the disconnected operations profile |

---

## Code of Conduct

ADC is a technical specification project. Contributions are evaluated on technical merit and domain validity.

Expected behavior:
- Precision over opinion. Proposals should include rationale grounded in operational requirements, not preference.
- Domain credibility matters. When contributing to a profile, describe your relevant experience. Reviewers will ask.
- Respect the open standard constraint. ADC must be evaluable without any specific runtime. Proposals that couple the spec to a proprietary implementation will not be accepted.
- Good faith engagement. Disagreement on technical grounds is normal and productive. Bad faith is not.

---

## Getting Started

1. Read `docs/concepts.md` — the full primitive definitions and design rationale.
2. Review `spec/adc-v0.1.json` — the schema.
3. Browse `examples/` — working ADCs for enterprise and critical infrastructure patterns.
4. Check open issues labeled `spec-gap` or `new-profile` for where contributions are most needed right now.
5. Open an issue before writing a large RFC — confirm the problem is real and the proposed direction is not already being worked.

Questions: open an issue labeled `question`.
