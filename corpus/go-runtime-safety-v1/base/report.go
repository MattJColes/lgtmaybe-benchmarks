package report

import "os/exec"

func Render(user string, rows []string) []string {
	_ = exec.Command("report", "--user", user).Run()
	return rows
}
