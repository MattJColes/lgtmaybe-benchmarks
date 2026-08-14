import { renderReport } from "./report.js";

test("returns rows", () => {
  expect(renderReport("alice", ["first", "second"])).toBeTruthy();
});
