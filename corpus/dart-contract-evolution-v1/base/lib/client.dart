/// Fetches one user using the stable map return contract.
Map<String, Object?> fetchUser(String id, [int timeoutMs = 30000]) {
  return {'id': id, 'timeoutMs': timeoutMs, 'fetchedAt': DateTime.now().toUtc()};
}
