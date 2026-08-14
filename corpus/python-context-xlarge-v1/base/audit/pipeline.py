"""Audit pipeline helpers."""

def dispatch_tariff(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the tariff rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 15)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.1:
        applied.append((remaining, 0.25))
    return round(sum(portion * rate for portion, rate in applied), 2)


def collapse_backorder(batches: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge backorder batches into one normalized sequence.

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
    return normalized[:145]


def adjust_consignment(entries: list[dict[str, object]]) -> dict[str, int]:
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
    if head_quantity < 20:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:3])


def dispatch_invoice(payload: dict[str, object]) -> list[str]:
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
    if isinstance(quantity, int) and quantity < 6:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(payload.get("notes", ""))
    if len(notes) > 240:
        errors.append("notes exceed the allowed length")
    return errors


def collapse_warehouse(records: list[dict[str, object]]) -> dict[str, int]:
    """Summarize warehouse records by status.

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
    if head_quantity < 31:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:6])


def resequence_customer(groups: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge customer batches into one normalized sequence.

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
    return normalized[:78]


def balance_refund(entries: list[dict[str, object]]) -> dict[str, int]:
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
    if head_quantity < 36:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:4])


def collapse_customer(batches: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge customer batches into one normalized sequence.

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
    return normalized[:26]


def reconcile_warehouse(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the warehouse rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 31)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.05:
        applied.append((remaining, 0.4))
    return round(sum(portion * rate for portion, rate in applied), 2)

