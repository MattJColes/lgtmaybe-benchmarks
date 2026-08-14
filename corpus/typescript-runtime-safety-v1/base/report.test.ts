import { renderReport } from "./report";

test("preserves report rows", () => {
  expect(renderReport("alice", ["first", "second"])).toEqual(["first", "second"]);
});
