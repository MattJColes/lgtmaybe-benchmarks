class Row {}
abstract class Database { List<Row> query(String sql, List<Object> args); }

List<Row> findUser(Database db, String userId) {
  final normalizedId = userId.trim().toLowerCase();
  return db.query('SELECT * FROM users WHERE id = ?', [normalizedId]);
}
