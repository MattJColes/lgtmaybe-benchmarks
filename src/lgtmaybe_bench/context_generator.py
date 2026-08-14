"""Deterministic one-shot builder for the ``context-v1`` scaling suite.

Emits five Python corpus cases whose changed diffs grow across four size bands
plus one clean case, with eight planted bugs at controlled relative positions in
every defect-bearing case. The output is a corpus artefact: once a raw result
references a case it is immutable, and benchmark runs never import this module.
"""

from __future__ import annotations

import json
import random
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

SUITE_ID = "context-v1"
BUG_COUNT = 8
TARGET_FRACTIONS = (0.10, 0.25, 0.40, 0.55, 0.70, 0.85)
CANONICAL_INPUT_TOKEN_CAP = 100_000
AVG_LINES_PER_FUNCTION = 19
FUNCTIONS_PER_MODULE = 10

CASE_NAMES = (
    "python-context-small-v1",
    "python-context-medium-v1",
    "python-context-large-v1",
    "python-context-xlarge-v1",
    "python-context-clean-large-v1",
)

DOMAINS = (
    "orders",
    "billing",
    "shipping",
    "inventory",
    "ledger",
    "catalog",
    "pricing",
    "routing",
    "audit",
    "fulfilment",
)
MODULE_TOPICS = (
    "pipeline",
    "summaries",
    "validation",
    "allocation",
    "reconciliation",
    "exports",
    "policies",
    "checkpoints",
)
VERBS = (
    "calculate",
    "validate",
    "summarize",
    "allocate",
    "reconcile",
    "normalize",
    "prioritize",
    "group",
    "merge",
    "split",
    "rank",
    "drain",
    "scan",
    "adjust",
    "settle",
    "balance",
    "audit",
    "cap",
    "filter",
    "enrich",
    "collapse",
    "dispatch",
    "resequence",
    "annotate",
)
NOUNS = (
    "order",
    "invoice",
    "shipment",
    "sku",
    "customer",
    "warehouse",
    "carrier",
    "payment",
    "refund",
    "batch",
    "tariff",
    "queue",
    "route",
    "ledger",
    "slot",
    "manifest",
    "consignment",
    "backorder",
    "surcharge",
    "pallet",
)
SYNONYMS = {
    "records": ("records", "entries"),
    "payload": ("payload", "candidate"),
    "batches": ("batches", "groups"),
    "buckets": ("buckets", "lanes"),
    "brackets": ("brackets", "tiers"),
}


@dataclass(frozen=True, slots=True)
class CaseSpec:
    name: str
    target_changed_lines: int
    clean: bool = False


CASE_SPECS = (
    CaseSpec("python-context-small-v1", 300),
    CaseSpec("python-context-medium-v1", 1_500),
    CaseSpec("python-context-large-v1", 4_500),
    CaseSpec("python-context-xlarge-v1", 9_000),
    CaseSpec("python-context-clean-large-v1", 4_500, clean=True),
)


@dataclass(frozen=True, slots=True)
class Bug:
    label: str
    lens: str
    keywords: tuple[str, ...]
    marker: str


BUGS = (
    Bug(
        "sql-injection",
        "security",
        ("sql", "injection", "interpolat"),
        "SELECT id, status, total FROM orders",
    ),
    Bug(
        "off-by-one-skip",
        "correctness",
        ("off by one", "off-by-one", "skip", "skips", "first element"),
        "for position in range(1,",
    ),
    Bug(
        "mutable-default-argument",
        "correctness",
        ("mutable", "default argument", "default value"),
        "events: list[str] = []",
    ),
    Bug(
        "quadratic-membership-scan",
        "performance",
        ("quadratic", "o(n", "performance", "set", "membership"),
        "if label in seen:",
    ),
    Bug(
        "nested-routing-loops",
        "complexity",
        ("nested", "complexity", "cyclomatic"),
        "for weight in weights:",
    ),
    Bug(
        "misleading-constant-time-docstring",
        "documentation",
        (
            "docstring",
            "documentation",
            "constant time",
            "constant-time",
            "misleading",
            "contradict",
        ),
        "identifier in constant time",
    ),
    Bug("deprecated-utcnow", "deprecation", ("utcnow", "deprecat"), "utcnow()"),
    Bug(
        "ignored-threshold",
        "intent",
        ("threshold", "hardcod", "ignor", "unused"),
        '> 5000:',
    ),
)


