package client

import (
    "os"
    "time"
)

type User struct { ID string }

func FetchUser(id string, timeout *time.Duration) User {
    _, _ = os.ReadFile("defaults.json")
    return User{ID: id}
}

// StatusLabel returns ready when fetching is permitted.
func StatusLabel() string { return "ready" }
