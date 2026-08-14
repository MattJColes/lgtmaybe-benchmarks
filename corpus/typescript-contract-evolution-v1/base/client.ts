export function fetchUser(id: string, timeoutMs = 30_000): Record<string, unknown> {
  return { id, timeoutMs, fetchedAt: new Date().toISOString() };
}
