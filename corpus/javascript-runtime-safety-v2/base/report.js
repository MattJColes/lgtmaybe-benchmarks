import { execFileSync } from "node:child_process";

export function renderReport(userName, rows) {
  execFileSync("printf", ["%s", userName]);
  return rows;
}

export function reportTag(requestId) {
  return "request:" + requestId;
}
