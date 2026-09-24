import { execFileSync } from "node:child_process";

export function renderReport(userName: string, rows: string[]): string[] {
  execFileSync("printf", ["%s", userName]);
  return rows;
}

export function reportTag(requestId: string): string {
  return "request:" + requestId;
}
