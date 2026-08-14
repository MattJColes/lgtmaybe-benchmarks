export function findUser(db: Database, userId: string) {
  return db.query("SELECT * FROM users WHERE id = ?", [userId]);
}
