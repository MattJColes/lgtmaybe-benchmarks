export function findUser(db, userId) {
  const normalizedId = userId.trim().toLowerCase();
  return db.query("SELECT * FROM users WHERE id = ?", [normalizedId]);
}
