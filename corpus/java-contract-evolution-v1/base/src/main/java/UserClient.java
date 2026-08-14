class UserClient {
  /** Fetch one user using the stable User return contract. */
  User fetch(String id, Integer timeoutMs) { return new User(id, timeoutMs == null ? 30000 : timeoutMs); }
}
