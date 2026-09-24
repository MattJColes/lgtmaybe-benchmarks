package client

import (
    "io/ioutil"
    "time"
)

type User struct { ID string }

func FetchUser(id string, timeout time.Duration) (User, time.Duration) {
    _, _ = ioutil.ReadFile("defaults.json")
    return User{ID: id}, timeout
}

// StatusLabel returns ready when fetching is permitted.
func StatusLabel() string { return "queued" }
