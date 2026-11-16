# ADC Domain Profiles

Domain profiles extend the ADC core specification for specific operational contexts. A profile defines required field usage, required constraints, recommended escalation patterns, and example ADCs for a specific deployment domain.

The core ADC schema is domain-invariant. Profiles are how domain-specific requirements are expressed without modifying the core.

---

## Profile Status

| Profile | File | Status | RFC |
|---|---|---|---|
| Enterprise AI Governance | `enterprise-ai-governance.md` | Working Draft (v0.1) | N/A |
| Disconnected Operations | `disconnected-operations.md` | Working Draft | RFC-0002 (forthcoming) |
| Critical Infrastructure | — | Placeholder | Open — see CONTRIBUTING.md |
| Defense / National Security | — | Placeholder | Open — see CONTRIBUTING.md |
| Autonomous Field Operations | — | Placeholder | Open — see CONTRIBUTING.md |
| High-Latency Autonomous (Space) | — | Placeholder | Open — see CONTRIBUTING.md |

---

## Contributing a Profile

If you have domain expertise in one of the placeholder domains, your contribution is needed. Open an issue labeled `new-profile` describing your domain context and which ADC primitives require extension or normative guidance.

See `CONTRIBUTING.md` for the full RFC process.
