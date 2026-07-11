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
      unsafe: "治安面で注意が必要な場所"
    },
    toilet: {
      clean: "清潔と報告されています",
      dirty: "汚れが気になるとの報告あり",
      free: "無料で利用できます",
      long_wait: "混雑時は待ち時間あり",
      gender_separated: "男女別トイレです"
    },
    coin_locker: {
      small: "小型ロッカー（手荷物向け）",
      medium: "中型ロッカー（機内持込サイズ）",
      large: "大型ロッカー（預け入れサイズ）",
      suitcase_ok: "スーツケース収納可",
      suitcase_too_big: "大型スーツケースは入りません"
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

  var state = { activeCategory: CATEGORIES[0].id, data: {} };

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

  function renderCard(poi, categoryId) {
    var isGrayZone = poi.type === "unofficial" || !!poi.gray_zone_note;
    var tagCopy = TAG_COPY[categoryId] || {};
    var tagsHtml = (poi.tags || [])
      .map(function (tag) {
        var caption = tagCopy[tag] || tag;
        return '<span class="tag-chip">' + escapeHtml(caption) + "</span>";
      })
      .join("");
    var fresh = freshnessBadge(poi.last_updated);
    var freshHtml = fresh ? '<span class="freshness-badge ' + fresh.cls + '">' + fresh.text + "</span>" : "";
    var grayZoneHtml = isGrayZone
      ? '<div class="gray-zone-banner">' + DISCLAIMER_JA + "<br>" + DISCLAIMER_EN +
        (poi.gray_zone_note ? "<br>" + escapeHtml(poi.gray_zone_note) : "") + "</div>"
      : "";

    return (
      '<article class="poi-card">' +
      freshHtml +
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

  function renderList() {
    var container = document.getElementById("poi-list");
    var pois = state.data[state.activeCategory] || [];
    if (!pois.length) {
      container.innerHTML =
        '<p class="no-results">このカテゴリに該当する場所が見つかりませんでした。<br>別のカテゴリを選択してください。</p>';
      return;
    }
    container.innerHTML = pois.map(function (poi) { return renderCard(poi, state.activeCategory); }).join("");
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
        renderNav();
        renderList();
      });
    });
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
    loadAll().then(renderList);
  });
})();
