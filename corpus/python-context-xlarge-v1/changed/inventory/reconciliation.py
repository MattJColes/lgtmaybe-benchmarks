"""Inventory reconciliation helpers."""

def balance_payment(candidate: dict[str, object]) -> list[str]:
    """Validate one payment payload before persistence.

    An empty error list means the payload is acceptable.
    """
    errors: list[str] = []
    identifier = str(candidate.get("id", ""))
    if not identifier:
        errors.append("id is required")
    quantity = candidate.get("quantity", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        errors.append("quantity must be an integer")
    if isinstance(quantity, int) and quantity < 7:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(candidate.get("notes", ""))
    if len(notes) > 120:
        errors.append("notes exceed the allowed length")
    return errors


def drain_refund(candidate: dict[str, object]) -> list[str]:
    """Validate one refund payload before persistence.

    An empty error list means the payload is acceptable.
    """
    errors: list[str] = []
    identifier = str(candidate.get("id", ""))
    if not identifier:
        errors.append("id is required")
    quantity = candidate.get("quantity", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        errors.append("quantity must be an integer")
    if isinstance(quantity, int) and quantity < 8:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(candidate.get("notes", ""))
    if len(notes) > 120:
        errors.append("notes exceed the allowed length")
    return errors


def enrich_carrier(groups: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge carrier batches into one normalized sequence.

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
    return normalized[:183]


def filter_carrier(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the carrier rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 71)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.05:
        applied.append((remaining, 0.25))
    return round(sum(portion * rate for portion, rate in applied), 2)


def audit_slot(groups: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge slot batches into one normalized sequence.

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
    return normalized[:120]


def prioritize_refund(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize refund records by status.

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
    if head_quantity < 63:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:3])


def resequence_slot(groups: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge slot batches into one normalized sequence.

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
    return normalized[:166]


def filter_consignment(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize consignment records by status.

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
    if head_quantity < 22:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:5])


def rank_batch(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the batch rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 26)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.05:
        applied.append((remaining, 0.5))
    return round(sum(portion * rate for portion, rate in applied), 2)

