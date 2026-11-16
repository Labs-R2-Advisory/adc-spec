#!/usr/bin/env python3
"""ADC v0.1 repository validation harness.

Checks, in order:
  1. The schema itself is a valid JSON Schema (Draft 2020-12).
  2. Every file in examples/ validates against spec/adc-v0.1.json (with format checks).
  3. Every ```json block in the root Markdown files and docs/ is accounted for:
     validated against the matching part of the schema, skipped with a stated
     reason (warning), or reported as malformed (blocking failure). A coverage
     line gives the counts.
  4. Negative tests: known-bad contracts must FAIL validation.
  5. Static consistency lint for examples (advisory, not schema conformance):
     pre-authorization envelope references, prose-only constraints,
     auto-approve timeouts, contract expiry. 5b checks the deliberately
     expired fixture in tests/fixtures/ (blocking).
  6. Relative Markdown links resolve to files in the repository.

Schema validity is structural only. Passing this harness does NOT mean a contract
is enforceable, that a runtime exists, or that any runtime behaves as documented.

Usage:  python3 tests/validate.py [--as-of YYYY-MM-DD]
Exit code 0 when every blocking check passes. Lint findings are warnings.
Requires: pip install jsonschema rfc3339-validator rfc3986-validator
"""
import argparse
import copy
import datetime as dt
import glob
import json
import os
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(ROOT, "spec", "adc-v0.1.json")

failures = []
warnings = []


def fail(msg):
    failures.append(msg)
    print(f"  FAIL  {msg}")


def ok(msg):
    print(f"  PASS  {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  WARN  {msg}")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validator_for(schema, subschema=None):
    target = subschema if subschema is not None else schema
    if subschema is not None and subschema is not schema:
        # Keep $defs reachable for $ref resolution inside subschemas.
        target = dict(subschema)
        target["$defs"] = schema.get("$defs", {})
    return Draft202012Validator(target, format_checker=FormatChecker())


def errors_of(v, instance):
    return sorted(v.iter_errors(instance), key=lambda e: list(e.absolute_path))


