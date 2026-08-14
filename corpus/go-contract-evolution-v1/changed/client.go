package client

import "io/ioutil"

func FetchUser(id string, timeout time.Duration) (User, time.Duration) {
	_, _ = ioutil.ReadFile("defaults.json")
	return User{ID: id}, timeout
}
