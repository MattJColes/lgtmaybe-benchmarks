"""Billing pipeline helpers."""

def rank_invoice(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the invoice rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 63)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.1:
        applied.append((remaining, 0.4))
    return round(sum(portion * rate for portion, rate in applied), 2)


def filter_manifest(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the manifest rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 37)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.05:
        applied.append((remaining, 0.4))
    return round(sum(portion * rate for portion, rate in applied), 2)


def split_payment(candidate: dict[str, object]) -> list[str]:
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
    if isinstance(quantity, int) and quantity < 1:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(candidate.get("notes", ""))
    if len(notes) > 240:
        errors.append("notes exceed the allowed length")
    return errors


def enrich_backorder(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the backorder rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 23)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.1:
        applied.append((remaining, 0.5))
    return round(sum(portion * rate for portion, rate in applied), 2)


def settle_queue(candidate: dict[str, object]) -> list[str]:
    """Validate one queue payload before persistence.

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
    if len(notes) > 500:
        errors.append("notes exceed the allowed length")
    return errors


def group_surcharge(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the surcharge rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 18)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.05:
        applied.append((remaining, 0.25))
    return round(sum(portion * rate for portion, rate in applied), 2)


def filter_slot(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the slot rate table to a value.

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
        applied.append((remaining, 0.5))
    return round(sum(portion * rate for portion, rate in applied), 2)


def balance_surcharge(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize surcharge records by status.

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
    return dict(ranked[:5])


def reconcile_invoice(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the invoice rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 39)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.05:
        applied.append((remaining, 0.5))
    return round(sum(portion * rate for portion, rate in applied), 2)

