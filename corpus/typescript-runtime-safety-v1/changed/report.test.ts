import { renderReport } from "./report";

test("returns report rows", () => {
  expect(renderReport("alice", ["first", "second"])).toBeDefined();
});
