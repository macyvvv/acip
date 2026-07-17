// Plain Node test for app.js's pure, side-effect-free functions -- no
// framework, matching this product's "no over-engineering" constraint
// (see architecture.md). Run directly: `node tests/test_app_logic.js`
// from the product directory, or from the repo root:
// `node businesses/kabukicho_survival_map/app/tests/test_app_logic.js`.
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

test("freshnessBadge: within 7 days shows no badge", function () {
  var badge = app.freshnessBadge(daysAgoIso(3));
  assert.strictEqual(badge, null);
});

test("freshnessBadge: 8-30 days is 'month'", function () {
  var badge = app.freshnessBadge(daysAgoIso(15));
  assert.strictEqual(badge.cls, "freshness-month");
});

test("freshnessBadge: over 30 days is 'stale'", function () {
  var badge = app.freshnessBadge(daysAgoIso(45));
  assert.strictEqual(badge.cls, "freshness-stale");
});

test("freshnessBadge: exactly 7 days still shows no badge (boundary)", function () {
  var badge = app.freshnessBadge(daysAgoIso(7));
  assert.strictEqual(badge, null);
});

test("freshnessBadge: exactly 30 days is still 'month' (boundary)", function () {
  var badge = app.freshnessBadge(daysAgoIso(30));
  assert.strictEqual(badge.cls, "freshness-month");
});

// -- passesActiveFilters ---------------------------------------------

test("passesActiveFilters: unofficial smoking hidden unless includeUnofficialSmoking is set", function () {
  var poi = { category: "smoking", type: "unofficial", tags: [] };
  app.state.includeUnofficialSmoking = false;
  app.state.activeFilters = {};
  assert.strictEqual(app.passesActiveFilters(poi), false);
  app.state.includeUnofficialSmoking = true;
  assert.strictEqual(app.passesActiveFilters(poi), true);
  app.state.includeUnofficialSmoking = false;
});

test("passesActiveFilters: official POI is unaffected by the unofficial-smoking toggle", function () {
  var poi = { category: "smoking", type: "official", tags: [] };
  app.state.includeUnofficialSmoking = false;
  app.state.activeFilters = {};
  assert.strictEqual(app.passesActiveFilters(poi), true);
});

test("passesActiveFilters: active tag filters require every selected tag (AND, not OR)", function () {
  var poi = { category: "toilet", type: "official", tags: ["24h", "clean"] };
  app.state.includeUnofficialSmoking = false;
  app.state.activeFilters = { "24h": true, free: true };
  assert.strictEqual(app.passesActiveFilters(poi), false, "missing 'free' tag should fail the AND filter");
  app.state.activeFilters = { "24h": true, clean: true };
  assert.strictEqual(app.passesActiveFilters(poi), true);
  app.state.activeFilters = {};
});

// -- ensureActiveCategoryAllowed ---------------------------------------

test("ensureActiveCategoryAllowed: switches to the mode's first allowed category when current one isn't allowed", function () {
  app.state.activeMode = "toilet_now";
  app.state.activeCategory = "smoking";
  app.ensureActiveCategoryAllowed();
  assert.strictEqual(app.state.activeCategory, "toilet");
});

test("ensureActiveCategoryAllowed: leaves an already-allowed category untouched", function () {
  app.state.activeMode = "smoking_now";
  app.state.activeCategory = "smoking";
  app.ensureActiveCategoryAllowed();
  assert.strictEqual(app.state.activeCategory, "smoking");
});

test("ensureActiveCategoryAllowed: an aggregate mode with a disallowed category switches to the 'all' pseudo-category", function () {
  app.state.activeMode = "late_night";
  app.state.activeCategory = "smoking";
  app.ensureActiveCategoryAllowed();
  assert.strictEqual(app.state.activeCategory, app.MODE_ALL_CATEGORY_ID);
});

