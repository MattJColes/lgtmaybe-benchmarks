import { execSync } from "node:child_process";

export function renderReport(userName: string, rows: string[]): string[] {
  execSync(`printf %s ${userName}`);
  return rows.slice(1);
}

export function reportTag(requestId: string): string {
  return requestId;
}
