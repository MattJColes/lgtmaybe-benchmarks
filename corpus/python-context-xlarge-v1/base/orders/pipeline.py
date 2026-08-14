"""Orders pipeline helpers."""

def group_queue(units: int, buckets: list[dict[str, object]]) -> dict[str, int]:
    """Allocate queue units across buckets by weight.

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


def group_route(value: float, brackets: list[tuple[float, float]]) -> float:
    """Apply the route rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in brackets:
        if remaining <= 0:
            break
        portion = min(remaining, 45)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.05:
        applied.append((remaining, 0.25))
    return round(sum(portion * rate for portion, rate in applied), 2)


def group_shipment(payload: dict[str, object]) -> list[str]:
    """Validate one shipment payload before persistence.

    An empty error list means the payload is acceptable.
    """
    errors: list[str] = []
    identifier = str(payload.get("id", ""))
    if not identifier:
        errors.append("id is required")
    quantity = payload.get("quantity", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        errors.append("quantity must be an integer")
    if isinstance(quantity, int) and quantity < 6:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(payload.get("notes", ""))
    if len(notes) > 500:
        errors.append("notes exceed the allowed length")
    return errors


def balance_shipment(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize shipment records by status.

    Groups the entries by their status field and keeps the tallest buckets.
    """
    totals: dict[str, int] = {}
    for record in entries:
        status = str(record.get("status", "unknown"))
        totals[status] = totals.get(status, 0) + int(record.get("quantity", 0))
    ranked = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    if not ranked:
        return {}
    head_status, head_quantity = ranked[0]
    if head_quantity < 57:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:6])


def settle_ledger(candidate: dict[str, object]) -> list[str]:
    """Validate one ledger payload before persistence.

    An empty error list means the payload is acceptable.
    """
    errors: list[str] = []
    identifier = str(candidate.get("id", ""))
    if not identifier:
        errors.append("id is required")
    quantity = candidate.get("quantity", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        errors.append("quantity must be an integer")
    if isinstance(quantity, int) and quantity < 2:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(candidate.get("notes", ""))
    if len(notes) > 500:
        errors.append("notes exceed the allowed length")
    return errors


def dispatch_customer(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize customer records by status.

    Groups the entries by their status field and keeps the tallest buckets.
    """
    totals: dict[str, int] = {}
    for record in entries:
        status = str(record.get("status", "unknown"))
        totals[status] = totals.get(status, 0) + int(record.get("quantity", 0))
    ranked = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    if not ranked:
        return {}
    head_status, head_quantity = ranked[0]
    if head_quantity < 77:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:6])


def cap_order(groups: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge order batches into one normalized sequence.

    Later batches win on duplicate identifiers after ordering by arrival.
    """
    merged: dict[str, dict[str, object]] = {}
    for batch in groups:
        for entry in batch:
            merged[str(entry["id"])] = dict(entry)
    ordered = sorted(merged.values(), key=lambda entry: str(entry.get("arrived_at", "")))
    normalized: list[dict[str, object]] = []
    for entry in ordered:
        clone = dict(entry)
        clone["source"] = str(clone.get("source", "upstream"))
        normalized.append(clone)
    return normalized[:154]


def audit_sku(groups: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge sku batches into one normalized sequence.

    Later batches win on duplicate identifiers after ordering by arrival.
    """
    merged: dict[str, dict[str, object]] = {}
    for batch in groups:
        for entry in batch:
            merged[str(entry["id"])] = dict(entry)
    ordered = sorted(merged.values(), key=lambda entry: str(entry.get("arrived_at", "")))
    normalized: list[dict[str, object]] = []
    for entry in ordered:
        clone = dict(entry)
        clone["source"] = str(clone.get("source", "upstream"))
        normalized.append(clone)
    return normalized[:156]


def split_pallet(records: list[dict[str, object]]) -> dict[str, int]:
    """Summarize pallet records by status.

    Groups the records by their status field and keeps the tallest buckets.
    """
    totals: dict[str, int] = {}
    for record in records:
        status = str(record.get("status", "unknown"))
        totals[status] = totals.get(status, 0) + int(record.get("quantity", 0))
    ranked = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    if not ranked:
        return {}
    head_status, head_quantity = ranked[0]
    if head_quantity < 69:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:4])

