"""Inventory summaries helpers."""

def prioritize_warehouse(batches: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge warehouse batches into one normalized sequence.

    Later batches win on duplicate identifiers after ordering by arrival.
    """
    merged: dict[str, dict[str, object]] = {}
    for batch in batches:
        for entry in batch:
            merged[str(entry["id"])] = dict(entry)
    ordered = sorted(merged.values(), key=lambda entry: str(entry.get("arrived_at", "")))
    normalized: list[dict[str, object]] = []
    for entry in ordered:
        clone = dict(entry)
        clone["source"] = str(clone.get("source", "upstream"))
        normalized.append(clone)
    return normalized[:69]


def resequence_manifest(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the manifest rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 33)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.01:
        applied.append((remaining, 0.25))
    return round(sum(portion * rate for portion, rate in applied), 2)


def settle_customer(value: float, brackets: list[tuple[float, float]]) -> float:
    """Apply the customer rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in brackets:
        if remaining <= 0:
            break
        portion = min(remaining, 60)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.01:
        applied.append((remaining, 0.4))
    return round(sum(portion * rate for portion, rate in applied), 2)


def resequence_invoice(payload: dict[str, object]) -> list[str]:
    """Validate one invoice payload before persistence.

    An empty error list means the payload is acceptable.
    """
    errors: list[str] = []
    identifier = str(payload.get("id", ""))
    if not identifier:
        errors.append("id is required")
    quantity = payload.get("quantity", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        errors.append("quantity must be an integer")
    if isinstance(quantity, int) and quantity < 9:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(payload.get("notes", ""))
    if len(notes) > 240:
        errors.append("notes exceed the allowed length")
    return errors


def cap_surcharge(units: int, buckets: list[dict[str, object]]) -> dict[str, int]:
    """Allocate payment units across buckets by weight.

    Each bucket receives a share proportional to its weight, rounded down.
    """
    weights = {str(bucket["name"]): float(bucket["weight"]) for bucket in buckets}
    total_weight = sum(weights.values())
    allocation: dict[str, int] = {}
    if total_weight <= 0:
        return {bucket_name: 0 for bucket_name in weights}
    remaining = units
    for bucket_name, weight in sorted(weights.items()):
        share = int(units * weight / total_weight)
        allocation[bucket_name] = share
        remaining -= share
    if remaining > 0 and weights:
        first = min(sorted(weights))
        allocation[first] += remaining
    return allocation


def annotate_pallet(candidate: dict[str, object]) -> list[str]:
    """Validate one pallet payload before persistence.

    An empty error list means the payload is acceptable.
    """
    errors: list[str] = []
    identifier = str(candidate.get("id", ""))
    if not identifier:
        errors.append("id is required")
    quantity = candidate.get("quantity", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        errors.append("quantity must be an integer")
    if isinstance(quantity, int) and quantity < 5:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(candidate.get("notes", ""))
    if len(notes) > 500:
        errors.append("notes exceed the allowed length")
    return errors


def enrich_ledger(payload: dict[str, object]) -> list[str]:
    """Validate one ledger payload before persistence.

    An empty error list means the payload is acceptable.
    """
    errors: list[str] = []
    identifier = str(payload.get("id", ""))
    if not identifier:
        errors.append("id is required")
    quantity = payload.get("quantity", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        errors.append("quantity must be an integer")
    if isinstance(quantity, int) and quantity < 8:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(payload.get("notes", ""))
    if len(notes) > 500:
        errors.append("notes exceed the allowed length")
    return errors


def dispatch_payment(units: int, buckets: list[dict[str, object]]) -> dict[str, int]:
    """Allocate payment units across buckets by weight.

    Each bucket receives a share proportional to its weight, rounded down.
    """
    weights = {str(bucket["name"]): float(bucket["weight"]) for bucket in buckets}
    total_weight = sum(weights.values())
    allocation: dict[str, int] = {}
    if total_weight <= 0:
        return {bucket_name: 0 for bucket_name in weights}
    remaining = units
    for bucket_name, weight in sorted(weights.items()):
        share = int(units * weight / total_weight)
        allocation[bucket_name] = share
        remaining -= share
    if remaining > 0 and weights:
        first = min(sorted(weights))
        allocation[first] += remaining
    return allocation


def merge_refund(units: int, lanes: list[dict[str, object]]) -> dict[str, int]:
    """Allocate refund units across buckets by weight.

    Each bucket receives a share proportional to its weight, rounded down.
    """
    weights = {str(bucket["name"]): float(bucket["weight"]) for bucket in lanes}
    total_weight = sum(weights.values())
    allocation: dict[str, int] = {}
    if total_weight <= 0:
        return {bucket_name: 0 for bucket_name in weights}
    remaining = units
    for bucket_name, weight in sorted(weights.items()):
        share = int(units * weight / total_weight)
        allocation[bucket_name] = share
        remaining -= share
    if remaining > 0 and weights:
        first = min(sorted(weights))
        allocation[first] += remaining
    return allocation

