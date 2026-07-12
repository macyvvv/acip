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

  // Tag copy templates, from scenario_writing/task-0001 -- one line per tag,
  // <=50 chars, meant to render as a single-line chip caption.
  var TAG_COPY = {
    smoking: {
      indoor: "屋内喫煙所・雨天も利用可",
      outdoor: "屋外の喫煙所です",
      rain_ok: "屋根あり・雨の日も安心",
      crowded: "混雑しやすい時間帯あり",
      hidden: "見つけにくい場所・要注意",
      unsafe: "治安面で注意が必要な場所",
      "24h": "24時間利用可"
    },
    toilet: {
      clean: "清潔と報告されています",
      dirty: "汚れが気になるとの報告あり",
      free: "無料で利用できます",
      long_wait: "混雑時は待ち時間あり",
      gender_separated: "男女別トイレです",
      "24h": "24時間利用可"
    },
    coin_locker: {
      small: "小型ロッカー（手荷物向け）",
      medium: "中型ロッカー（機内持込サイズ）",
      large: "大型ロッカー（預け入れサイズ）",
      suitcase_ok: "スーツケース収納可",
      suitcase_too_big: "大型スーツケースは入りません",
      "24h": "24時間利用可"
    },
    lodging: {
      shower_available: "シャワーあり（別料金の場合あり）",
      no_shower: "シャワー設備なし",
      price_band_budget: "予算重視の価格帯",
      price_band_mid: "標準的な価格帯",
      "24h": "24時間営業",
      overnight_friendly: "深夜〜宿泊利用に対応"
    },
    convenience: { "24h": "24時間営業", atm_instore: "ATM併設", phone_charging: "モバイルバッテリー貸出あり" },
    atm: { "24h": "24時間利用可", international_card_ok: "海外カード利用可" }
  };

  var DISCLAIMER_JA = "⚠ 非公式情報・内容は変更される場合があります・ご利用は自己責任でお願いします";
  var DISCLAIMER_EN = "⚠ Unofficial Information / Subject to change / Use at your own risk";

  // Kabukicho's approximate centroid -- used as the map's default center
  // before (or in place of) a real geolocation fix.
  var KABUKICHO_CENTER = { lat: 35.6949, lng: 139.7028 };

  var state = {
    activeCategory: CATEGORIES[0].id,
    data: {},
    map: null,
    markers: [],
    infoWindow: null,
    userLocation: null,
    userMarker: null,
    locationStatus: "idle", // idle | requesting | granted | denied | unsupported
    // Tag ids currently toggled on, e.g. {shower_available: true}. A POI
    // must carry every active tag (AND, not OR) to survive the filter --
    // each additional toggle narrows the list further, matching how a
    // "narrow down" filter is normally expected to behave. Reset on every
    // category switch since each category's tag vocabulary is different
    // (TAG_COPY[categoryId]); carrying a filter across categories would
    // silently no-op or, worse, coincidentally match an unrelated tag.
    activeFilters: {}
  };

  function getFilteredPois(categoryId) {
    var pois = state.data[categoryId] || [];
    var activeTags = Object.keys(state.activeFilters).filter(function (t) { return state.activeFilters[t]; });
    if (!activeTags.length) return pois;
    return pois.filter(function (poi) {
      var tags = poi.tags || [];
      return activeTags.every(function (t) { return tags.indexOf(t) !== -1; });
    });
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

  function formatDistance(meters) {
    if (meters < 1000) return Math.round(meters) + "m";
    return (meters / 1000).toFixed(1) + "km";
  }

  function sortedByDistance(pois) {
    if (!state.userLocation) return pois;
    var withDistance = pois.map(function (poi) {
      return {
        poi: poi,
        distance: haversineDistanceMeters(state.userLocation.lat, state.userLocation.lng, poi.lat, poi.lng)
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

  function mapsUrl(lat, lng) {
    return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(lat + "," + lng);
  }

  function escapeHtml(str) {
    return String(str == null ? "" : str).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function renderCard(poi, categoryId, index) {
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
    var tagsHtml = (poi.tags || [])
      .map(function (tag) {
        var caption = tagCopy[tag] || tag;
        return '<span class="tag-chip">' + escapeHtml(caption) + "</span>";
      })
      .join("");
    var fresh = freshnessBadge(poi.last_updated);
    var freshHtml = fresh ? '<span class="freshness-badge ' + fresh.cls + '">' + fresh.text + "</span>" : "";
    var distanceHtml =
      typeof poi._distanceMeters === "number"
        ? '<span class="distance-badge">📍 現在地から ' + formatDistance(poi._distanceMeters) + "</span>"
        : "";
    var grayZoneHtml = isGrayZone
      ? '<div class="gray-zone-banner">' + DISCLAIMER_JA + "<br>" + DISCLAIMER_EN +
        (poi.gray_zone_note ? "<br>" + escapeHtml(poi.gray_zone_note) : "") + "</div>"
      : (poi.gray_zone_note ? '<div class="info-note">' + escapeHtml(poi.gray_zone_note) + "</div>" : "");

    return (
      '<article class="poi-card" data-poi-index="' + index + '">' +
      '<div class="card-meta-row">' + freshHtml + distanceHtml + "</div>" +
      "<h2>" + escapeHtml(poi.name) + "</h2>" +
      grayZoneHtml +
      '<p class="description">' + escapeHtml(poi.description) + "</p>" +
      '<div class="tag-row">' + tagsHtml + "</div>" +
      '<a class="maps-link" target="_blank" rel="noopener" href="' +
      mapsUrl(poi.lat, poi.lng) +
      '">位置情報を見る</a>' +
      "</article>"
    );
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
    var totalInCategory = (state.data[state.activeCategory] || []).length;
    var pois = sortedByDistance(getFilteredPois(state.activeCategory));
    var hasActiveFilter = Object.keys(state.activeFilters).some(function (t) { return state.activeFilters[t]; });

    if (!pois.length) {
      var emptyMessage = hasActiveFilter
        ? '<p class="no-results">選択した条件に該当する場所が見つかりませんでした。<br>絞り込みを解除するか、別の条件をお試しください。</p>'
        : '<p class="no-results">このカテゴリに該当する場所が見つかりませんでした。<br>別のカテゴリを選択してください。</p>';
      container.innerHTML = locationHintHtml() + emptyMessage;
      return;
    }
    var countNoteHtml =
      hasActiveFilter
        ? '<p class="filter-count-note">' + pois.length + " / " + totalInCategory + " 件を表示中</p>"
        : "";
    container.innerHTML =
      locationHintHtml() +
      countNoteHtml +
      pois.map(function (poi, index) { return renderCard(poi, state.activeCategory, index); }).join("");

    Array.prototype.forEach.call(container.querySelectorAll(".poi-card"), function (card) {
      card.addEventListener("click", function (evt) {
        if (evt.target.closest(".maps-link")) return;
        var idx = Number(card.getAttribute("data-poi-index"));
        focusMarker(pois[idx]);
      });
    });
  }

  function renderFilterBar() {
    var bar = document.getElementById("filter-bar");
    var tagCopy = TAG_COPY[state.activeCategory] || {};
    var tagIds = Object.keys(tagCopy);
    if (!tagIds.length) {
      bar.innerHTML = "";
      bar.hidden = true;
      return;
    }
    bar.hidden = false;
    bar.innerHTML = tagIds.map(function (tagId) {
      var active = !!state.activeFilters[tagId];
      return (
        '<button class="filter-chip" data-tag="' + tagId + '" aria-pressed="' + active + '">' +
        escapeHtml(tagCopy[tagId]) +
        "</button>"
      );
    }).join("");

    Array.prototype.forEach.call(bar.querySelectorAll(".filter-chip"), function (btn) {
      btn.addEventListener("click", function () {
        var tagId = btn.getAttribute("data-tag");
        state.activeFilters[tagId] = !state.activeFilters[tagId];
        renderFilterBar();
        renderList();
        renderMarkers();
      });
    });
  }

  function renderNav() {
    var nav = document.getElementById("bottom-nav");
    nav.innerHTML = CATEGORIES.map(function (cat) {
      var pressed = cat.id === state.activeCategory ? "true" : "false";
      return (
        '<button class="nav-btn" data-category="' + cat.id + '" aria-pressed="' + pressed + '">' +
        '<span class="nav-icon">' + cat.icon + "</span>" +
        "<span>" + escapeHtml(cat.label) + "</span>" +
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
        renderNav();
        renderFilterBar();
        renderList();
        renderMarkers();
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

  function renderMarkers() {
    if (!state.map) return;
    clearMarkers();
    // Same filtered set as the list -- map and list must always agree on
    // what's currently "shown", or a pin with no matching card (or vice
    // versa) reads as a bug, not a feature.
    var pois = getFilteredPois(state.activeCategory);
    if (!state.infoWindow) state.infoWindow = new google.maps.InfoWindow();

    var bounds = new google.maps.LatLngBounds();
    pois.forEach(function (poi) {
      var marker = new google.maps.Marker({
        position: { lat: poi.lat, lng: poi.lng },
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
      state.map.setZoom(16);
    } else if (pois.length === 1 && !state.userLocation) {
      state.map.setCenter(bounds.getCenter());
      state.map.setZoom(17);
    } else {
      state.map.fitBounds(bounds, 48);
    }
  }

  function openInfoWindow(poi, marker) {
    var html =
      '<div class="map-infowindow"><strong>' + escapeHtml(poi.name) + "</strong><br>" +
      escapeHtml(poi.description) + "</div>";
    state.infoWindow.setContent(html);
    state.infoWindow.open({ anchor: marker, map: state.map });
  }

  function focusMarker(poi) {
    if (!state.map) return;
    state.map.panTo({ lat: poi.lat, lng: poi.lng });
    state.map.setZoom(18);
    if (poi._marker) openInfoWindow(poi, poi._marker);
    document.getElementById("map-pane").scrollIntoView({ behavior: "smooth", block: "start" });
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
      },
      function () {
        state.locationStatus = "denied";
        renderList();
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  }

  function showMapNotice(message) {
    var pane = document.getElementById("map-pane");
    pane.innerHTML = '<div class="map-notice">' + message + "</div>";
  }

  window.initKabukichoMap = function () {
    state.map = new google.maps.Map(document.getElementById("map"), {
      center: state.userLocation || KABUKICHO_CENTER,
      zoom: 16,
      streetViewControl: false,
      mapTypeControl: false,
      fullscreenControl: false
    });
    renderMarkers();
    // A location fix from before the map finished loading (distance
    // sorting doesn't wait on the map) has no marker yet -- add it now.
    if (state.userLocation) renderUserMarker();
  };

  window.gm_authFailure = function () {
    showMapNotice("⚠ 地図を読み込めませんでした。APIキーの設定をご確認ください。");
  };

  function loadGoogleMaps() {
    var apiKey = window.KABUKICHO_GMAPS_API_KEY;
    if (!apiKey) {
      showMapNotice(
        "🗺️ 地図機能は準備中です。<br>" +
        '<span class="map-notice-sub">Google Maps APIキーが設定されると、ここにカテゴリのピンが表示されます。</span>'
      );
      return;
    }
    var script = document.createElement("script");
    script.src =
      "https://maps.googleapis.com/maps/api/js?key=" +
      encodeURIComponent(apiKey) +
      "&callback=initKabukichoMap&loading=async";
    script.async = true;
    script.onerror = function () {
      showMapNotice("⚠ 地図の読み込みに失敗しました。通信環境をご確認のうえ、再度お試しください。");
    };
    document.head.appendChild(script);
  }

  function loadAll() {
    // Fetched relative to this file so the app is self-contained and
    // deployable as a static bundle -- data/ is a build-time copy of
    // system/runtime/data/kabukicho/ (the canonical source), see build.py.
    return Promise.all(
      CATEGORIES.map(function (cat) {
        return fetch("data/" + cat.file)
          .then(function (res) { return res.json(); })
          .then(function (json) { state.data[cat.id] = json; })
          .catch(function () { state.data[cat.id] = []; });
      })
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    renderNav();
    renderFilterBar();
    loadAll().then(function () {
      renderList();
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
})();
