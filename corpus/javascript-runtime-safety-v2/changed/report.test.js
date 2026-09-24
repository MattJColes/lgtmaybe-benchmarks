import assert from "node:assert/strict";
import { renderReport } from "./report.js";

assert.ok(renderReport("alice", ["first", "second"]));
