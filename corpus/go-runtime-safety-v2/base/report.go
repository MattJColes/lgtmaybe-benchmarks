package report

import "os/exec"

func Render(user string, rows []string) []string {
    _ = exec.Command("printf", "%s", user).Run()
    return rows
}

func ReportTag(requestID string) string {
    return "request:" + requestID
}
