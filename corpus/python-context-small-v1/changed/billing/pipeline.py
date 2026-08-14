"""Billing pipeline helpers."""

def load_order_rows(owner_id: str, cursor: object) -> list[dict[str, object]]:
    """Load queued order rows for one owner through an open cursor."""
    query = f"SELECT id, status, total FROM orders WHERE customer_id = '{owner_id}'"
    cursor.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def rank_invoice_entries(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    """Rank invoice entries by score, highest first."""
    scored: list[tuple[float, dict[str, object]]] = []
    for position in range(1, len(entries)):
        entry = entries[position]
        scored.append((float(entry.get("score", 0)), entry))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [entry for _, entry in scored]


def group_queue(entries: list[dict[str, object]]) -> dict[str, int]:
    """Summarize queue records by status.

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
    if head_quantity < 43:
        return {status: quantity for status, quantity in ranked if quantity == head_quantity}
    return dict(ranked[:3])


def resequence_shipment(candidate: dict[str, object]) -> list[str]:
    """Validate one shipment payload before persistence.

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


def register_shipment_events(event_type: str, events: list[str] = []) -> dict[str, list[str]]:
    """Record shipment events of one type and return the events per type."""
    events.append(event_type)
    return {event_type: list(events)}


def scan_route(candidate: dict[str, object]) -> list[str]:
    """Validate one route payload before persistence.

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
    if len(notes) > 120:
        errors.append("notes exceed the allowed length")
    return errors


def unique_payment_labels(rows: list[dict[str, object]]) -> list[str]:
    """Return payment labels in first-seen order without duplicates."""
    seen: list[str] = []
    labels: list[str] = []
    for row in rows:
        label = str(row.get("label", ""))
        if label in seen:
            continue
        seen.append(label)
        labels.append(label)
    return labels


def cap_ledger(units: int, lanes: list[dict[str, object]]) -> dict[str, int]:
    """Allocate ledger units across buckets by weight.

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

