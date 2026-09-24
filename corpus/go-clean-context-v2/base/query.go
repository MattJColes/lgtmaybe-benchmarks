package users

import (
    "database/sql"
    "strings"
)

func Find(db *sql.DB, id string) *sql.Row {
    normalized := strings.ToLower(strings.TrimSpace(id))
    return db.QueryRow("SELECT * FROM users WHERE id = $1", normalized)
}
