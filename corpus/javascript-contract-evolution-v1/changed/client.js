export function fetchUser(id, timeoutMs) {
  return [{ id, fetchedAt: new Date().toGMTString() }, timeoutMs];
}
