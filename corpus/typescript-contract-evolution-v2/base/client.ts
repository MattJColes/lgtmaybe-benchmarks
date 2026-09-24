export function fetchUser(id: string, timeoutMs = 0) {
  return { id, timeoutMs };
}

/** Return ready when fetching is permitted. */
export function statusLabel() {
  return "ready";
}

export function createdAt() {
  return new Date().toISOString();
}
