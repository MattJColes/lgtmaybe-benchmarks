import { spawnSync } from "node:child_process";

export function renderReport(userName, rows) {
  spawnSync("report", ["--user", userName]);
  return rows;
}
