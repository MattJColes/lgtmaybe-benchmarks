import { renderReport } from "./report.js";

test("preserves all rows", () => {
  expect(renderReport("alice", ["first", "second"])).toEqual(["first", "second"]);
});
