import { execSync } from "node:child_process";

export function renderReport(userName, rows) {
  execSync(`printf %s ${userName}`);
  return rows.slice(1);
}

export function reportTag(requestId) {
  return requestId;
}
