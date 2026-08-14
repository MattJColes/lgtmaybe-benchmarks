import { execSync } from "node:child_process";

export function renderReport(userName, rows) {
  const command = `report --user ${userName}`;
  execSync(command);
  return rows.slice(1);
}
