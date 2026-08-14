List<Row> findUser(Database db, String userId) {
  return db.query('SELECT * FROM users WHERE id = ?', [userId]);
}
