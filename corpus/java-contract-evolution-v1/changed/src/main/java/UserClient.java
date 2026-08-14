import java.util.Date;

class UserClient {
  Map.Entry<User, Integer> fetch(String id, int timeoutMs) {
    var user = new User(id, new Date().toGMTString());
    return Map.entry(user, timeoutMs);
  }
}
