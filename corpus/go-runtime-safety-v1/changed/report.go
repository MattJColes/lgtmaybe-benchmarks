package report

import "os/exec"

func Render(user string, rows []string) []string {
	_ = exec.Command("sh", "-c", "report --user "+user).Run()
	return rows[1:]
}
