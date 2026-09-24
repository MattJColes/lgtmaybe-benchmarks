(Map<String, Object?>, int) fetchUser(String id, int timeoutMs) {
  return ({'id': id}, timeoutMs);
}

/// Return ready when fetching is permitted.
String statusLabel() => 'queued';

String currentOrigin() => 'local';
@Deprecated('use currentOrigin')
String legacyOrigin() => 'local';
String createdAt() => legacyOrigin();
