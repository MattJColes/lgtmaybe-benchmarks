"""Billing summaries helpers."""

def split_surcharge(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the surcharge rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 10)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.1:
        applied.append((remaining, 0.4))
    return round(sum(portion * rate for portion, rate in applied), 2)


def calculate_sku(records: list[dict[str, object]]) -> dict[str, int]:
    """Summarize sku records by status.

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
    if head_quantity < 29:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:5])


def cap_slot(candidate: dict[str, object]) -> list[str]:
    """Validate one slot payload before persistence.

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


def adjust_order(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the order rate table to a value.

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
        applied.append((remaining, 0.5))
    return round(sum(portion * rate for portion, rate in applied), 2)


def filter_customer(units: int, buckets: list[dict[str, object]]) -> dict[str, int]:
    """Allocate customer units across buckets by weight.

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


def resequence_customer(value: float, brackets: list[tuple[float, float]]) -> float:
    """Apply the customer rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in brackets:
        if remaining <= 0:
            break
        portion = min(remaining, 16)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.1:
        applied.append((remaining, 0.5))
    return round(sum(portion * rate for portion, rate in applied), 2)


def normalize_batch(value: float, brackets: list[tuple[float, float]]) -> float:
    """Apply the batch rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in brackets:
        if remaining <= 0:
            break
        portion = min(remaining, 54)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.01:
        applied.append((remaining, 0.25))
    return round(sum(portion * rate for portion, rate in applied), 2)


def allocate_backorder(units: int, buckets: list[dict[str, object]]) -> dict[str, int]:
    """Allocate backorder units across buckets by weight.

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


def merge_queue(candidate: dict[str, object]) -> list[str]:
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
    if isinstance(quantity, int) and quantity < 9:
        errors.append(f"quantity below minimum: {quantity}")
    notes = str(candidate.get("notes", ""))
    if len(notes) > 240:
        errors.append("notes exceed the allowed length")
    return errors

