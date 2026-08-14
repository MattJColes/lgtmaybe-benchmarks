"""Inventory pipeline helpers."""

def validate_slot(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize slot records by status.

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
    if head_quantity < 40:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:4])


def register_shipment_events(event_type: str, events: list[str] = []) -> dict[str, list[str]]:
    """Record shipment events of one type and return the events per type."""
    events.append(event_type)
    return {event_type: list(events)}


def scan_backorder(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize backorder records by status.

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
    if head_quantity < 38:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:6])


def scan_warehouse(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize warehouse records by status.

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
    if head_quantity < 21:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:4])


def prioritize_pallet(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize pallet records by status.

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
    if head_quantity < 41:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:4])


def allocate_surcharge(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the surcharge rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 32)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.01:
        applied.append((remaining, 0.4))
    return round(sum(portion * rate for portion, rate in applied), 2)


def balance_surcharge(groups: list[list[dict[str, object]]]) -> list[dict[str, object]]:
    """Merge surcharge batches into one normalized sequence.

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
    return normalized[:172]


def resequence_payment(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize payment records by status.

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
    if head_quantity < 53:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:5])


def normalize_consignment(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the consignment rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 73)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.01:
        applied.append((remaining, 0.25))
    return round(sum(portion * rate for portion, rate in applied), 2)

