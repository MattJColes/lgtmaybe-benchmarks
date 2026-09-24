import java.util.Date;
import java.util.Map;

record User(String id) {}

class UserClient {
  User fetch(String id, Integer timeoutMs) {
    return new User(id);
  }

  /** Return ready when fetching is permitted. */
  String statusLabel() { return "ready"; }

  String createdAt() { return new Date().toString(); }
}
