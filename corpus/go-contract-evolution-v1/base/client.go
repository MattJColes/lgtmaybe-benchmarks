package client

// FetchUser returns one user while preserving the stable User contract.
func FetchUser(id string, timeout *time.Duration) User { return User{ID: id} }
