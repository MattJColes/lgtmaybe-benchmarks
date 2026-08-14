export function fetchUser(id, timeoutMs = 30000) {
  return { id, timeoutMs, fetchedAt: new Date().toISOString() };
}