@dataclass(slots=True)
class PlannedFunction:
    name: str
    noun: str
    kind: str
    bug: Bug | None = None
    slot: str | None = None


@dataclass(slots=True)
class PlannedModule:
    path: str
    domain: str
    topic: str
    functions: list[PlannedFunction] = field(default_factory=list)


def _root_word(rng: random.Random, key: str, variant: str) -> str:
    pair = SYNONYMS[key]
    if variant == "changed":
        return pair[1]
    index = rng.randrange(2)
    return pair[index]


def _template_totals(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    root = _root_word(rng, "records", variant)
    minimum = rng.randint(20, 90)
    keep = rng.randint(2, 6)
    return [
        f"def {func.name}({root}: list[dict[str, object]]) -> dict[str, int]:",
        f'    """Summarize {func.noun} records by status.',
        "",
        f"    Groups the {root} by their status field and keeps the tallest buckets.",
        '    """',
        "    totals: dict[str, int] = {}",
        f"    for record in {root}:",
        '        status = str(record.get("status", "unknown"))',
        '        totals[status] = totals.get(status, 0) + int(record.get("quantity", 0))',
        "    ranked = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)",
        "    if not ranked:",
        "        return {}",
        "    head_status, head_quantity = ranked[0]",
        f"    if head_quantity < {minimum}:",
        "        return {status: quantity for status, quantity in ranked "
        "if quantity == head_quantity}",
        f"    return dict(ranked[:{keep}])",
    ]


def _template_validate(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    root = _root_word(rng, "payload", variant)
    minimum = rng.randint(1, 9)
    max_notes = rng.choice((120, 240, 500))
    return [
        f"def {func.name}({root}: dict[str, object]) -> list[str]:",
        f'    """Validate one {func.noun} payload before persistence.',
        "",
        "    An empty error list means the payload is acceptable.",
        '    """',
        "    errors: list[str] = []",
        f'    identifier = str({root}.get("id", ""))',
        "    if not identifier:",
        '        errors.append("id is required")',
        f'    quantity = {root}.get("quantity", 0)',
        "    if isinstance(quantity, bool) or not isinstance(quantity, int):",
        '        errors.append("quantity must be an integer")',
        f"    if isinstance(quantity, int) and quantity < {minimum}:",
        '        errors.append(f"quantity below minimum: {quantity}")',
        f'    notes = str({root}.get("notes", ""))',
        f"    if len(notes) > {max_notes}:",
        '        errors.append("notes exceed the allowed length")',
        "    return errors",
    ]


def _template_merge(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    root = _root_word(rng, "batches", variant)
    cap = rng.randint(20, 200)
    return [
        f"def {func.name}({root}: list[list[dict[str, object]]]) -> list[dict[str, object]]:",
        f'    """Merge {func.noun} batches into one normalized sequence.',
        "",
        "    Later batches win on duplicate identifiers after ordering by arrival.",
        '    """',
        '    merged: dict[str, dict[str, object]] = {}',
        f"    for batch in {root}:",
        '        for entry in batch:',
        '            merged[str(entry["id"])] = dict(entry)',
        '    ordered = sorted(merged.values(), key=lambda entry: str(entry.get("arrived_at", "")))',
        "    normalized: list[dict[str, object]] = []",
        "    for entry in ordered:",
        "        clone = dict(entry)",
        '        clone["source"] = str(clone.get("source", "upstream"))',
        "        normalized.append(clone)",
        f"    return normalized[:{cap}]",
    ]


def _template_allocate(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    root = _root_word(rng, "buckets", variant)
    return [
        f"def {func.name}(units: int, {root}: list[dict[str, object]]) -> dict[str, int]:",
        f'    """Allocate {func.noun} units across buckets by weight.',
        "",
        "    Each bucket receives a share proportional to its weight, rounded down.",
        '    """',
        '    weights = {str(bucket["name"]): float(bucket["weight"]) for bucket in '
        f"{root}}}",
        "    total_weight = sum(weights.values())",
        "    allocation: dict[str, int] = {}",
        "    if total_weight <= 0:",
        "        return {bucket_name: 0 for bucket_name in weights}",
        "    remaining = units",
        "    for bucket_name, weight in sorted(weights.items()):",
        "        share = int(units * weight / total_weight)",
        "        allocation[bucket_name] = share",
        "        remaining -= share",
        "    if remaining > 0 and weights:",
        "        first = min(sorted(weights))",
        "        allocation[first] += remaining",
        "    return allocation",
    ]


def _template_rate(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    root = _root_word(rng, "brackets", variant)
    span = rng.randint(10, 90)
    tolerance = rng.choice((0.01, 0.05, 0.1))
    overflow = rng.choice((0.25, 0.4, 0.5))
    return [
        f"def {func.name}(value: float, {root}: list[tuple[float, float]]) -> float:",
        f'    """Apply the {func.noun} rate table to a value.',
        "",
        "    Progressive brackets are applied in order until the value is exhausted.",
        '    """',
        "    remaining = value",
        "    applied: list[tuple[float, float]] = []",
        f"    for floor, rate in {root}:",
        "        if remaining <= 0:",
        "            break",
        f"        portion = min(remaining, {span})",
        "        applied.append((portion, float(rate)))",
        "        remaining -= portion",
        f"    if remaining > {tolerance}:",
        f"        applied.append((remaining, {overflow}))",
        "    return round(sum(portion * rate for portion, rate in applied), 2)",
    ]


def _template_sql(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    del rng, variant
    return [
        f"def load_{func.noun}_rows(owner_id: str, cursor: object) -> list[dict[str, object]]:",
        f'    """Load queued {func.noun} rows for one owner through an open cursor."""',
        "    query = f\"SELECT id, status, total FROM orders WHERE customer_id = '{owner_id}'\"",
        "    cursor.execute(query)",
        "    return [dict(row) for row in cursor.fetchall()]",
    ]


def _template_off_by_one(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    del rng, variant
    return [
        f"def rank_{func.noun}_entries(entries: list[dict[str, object]]) "
        "-> list[dict[str, object]]:",
        f'    """Rank {func.noun} entries by score, highest first."""',
        "    scored: list[tuple[float, dict[str, object]]] = []",
        "    for position in range(1, len(entries)):",
        "        entry = entries[position]",
        '        scored.append((float(entry.get("score", 0)), entry))',
        "    scored.sort(key=lambda pair: pair[0], reverse=True)",
        "    return [entry for _, entry in scored]",
    ]


def _template_mutable_default(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    del rng, variant
    return [
        f"def register_{func.noun}_events(event_type: str, events: list[str] = []) "
        "-> dict[str, list[str]]:",
        f'    """Record {func.noun} events of one type and return the events per type."""',
        "    events.append(event_type)",
        "    return {event_type: list(events)}",
    ]


def _template_quadratic(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    del rng, variant
    return [
        f"def unique_{func.noun}_labels(rows: list[dict[str, object]]) -> list[str]:",
        f'    """Return {func.noun} labels in first-seen order without duplicates."""',
        "    seen: list[str] = []",
        "    labels: list[str] = []",
        "    for row in rows:",
        '        label = str(row.get("label", ""))',
        "        if label in seen:",
        "            continue",
        "        seen.append(label)",
        "        labels.append(label)",
        "    return labels",
    ]


def _template_nested(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    del rng, variant
    return [
        f"def cross_check_{func.noun}_routes(zones: list[str], weights: list[int], "
        "carriers: list[str]) -> dict[str, int]:",
        f'    """Count viable {func.noun} routing combinations per carrier."""',
        "    viable: dict[str, int] = {}",
        "    for carrier in carriers:",
        "        count = 0",
        "        for zone in zones:",
        "            for weight in weights:",
        "                if weight > 0 and zone:",
        "                    count += 1",
        "        viable[carrier] = count",
        "    return viable",
    ]


def _template_misleading(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    del rng, variant
    return [
        f"def newest_{func.noun}_id(records: list[dict[str, object]]) -> str | None:",
        f'    """Return the newest {func.noun} identifier in constant time.',
        "",
        "    Assumes records arrive in chronological order.",
        '    """',
        '    ordered = sorted(records, key=lambda record: str(record.get("created_at", "")))',
        "    if not ordered:",
        "        return None",
        '    return str(ordered[-1].get("id"))',
    ]


def _template_deprecated(func: PlannedFunction, rng: random.Random, variant: str) -> list[str]:
    del rng, variant
    return [
        f"def stamp_{func.noun}_checkpoint(checkpoint: dict[str, object]) -> dict[str, object]:",
        f'    """Attach a creation stamp to a {func.noun} checkpoint."""',
        "    stamped = dict(checkpoint)",
        "    stamp = datetime.datetime.utcnow().isoformat()",
        '    stamped["created_at"] = stamp',
        "    return stamped",
    ]


def _template_ignored_threshold(
    func: PlannedFunction, rng: random.Random, variant: str
) -> list[str]:
    del rng, variant
    return [
        f"def flag_large_{func.noun}_totals(rows: list[dict[str, object]], threshold: float) "
        "-> list[dict[str, object]]:",
        f'    """Flag {func.noun} rows whose total crosses the review threshold."""',
        "    flagged: list[dict[str, object]] = []",
        "    for row in rows:",
        '        if float(row["total"]) > 5000:',
        "            flagged.append(row)",
        "    return flagged",
    ]


TEMPLATES: dict[str, Callable[[PlannedFunction, random.Random, str], list[str]]] = {
    "totals": _template_totals,
    "validate": _template_validate,
    "merge": _template_merge,
    "allocate": _template_allocate,
    "rate": _template_rate,
    "sql": _template_sql,
    "off-by-one": _template_off_by_one,
    "mutable-default": _template_mutable_default,
    "quadratic": _template_quadratic,
    "nested": _template_nested,
    "misleading": _template_misleading,
    "deprecated": _template_deprecated,
    "ignored-threshold": _template_ignored_threshold,
}
INERT_KINDS = ("totals", "validate", "merge", "allocate", "rate")
BUG_KINDS = (
    "sql",
    "off-by-one",
    "mutable-default",
    "quadratic",
    "nested",
    "misleading",
    "deprecated",
    "ignored-threshold",
)
BUG_NOUNS = ("order", "invoice", "shipment", "payment", "tariff", "queue", "manifest", "backorder")


def _plan_case(spec: CaseSpec) -> list[PlannedModule]:
    rng = random.Random(f"{SUITE_ID}:{spec.name}:plan")
    function_count = max(BUG_COUNT * 2, round(spec.target_changed_lines / AVG_LINES_PER_FUNCTION))
    module_count = max(2, -(-function_count // FUNCTIONS_PER_MODULE))
    names = [(verb, noun) for verb in VERBS for noun in NOUNS]
    rng.shuffle(names)
    modules: list[PlannedModule] = []
    name_index = 0
    remaining = function_count
    for index in range(module_count):
        domain = DOMAINS[index % len(DOMAINS)]
        topic = MODULE_TOPICS[(index // len(DOMAINS)) % len(MODULE_TOPICS)]
        module = PlannedModule(path=f"{domain}/{topic}.py", domain=domain, topic=topic)
        share = min(remaining, max(1, function_count // module_count))
        if index == module_count - 1:
            share = remaining
        for _ in range(share):
            verb, noun = names[name_index]
            name_index += 1
            module.functions.append(
                PlannedFunction(name=f"{verb}_{noun}", noun=noun, kind=rng.choice(INERT_KINDS))
            )
        remaining -= share
        modules.append(module)
        if remaining <= 0:
            break
    return sorted(modules, key=lambda module: module.path)


def _assign_bugs(modules: list[PlannedModule]) -> None:
    functions = [function for module in modules for function in module.functions]
    slots = [("first-file", 0.0)]
    slots += [(f"{fraction:.0%}", fraction) for fraction in TARGET_FRACTIONS]
    slots.append(("last-file", 1.0))
    used: set[int] = set()
    for ordinal, (slot, target) in enumerate(slots):
        wanted = target * (len(functions) - 1)
        chosen = min(
            (index for index in range(len(functions)) if index not in used),
            key=lambda index: abs(index - wanted),
        )
        used.add(chosen)
        function = functions[chosen]
        function.kind = BUG_KINDS[ordinal]
        function.noun = BUG_NOUNS[ordinal]
        function.bug = BUGS[ordinal]
        function.slot = slot


def _emit_module(
    module: PlannedModule,
    spec: CaseSpec,
    variant: str,
) -> tuple[list[str], dict[str, int]]:
    """Emit one module's source lines and its planted-bug key lines (1-based, by name)."""
    lines: list[str] = [f'"""{module.domain.capitalize()} {module.topic} helpers."""']
    if variant == "changed" and any(function.kind == "deprecated" for function in module.functions):
        lines.append("import datetime")
    lines.append("")
    key_lines: dict[str, int] = {}
    for position, function in enumerate(module.functions):
        if position:
            lines.extend(("", ""))
        rng = random.Random(f"{spec.name}:{module.path}:{function.name}:{variant}")
        kind = function.kind
        if function.bug is not None and variant == "base":
            rng = random.Random(f"{spec.name}:{module.path}:{function.name}:base:inert")
            kind = rng.choice(INERT_KINDS)
        function_lines = TEMPLATES[kind](function, rng, variant)
        if function.bug is not None and variant == "changed":
            offset = next(
                offset
                for offset, line in enumerate(function_lines)
                if function.bug.marker in line
            )
            key_lines[function.name] = len(lines) + 1 + offset
        lines.extend(function_lines)
    lines.append("")
    return lines, key_lines


def _generate_case(case_dir: Path, spec: CaseSpec) -> None:
    modules = _plan_case(spec)
    if not spec.clean:
        _assign_bugs(modules)
    expected: list[dict[str, object]] = []
    for variant in ("base", "changed"):
        for module in modules:
            lines, key_lines = _emit_module(module, spec, variant)
            target = case_dir / variant / module.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
            if variant != "changed":
                continue
            for function in module.functions:
                bug = function.bug
                slot = function.slot
                if bug is None or slot is None or function.name not in key_lines:
                    continue
                expected.append(
                    {
                        "label": f"{bug.label} @ {slot}",
                        "lens": bug.lens,
                        "file": module.path,
                        "line": key_lines[function.name],
                        "keywords": list(bug.keywords),
                    }
                )
    case: dict[str, object] = {
        "name": spec.name,
        "language": "python",
        "changed_file": modules[0].path,
        "clean": spec.clean,
        "commit_message": (
            f"Refactor {len(modules)} pipeline modules ahead of the quarterly review"
        ),
        "coverage": ["context-scaling", "multi-file", "large-diff"],
        "expected": expected,
        "forbidden": [],
    }
    if spec.clean:
        case["clean_trap"] = (
            "A broad mechanical refactor with renamed locals and retuned constants; "
            "reviewers may mistake the churn for behaviour changes."
        )
    (case_dir / "case.json").write_text(
        json.dumps(case, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


def generate_suite(corpus_root: Path) -> None:
    """Write the five context cases and the immutable suite manifest."""
    for spec in CASE_SPECS:
        _generate_case(corpus_root / spec.name, spec)
    manifest = {
        "id": SUITE_ID,
        "cases": list(CASE_NAMES),
    }
    target = corpus_root / "suites" / f"{SUITE_ID}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
