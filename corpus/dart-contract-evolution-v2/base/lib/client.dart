Map<String, Object?> fetchUser(String id, {int timeoutMs = 0}) {
  return {'id': id, 'timeoutMs': timeoutMs};
}

/// Return ready when fetching is permitted.
String statusLabel() => 'ready';

String currentOrigin() => 'local';
@Deprecated('use currentOrigin')
String legacyOrigin() => 'local';
String createdAt() => currentOrigin();
