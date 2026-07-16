(function () {
  "use strict";

  // Category order matches doc_creation/task-0001-seo-copy's recommended
  // sort: by frequency/urgency, not alphabetically.
  var CATEGORIES = [
    { id: "toilet", file: "toilet.json", label: "トイレ", icon: "🚻", subtitle: "Public restrooms" },
    { id: "smoking", file: "smoking.json", label: "喫煙所", icon: "🚬", subtitle: "Designated smoking zones" },
    { id: "convenience", file: "convenience.json", label: "コンビニ", icon: "🏪", subtitle: "24/7 services" },
    { id: "atm", file: "atm.json", label: "ATM・両替", icon: "💳", subtitle: "Cash withdrawal & exchange" },
    { id: "coin_locker", file: "coin_locker.json", label: "コインロッカー", icon: "🧳", subtitle: "Luggage storage" },
    { id: "lodging", file: "lodging.json", label: "宿泊・ネット", icon: "🏨", subtitle: "Overnight & day-use facilities" }
  ];

  var MODES = [
    {
      id: "nearby",
      label: "近くで探す",
      copy: "カテゴリ別に通常探索",
      targetCategories: CATEGORIES.map(function (cat) { return cat.id; }),
      aggregateCategories: false,
      preferredTags: [],
      negativeTags: [],
      categoryBoosts: {},
      sortStrategy: ["distance", "freshness"],
      emptyStateMessage: null,
      summary: "現在地に近い順を基本に、カテゴリごとに通常の地図探索ができます。"
    },
    {
      id: "toilet_now",
      label: "トイレ急ぎ",
      copy: "近くて使いやすい順",
      targetCategories: ["toilet"],
      aggregateCategories: false,
      preferredTags: ["24h", "free", "clean", "gender_separated"],
      negativeTags: ["dirty", "long_wait"],
      categoryBoosts: { toilet: 4 },
      sortStrategy: ["distance", "modeScore", "freshness"],
      emptyStateMessage: "近くで使いやすいトイレが見つかりませんでした。通常のトイレ一覧に切り替えて探してください。",
      summary: "いま一番早く使えそうなトイレを、距離と使いやすさで優先表示します。"
    },
    {
      id: "late_night",
      label: "朝まで過ごす",
      copy: "終電後の避難導線",
      targetCategories: ["lodging", "convenience", "toilet", "atm", "coin_locker"],
      aggregateCategories: true,
      preferredTags: ["24h", "overnight_friendly", "shower_available", "suitcase_ok", "large"],
      negativeTags: [],
      categoryBoosts: { lodging: 5, convenience: 2, toilet: 1, atm: 1, coin_locker: 1 },
      sortStrategy: ["distance", "modeScore", "freshness", "reliability"],
      emptyStateMessage: "朝まで向きの候補が見つかりませんでした。宿泊・ネットかコンビニを個別に確認してください。",
      summary: "終電後に必要な宿泊・休憩・現金・荷物導線をまとめて、朝までしのげる候補を優先します。"
    },
    {
      id: "smoking_now",
      label: "今吸える場所",
      copy: "使いやすさ優先",
      targetCategories: ["smoking"],
      aggregateCategories: false,
      preferredTags: ["indoor", "24h", "rain_ok"],
      negativeTags: ["crowded", "hidden", "unsafe"],
      categoryBoosts: { smoking: 4 },
      sortStrategy: ["distance", "modeScore", "freshness", "reliability"],
      emptyStateMessage: "近くで使いやすい喫煙所が見つかりませんでした。通常の喫煙所一覧で候補を広げてください。",
      summary: "近さに加えて、屋内・24時間・混雑しにくさを加味して、現実的に使える喫煙所を優先します。"
    }
  ];

  // Tag copy templates, from scenario_writing/task-0001 -- one line per tag,
  // <=50 chars, meant to render as a single-line chip caption.
  var TAG_COPY = {
    smoking: {
      indoor: "屋内",
      outdoor: "屋外",
      rain_ok: "雨OK",
      crowded: "混雑",
      hidden: "見つけにくい",
      unsafe: "注意",
      "24h": "24h"
    },
    toilet: {
      clean: "清潔",
      dirty: "汚れ",
      free: "無料",
      long_wait: "待ち",
      gender_separated: "男女別",
      "24h": "24h"
    },
    coin_locker: {
      small: "小型",
      medium: "中型",
      large: "大型",
      suitcase_ok: "スーツケース可",
      suitcase_too_big: "大型不可",
      "24h": "24h"
    },
    lodging: {
      shower_available: "シャワーあり",
      no_shower: "シャワーなし",
      price_band_budget: "予算",
      price_band_mid: "標準",
      price_band_high: "高価格",
      "24h": "24h",
      overnight_friendly: "深夜対応"
    },
    convenience: { "24h": "24h", atm_instore: "ATM併設", phone_charging: "充電可" },
    atm: { "24h": "24h", international_card_ok: "海外カード" }
  };

  var NON_FILTER_TAG_IDS = {
    dirty: true,
    long_wait: true,
    hidden: true,
    unsafe: true
  };

  var NONE_FILTER_TAG_ID = "__none__";

  var DISCLAIMER_JA = "⚠ 非公式情報・内容は変更される場合があります・ご利用は自己責任でお願いします";
  var DISCLAIMER_EN = "⚠ Unofficial Information / Subject to change / Use at your own risk";

  // Kabukicho's approximate centroid -- used as the map's default center
  // before (or in place of) a real geolocation fix.
  var KABUKICHO_CENTER = { lat: 35.6949, lng: 139.7028 };
  var REFINED_POSITION_CACHE_KEY = "kabukicho_refined_positions_v2";
  var MAX_ACCEPTABLE_GEOCODE_DRIFT_METERS = 600;
  var ENABLE_RUNTIME_REFINEMENT = false;

  var state = {
    activeMode: MODES[0].id,
    activeCategory: CATEGORIES[0].id,
    data: {},
    map: null,
    markers: [],
    infoWindow: null,
    userLocation: null,
    userMarker: null,
    locationStatus: "idle", // idle | requesting | granted | denied | unsupported
    // categoryId -> true when its data/*.json fetch failed (network error
    // or non-2xx response). Kept separate from state.data so a failed
    // load can be shown as an error, not silently rendered as "0 results
    // in this category."
    loadFailed: {},
    // Tag ids currently toggled on, e.g. {shower_available: true}. A POI
    // must carry every active tag (AND, not OR) to survive the filter --
    // each additional toggle narrows the list further, matching how a
    // "narrow down" filter is normally expected to behave. Reset on every
    // category switch since each category's tag vocabulary is different
    // (TAG_COPY[categoryId]); carrying a filter across categories would
    // silently no-op or, worse, coincidentally match an unrelated tag.
    activeFilters: {},
    expandedCardKey: null,
    controlsOpen: false,
    focusedPoiKey: null,
    mapFailureReason: "loading",
    geocoder: null,
    refinedPositions: {},
    skippedRefinements: {},
    refineInFlight: false,
    refineQueue: []
  };

  var MODE_ALL_CATEGORY_ID = "__mode_all__";

  function getModeDefinition(modeId) {
    return MODES.find(function (mode) { return mode.id === modeId; }) || MODES[0];
  }

  function getCategoryDefinition(categoryId) {
    return CATEGORIES.find(function (cat) { return cat.id === categoryId; }) || null;
  }

  function getAllowedCategories() {
    return getModeDefinition(state.activeMode).targetCategories;
  }

  function ensureActiveCategoryAllowed() {
    var allowed = getAllowedCategories();
    var mode = getModeDefinition(state.activeMode);
    if (mode.aggregateCategories && state.activeCategory === MODE_ALL_CATEGORY_ID) return;
    if (allowed.indexOf(state.activeCategory) === -1) {
      state.activeCategory = mode.aggregateCategories ? MODE_ALL_CATEGORY_ID : allowed[0];
    }
  }

  function getModePois() {
    var mode = getModeDefinition(state.activeMode);
    if (!mode.aggregateCategories || state.activeCategory !== MODE_ALL_CATEGORY_ID) {
      return getFilteredPois(state.activeCategory);
    }
    var merged = [];
    mode.targetCategories.forEach(function (categoryId) {
      var pois = state.data[categoryId] || [];
      pois.forEach(function (poi) {
        if (passesActiveFilters(poi)) merged.push(poi);
      });
    });
    return merged;
  }

  function passesActiveFilters(poi) {
    var activeTags = Object.keys(state.activeFilters).filter(function (t) { return state.activeFilters[t]; });
    if (!activeTags.length) return true;
    var tags = poi.tags || [];
    return activeTags.every(function (t) { return tags.indexOf(t) !== -1; });
  }

  function getFilteredPois(categoryId) {
    var pois = state.data[categoryId] || [];
    return pois.filter(passesActiveFilters);
  }

  function getPoiKey(poi) {
    return [poi.category, poi.name, poi.lat, poi.lng].join("::");
  }

  function isMobileViewport() {
    return typeof window !== "undefined" && window.matchMedia("(max-width: 1023px)").matches;
  }

  function mapDefaultZoom() {
    return isMobileViewport() ? 15 : 16;
  }

  function mapSinglePoiZoom() {
    return isMobileViewport() ? 16 : 17;
  }

  function mapFitBoundsPadding() {
    return isMobileViewport() ? 24 : 48;
  }

  function syncDesktopControlsInlineState() {
    if (typeof document === "undefined") return;
    var panel = document.getElementById("control-panel");
    var overlay = document.getElementById("controls-panel-overlay");
    if (!panel) return;

    if (isMobileViewport()) {
      panel.style.removeProperty("max-height");
      panel.style.removeProperty("opacity");
      panel.style.removeProperty("pointer-events");
      panel.style.removeProperty("transform");
      if (overlay) {
        overlay.style.removeProperty("max-height");
        overlay.style.removeProperty("overflow");
      }
      return;
    }

    var overlayMaxByMode = {
      nearby: "72dvh",
      toilet_now: "76dvh",
      smoking_now: "76dvh",
      late_night: "80dvh"
    };

    panel.style.setProperty("transform", "translateY(0)");
    panel.style.setProperty("opacity", "1");
    panel.style.setProperty("pointer-events", "auto", "important");
    panel.style.setProperty("max-height", "84px", "important");

    if (overlay) {
      var overlayMax = overlayMaxByMode[state.activeMode] || "74dvh";
      overlay.style.setProperty("max-height", overlayMax, "important");
      overlay.style.setProperty("overflow", "visible", "important");
    }
  }

  function setControlsOpen(open) {
    state.controlsOpen = !!open;
    if (typeof document === "undefined") return;

    document.body.classList.toggle("controls-open", state.controlsOpen);

    var backdrop = document.getElementById("controls-backdrop");
    if (backdrop) backdrop.hidden = !state.controlsOpen;

    ["controls-toggle", "reopen-controls"].forEach(function (id) {
      var button = document.getElementById(id);
      if (button) button.setAttribute("aria-expanded", state.controlsOpen ? "true" : "false");
    });

    var close = document.getElementById("controls-close");
    if (close) {
      var label = state.controlsOpen ? "閉じる" : "開く";
      close.textContent = label;
      close.setAttribute("aria-label", "条件パネルを" + label);
    }

    syncDesktopControlsInlineState();
  }

  function closeControlsOnMobile() {
    if (isMobileViewport()) setControlsOpen(false);
  }

  function applyFilterSelection() {
    renderFilterBar();
    renderList();
    renderMarkers();
    setControlsOpen(false);
  }

  function clearExpandedCardIfMissing(pois) {
    if (!state.expandedCardKey) return;
    var stillVisible = pois.some(function (poi) { return getPoiKey(poi) === state.expandedCardKey; });
    if (!stillVisible) state.expandedCardKey = null;
  }

  function getAggregateLoadFailures(mode) {
    if (!mode.aggregateCategories || state.activeCategory !== MODE_ALL_CATEGORY_ID) return [];
    return mode.targetCategories.filter(function (categoryId) { return state.loadFailed[categoryId]; });
  }

  function getVisibleCountLabel(pois, totalInCategory) {
    if (!pois.length) return "0件";
    if (Object.keys(state.activeFilters).some(function (t) { return state.activeFilters[t]; })) {
      return pois.length + " / " + totalInCategory + "件";
    }
    return pois.length + "件";
  }

  function hasActiveFilterSelections() {
    return Object.keys(state.activeFilters).some(function (t) { return state.activeFilters[t]; });
  }

  function getCurrentVisiblePois() {
    ensureActiveCategoryAllowed();
    return sortPoisForMode(state.activeMode, sortedByDistance(getModePois()));
  }

  function haversineDistanceMeters(lat1, lng1, lat2, lng2) {
    var R = 6371000;
    var toRad = function (deg) { return (deg * Math.PI) / 180; };
    var dLat = toRad(lat2 - lat1);
    var dLng = toRad(lng2 - lng1);
    var a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
  }

  function toFiniteNumber(value) {
    var n = typeof value === "number" ? value : Number(value);
    return Number.isFinite(n) ? n : null;
  }

  function rawPoiPosition(poi) {
    var lat = toFiniteNumber(poi && poi.lat);
    var lng = toFiniteNumber(poi && poi.lng);
    if (lat === null || lng === null) return null;
    return { lat: lat, lng: lng };
  }

  function refinedPoiPosition(poi) {
    var key = getPoiKey(poi);
    if (state.refinedPositions[key]) return state.refinedPositions[key];
    return rawPoiPosition(poi);
  }

  function formatDistance(meters) {
    if (meters < 1000) return Math.round(meters) + "m";
    return (meters / 1000).toFixed(1) + "km";
  }

  function sortedByDistance(pois) {
    if (!state.userLocation) return pois;
    var withDistance = pois.map(function (poi) {
      var position = refinedPoiPosition(poi);
      if (!position) {
        return { poi: poi, distance: Number.POSITIVE_INFINITY };
      }
      return {
        poi: poi,
        distance: haversineDistanceMeters(state.userLocation.lat, state.userLocation.lng, position.lat, position.lng)
      };
    });
    withDistance.sort(function (a, b) { return a.distance - b.distance; });
    return withDistance.map(function (entry) {
      entry.poi._distanceMeters = entry.distance;
      return entry.poi;
    });
  }

  function freshnessBadge(lastUpdated) {
    if (!lastUpdated) return null;
    var updated = new Date(lastUpdated);
    var now = new Date();
    var days = Math.floor((now - updated) / (1000 * 60 * 60 * 24));
    if (days <= 7) return { cls: "freshness-recent", text: "✓ 最近更新されました" };
    if (days <= 30) return { cls: "freshness-month", text: "✓✓ 1ヶ月以内に確認" };
    return { cls: "freshness-stale", text: "⚠ 情報が古い可能性あり" };
  }

  function freshnessWeight(lastUpdated) {
    var fresh = freshnessBadge(lastUpdated);
    if (!fresh) return 0;
    if (fresh.cls === "freshness-recent") return 3;
    if (fresh.cls === "freshness-month") return 2;
    return 1;
  }

  function mapsUrl(lat, lng) {
    return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(lat + "," + lng);
  }

  function getAllPoisFlat() {
    var all = [];
    CATEGORIES.forEach(function (cat) {
      var list = state.data[cat.id] || [];
      list.forEach(function (poi) { all.push(poi); });
    });
    return all;
  }

  function loadRefinedPositionCache() {
    if (typeof window === "undefined" || !window.localStorage) return;
    try {
      var raw = window.localStorage.getItem(REFINED_POSITION_CACHE_KEY);
      if (!raw) return;
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object") return;
      Object.keys(parsed).forEach(function (key) {
        var item = parsed[key] || {};
        var lat = toFiniteNumber(item.lat);
        var lng = toFiniteNumber(item.lng);
        if (lat === null || lng === null) return;
        state.refinedPositions[key] = { lat: lat, lng: lng };
      });
    } catch (error) {
      // Ignore invalid cache contents.
    }
  }

  function saveRefinedPositionCache() {
    if (typeof window === "undefined" || !window.localStorage) return;
    try {
      window.localStorage.setItem(REFINED_POSITION_CACHE_KEY, JSON.stringify(state.refinedPositions));
    } catch (error) {
      // Storage can fail in private mode or quota pressure.
    }
  }

  function scoreLocationType(type) {
    if (type === "ROOFTOP") return 120;
    if (type === "RANGE_INTERPOLATED") return 80;
    if (type === "GEOMETRIC_CENTER") return 40;
    return 10;
  }

  function extractAddressHints(poi) {
    var hints = [];
    var body = [poi.name || "", poi.description || "", poi.gray_zone_note || ""].join(" ");
    var regex = /(?:東京都)?新宿区[^。\n,、]{0,40}\d{1,3}-\d{1,3}(?:-\d{1,3})?/g;
    var match;
    while ((match = regex.exec(body)) !== null) {
      var hint = (match[0] || "").trim();
      if (hint && hints.indexOf(hint) === -1) hints.push(hint);
    }
    return hints;
  }

  function buildGeocodeQueries(poi) {
    var queries = [];
    var hints = extractAddressHints(poi);
    hints.forEach(function (hint) {
      queries.push((poi.name || "") + " " + hint);
      queries.push(hint);
    });
    queries.push((poi.name || "") + " 東京都新宿区歌舞伎町");
    queries.push((poi.name || "") + " 新宿");
    queries.push((poi.name || "") + " Kabukicho");

    return queries
      .map(function (q) { return q.replace(/\s+/g, " ").trim(); })
      .filter(function (q, idx, arr) { return q && arr.indexOf(q) === idx; })
      .slice(0, 5);
  }

  function scoreGeocodeResult(result, original) {
    if (!result || !result.geometry || !result.geometry.location) return null;
    var pos = {
      lat: result.geometry.location.lat(),
      lng: result.geometry.location.lng()
    };
    var drift = haversineDistanceMeters(original.lat, original.lng, pos.lat, pos.lng);
    if (drift > MAX_ACCEPTABLE_GEOCODE_DRIFT_METERS) return null;

    var addr = (result.formatted_address || "") + " " + ((result.address_components || []).map(function (c) {
      return c.long_name || "";
    }).join(" "));
    var inShinjuku = addr.indexOf("新宿") !== -1 || addr.toLowerCase().indexOf("shinjuku") !== -1;

    var score = 1000 - drift;
    score += scoreLocationType(result.geometry.location_type || "");
    if (inShinjuku) score += 90;
    if (result.partial_match) score -= 120;

    return {
      position: pos,
      score: score
    };
  }

  function geocodePoiWithQueries(poi, done) {
    if (!state.geocoder) {
      done(false);
      return;
    }
    var key = getPoiKey(poi);
    var original = rawPoiPosition(poi);
    if (!original) {
      state.skippedRefinements[key] = true;
      done(false);
      return;
    }

    var queries = buildGeocodeQueries(poi);
    var best = null;
    var idx = 0;
    var searchBounds = new google.maps.LatLngBounds(
      { lat: KABUKICHO_CENTER.lat - 0.025, lng: KABUKICHO_CENTER.lng - 0.025 },
      { lat: KABUKICHO_CENTER.lat + 0.025, lng: KABUKICHO_CENTER.lng + 0.025 }
    );

    function runNextQuery() {
      if (idx >= queries.length) {
        if (!best) {
          state.skippedRefinements[key] = true;
          done(false);
          return;
        }
        state.refinedPositions[key] = best.position;
        saveRefinedPositionCache();
        done(true);
        return;
      }

      var q = queries[idx];
      idx += 1;
      state.geocoder.geocode(
        { address: q, region: "JP", bounds: searchBounds },
        function (results, status) {
          if (status === "OK" && results && results.length) {
            results.slice(0, 4).forEach(function (result) {
              var scored = scoreGeocodeResult(result, original);
              if (!scored) return;
              if (!best || scored.score > best.score) best = scored;
            });
          }
          runNextQuery();
        }
      );
    }

    runNextQuery();
  }

  function findPoiByKey(key) {
    var all = getAllPoisFlat();
    for (var i = 0; i < all.length; i += 1) {
      if (getPoiKey(all[i]) === key) return all[i];
    }
    return null;
  }

  function scheduleRefinementQueue() {
    if (!ENABLE_RUNTIME_REFINEMENT) return;
    if (state.refineInFlight || !state.geocoder || !state.refineQueue.length) return;
    var nextKey = state.refineQueue.shift();
    var poi = findPoiByKey(nextKey);
    if (!poi) {
      scheduleRefinementQueue();
      return;
    }

    state.refineInFlight = true;
    geocodePoiWithQueries(poi, function (updated) {
      state.refineInFlight = false;
      if (updated) {
        renderMarkers();
        renderList();
        if (!state.map) renderMapFallback(state.mapFailureReason || "loading");
      }
      if (state.refineQueue.length) {
        setTimeout(function () { scheduleRefinementQueue(); }, 180);
      }
    });
  }

  function enqueueRefinementForPois(pois) {
    if (!ENABLE_RUNTIME_REFINEMENT) return;
    if (!pois || !pois.length) return;
    pois.forEach(function (poi) {
      var key = getPoiKey(poi);
      if (state.refinedPositions[key] || state.skippedRefinements[key]) return;
      if (state.refineQueue.indexOf(key) !== -1) return;
      state.refineQueue.push(key);
    });
    scheduleRefinementQueue();
  }

  function mapsUrlForPoi(poi) {
    var pos = refinedPoiPosition(poi) || rawPoiPosition(poi);
    if (!pos) return "https://www.google.com/maps";
    return mapsUrl(pos.lat, pos.lng);
  }

  // Shared across platform/app/products/* -- see platform/app/shared/dom_escape.js. In the
  // browser it's loaded via a <script> tag before this file (no bundler);
  // in the Node test harness (tests/test_app_logic.js), window is
  // undefined, so require() it directly instead.
  var escapeHtml = (typeof window !== "undefined" && window.AcipDomUtils)
    ? window.AcipDomUtils.escapeHtml
    : require("../../shared/dom_escape.js").escapeHtml;

  function modeSummaryHtml() {
    var mode = getModeDefinition(state.activeMode);
    if (mode.id === "nearby") return "";
    return (
      '<div class="mode-summary">' +
      '<span class="mode-summary-title">' + escapeHtml(mode.label) + '</span>' +
      '<span class="mode-summary-copy">' + escapeHtml(mode.summary) + '</span>' +
      '</div>'
    );
  }

  function scrollListToTop() {
    if (typeof document === "undefined") return;
    var list = document.getElementById("poi-list");
    if (list) list.scrollTop = 0;
  }

  function renderCurrentContext(pois, totalInCategory, aggregateFailures) {
    var containers = [
      document.getElementById("current-context"),
      document.getElementById("current-context-overlay")
    ].filter(function (el) { return !!el; });
    if (!containers.length) return;

    var mode = getModeDefinition(state.activeMode);
    var activeFilterCount = Object.keys(state.activeFilters).filter(function (key) { return state.activeFilters[key]; }).length;
    var categoryLabel;
    if (state.activeCategory === MODE_ALL_CATEGORY_ID) {
      categoryLabel = "まとめ";
    } else {
      var category = getCategoryDefinition(state.activeCategory);
      categoryLabel = category ? category.label : "カテゴリ";
    }

    var pills = [
      '<span class="current-context-pill">' + escapeHtml(mode.label) + '</span>',
      '<span class="current-context-pill">' + escapeHtml(categoryLabel) + '</span>',
      '<span class="current-context-pill">' + escapeHtml(getVisibleCountLabel(pois, totalInCategory)) + '</span>'
    ];
    if (activeFilterCount) pills.push('<span class="current-context-pill">絞り込み ' + activeFilterCount + '</span>');

    var note = aggregateFailures.length
      ? "一部カテゴリの読み込みに失敗しているため、結果は部分表示です。"
      : (mode.id === "nearby"
        ? "必要な施設だけを短く見て、詳細はタップで展開できます。"
        : mode.summary);

    var html =
      '<div class="current-context-head">' + pills.join("") + '</div>' +
      '<p class="current-context-note">' + escapeHtml(note) + '</p>';
    containers.forEach(function (container) {
      container.innerHTML = html;
    });
  }

  function scorePoiForMode(modeId, poi) {
    var mode = getModeDefinition(modeId);
    var tags = poi.tags || [];
    var score = 0;

    if (mode.categoryBoosts && mode.categoryBoosts[poi.category]) {
      score += mode.categoryBoosts[poi.category];
    }

    mode.preferredTags.forEach(function (tag) {
      if (tags.indexOf(tag) !== -1) score += 2;
    });
    mode.negativeTags.forEach(function (tag) {
      if (tags.indexOf(tag) !== -1) score -= 3;
    });

    if (typeof poi.reliability_score === "number") score += poi.reliability_score * 0.15;
    score += freshnessWeight(poi.last_updated) * 0.25;
    return score;
  }

  function sortPoisForMode(modeId, pois) {
    var mode = getModeDefinition(modeId);
    var prepared = pois.map(function (poi) {
      poi._modeScore = scorePoiForMode(modeId, poi);
      return poi;
    });

    prepared.sort(function (a, b) {
      for (var i = 0; i < mode.sortStrategy.length; i += 1) {
        var key = mode.sortStrategy[i];
        if (key === "distance") {
          var aDist = typeof a._distanceMeters === "number" ? a._distanceMeters : Number.POSITIVE_INFINITY;
          var bDist = typeof b._distanceMeters === "number" ? b._distanceMeters : Number.POSITIVE_INFINITY;
          if (aDist !== bDist) return aDist - bDist;
        }
        if (key === "modeScore" && a._modeScore !== b._modeScore) return b._modeScore - a._modeScore;
        if (key === "freshness") {
          var aFresh = freshnessWeight(a.last_updated);
          var bFresh = freshnessWeight(b.last_updated);
          if (aFresh !== bFresh) return bFresh - aFresh;
        }
        if (key === "reliability") {
          var aRel = typeof a.reliability_score === "number" ? a.reliability_score : 0;
          var bRel = typeof b.reliability_score === "number" ? b.reliability_score : 0;
          if (aRel !== bRel) return bRel - aRel;
        }
      }
      return 0;
    });
    return prepared;
  }

  function modePriorityLabel(poi) {
    var modeId = state.activeMode;
    var tags = poi.tags || [];
    if (modeId === "late_night") {
      if (poi.category === "lodging" && tags.indexOf("overnight_friendly") !== -1) return "朝まで滞在向き";
      if (poi.category === "lodging" && tags.indexOf("shower_available") !== -1) return "シャワーあり";
      if (poi.category === "convenience" && tags.indexOf("24h") !== -1) return "24時間の補給拠点";
      if (poi.category === "atm" && tags.indexOf("24h") !== -1) return "深夜の現金確保";
      if (poi.category === "coin_locker" && (tags.indexOf("large") !== -1 || tags.indexOf("suitcase_ok") !== -1)) return "荷物を預けやすい";
      if (poi.category === "toilet" && tags.indexOf("24h") !== -1) return "深夜でも使いやすい";
      return "終電後に役立つ候補";
    }
    if (modeId === "toilet_now") {
      if (tags.indexOf("24h") !== -1 && tags.indexOf("free") !== -1) return "24時間・無料";
      if (tags.indexOf("clean") !== -1) return "清潔寄り";
      return "今使いやすい候補";
    }
    if (modeId === "smoking_now") {
      if (tags.indexOf("indoor") !== -1) return "屋内で使いやすい";
      if (tags.indexOf("24h") !== -1) return "時間を気にしにくい";
      return "喫煙しやすい候補";
    }
    return "";
  }

  function shortDescription(text) {
    if (!text) return "";
    return text.length > 54 ? text.slice(0, 54) + "..." : text;
  }

  function getJudgmentSignals(poi) {
    var tags = poi.tags || [];
    var categoryId = poi.category || state.activeCategory;
    var modeId = state.activeMode;
    var candidates = {
      "24h": { tag: "24h", label: "24時間", tone: "strong", base: 70 },
      free: { tag: "free", label: "無料", tone: "strong", base: 72 },
      clean: { tag: "clean", label: "清潔", tone: "strong", base: 64 },
      gender_separated: { tag: "gender_separated", label: "男女別", tone: "neutral", base: 55 },
      indoor: { tag: "indoor", label: "屋内", tone: "strong", base: 66 },
      rain_ok: { tag: "rain_ok", label: "雨でも可", tone: "neutral", base: 58 },
      overnight_friendly: { tag: "overnight_friendly", label: "朝まで可", tone: "strong", base: 76 },
      shower_available: { tag: "shower_available", label: "シャワー", tone: "strong", base: 73 },
      no_shower: { tag: "no_shower", label: "シャワーなし", tone: "warn", base: 40 },
      suitcase_ok: { tag: "suitcase_ok", label: "スーツケース可", tone: "strong", base: 71 },
      large: { tag: "large", label: "大型対応", tone: "strong", base: 67 },
      medium: { tag: "medium", label: "中型対応", tone: "neutral", base: 48 },
      small: { tag: "small", label: "小型のみ", tone: "neutral", base: 42 },
      suitcase_too_big: { tag: "suitcase_too_big", label: "大型不可", tone: "warn", base: 38 },
      international_card_ok: { tag: "international_card_ok", label: "海外カード", tone: "neutral", base: 62 },
      atm_instore: { tag: "atm_instore", label: "ATMあり", tone: "neutral", base: 54 },
      phone_charging: { tag: "phone_charging", label: "充電可", tone: "neutral", base: 52 },
      price_band_budget: { tag: "price_band_budget", label: "低価格", tone: "strong", base: 68 },
      price_band_mid: { tag: "price_band_mid", label: "標準価格", tone: "neutral", base: 44 },
      price_band_high: { tag: "price_band_high", label: "高価格", tone: "neutral", base: 28 },
      crowded: { tag: "crowded", label: "混雑注意", tone: "warn", base: 46 },
      long_wait: { tag: "long_wait", label: "待ち時間あり", tone: "warn", base: 50 },
      dirty: { tag: "dirty", label: "清潔さ注意", tone: "warn", base: 48 },
      unsafe: { tag: "unsafe", label: "周辺注意", tone: "warn", base: 51 },
      hidden: { tag: "hidden", label: "見つけにくい", tone: "warn", base: 43 },
      outdoor: { tag: "outdoor", label: "屋外", tone: "neutral", base: 36 }
    };
    var categoryPriority = {
      toilet: ["free", "24h", "clean", "gender_separated", "long_wait", "dirty"],
      smoking: ["indoor", "rain_ok", "24h", "crowded", "unsafe", "hidden", "outdoor"],
      convenience: ["24h", "atm_instore", "phone_charging"],
      atm: ["24h", "international_card_ok"],
      coin_locker: ["suitcase_ok", "large", "24h", "medium", "small", "suitcase_too_big"],
      lodging: ["overnight_friendly", "shower_available", "24h", "price_band_budget", "price_band_mid", "price_band_high", "no_shower"]
    };
    var modeBoosts = {
      toilet_now: { free: 30, "24h": 34, clean: 28, gender_separated: 18, long_wait: 8, dirty: 12 },
      smoking_now: { indoor: 34, rain_ok: 28, "24h": 24, crowded: 10, unsafe: 10, hidden: 8 },
      late_night: { overnight_friendly: 34, shower_available: 28, suitcase_ok: 22, large: 20, "24h": 20, price_band_budget: 16 }
    };
    var order = categoryPriority[categoryId] || Object.keys(candidates);
    var boosts = modeBoosts[modeId] || {};

    return order
      .filter(function (tag) { return tags.indexOf(tag) !== -1 && candidates[tag]; })
      .map(function (tag, index) {
        var signal = candidates[tag];
        return {
          tag: signal.tag,
          label: signal.label,
          tone: signal.tone,
          score: signal.base + (boosts[tag] || 0) - index * 0.1
        };
      })
      .sort(function (a, b) { return b.score - a.score; })
      .slice(0, categoryId === "lodging" ? 3 : 4)
      .map(function (signal) {
        return { tag: signal.tag, label: signal.label, tone: signal.tone };
      });
  }

  function renderCard(poi, categoryId, index, options) {
    options = options || {};
    // type="unofficial" is the actual gray-zone/disclaimer signal -- the
    // full "⚠ Unofficial Information" banner is reserved for that. A
    // gray_zone_note on an official entry is ordinary supplementary info
    // (hours limits, boundary notes, licensing nuance -- several
    // official love-hotel entries' own notes explicitly say "not a
    // gray-zone business"), not a warning, so it renders as a plain note
    // instead of the disclaimer banner. Was previously conflated
    // (isGrayZone = type==="unofficial" || !!gray_zone_note), which put
    // the "unofficial, use at your own risk" banner on licensed
    // businesses whose own note text said the opposite.
    var isGrayZone = poi.type === "unofficial";
    var tagCopy = TAG_COPY[categoryId] || {};
    var judgmentSignals = getJudgmentSignals(poi);
    var quickTagsHtml = judgmentSignals
      .map(function (signal) {
        return '<span class="signal-chip signal-chip-' + signal.tone + '">' + escapeHtml(signal.label) + "</span>";
      })
      .join("");
    var freshHtml = "";
    var distanceHtml =
      typeof poi._distanceMeters === "number"
        ? '<span class="distance-badge">📍 現在地から ' + formatDistance(poi._distanceMeters) + "</span>"
        : "";
    var mode = getModeDefinition(state.activeMode);
    var modeBadgeHtml = mode.id !== "nearby"
      ? '<span class="mode-badge">' + escapeHtml(mode.label) + "</span>"
      : "";
    var category = getCategoryDefinition(poi.category || categoryId);
    var categoryBadgeHtml =
      mode.aggregateCategories && state.activeCategory === MODE_ALL_CATEGORY_ID && category
        ? '<span class="mode-badge">' + escapeHtml(category.icon + " " + category.label) + "</span>"
        : "";
    // reliability_score (1-5) is collected for every entry but was never
    // surfaced -- only flag the low end (<=2, ~8 of ~90 entries) rather
    // than showing a score on every card, matching how freshness/
    // gray-zone info only appears when there's actually something to
    // flag instead of cluttering every card with a routine "OK" signal.
    var lowReliabilityHtml =
      typeof poi.reliability_score === "number" && poi.reliability_score <= 2
        ? '<span class="reliability-badge">ℹ️ 情報の確度: 参考程度</span>'
        : "";
    var priorityLabel = modePriorityLabel(poi);
    var priorityHtml = priorityLabel
      ? '<div class="priority-line">' + escapeHtml(priorityLabel) + "</div>"
      : "";
    var featuredLabelHtml = options.featured
      ? '<div class="featured-kicker">この条件で最初に見る候補</div>'
      : "";
    var grayZoneHtml = isGrayZone
      ? '<div class="gray-zone-banner">' + DISCLAIMER_JA + "<br>" + DISCLAIMER_EN +
        (poi.gray_zone_note ? "<br>" + escapeHtml(poi.gray_zone_note) : "") + "</div>"
      : (poi.gray_zone_note ? '<div class="info-note">' + escapeHtml(poi.gray_zone_note) + "</div>" : "");
    var poiKey = getPoiKey(poi);
    var expanded = state.expandedCardKey === poiKey;
    var summaryLine = shortDescription(poi.description);
    var signalTagMap = {};
    judgmentSignals.forEach(function (signal) { signalTagMap[signal.tag] = true; });
    var detailTagsHtml = (poi.tags || [])
      .filter(function (tag) { return !signalTagMap[tag]; })
      .map(function (tag) {
        var caption = tagCopy[tag] || tag;
        return '<span class="tag-chip">' + escapeHtml(caption) + "</span>";
      })
      .join("");
    var collapsedMetaHtml = quickTagsHtml + freshHtml + lowReliabilityHtml;
    if (mode.aggregateCategories && state.activeCategory === MODE_ALL_CATEGORY_ID && categoryBadgeHtml) {
      collapsedMetaHtml += categoryBadgeHtml;
    }
    var supportingHtml = collapsedMetaHtml
      ? '<div class="poi-card-quick-tags">' + collapsedMetaHtml + '</div>'
      : '<p class="poi-card-supporting">' + escapeHtml(summaryLine) + '</p>';
    var detailMetaHtml = modeBadgeHtml + categoryBadgeHtml;

    return (
      '<article class="poi-card' + (options.featured ? ' poi-card-featured' : '') + '" data-poi-index="' + index + '" data-expanded="' + (expanded ? "true" : "false") + '">' +
      '<button class="poi-card-head" type="button" data-card-toggle="' + escapeHtml(poiKey) + '" aria-expanded="' + (expanded ? "true" : "false") + '">' +
      '<div class="poi-card-main">' +
      '<div class="poi-card-topline">' + featuredLabelHtml + priorityHtml + '</div>' +
      "<h2>" + escapeHtml(poi.name) + "</h2>" +
      supportingHtml +
      '</div>' +
      '<div class="poi-card-side">' + distanceHtml + '<span class="poi-card-toggle-text">' + (expanded ? '閉じる' : '詳細') + '</span><span class="poi-card-chevron">⌄</span></div>' +
      '</button>' +
      '<div class="poi-card-detail"' + (expanded ? '' : ' hidden') + '>' +
      (detailMetaHtml ? '<div class="card-meta-row">' + detailMetaHtml + '</div>' : '') +
      grayZoneHtml +
      '<p class="description">' + escapeHtml(poi.description) + "</p>" +
      (detailTagsHtml ? '<div class="tag-row">' + detailTagsHtml + '</div>' : '') +
      '</div>' +
      "</article>"
    );
  }

  function bindCardInteractions(container, pois) {
    Array.prototype.forEach.call(container.querySelectorAll("[data-card-toggle]"), function (button) {
      button.addEventListener("click", function () {
        var poiKey = button.getAttribute("data-card-toggle");
        var nextExpanded = state.expandedCardKey === poiKey ? null : poiKey;
        var targetPoi = pois.find(function (poi) { return getPoiKey(poi) === poiKey; });
        if (targetPoi) focusMarker(targetPoi);
        state.expandedCardKey = nextExpanded;
        renderList();
      });
    });
  }

  function inlineSponsoredHtml(index) {
    var slotNum = Math.floor(index / 5) + 1;
    var title;
    var copy;
    if (state.activeMode === "late_night") {
      title = "終電後サポート提携枠";
      copy = "朝まで利用しやすい宿泊・休憩・荷物預かりサービスの提携先を掲載します。";
    } else if (state.activeMode === "toilet_now") {
      title = "周辺サービス提携枠";
      copy = "移動前後に使いやすい関連サービスの提携先を掲載します。";
    } else if (state.activeMode === "smoking_now") {
      title = "喫煙者向け提携枠";
      copy = "休憩導線に合わせた周辺サービスをこの位置に表示します。";
    } else {
      title = "関連サービス提携枠";
      copy = "一覧閲覧中に邪魔しない位置で、比較検討しやすい提携情報を掲載します。";
    }

    return (
      '<aside class="inline-sponsored-card" aria-label="スポンサー情報 ' + slotNum + '">' +
      '<span class="inline-sponsored-label">SPONSORED</span>' +
      '<strong>' + escapeHtml(title) + '</strong>' +
      '<p>' + escapeHtml(copy) + '</p>' +
      '</aside>'
    );
  }

  function cardsWithInlineSponsored(pois, categoryId, startIndex) {
    var html = "";
    var offset = startIndex || 0;
    pois.forEach(function (poi, localIndex) {
      var absoluteIndex = offset + localIndex;
      html += renderCard(poi, poi.category || categoryId, absoluteIndex);
      if ((localIndex + 1) % 5 === 0 && localIndex < pois.length - 1) {
        html += inlineSponsoredHtml(localIndex);
      }
    });
    return html;
  }

  function locationHintHtml() {
    if (state.locationStatus === "granted") return "";
    if (state.locationStatus === "requesting") {
      return '<div class="location-hint">📡 現在地を取得しています…</div>';
    }
    if (state.locationStatus === "denied" || state.locationStatus === "unsupported") {
      return '<div class="location-hint">📍 現在地が取得できないため、標準の順番で表示しています。</div>';
    }
    return "";
  }

  function renderList() {
    var container = document.getElementById("poi-list");
    ensureActiveCategoryAllowed();
    var mode = getModeDefinition(state.activeMode);
    var aggregateFailures = getAggregateLoadFailures(mode);

    if (state.loadFailed[state.activeCategory]) {
      container.innerHTML =
        '<p class="no-results">⚠ データの読み込みに失敗しました。<br>通信環境をご確認のうえ、ページを再読み込みしてください。</p>';
      renderCurrentContext([], 0, []);
      return;
    }

    var totalInCategory = state.activeCategory === MODE_ALL_CATEGORY_ID
      ? getModeDefinition(state.activeMode).targetCategories.reduce(function (sum, categoryId) {
          return sum + ((state.data[categoryId] || []).filter(passesActiveFilters).length);
        }, 0)
      : (state.data[state.activeCategory] || []).length;
    var pois = sortPoisForMode(state.activeMode, sortedByDistance(getModePois()));
    clearExpandedCardIfMissing(pois);
    var hasActiveFilter = Object.keys(state.activeFilters).some(function (t) { return state.activeFilters[t]; });
    var partialLoadHtml = aggregateFailures.length
      ? '<div class="partial-load-note">⚠ 一部カテゴリを読み込めなかったため、表示結果は完全ではありません。</div>'
      : "";

    renderCurrentContext(pois, totalInCategory, aggregateFailures);

    if (!pois.length) {
      var emptyMessage = hasActiveFilter
        ? '<p class="no-results">選択した条件に該当する場所が見つかりませんでした。<br>絞り込みを解除するか、別の条件をお試しください。</p>'
        : '<p class="no-results">' + escapeHtml(mode.emptyStateMessage || "このカテゴリに該当する場所が見つかりませんでした。別のカテゴリを選択してください。") + '</p>';
      container.innerHTML = modeSummaryHtml() + locationHintHtml() + partialLoadHtml + emptyMessage;
      return;
    }
    var countNoteHtml =
      hasActiveFilter
        ? '<p class="filter-count-note">' + pois.length + " / " + totalInCategory + " 件を表示中</p>"
        : "";
    var cardsHtml;
    if (state.activeMode === "late_night" && state.activeCategory === MODE_ALL_CATEGORY_ID && pois.length > 1) {
      cardsHtml =
        '<section class="featured-result">' + renderCard(pois[0], pois[0].category || state.activeCategory, 0, { featured: true }) + '</section>' +
        '<section class="result-cluster">' +
        '<h3 class="result-cluster-title">他の候補</h3>' +
        cardsWithInlineSponsored(pois.slice(1), state.activeCategory, 1) +
        '</section>';
    } else {
      cardsHtml = cardsWithInlineSponsored(pois, state.activeCategory, 0);
    }
    container.innerHTML =
      modeSummaryHtml() +
      locationHintHtml() +
      partialLoadHtml +
      countNoteHtml +
      cardsHtml;

    bindCardInteractions(container, pois);
  }

  function renderFilterBar() {
    var bar = document.getElementById("filter-bar");
    ensureActiveCategoryAllowed();
    if (state.activeCategory === MODE_ALL_CATEGORY_ID) {
      bar.innerHTML = "";
      bar.hidden = true;
      return;
    }
    var tagCopy = TAG_COPY[state.activeCategory] || {};
    var tagIds = Object.keys(tagCopy).filter(function (tagId) { return !NON_FILTER_TAG_IDS[tagId]; });
    if (!tagIds.length) {
      bar.innerHTML = "";
      bar.hidden = true;
      return;
    }
    bar.hidden = false;
    var noneActive = !hasActiveFilterSelections();
    var chips = [
      '<button class="filter-chip filter-chip-none" data-tag="' + NONE_FILTER_TAG_ID + '" aria-pressed="' + noneActive + '">' +
      '<span class="filter-chip-check" aria-hidden="true"></span>' +
      '<span class="filter-chip-label">条件指定なし</span>' +
      '</button>'
    ];
    chips = chips.concat(tagIds.map(function (tagId) {
      var active = !!state.activeFilters[tagId];
      return (
        '<button class="filter-chip" data-tag="' + tagId + '" aria-pressed="' + active + '">' +
        '<span class="filter-chip-check" aria-hidden="true"></span>' +
        '<span class="filter-chip-label">' + escapeHtml(tagCopy[tagId]) + '</span>' +
        "</button>"
      );
    }));
    bar.innerHTML = chips.join("");

    Array.prototype.forEach.call(bar.querySelectorAll(".filter-chip"), function (btn) {
      btn.addEventListener("click", function () {
        var tagId = btn.getAttribute("data-tag");
        if (tagId === NONE_FILTER_TAG_ID) {
          state.activeFilters = {};
        } else {
          state.activeFilters[tagId] = !state.activeFilters[tagId];
          if (hasActiveFilterSelections()) {
            state.activeFilters[NONE_FILTER_TAG_ID] = false;
          }
        }
        // Reflect chip selection immediately so taps feel responsive.
        renderFilterBar();
      });
    });
  }

  function renderNav() {
    var nav = document.getElementById("bottom-nav");
    ensureActiveCategoryAllowed();
    var allowed = getAllowedCategories();
    var navItems = [];
    var mode = getModeDefinition(state.activeMode);
    if (mode.aggregateCategories) {
      navItems.push({ id: MODE_ALL_CATEGORY_ID, label: "まとめ", icon: "🌙" });
    }
    navItems = navItems.concat(CATEGORIES.filter(function (cat) {
      return allowed.indexOf(cat.id) !== -1;
    }));
    nav.innerHTML = navItems.map(function (item) {
      var pressed = item.id === state.activeCategory ? "true" : "false";
      return (
        '<button class="nav-btn" data-category="' + item.id + '" aria-pressed="' + pressed + '">' +
        '<span class="nav-icon">' + item.icon + "</span>" +
        "<span>" + escapeHtml(item.label) + "</span>" +
        "</button>"
      );
    }).join("");
    Array.prototype.forEach.call(nav.querySelectorAll(".nav-btn"), function (btn) {
      btn.addEventListener("click", function () {
        state.activeCategory = btn.getAttribute("data-category");
        // Each category has its own tag vocabulary (TAG_COPY[categoryId]) --
        // carrying filters across categories would silently no-op or match
        // an unrelated same-named tag, so start clean on every switch.
        state.activeFilters = {};
        state.expandedCardKey = null;
        renderNav();
        renderFilterBar();
        renderList();
        renderMarkers();
        syncDesktopControlsInlineState();
        scrollListToTop();
      });
    });
  }

  function renderModeBar() {
    var bar = document.getElementById("mode-bar");
    if (!bar) return;
    bar.innerHTML = MODES.map(function (mode) {
      var pressed = mode.id === state.activeMode ? "true" : "false";
      return (
        '<button class="mode-chip" data-mode="' + mode.id + '" aria-pressed="' + pressed + '">' +
        '<span class="mode-chip-title">' + escapeHtml(mode.label) + '</span>' +
        '<span class="mode-chip-copy">' + escapeHtml(mode.copy) + '</span>' +
        '</button>'
      );
    }).join("");

    Array.prototype.forEach.call(bar.querySelectorAll(".mode-chip"), function (btn) {
      btn.addEventListener("click", function () {
        state.activeMode = btn.getAttribute("data-mode");
        state.activeFilters = {};
        state.expandedCardKey = null;
        ensureActiveCategoryAllowed();
        renderModeBar();
        renderNav();
        renderFilterBar();
        renderList();
        renderMarkers();
        scrollListToTop();
      });
    });
  }

  // ---- Google Maps -------------------------------------------------------
  // Loaded only when an operator has configured a real API key
  // (window.KABUKICHO_GMAPS_API_KEY); otherwise the map pane shows a setup
  // notice instead of silently staying blank. Uses the classic
  // google.maps.Marker (not AdvancedMarkerElement) to avoid pulling in the
  // extra `libraries=marker` param for what is a handful of static pins --
  // consistent with this product's "no over-engineering" constraint.

  function clearMarkers() {
    state.markers.forEach(function (marker) { marker.setMap(null); });
    state.markers = [];
  }

  function mapFallbackCopy(reason) {
    if (reason === "auth") {
      return {
        kicker: "MAP FALLBACK",
        title: "地図APIは認証エラーです",
        note: "この端末のURLがGoogle Cloud側の許可リファラに入っていない可能性があります。下の簡易マップで位置関係は確認できます。"
      };
    }
    if (reason === "network") {
      return {
        kicker: "MAP FALLBACK",
        title: "地図APIの読み込みに失敗しました",
        note: "通信または外部APIの問題です。下の簡易マップで位置関係は確認できます。"
      };
    }
    if (reason === "missing_key") {
      return {
        kicker: "MAP FALLBACK",
        title: "地図APIキーが未設定です",
        note: "本番ではGoogle Mapsを表示しつつ、キーが無い環境でもこの簡易マップが残ります。"
      };
    }
    return {
      kicker: "MAP OVERVIEW",
      title: "位置関係を簡易表示しています",
      note: "Google Mapsの読み込み前でも、カテゴリ内の位置関係を先に確認できます。"
    };
  }

  function renderMapFallback(reason) {
    var fallback = document.getElementById("map-fallback");
    var mapCanvas = document.getElementById("map");
    if (!fallback) return;

    if (reason) state.mapFailureReason = reason;
    var copy = mapFallbackCopy(state.mapFailureReason);
    var pois = getCurrentVisiblePois().slice(0, 24);
    var focusedKey = state.focusedPoiKey;
    var latitudes = pois.map(function (poi) {
      var pos = refinedPoiPosition(poi);
      return pos ? pos.lat : KABUKICHO_CENTER.lat;
    });
    var longitudes = pois.map(function (poi) {
      var pos = refinedPoiPosition(poi);
      return pos ? pos.lng : KABUKICHO_CENTER.lng;
    });

    if (state.userLocation) {
      latitudes.push(state.userLocation.lat);
      longitudes.push(state.userLocation.lng);
    }
    latitudes.push(KABUKICHO_CENTER.lat);
    longitudes.push(KABUKICHO_CENTER.lng);

    var minLat = Math.min.apply(null, latitudes);
    var maxLat = Math.max.apply(null, latitudes);
    var minLng = Math.min.apply(null, longitudes);
    var maxLng = Math.max.apply(null, longitudes);
    var latRange = Math.max(maxLat - minLat, 0.0012);
    var lngRange = Math.max(maxLng - minLng, 0.0012);

    function normalize(value, min, range) {
      return 10 + ((value - min) / range) * 80;
    }

    var dotsHtml = pois.map(function (poi, index) {
      var pos = refinedPoiPosition(poi) || KABUKICHO_CENTER;
      var x = normalize(pos.lng, minLng, lngRange);
      var y = 90 - normalize(pos.lat, minLat, latRange);
      var classes = ["map-fallback-dot"];
      if (index === 0) classes.push("is-featured");
      if (focusedKey && focusedKey === getPoiKey(poi)) classes.push("is-focused");
      return '<span class="' + classes.join(" ") + '" style="left:' + x + '%;top:' + y + '%" title="' + escapeHtml(poi.name) + '"></span>';
    }).join("");
    var userHtml = state.userLocation
      ? '<span class="map-fallback-user-dot" style="left:' + normalize(state.userLocation.lng, minLng, lngRange) + '%;top:' + (90 - normalize(state.userLocation.lat, minLat, latRange)) + '%" title="現在地"></span>'
      : "";

    fallback.hidden = false;
    if (mapCanvas) mapCanvas.style.visibility = "hidden";
    fallback.innerHTML =
      '<div class="map-fallback-surface">' +
      '<div class="map-fallback-header">' +
      '<span class="map-fallback-kicker">' + escapeHtml(copy.kicker) + '</span>' +
      '<strong class="map-fallback-title">' + escapeHtml(copy.title) + '</strong>' +
      '<span class="map-fallback-note">' + escapeHtml(copy.note) + '</span>' +
      '</div>' +
      '<div class="map-fallback-grid">' +
      '<div class="map-fallback-dots">' + dotsHtml + '</div>' +
      '<div class="map-fallback-user">' + userHtml + '</div>' +
      '</div>' +
      '<div class="map-fallback-legend">' +
      '<span class="map-fallback-legend-item"><span class="map-fallback-legend-swatch poi"></span>候補</span>' +
      (focusedKey ? '<span class="map-fallback-legend-item"><span class="map-fallback-legend-swatch focused"></span>選択中</span>' : '') +
      (state.userLocation ? '<span class="map-fallback-legend-item"><span class="map-fallback-legend-swatch user"></span>現在地</span>' : '') +
      '</div>' +
      '</div>';
  }

  function hideMapFallback() {
    var fallback = document.getElementById("map-fallback");
    var mapCanvas = document.getElementById("map");
    if (fallback) {
      fallback.hidden = true;
      fallback.innerHTML = "";
    }
    if (mapCanvas) mapCanvas.style.visibility = "visible";
  }

  function renderMarkers() {
    if (!state.map) {
      renderMapFallback(state.mapFailureReason || "loading");
      return;
    }
    clearMarkers();
    ensureActiveCategoryAllowed();
    // Same filtered set as the list -- map and list must always agree on
    // what's currently "shown", or a pin with no matching card (or vice
    // versa) reads as a bug, not a feature.
    var pois = sortPoisForMode(state.activeMode, sortedByDistance(getModePois()));
    if (!state.infoWindow) state.infoWindow = new google.maps.InfoWindow();

    var bounds = new google.maps.LatLngBounds();
    pois.forEach(function (poi) {
      var pos = refinedPoiPosition(poi);
      if (!pos) return;
      var marker = new google.maps.Marker({
        position: { lat: pos.lat, lng: pos.lng },
        map: state.map,
        title: poi.name
      });
      marker.addListener("click", function () { openInfoWindow(poi, marker); });
      // Stored directly on the POI object (not looked up by lat/lng) --
      // several real entries share exact coordinates (co-located POIs:
      // Golden Gai bars, Tokyu Tower locker banks, paired ATMs), so
      // position-based lookup in focusMarker() would silently resolve to
      // the wrong marker whenever duplicates exist.
      poi._marker = marker;
      state.markers.push(marker);
      bounds.extend(marker.getPosition());
    });

    if (state.userLocation) bounds.extend(state.userLocation);

    if (!pois.length) {
      state.map.setCenter(state.userLocation || KABUKICHO_CENTER);
      state.map.setZoom(mapDefaultZoom());
    } else if (pois.length === 1 && !state.userLocation) {
      state.map.setCenter(bounds.getCenter());
      state.map.setZoom(mapSinglePoiZoom());
    } else {
      state.map.fitBounds(bounds, mapFitBoundsPadding());
    }
    hideMapFallback();
    enqueueRefinementForPois(pois);
  }

  function openInfoWindow(poi, marker) {
    var html = '<div class="map-infowindow"><strong>' + escapeHtml(poi.name) + "</strong></div>";
    state.infoWindow.setContent(html);
    state.infoWindow.open({ anchor: marker, map: state.map });
  }

  function focusMarker(poi) {
    state.focusedPoiKey = getPoiKey(poi);
    if (!state.map) {
      renderMapFallback(state.mapFailureReason || "loading");
      document.getElementById("map-pane").scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    var pos = refinedPoiPosition(poi) || rawPoiPosition(poi) || KABUKICHO_CENTER;
    state.map.panTo({ lat: pos.lat, lng: pos.lng });
    state.map.setZoom(18);
    if (poi._marker) openInfoWindow(poi, poi._marker);
    document.getElementById("map-pane").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function setupControlsSurface() {
    var toggle = document.getElementById("controls-toggle");
    var reopen = document.getElementById("reopen-controls");
    var close = document.getElementById("controls-close");
    var panelHead = document.querySelector(".controls-panel-head");
    var backdrop = document.getElementById("controls-backdrop");
    var apply = document.getElementById("filter-apply");

    function openControls() { setControlsOpen(true); }
    function toggleControls() { setControlsOpen(!state.controlsOpen); }

    if (toggle) {
      toggle.addEventListener("click", function () {
        setControlsOpen(!state.controlsOpen);
      });
    }
    if (reopen) openControls && reopen.addEventListener("click", openControls);
    if (close) {
      close.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        toggleControls();
      });
    }
    if (panelHead) {
      panelHead.addEventListener("click", function (event) {
        if (event.target && event.target.id === "controls-close") return;
        if (!state.controlsOpen && !isMobileViewport()) setControlsOpen(true);
      });
    }
    if (backdrop) backdrop.addEventListener("click", function () { setControlsOpen(false); });
    if (apply) apply.addEventListener("click", applyFilterSelection);

    if (typeof window !== "undefined") {
      window.addEventListener("resize", function () {
        if (!isMobileViewport()) {
          setControlsOpen(true);
        } else {
          setControlsOpen(false);
        }
      });

      // Desktop keeps controls visible by default but allows explicit close.
      if (!isMobileViewport()) {
        setControlsOpen(true);
      }
    }
  }

  function renderUserMarker() {
    if (!state.map || !state.userLocation) return;
    if (state.userMarker) state.userMarker.setMap(null);
    state.userMarker = new google.maps.Marker({
      position: state.userLocation,
      map: state.map,
      title: "現在地",
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 8,
        fillColor: "#1a73e8",
        fillOpacity: 1,
        strokeColor: "#ffffff",
        strokeWeight: 2
      },
      zIndex: 999
    });
  }

  function requestUserLocation() {
    if (!("geolocation" in navigator)) {
      state.locationStatus = "unsupported";
      renderList();
      return;
    }
    state.locationStatus = "requesting";
    renderList();
    navigator.geolocation.getCurrentPosition(
      function (position) {
        state.userLocation = { lat: position.coords.latitude, lng: position.coords.longitude };
        state.locationStatus = "granted";
        renderUserMarker();
        renderMarkers();
        renderList();
        if (!state.map) renderMapFallback(state.mapFailureReason || "loading");
      },
      function () {
        state.locationStatus = "denied";
        renderList();
        if (!state.map) renderMapFallback(state.mapFailureReason || "loading");
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  }

  // Guarded for the same reason as the DOMContentLoaded registration
  // below -- lets this file be require()d from a plain Node test script
  // with no `window` global, with no effect on real browser behavior.
  if (typeof window !== "undefined") {
    window.initKabukichoMap = function () {
      state.mapFailureReason = null;
      state.geocoder = new google.maps.Geocoder();
      state.map = new google.maps.Map(document.getElementById("map"), {
        center: state.userLocation || KABUKICHO_CENTER,
        zoom: mapDefaultZoom(),
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: false
      });
      renderMarkers();
      enqueueRefinementForPois(getAllPoisFlat());
      // A location fix from before the map finished loading (distance
      // sorting doesn't wait on the map) has no marker yet -- add it now.
      if (state.userLocation) renderUserMarker();
    };

    window.gm_authFailure = function () {
      state.map = null;
      renderMapFallback("auth");
    };
  }

  function loadGoogleMaps() {
    var apiKey = window.KABUKICHO_GMAPS_API_KEY;
    if (!apiKey) {
      renderMapFallback("missing_key");
      return;
    }
    var script = document.createElement("script");
    script.src =
      "https://maps.googleapis.com/maps/api/js?key=" +
      encodeURIComponent(apiKey) +
      "&callback=initKabukichoMap&loading=async";
    script.async = true;
    script.onerror = function () {
      state.map = null;
      renderMapFallback("network");
    };
    document.head.appendChild(script);
  }

  function loadAll() {
    // Fetched relative to this file so the app is self-contained and
    // deployable as a static bundle -- data/ is a build-time copy of
    // platform/system/runtime/data/kabukicho/ (the canonical source), see build.py.
    // A failed fetch used to silently set state.data[cat.id] = [], which
    // renderList() then displayed as an ordinary "no POIs in this
    // category" empty state -- indistinguishable from a genuinely empty
    // category. state.loadFailed tracks the real cause separately so the
    // UI can tell "we checked, there's nothing" apart from "we couldn't
    // check."
    return Promise.all(
      CATEGORIES.map(function (cat) {
        return fetch("data/" + cat.file)
          .then(function (res) {
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
          })
          .then(function (json) {
            state.data[cat.id] = json.map(function (poi) {
              var parsedLat = toFiniteNumber(poi.lat);
              var parsedLng = toFiniteNumber(poi.lng);
              poi.lat = parsedLat === null ? KABUKICHO_CENTER.lat : parsedLat;
              poi.lng = parsedLng === null ? KABUKICHO_CENTER.lng : parsedLng;
              poi.category = cat.id;
              return poi;
            });
          })
          .catch(function () {
            state.data[cat.id] = [];
            state.loadFailed[cat.id] = true;
          });
      })
    );
  }

  // Guarded so this file can also be `require()`d from a plain Node test
  // script (see tests/test_app_logic.js) without a DOM/fetch/Google Maps
  // environment -- browser behavior is unchanged, `document` is always
  // defined there.
  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", function () {
      setupControlsSurface();
      renderMapFallback("loading");
      renderModeBar();
      renderNav();
      renderFilterBar();
      renderCurrentContext([], 0, []);
      loadAll().then(function () {
        if (ENABLE_RUNTIME_REFINEMENT) loadRefinedPositionCache();
        renderList();
        renderMapFallback(state.mapFailureReason || "loading");
        // Map init (initKabukichoMap) fires asynchronously once the Google
        // Maps script loads and calls back -- it re-renders markers itself,
        // so it's safe to kick off in parallel with the initial list render.
        loadGoogleMaps();
        // Distance-based sorting for the bottom list doesn't depend on the
        // map -- request it independently so it works even before the map
        // finishes loading, or when no API key is configured at all.
        requestUserLocation();
      });
    });
  }

  // Exposes a handful of pure, side-effect-free functions for direct
  // Node-based unit testing (tests/test_app_logic.js) -- never runs in
  // the browser (module is undefined there), so this has no effect on
  // the shipped product.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { haversineDistanceMeters: haversineDistanceMeters, formatDistance: formatDistance, freshnessBadge: freshnessBadge };
  }
})();
