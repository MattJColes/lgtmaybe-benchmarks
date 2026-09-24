import assert from "node:assert/strict";
import { renderReport } from "./report.ts";

assert.ok(renderReport("alice", ["first", "second"]));
