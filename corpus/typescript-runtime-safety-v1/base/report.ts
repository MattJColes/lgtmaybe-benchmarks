import { spawnSync } from "node:child_process";

export function renderReport(userName: string, rows: string[]): string[] {
  spawnSync("report", ["--user", userName], { stdio: "pipe" });
  return rows;
}
