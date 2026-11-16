# Changelog

All notable changes to the ADC specification are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) from v1.0 onward.
Pre-v1.0 versions are working drafts. Breaking changes may occur between working draft releases.

---

## [0.1.1] (release candidate, unreleased)

Documentation and example consistency release. **The schema (`spec/adc-v0.1.json`) is unchanged.** Contracts continue to declare `"adc_version": "0.1"`. No previously valid contract becomes invalid, and no previously invalid contract becomes valid, so no RFC is required under `CONTRIBUTING.md`.

### Fixed

- `examples/critical-infrastructure-grid-agent.json` and `examples/enterprise-procurement-agent.json`: escalation `on_timeout` used `deny_and_halt`, which is not in the timeout enum (`deny`, `approve`, `escalate_further`, `halt`). Both examples failed schema validation. Changed to `halt`.
- `docs/authoring-guide.md` and `docs/profiles/enterprise-ai-governance.md`: the same invalid `on_timeout: deny_and_halt` in example snippets. Changed to `halt`.
- `docs/authoring-guide.md`: the Step 1 sample `contract_id` used `{placeholder}` braces, which is not a valid URI. Replaced with a concrete URN; the template remains in the prose.
- `CONTRIBUTING.md`: broken link to an unpublished RFC-0002 file.
- `README.md`: repository structure listed existing documents as "forthcoming".

### Changed

- `examples/critical-infrastructure-grid-agent.json`: the connected overload escalation now times out to `deny` instead of `approve`, so an unanswered escalation grants no additional authority. Added a note that ADC authorization does not replace independent protection systems. Profile label now `working-draft-experimental`.
- `examples/enterprise-procurement-agent.json`: v1 expired on 2026-10-16. Reissued as `urn:adc:example:procurement-agent:2026-11-16:v2` with a current validity window, following the immutability rule that changed terms need a new `contract_id`.
- `README.md`, `docs/concepts.md`, `docs/profiles/*`: claims aligned with v0.1 maturity. Removed "non-repudiable record" and the unspecified "SIEM-compatible JSON Lines export"; regulatory alignment now says contracts "can express" controls rather than "implement" them; versioning table no longer states a Q4 2026 v1.0 target.
- `docs/authoring-guide.md`: replaced a product-specific deployment reference with neutral wording.
- `docs/profiles/enterprise-ai-governance.md`: status relabeled from Normative to Working Draft until ADC defines normative evaluation semantics and conformance criteria. The profile's requirements are unchanged. References updated in `README.md`, `CONTRIBUTING.md`, `docs/profiles/README.md` and `docs/concepts.md`.
- `README.md`, `docs/concepts.md`, `docs/field-reference.md`: enforcement statements (classification ceilings, infrastructure mode, OWASP mitigations, span of control) now say enforcement depends on a runtime that implements ADC.

### Added

- `README.md`: Maturity and Limits section.
- `docs/concepts.md`: clarifications that prose-only constraints are not machine-enforceable, escalation triggers have no normative grammar, the delegation subset invariant is not schema-verified, identifiers are not authentication, and `audit_required` does not define an evidence format; a v0.1 maturity section; a statement that ADC is not a safety function. Fail-closed handling of unevaluable constraints is described as a proposal, not a v0.1 requirement.
- `docs/profiles/disconnected-operations.md`: marked experimental and not a safety certification.
- `docs/concepts.md` and `examples/enterprise-procurement-agent.json`: decisions and tool actions are separate grants; the procurement example explains why `approve_purchase_order` has no matching ERP `approve` action. No authority was added.
- `tests/validate.py`: schema self-check, example validation with format checks, validation of every fenced JSON block in the Markdown files (with a coverage count; malformed blocks fail, unmatched blocks are reported as skipped), 13 negative tests, an expired-contract lifecycle test, advisory lint, and relative link checks.
- `tests/fixtures/expired-contract.json`: the original procurement contract lifecycle, kept deliberately expired.
- `.github/workflows/validate.yml`: runs `tests/validate.py` on push and pull request.

---

## [0.1.0] — 2026-04-16

### Added

**Core Schema (`spec/adc-v0.1.json`)**
- `adc_version`: spec conformance field
- `contract_id`: globally unique URI identifier, immutable
- `contract_meta`: authorship, lifecycle, and labeling metadata
- `agent`: identity and classification block; agent types: `ai_assistant`, `planning_agent`, `task_agent`, `data_agent`, `infrastructure_agent`, `autonomous_system`, `composite_agent`, `human_node`
- `principal`: authorizing party block; principal types: `human`, `agent`, `organization`, `system`; `delegation_depth` field for chain tracking
- `authority.data_access`: data domain permissions with classification ceiling, operations, and conditions
- `authority.tools`: tool/API permissions with permitted actions, rate limits, and conditions
- `authority.decisions`: autonomous decision type definitions with thresholds and conditions
- `authority.delegation`: sub-agent delegation permissions with depth limiting
- `constraints`: contract-level prohibitions with override semantics; evaluated before permissions
- `escalation`: human-in-the-loop rules with trigger, target, timeout, and priority
- `connectivity`: connectivity mode model with four states (connected, degraded, disconnected, contested); `pre_authorization_envelope` field (working draft); reconnection behavior
- `binding`: enforcement mode (native, overseer, infrastructure); lifecycle behavior (on_violation, on_expiry, immutable, audit_required)
- Shared `$defs`: `condition` (contextual permission conditions), `constraint` (prohibition definition)

**Documentation**
- `docs/concepts.md`: full primitive definitions, intellectual lineage, consumption patterns, domain applicability
- `README.md`: spec overview, primitives table, examples, contributing guide, versioning

**Examples**
- `examples/enterprise-procurement-agent.json`: enterprise AI governance pattern; connected operation; native enforcement mode
- `examples/critical-infrastructure-grid-agent.json`: OT/ICS disconnected operations pattern; infrastructure enforcement mode; pre-authorization envelope (working draft)

**Governance**
- `CONTRIBUTING.md`: RFC process, contribution types, issue labels, domain contributor guide
- `LICENSE`: Apache 2.0

### Working Draft Fields

The following fields have defined schema and semantics but normative evaluation requirements are in progress. Community contributions are invited.

- `connectivity.pre_authorization_envelope`: cryptographic signing requirements and state reconciliation protocol
- `connectivity.reconnection_behavior.await_ratification`: ratification evaluation semantics

### Open Profiles (RFC Invited)

- `disconnected-operations`: defense/C2, OT/ICS
- `critical-infrastructure`: power, pipeline, water, transportation
- `defense-national-security`: autonomous systems in denied/contested environments
- `autonomous-field-operations`: field robotics, remote operations
- `high-latency-autonomous`: space-based autonomous systems
