interface Database { query(sql: string, params: string[]): unknown }
export function findUser(db: Database, userId: string) {
  const normalizedId = userId.trim().toLowerCase();
  const params = [normalizedId];
  return db.query("SELECT * FROM users WHERE id = ?", params);
}
