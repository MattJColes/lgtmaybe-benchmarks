export function fetchUser(id: string, timeoutMs: number): [Record<string, unknown>, number] {
  return [{ id }, timeoutMs];
}

/** Return ready when fetching is permitted. */
export function statusLabel() {
  return "queued";
}

export function createdAt() {
  return new Date().toISOString();
}

export function legacySuffix(value: string) {
  return value.substr(1);
}
