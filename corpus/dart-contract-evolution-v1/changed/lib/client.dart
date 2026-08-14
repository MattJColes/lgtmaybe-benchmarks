import 'dart:html';

(Map<String, Object?>, int) fetchUser(String id, int timeoutMs) {
  return ({'id': id, 'origin': window.location.origin}, timeoutMs);
}
