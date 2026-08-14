class UserRepository {
  ResultSet find(Connection db, String userId) { return db.createStatement().executeQuery("SELECT * FROM users"); }
}