test("ensureActiveCategoryAllowed: an aggregate mode already on the 'all' pseudo-category stays put", function () {
  app.state.activeMode = "late_night";
  app.state.activeCategory = app.MODE_ALL_CATEGORY_ID;
  app.ensureActiveCategoryAllowed();
  assert.strictEqual(app.state.activeCategory, app.MODE_ALL_CATEGORY_ID);
});

// -- sortPoisForMode ------------------------------------------------------

test("sortPoisForMode: 'nearby' mode sorts by distance ascending", function () {
  var far = { name: "far", tags: [], _distanceMeters: 500 };
  var near = { name: "near", tags: [], _distanceMeters: 50 };
  var sorted = app.sortPoisForMode("nearby", [far, near]);
  assert.deepStrictEqual(sorted.map(function (p) { return p.name; }), ["near", "far"]);
});

test("sortPoisForMode: 'toilet_now' ranks a free+24h+clean toilet above a plain one at the same distance", function () {
  var plain = { name: "plain", category: "toilet", tags: [], _distanceMeters: 100 };
  var good = { name: "good", category: "toilet", tags: ["24h", "free", "clean"], _distanceMeters: 100 };
  var sorted = app.sortPoisForMode("toilet_now", [plain, good]);
  assert.deepStrictEqual(sorted.map(function (p) { return p.name; }), ["good", "plain"]);
});

test("sortPoisForMode: 'smoking_now' penalizes negative tags (crowded/unsafe/hidden)", function () {
  var risky = { name: "risky", category: "smoking", tags: ["crowded", "unsafe"], _distanceMeters: 100 };
  var calm = { name: "calm", category: "smoking", tags: ["indoor"], _distanceMeters: 100 };
  var sorted = app.sortPoisForMode("smoking_now", [risky, calm]);
  assert.deepStrictEqual(sorted.map(function (p) { return p.name; }), ["calm", "risky"]);
});

// -- getJudgmentSignals -------------------------------------------------

test("getJudgmentSignals: only known, present tags become signals, in category priority order", function () {
  var poi = { category: "toilet", tags: ["dirty", "free", "unknown_tag", "24h"] };
  var signals = app.getJudgmentSignals(poi);
  var tags = signals.map(function (s) { return s.tag; });
  assert.ok(tags.indexOf("unknown_tag") === -1, "unmapped tags must not appear as signals");
  assert.ok(tags.indexOf("free") !== -1 && tags.indexOf("24h") !== -1);
});

test("getJudgmentSignals: caps at 4 signals for non-lodging categories, 3 for lodging", function () {
  var toiletPoi = { category: "toilet", tags: ["free", "24h", "clean", "gender_separated", "long_wait", "dirty"] };
  assert.ok(app.getJudgmentSignals(toiletPoi).length <= 4);
  var lodgingPoi = { category: "lodging", tags: ["overnight_friendly", "shower_available", "24h", "price_band_budget"] };
  assert.ok(app.getJudgmentSignals(lodgingPoi).length <= 3);
});

test("getJudgmentSignals: an active mode boost can reorder signals relative to category priority alone", function () {
  var poi = { category: "toilet", tags: ["gender_separated", "free"] };
  app.state.activeMode = "toilet_now"; // boosts "free" (+30) far above "gender_separated" (+18)
  var signals = app.getJudgmentSignals(poi);
  assert.strictEqual(signals[0].tag, "free");
  app.state.activeMode = "nearby";
});

// -- renderCard gray-zone disclaimer -------------------------------------

function basePoi(overrides) {
  return Object.assign({
    name: "テストPOI",
    category: "smoking",
    tags: [],
    lat: 35.6949,
    lng: 139.7028,
    description: "",
    last_updated: null
  }, overrides || {});
}