def fmt_err(e):
    path = "/".join(str(p) for p in e.absolute_path) or "(root)"
    return f"{path}: {e.message}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", help="Reference date for expiry lint (default: today, UTC)")
    args = ap.parse_args()
    as_of = (dt.datetime.fromisoformat(args.as_of).replace(tzinfo=dt.timezone.utc)
             if args.as_of else dt.datetime.now(dt.timezone.utc))

    schema = load(SCHEMA_PATH)
    props = schema["properties"]
    full_v = validator_for(schema)

    print("1. Schema self-check")
    try:
        Draft202012Validator.check_schema(schema)
        ok("spec/adc-v0.1.json is a valid Draft 2020-12 schema")
    except Exception as exc:  # noqa: BLE001
        fail(f"schema invalid: {exc}")

    print("2. Examples validate against the schema")
    examples = sorted(glob.glob(os.path.join(ROOT, "examples", "*.json")))
    if not examples:
        fail("no examples found")
    for path in examples:
        rel = os.path.relpath(path, ROOT)
        try:
            inst = load(path)
        except json.JSONDecodeError as exc:
            fail(f"{rel}: JSON parse error: {exc}")
            continue
        errs = errors_of(full_v, inst)
        if errs:
            for e in errs:
                fail(f"{rel}: {fmt_err(e)}")
        else:
            ok(f"{rel}")

    print("3. JSON snippets in Markdown validate (every ```json block is accounted for)")
    md_files = sorted(glob.glob(os.path.join(ROOT, "*.md"))) + sorted(
        glob.glob(os.path.join(ROOT, "docs", "**", "*.md"), recursive=True))
    block_re = re.compile(r"```json\n(.*?)```", re.S)
    coverage = {"blocks": 0, "validated": 0, "partial": 0, "skipped": 0, "malformed": 0}
    skipped = []
    for md in md_files:
        rel = os.path.relpath(md, ROOT)
        text = open(md, encoding="utf-8").read()
        for i, m in enumerate(block_re.finditer(text), 1):
            coverage["blocks"] += 1
            raw = m.group(1).strip()
            label = f"{rel} block {i}"
            obj, err = None, None
            for candidate in (raw, "{" + raw + "}"):
                try:
                    obj = json.loads(candidate)
                    break
                except json.JSONDecodeError as exc:
                    err = exc
            if obj is None:
                coverage["malformed"] += 1
                fail(f"{label}: fenced as json but does not parse, even as a key-value excerpt: {err}")
                continue
            targets = snippet_targets(schema, obj)
            if not targets:
                coverage["skipped"] += 1
                reason = f"no matching schema part for keys {sorted(obj)[:5] if isinstance(obj, dict) else type(obj).__name__}"
                skipped.append(f"{label}: {reason}")
                warn(f"{label} skipped: {reason}")
                continue
            partial = any(t[0] == "partial contract" for t in targets)
            coverage["partial" if partial else "validated"] += 1
            for kind, subschema, inst in targets:
                v = validator_for(schema, subschema) if subschema is not schema else full_v
                errs = errors_of(v, inst)
                tag = f"{label} ({kind})"
                if errs:
                    for e in errs:
                        fail(f"{tag}: {fmt_err(e)}")
                else:
                    ok(tag)
    print(f"  COVERAGE  {coverage['blocks']} json blocks: {coverage['validated']} validated, "
          f"{coverage['partial']} partial contracts (present fields validated; required-field "
          f"check not applicable), {coverage['skipped']} skipped, {coverage['malformed']} malformed")
    if coverage["validated"] + coverage["partial"] == 0:
        fail("no documentation snippets were checkable")

    print("4. Negative tests (each must be rejected)")
    base = load(os.path.join(ROOT, "examples", "enterprise-procurement-agent.json"))
    for esc in base.get("escalation", []):  # negatives start from a schema-valid base
        if esc["timeout"]["on_timeout"] not in ("deny", "approve", "escalate_further", "halt"):
            esc["timeout"]["on_timeout"] = "halt"
    if errors_of(full_v, base):
        fail("negative-test base contract is not schema-valid; negatives are meaningless")
    negatives = {
        "on_timeout outside enum (deny_and_halt)":
            lambda c: c["escalation"][0]["timeout"].__setitem__("on_timeout", "deny_and_halt"),
        "missing required binding": lambda c: c.pop("binding"),
        "missing required principal": lambda c: c.pop("principal"),
        "missing binding.enforcement_mode": lambda c: c["binding"].pop("enforcement_mode"),
        "adc_version not 0.1": lambda c: c.__setitem__("adc_version", "0.2"),
        "agent_type outside enum": lambda c: c["agent"].__setitem__("agent_type", "superagent"),
        "principal_type outside enum": lambda c: c["principal"].__setitem__("principal_type", "robot"),
        "classification_ceiling outside enum":
            lambda c: c["authority"]["data_access"][0].__setitem__("classification_ceiling", "ultra"),
        "escalation rule without timeout": lambda c: c["escalation"][0].pop("timeout"),
        "constraint without applies_to": lambda c: c["constraints"][0].pop("applies_to"),
        "negative delegation_depth": lambda c: c["principal"].__setitem__("delegation_depth", -1),
        "contract_id not a URI": lambda c: c.__setitem__("contract_id", "not a uri"),
        "expires_at not date-time":
            lambda c: c["contract_meta"].__setitem__("expires_at", "next tuesday"),
    }
    for name, mutate in negatives.items():
        inst = copy.deepcopy(base)
        mutate(inst)
        if errors_of(full_v, inst):
            ok(f"rejected: {name}")
        else:
            fail(f"NOT rejected: {name}")

    # Known permissive behaviour, documented rather than failed.
    inst = copy.deepcopy(base)
    inst["authority"]["decisons"] = []  # misspelled key
    if not errors_of(full_v, inst):
        warn("schema accepts unknown/misspelled properties (no additionalProperties: false); "
             "a typo such as 'decisons' passes validation silently")

    print("5. Static consistency lint (advisory)")
    for path in examples:
        rel = os.path.relpath(path, ROOT)
        try:
            c = load(path)
        except json.JSONDecodeError:
            continue
        lint_contract(rel, c, as_of)

    print("5b. Lifecycle fixtures (blocking)")
    fixture = os.path.join(ROOT, "tests", "fixtures", "expired-contract.json")
    fx = load(fixture)
    fx_errs = errors_of(full_v, fx)
    if fx_errs:
        for e in fx_errs:
            fail(f"tests/fixtures/expired-contract.json: {fmt_err(e)}")
    exp = dt.datetime.fromisoformat(fx["contract_meta"]["expires_at"].replace("Z", "+00:00"))
    if exp <= as_of:
        ok("expired fixture is schema-valid and detected as past expires_at "
           "(schema validity does not imply the contract is in force)")
    else:
        fail("expired fixture is not past expires_at; expiry coverage lost")

    print("6. Relative Markdown links")
    link_re = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
    for md in md_files:
        rel = os.path.relpath(md, ROOT)
        text = open(md, encoding="utf-8").read()
        for target in link_re.findall(text):
            if re.match(r"^[a-z]+:", target):
                continue  # external URL, not checked offline
            resolved = os.path.normpath(os.path.join(os.path.dirname(md), target))
            if os.path.exists(resolved):
                ok(f"{rel} -> {target}")
            else:
                fail(f"{rel}: broken relative link -> {target}")

    print()
    print(f"Blocking failures: {len(failures)}   Advisory warnings: {len(warnings)}")
    return 1 if failures else 0


