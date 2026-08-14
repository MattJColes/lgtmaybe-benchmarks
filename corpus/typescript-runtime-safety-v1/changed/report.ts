import { execSync } from "node:child_process";

export function renderReport(userName: string, rows: string[]): string[] {
  const command = `report --user ${userName}`;
  execSync(command);
  return rows.slice(1);
}
