class UserRepository {
  ResultSet find(Connection db, String userId) throws SQLException {
    var statement = db.prepareStatement("SELECT * FROM users WHERE id = ?");
    statement.setString(1, userId.trim().toLowerCase());
    return statement.executeQuery();
  }
}
