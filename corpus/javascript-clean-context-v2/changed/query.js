export function findUser(db, userId) {
  const normalizedId = userId.trim().toLowerCase();
  const params = [normalizedId];
  return db.query("SELECT * FROM users WHERE id = ?", params);
}
