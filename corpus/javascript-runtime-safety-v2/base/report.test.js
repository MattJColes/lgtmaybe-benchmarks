import assert from "node:assert/strict";
import { renderReport } from "./report.js";

assert.deepEqual(renderReport("alice", ["first", "second"]), ["first", "second"]);