def snippet_targets(schema, obj):
    """Map a documentation snippet to (kind, subschema, instance) checks.

    Full contracts validate against the whole schema. A contract excerpt that
    lacks required top-level fields validates each present field against its
    own subschema. Single-key excerpts such as {"agent": {...}} validate
    against that property. Bare items validate against the array item schema
    they match. Returns [] when nothing matches, and the caller reports a skip.
    """
    props = schema["properties"]
    auth = props["authority"]["properties"]
    if not isinstance(obj, dict):
        return []
    if "adc_version" in obj:
        missing = [r for r in schema.get("required", []) if r not in obj]
        if not missing:
            return [("contract", schema, obj)]
        return [("partial contract", props[k], v) for k, v in obj.items() if k in props]
    if len(obj) == 1:
        (k, v), = obj.items()
        if k in props:
            return [(k, props[k], v)]
        if k in auth:
            return [(f"authority.{k}", auth[k], v)]
    items = {
        "escalation rule": (props["escalation"]["items"], {"trigger", "timeout"}),
        "constraint": (schema["$defs"]["constraint"], {"id", "applies_to"}),
        "data_access item": (auth["data_access"]["items"], {"domain", "classification_ceiling"}),
        "tool item": (auth["tools"]["items"], {"tool_id", "permitted_actions"}),
        "decision item": (auth["decisions"]["items"], {"decision_type", "autonomous"}),
    }
    for kind, (sub, keys) in items.items():
        if keys <= set(obj):
            return [(kind, sub, obj)]
    return []


def lint_contract(rel, c, as_of):
    auth = c.get("authority", {})
    decision_types = {d.get("decision_type") for d in auth.get("decisions", [])}
    autonomous = {d.get("decision_type") for d in auth.get("decisions", []) if d.get("autonomous")}
    domains = [d.get("domain") for d in auth.get("data_access", [])]

    env = c.get("connectivity", {}).get("pre_authorization_envelope")
    if env:
        for d in env.get("authorized_decisions", []):
            if d not in decision_types:
                warn(f"{rel}: envelope decision '{d}' not in authority.decisions")
            elif d not in autonomous:
                warn(f"{rel}: envelope decision '{d}' is not autonomous in authority.decisions")
        for dom in env.get("authorized_data_domains", []):
            if dom not in domains:
                warn(f"{rel}: envelope data domain '{dom}' not in authority.data_access")
        if "envelope_ttl_seconds" not in env:
            warn(f"{rel}: envelope has no envelope_ttl_seconds")
        else:
            ok(f"{rel}: envelope references are a subset of authority")

    for con in c.get("constraints", []):
        if not con.get("rule"):
            warn(f"{rel}: constraint '{con.get('id')}' is prose-only (no machine-evaluable rule)")

    for i, esc in enumerate(c.get("escalation", [])):
        t = esc.get("timeout", {})
        if t.get("on_timeout") == "approve":
            warn(f"{rel}: escalation[{i}] auto-approves on timeout "
                 f"(priority {esc.get('priority')}); review safety of the example")

    exp = c.get("contract_meta", {}).get("expires_at")
    if exp:
        exp_dt = dt.datetime.fromisoformat(exp.replace("Z", "+00:00"))
        if exp_dt <= as_of:
            warn(f"{rel}: contract_meta.expires_at {exp} is in the past as of "
                 f"{as_of.date()}; binding.on_expiry='{c.get('binding', {}).get('on_expiry')}' "
                 f"would apply")
        else:
            ok(f"{rel}: not expired as of {as_of.date()} (expires {exp})")


if __name__ == "__main__":
    sys.exit(main())
