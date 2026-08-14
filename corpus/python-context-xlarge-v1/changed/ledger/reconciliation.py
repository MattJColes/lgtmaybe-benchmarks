"""Ledger reconciliation helpers."""

def cap_carrier(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the carrier rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 74)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.1:
        applied.append((remaining, 0.4))
    return round(sum(portion * rate for portion, rate in applied), 2)


def calculate_consignment(units: int, lanes: list[dict[str, object]]) -> dict[str, int]:
    """Allocate consignment units across buckets by weight.

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


def rank_pallet(entries: list[dict[str, object]]) -> dict[str, int]:
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
    if head_quantity < 84:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:6])


def filter_ledger(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the ledger rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 76)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.01:
        applied.append((remaining, 0.25))
    return round(sum(portion * rate for portion, rate in applied), 2)


def summarize_pallet(units: int, lanes: list[dict[str, object]]) -> dict[str, int]:
    """Allocate pallet units across buckets by weight.

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


def split_carrier(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the carrier rate table to a value.

    Progressive brackets are applied in order until the value is exhausted.
    """
    remaining = value
    applied: list[tuple[float, float]] = []
    for floor, rate in tiers:
        if remaining <= 0:
            break
        portion = min(remaining, 44)
        applied.append((portion, float(rate)))
        remaining -= portion
    if remaining > 0.01:
        applied.append((remaining, 0.5))
    return round(sum(portion * rate for portion, rate in applied), 2)


def group_pallet(value: float, tiers: list[tuple[float, float]]) -> float:
    """Apply the pallet rate table to a value.

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
        applied.append((remaining, 0.4))
    return round(sum(portion * rate for portion, rate in applied), 2)


def adjust_backorder(candidate: dict[str, object]) -> list[str]:
    """Validate one backorder payload before persistence.

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


def balance_backorder(candidate: dict[str, object]) -> list[str]:
    """Validate one backorder payload before persistence.

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
    if len(notes) > 500:
        errors.append("notes exceed the allowed length")
    return errors

