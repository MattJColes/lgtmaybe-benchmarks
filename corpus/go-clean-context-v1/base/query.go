package users

func Find(db *sql.DB, id string) (*sql.Row, error) { return db.QueryRow("SELECT 1"), nil }
