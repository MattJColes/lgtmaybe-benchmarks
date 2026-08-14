export function fetchUser(id: string, timeoutMs: number): [Record<string, unknown>, number] {
  return [{ id, fetchedAt: new Date().toGMTString() }, timeoutMs];
}
