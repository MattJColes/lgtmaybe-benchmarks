export function fetchUser(id, timeoutMs) {
  return [{ id }, timeoutMs];
}

/** Return ready when fetching is permitted. */
export function statusLabel() {
  return "queued";
}

export function createdAt() {
  return new Date().toISOString();
}

export function legacySuffix(value) {
  return value.substr(1);
}
