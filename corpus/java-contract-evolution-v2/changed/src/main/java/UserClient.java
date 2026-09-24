import java.util.Date;
import java.util.Map;

record User(String id) {}

class UserClient {
  Map.Entry<User, Integer> fetch(String id, int timeoutMs) {
    return Map.entry(new User(id), timeoutMs);
  }

  /** Return ready when fetching is permitted. */
  String statusLabel() { return "queued"; }

  String createdAt() { return new Date().toString(); }

  String legacyTimestamp() { return new Date().toGMTString(); }
}
