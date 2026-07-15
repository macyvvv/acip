// Plain Node test for app.js's pure, side-effect-free functions -- no
// framework, matching this product's "no over-engineering" constraint
// (see architecture.md). Run directly: `node tests/test_app_logic.js`
// from the product directory, or from the repo root:
// `node app/products/kabukicho_survival_map/tests/test_app_logic.js`.
// Not part of the Python pytest suite (different runtime); intended as
// a quick regression check for the map/list logic that previously had
// zero automated coverage (only ad hoc Playwright checks during
// development).
"use strict";

var assert = require("assert");
var path = require("path");
var app = require(path.join(__dirname, "..", "app.js"));

var failures = 0;
var passed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
  } catch (err) {
    failures++;
    console.error("FAIL: " + name);
    console.error("  " + err.message);
  }
}

// -- haversineDistanceMeters -------------------------------------------

test("haversineDistanceMeters: same point is 0", function () {
  var d = app.haversineDistanceMeters(35.6949, 139.7028, 35.6949, 139.7028);
  assert.strictEqual(d, 0);
});

test("haversineDistanceMeters: Kabukicho center to Shinjuku Station is roughly 500-900m", function () {
  // 35.6949,139.7028 (Kabukicho centroid) to 35.6905,139.7003 (Shinjuku
  // Station area, used elsewhere in the data) -- real-world distance is
  // known to be in this range, not an exact fixture value.
  var d = app.haversineDistanceMeters(35.6949, 139.7028, 35.6905, 139.7003);
  assert.ok(d > 400 && d < 1000, "expected 400-1000m, got " + d);
});

test("haversineDistanceMeters: symmetric (A to B equals B to A)", function () {
  var ab = app.haversineDistanceMeters(35.6949, 139.7028, 35.6905, 139.7003);
  var ba = app.haversineDistanceMeters(35.6905, 139.7003, 35.6949, 139.7028);
  assert.strictEqual(ab, ba);
});

// -- formatDistance -------------------------------------------------------

test("formatDistance: sub-1000m renders as rounded meters", function () {
  assert.strictEqual(app.formatDistance(21.4), "21m");
  assert.strictEqual(app.formatDistance(999.6), "1000m");
});

test("formatDistance: >=1000m renders as km with 1 decimal", function () {
  assert.strictEqual(app.formatDistance(1000), "1.0km");
  // Avoid an exact x.x5 boundary (e.g. 1650 -> 1.65) -- toFixed's
  // rounding there depends on IEEE754 double representation, not a bug
  // in formatDistance, and would make this test assert on that quirk
  // instead of the function's actual behavior.
  assert.strictEqual(app.formatDistance(1620), "1.6km");
});

// -- freshnessBadge ---------------------------------------------------

function daysAgoIso(days) {
  var d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

test("freshnessBadge: null/undefined last_updated returns null", function () {
  assert.strictEqual(app.freshnessBadge(null), null);
  assert.strictEqual(app.freshnessBadge(undefined), null);
});

test("freshnessBadge: within 7 days is 'recent'", function () {
  var badge = app.freshnessBadge(daysAgoIso(3));
  assert.strictEqual(badge.cls, "freshness-recent");
});

test("freshnessBadge: 8-30 days is 'month'", function () {
  var badge = app.freshnessBadge(daysAgoIso(15));
  assert.strictEqual(badge.cls, "freshness-month");
});

test("freshnessBadge: over 30 days is 'stale'", function () {
  var badge = app.freshnessBadge(daysAgoIso(45));
  assert.strictEqual(badge.cls, "freshness-stale");
});

test("freshnessBadge: exactly 7 days is still 'recent' (boundary)", function () {
  var badge = app.freshnessBadge(daysAgoIso(7));
  assert.strictEqual(badge.cls, "freshness-recent");
});

test("freshnessBadge: exactly 30 days is still 'month' (boundary)", function () {
  var badge = app.freshnessBadge(daysAgoIso(30));
  assert.strictEqual(badge.cls, "freshness-month");
});

console.log(passed + " passed, " + failures + " failed");
process.exit(failures > 0 ? 1 : 0);