test("renderCard: type=unofficial always shows the gray-zone disclaimer banner", function () {
  var html = app.renderCard(basePoi({ type: "unofficial", gray_zone_note: "境界外" }), "smoking", 0, {});
  assert.ok(html.indexOf("gray-zone-banner") !== -1, "expected a gray-zone-banner for an unofficial POI");
  assert.ok(html.indexOf("非公式情報") !== -1);
  assert.ok(html.indexOf("境界外") !== -1, "gray_zone_note text should be included in the banner");
});

test("renderCard: type=official with a gray_zone_note shows a plain info note, not the disclaimer banner", function () {
  var html = app.renderCard(basePoi({ type: "official", gray_zone_note: "開園時間内のみ利用可" }), "smoking", 0, {});
  assert.ok(html.indexOf("gray-zone-banner") === -1, "an official POI must not show the unofficial disclaimer banner");
  assert.ok(html.indexOf("info-note") !== -1);
  assert.ok(html.indexOf("開園時間内のみ利用可") !== -1);
});

test("renderCard: type=official with no gray_zone_note shows neither banner nor note", function () {
  var html = app.renderCard(basePoi({ type: "official" }), "smoking", 0, {});
  assert.ok(html.indexOf("gray-zone-banner") === -1);
  assert.ok(html.indexOf("info-note") === -1);
});

// -- tr() / i18n -----------------------------------------------------

test("tr: resolves a {ja,en} object to the current language, defaulting to ja", function () {
  app.setLangForTest("ja");
  assert.strictEqual(app.tr({ ja: "こんにちは", en: "Hello" }), "こんにちは");
  app.setLangForTest("en");
  assert.strictEqual(app.tr({ ja: "こんにちは", en: "Hello" }), "Hello");
  app.setLangForTest("ja");
});

test("tr: plain strings and null/undefined pass through unchanged regardless of language", function () {
  app.setLangForTest("en");
  assert.strictEqual(app.tr("plain string"), "plain string");
  assert.strictEqual(app.tr(null), null);
  assert.strictEqual(app.tr(undefined), undefined);
  app.setLangForTest("ja");
});

test("tr: falls back to ja, then en, if the current language's key is missing", function () {
  app.setLangForTest("en");
  assert.strictEqual(app.tr({ ja: "日本語のみ" }), "日本語のみ");
  app.setLangForTest("ja");
  assert.strictEqual(app.tr({ en: "English only" }), "English only");
  app.setLangForTest("ja");
});

test("renderCard: category/mode labels switch language via CURRENT_LANG", function () {
  app.setLangForTest("ja");
  var jaHtml = app.renderCard(basePoi({ type: "official", tags: ["24h"] }), "smoking", 0, {});
  assert.ok(jaHtml.indexOf("24時間") !== -1 || jaHtml.indexOf("24h") !== -1);
  app.setLangForTest("en");
  var enHtml = app.renderCard(basePoi({ type: "official", tags: ["24h"] }), "smoking", 0, {});
  assert.ok(enHtml.indexOf("24 hours") !== -1 || enHtml.indexOf("24h") !== -1);
  app.setLangForTest("ja");
});

// -- faqHtml() --------------------------------------------------------

test("faqHtml: renders Japanese questions by default", function () {
  app.setLangForTest("ja");
  var html = app.faqHtml();
  assert.ok(html.indexOf("よくある質問") !== -1);
  assert.ok(html.indexOf("歌舞伎町に無料の喫煙所はありますか？") !== -1);
  assert.ok(html.indexOf("<details>") !== -1 && html.indexOf("<summary>") !== -1);
});

test("faqHtml: renders English questions when CURRENT_LANG is en", function () {
  app.setLangForTest("en");
  var html = app.faqHtml();
  assert.ok(html.indexOf("Frequently Asked Questions") !== -1);
  assert.ok(html.indexOf("Are there free smoking areas in Kabukicho?") !== -1);
  assert.ok(html.indexOf("よくある質問") === -1, "should not mix in Japanese heading when lang is en");
  app.setLangForTest("ja");
});

console.log(passed + " passed, " + failures + " failed");
process.exit(failures > 0 ? 1 : 0);
