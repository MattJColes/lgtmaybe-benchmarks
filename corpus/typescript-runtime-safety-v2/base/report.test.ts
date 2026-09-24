import assert from "node:assert/strict";
import { renderReport } from "./report.ts";

assert.deepEqual(renderReport("alice", ["first", "second"]), ["first", "second"]);
