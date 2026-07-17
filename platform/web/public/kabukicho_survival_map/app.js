(function () {
  "use strict";

  // Two-letter language codes only (ja/en) -- kept minimal per this
  // product's "no over-engineering" constraint (issue #33). See setLanguage()
  // below for how this is chosen/persisted, and tr() for how {ja,en} objects
  // throughout this file (CATEGORIES/MODES/TAG_COPY labels, FAQ_ITEMS, and
  // inline literal strings) get resolved to a display string. Named tr(),
  // not the shorter t(), because `t` is already this file's established
  // parameter name for "tag" in many filter closures (e.g. `function (t) {
  // return state.activeFilters[t]; }`) -- reusing it for translation would
  // silently shadow those and risk a "t is not a function" bug the moment
  // someone adds a translated string inside one of those closures.
  var CURRENT_LANG = "ja";

  // Resolves a {ja,en} object to the current language's string. Plain
  // strings (and null/undefined, used for e.g. MODES[0].emptyStateMessage)
  // pass through unchanged, so call sites that haven't been translated yet
  // never break.
  function tr(value) {
    if (value === null || typeof value === "undefined" || typeof value === "string") return value;
    return value[CURRENT_LANG] || value.ja || value.en || "";
  }

  var LANG_STORAGE_KEY = "kabukicho_lang";
  var PAGE_TITLE = {
    ja: "歌舞伎町サバイバルマップ | 終電後・24時間の困りごとをすぐ探せる地図",
    en: "Kabukicho Survival Map: Find What You Need, Even After the Last Train"
  };
  var PAGE_DESCRIPTION = {
    ja: "歌舞伎町で今すぐ使える喫煙所・24時間トイレ・ATM・コインロッカー・宿泊施設を状況別に検索。終電を逃した時も、朝まで過ごせる候補をすぐ確認できます。信頼度・最終確認日つきの実地検証データ。",
    en: "Find smoking areas, 24h toilets, ATMs, coin lockers, and lodging in Kabukicho right now, filtered by situation -- including what's open if you miss the last train. Verified POI details with freshness badges."
  };
  var PAGE_HEADING = { ja: "歌舞伎町サバイバルマップ", en: "Kabukicho Survival Map" };
  var PAGE_SUBTITLE = { ja: "近くで今使える場所を、状況別にすばやく探す", en: "Quickly find what you need nearby, by situation" };
  var CONTROLS_TOGGLE_LABEL = { ja: "条件", en: "Filters" };

  // Detects a stored preference first (an explicit prior choice always
  // wins), then falls back to the device's own language -- a tourist whose
  // phone is set to English gets an English UI on first visit without
  // having to find the toggle.
  function detectInitialLang() {
    if (typeof window !== "undefined" && window.localStorage) {
      try {
        var stored = window.localStorage.getItem(LANG_STORAGE_KEY);
        if (stored === "ja" || stored === "en") return stored;
      } catch (error) {
        // Storage can fail in private mode or quota pressure -- fall through.
      }
    }
    if (typeof navigator !== "undefined" && navigator.language) {
      return navigator.language.toLowerCase().indexOf("ja") === 0 ? "ja" : "en";
    }
    return "ja";
  }

  // Updates every static/chrome element that depends on CURRENT_LANG but
  // isn't already covered by the regular render* functions -- <title>,
  // meta description, h1/subtitle, the controls-toggle label, and the
  // toggle button's own text. Split out from setLanguage() so the initial
  // DOMContentLoaded pass can apply the detected language once, cheaply,
  // before the first real render (instead of running a full re-render
  // immediately followed by another one).
  function applyLanguageChrome() {
    if (typeof document === "undefined") return;
    document.documentElement.lang = CURRENT_LANG;
    document.title = tr(PAGE_TITLE);
    var descriptionTag = document.getElementById("page-description");
    if (descriptionTag) descriptionTag.setAttribute("content", tr(PAGE_DESCRIPTION));
    var ogTitleTag = document.getElementById("og-title");
    if (ogTitleTag) ogTitleTag.setAttribute("content", tr(PAGE_TITLE));
    var ogDescriptionTag = document.getElementById("og-description");
    if (ogDescriptionTag) ogDescriptionTag.setAttribute("content", tr(PAGE_DESCRIPTION));
    var twitterTitleTag = document.getElementById("twitter-title");
    if (twitterTitleTag) twitterTitleTag.setAttribute("content", tr(PAGE_TITLE));
    var twitterDescriptionTag = document.getElementById("twitter-description");
    if (twitterDescriptionTag) twitterDescriptionTag.setAttribute("content", tr(PAGE_DESCRIPTION));
    var headingEl = document.getElementById("page-heading");
    if (headingEl) headingEl.textContent = tr(PAGE_HEADING);
    var subtitleEl = document.getElementById("page-subtitle");
    if (subtitleEl) subtitleEl.textContent = tr(PAGE_SUBTITLE);
    var controlsToggleLabelEl = document.getElementById("controls-toggle-label");
    if (controlsToggleLabelEl) controlsToggleLabelEl.textContent = tr(CONTROLS_TOGGLE_LABEL);
    var langToggle = document.getElementById("lang-toggle");
    if (langToggle) {
      langToggle.textContent = CURRENT_LANG === "ja" ? "EN" : "日本語";
      langToggle.setAttribute("aria-label", CURRENT_LANG === "ja" ? "Switch to English" : "日本語に切り替え");
    }
  }

  function setLanguage(lang) {
    CURRENT_LANG = lang === "en" ? "en" : "ja";
    if (typeof window !== "undefined" && window.localStorage) {
      try {
        window.localStorage.setItem(LANG_STORAGE_KEY, CURRENT_LANG);
      } catch (error) {
        // Storage can fail in private mode or quota pressure -- non-fatal.
      }
    }
    if (typeof document === "undefined") return;

    applyLanguageChrome();
    renderModeBar();
    renderNav();
    renderFilterBar();
    renderList();
    renderMarkers();
    renderFaq();
    renderCurrentContext(getCurrentVisiblePois(), (state.data[state.activeCategory] || []).length, getAggregateLoadFailures(getModeDefinition(state.activeMode)));
  }

  // Category order matches doc_creation/task-0001-seo-copy's recommended
  // sort: by frequency/urgency, not alphabetically.
  var CATEGORIES = [
    { id: "convenience", file: "convenience.json", label: { ja: "コンビニ", en: "Convenience Store" }, icon: "🏪", subtitle: "24/7 services" },
    { id: "smoking", file: "smoking.json", label: { ja: "喫煙所", en: "Smoking Area" }, icon: "🚬", subtitle: "Designated smoking zones" },
    { id: "toilet", file: "toilet.json", label: { ja: "トイレ", en: "Toilet" }, icon: "🚻", subtitle: "Public restrooms" },
    { id: "atm", file: "atm.json", label: { ja: "ATM・両替", en: "ATM / Exchange" }, icon: "💳", subtitle: "Cash withdrawal & exchange" },
    { id: "coin_locker", file: "coin_locker.json", label: { ja: "コインロッカー", en: "Coin Locker" }, icon: "🧳", subtitle: "Luggage storage" },
    { id: "lodging", file: "lodging.json", label: { ja: "宿泊・ネカフェ", en: "Lodging / Net Cafe" }, icon: "🏨", subtitle: "Overnight & day-use facilities" },
    { id: "karaoke", file: "karaoke.json", label: { ja: "カラオケ", en: "Karaoke" }, icon: "🎤", subtitle: "Karaoke boxes" },
    { id: "shisha_bar", file: "shisha_bar.json", label: { ja: "シーシャバー", en: "Shisha Bar" }, icon: "💨", subtitle: "Shisha / hookah bars" }
  ];

  var MODES = [
    {
      id: "nearby",
      label: { ja: "近くで探す", en: "Nearby" },
      copy: { ja: "カテゴリ別に通常探索", en: "Browse by category" },
      // karaoke/shisha_bar are deliberately excluded here -- they're
      // late_night-only ("time to kill until morning", not something
      // you'd urgently need to find in the middle of the day the way the
      // other categories are), see the late_night mode below.
      targetCategories: CATEGORIES.filter(function (cat) {
        return cat.id !== "karaoke" && cat.id !== "shisha_bar";
      }).map(function (cat) { return cat.id; }),
      aggregateCategories: false,
      preferredTags: [],
      negativeTags: [],
      categoryBoosts: {},
      sortStrategy: ["distance", "freshness"],
      emptyStateMessage: null,
      summary: {
        ja: "現在地に近い順を基本に、カテゴリごとに通常の地図探索ができます。",
        en: "Sorted by distance from you, with normal category-by-category browsing."
      }
    },
    {
      id: "late_night",
      label: { ja: "朝まで過ごす", en: "Until Morning" },
      copy: { ja: "終電後の避難導線", en: "After the last train" },
      targetCategories: ["lodging", "convenience", "toilet", "karaoke", "shisha_bar"],
      aggregateCategories: true,
      preferredTags: ["24h", "overnight_friendly", "shower_available", "free_drink_bar", "group_friendly"],
      negativeTags: [],
      categoryBoosts: { lodging: 5, convenience: 2, toilet: 1, karaoke: 3, shisha_bar: 2 },
      sortStrategy: ["distance", "modeScore", "freshness", "reliability"],
      emptyStateMessage: {
        ja: "朝まで向きの候補が見つかりませんでした。宿泊・ネカフェかコンビニを個別に確認してください。",
        en: "No good options found for staying until morning. Try checking Lodging or Convenience Store individually."
      },
      summary: {
        ja: "終電後に必要な宿泊・休憩・時間つぶし導線をまとめて、朝までしのげる候補を優先します。",
        en: "Prioritizes lodging, rest, and time-killing options you'd need to make it through until morning."
      }
    },
    {
      id: "toilet_now",
      label: { ja: "トイレ急ぎ", en: "Toilet Now" },
      copy: { ja: "近くて使いやすい順", en: "Nearest & easiest" },
      targetCategories: ["toilet"],
      aggregateCategories: false,
      preferredTags: ["24h", "free", "clean", "gender_separated"],
      negativeTags: ["dirty", "long_wait"],
      categoryBoosts: { toilet: 4 },
      sortStrategy: ["distance", "modeScore", "freshness"],
      emptyStateMessage: {
        ja: "近くで使いやすいトイレが見つかりませんでした。通常のトイレ一覧に切り替えて探してください。",
        en: "No easy-to-use toilet found nearby. Try switching to the normal Toilet list."
      },
      summary: {
        ja: "いま一番早く使えそうなトイレを、距離と使いやすさで優先表示します。",
        en: "Prioritizes the toilet you can use soonest, by distance and ease of use."
      }
    },
    {
      id: "smoking_now",
      label: { ja: "今吸える場所", en: "Smoke Now" },
      copy: { ja: "使いやすさ優先", en: "Easiest first" },
      targetCategories: ["smoking"],
      aggregateCategories: false,
      preferredTags: ["indoor", "24h", "rain_ok"],
      negativeTags: ["crowded", "hidden", "unsafe"],
      categoryBoosts: { smoking: 4 },
      sortStrategy: ["distance", "modeScore", "freshness", "reliability"],
      emptyStateMessage: {
        ja: "近くで使いやすい喫煙所が見つかりませんでした。通常の喫煙所一覧で候補を広げてください。",
        en: "No easy-to-use smoking area found nearby. Try the normal Smoking Area list for more options."
      },
      summary: {
        ja: "近さに加えて、屋内・24時間・混雑しにくさを加味して、現実的に使える喫煙所を優先します。",
        en: "Prioritizes distance plus indoor, 24h, and low-crowding, for a smoking area you can actually use."
      }
    }
  ];

  // Tag copy templates, from scenario_writing/task-0001 -- one line per tag,
  // <=50 chars, meant to render as a single-line chip caption.
  var TAG_COPY = {
    smoking: {
      indoor: { ja: "屋内", en: "Indoor" },
      outdoor: { ja: "屋外", en: "Outdoor" },
      rain_ok: { ja: "雨OK", en: "Rain OK" },
      crowded: { ja: "混雑", en: "Crowded" },
      hidden: { ja: "見つけにくい", en: "Hard to find" },
      unsafe: { ja: "注意", en: "Caution" },
      "24h": { ja: "24h", en: "24h" }
    },
    toilet: {
      clean: { ja: "清潔", en: "Clean" },
      dirty: { ja: "汚れ", en: "Dirty" },
      free: { ja: "無料", en: "Free" },
      long_wait: { ja: "待ち", en: "Wait" },
      gender_separated: { ja: "男女別", en: "Gender-separated" },
      "24h": { ja: "24h", en: "24h" }
    },
    coin_locker: {
      small: { ja: "小型", en: "Small" },
      medium: { ja: "中型", en: "Medium" },
      large: { ja: "大型", en: "Large" },
      suitcase_ok: { ja: "スーツケース可", en: "Suitcase OK" },
      suitcase_too_big: { ja: "大型不可", en: "No large luggage" },
      "24h": { ja: "24h", en: "24h" }
    },
    lodging: {
      shower_available: { ja: "シャワーあり", en: "Shower available" },
      no_shower: { ja: "シャワーなし", en: "No shower" },
      price_band_budget: { ja: "予算", en: "Budget" },
      price_band_mid: { ja: "標準", en: "Mid-range" },
      price_band_high: { ja: "高価格", en: "High-end" },
      "24h": { ja: "24h", en: "24h" },
      overnight_friendly: { ja: "深夜対応", en: "Overnight-friendly" }
    },
    convenience: {
      "24h": { ja: "24h", en: "24h" },
      atm_instore: { ja: "ATM併設", en: "ATM inside" },
      phone_charging: { ja: "充電可", en: "Charging available" }
    },
    atm: {
      "24h": { ja: "24h", en: "24h" },
      international_card_ok: { ja: "海外カード", en: "Intl. cards OK" },
      convenience_colocated: { ja: "コンビニ併設", en: "Inside convenience store" }
    },
    karaoke: {
      "24h": { ja: "24h", en: "24h" },
      free_drink_bar: { ja: "フリードリンク", en: "Free drink bar" },
      one_person_ok: { ja: "一人カラオケ可", en: "Solo-friendly" }
    },
    shisha_bar: {
      "24h": { ja: "24h", en: "24h" },
      group_friendly: { ja: "グループ向け", en: "Group-friendly" },
      reservation_recommended: { ja: "予約推奨", en: "Reservation recommended" }
    }
  };

  var NON_FILTER_TAG_IDS = {
    dirty: true,
    long_wait: true,
    hidden: true,
    unsafe: true
  };

  var NONE_FILTER_TAG_ID = "__none__";
  var SMOKING_UNOFFICIAL_TOGGLE_ID = "__smoking_unofficial__";

  var DISCLAIMER_JA = "⚠ 非公式情報・内容は変更される場合があります・ご利用は自己責任でお願いします";
  var DISCLAIMER_EN = "⚠ Unofficial Information / Subject to change / Use at your own risk";

  var FILTER_NONE_LABEL = { ja: "条件指定なし", en: "No filter" };
  var INCLUDE_UNOFFICIAL_LABEL = { ja: "非公式導線を含む", en: "Include unofficial spots" };
  var ALL_CATEGORIES_LABEL = { ja: "まとめ", en: "All" };
  var FAQ_HEADING = { ja: "よくある質問", en: "Frequently Asked Questions" };

  // Mirrors build.py's FAQ_ITEMS (same questions/answers) -- that copy is
  // the SSG version a non-JS crawler sees (always Japanese); this one is
  // what renderFaq() below swaps in once JS runs, same "JS takes over
  // after SSG paints" pattern renderList() already uses for #poi-list.
  // Keep both in sync by hand; there is no shared source of truth between
  // the Python and JS builds (same tradeoff as CATEGORIES vs build.py's
  // own category list, see build.py's own comment on that).
  var FAQ_ITEMS = [
    {
      ja: {
        q: "歌舞伎町に無料の喫煙所はありますか？",
        a: "はい。本サイトのデータは「無料で使える屋外の指定喫煙所」のみを喫煙所カテゴリに掲載しています(店舗内の喫煙可能スペースは含みません)。カテゴリ「喫煙所」からタップ1つで一覧を確認できます。"
      },
      en: {
        q: "Are there free smoking areas in Kabukicho?",
        a: "Yes. This site's smoking category only lists free, outdoor designated smoking areas (not in-store smoking spaces). Tap the \"Smoking Area\" category to see the list."
      }
    },
    {
      ja: {
        q: "歌舞伎町のトイレは無料で使えますか？",
        a: "掲載しているトイレの多くは無料の公共トイレですが、施設ごとに条件が異なる場合があります。各POIカードのタグ(free/clean/gender_separatedなど)で個別に確認してください。"
      },
      en: {
        q: "Are the toilets in Kabukicho free to use?",
        a: "Most listed toilets are free public toilets, but conditions vary by facility. Check each listing's tags (free/clean/gender-separated, etc.) individually."
      }
    },
    {
      ja: {
        q: "深夜でも使えるコインロッカーはありますか？",
        a: "「24h」タグが付いているコインロッカー・コンビニ・ATMは24時間利用可能です。カテゴリ内でタグ絞り込みを使うと深夜対応の施設だけに絞れます。"
      },
      en: {
        q: "Are there coin lockers usable late at night?",
        a: "Coin lockers, convenience stores, and ATMs tagged \"24h\" are available around the clock. Use the tag filter within a category to narrow down to overnight-friendly spots only."
      }
    },
    {
      ja: {
        q: "掲載されている情報はどのくらい新しいですか？",
        a: "各POIには最終確認日(last_updated)と信頼度スコアがあり、8日から1ヶ月以内に確認された情報には更新目安バッジ、1ヶ月以上確認されていない情報には注意バッジが付きます。"
      },
      en: {
        q: "How up to date is the listed information?",
        a: "Each listing has a last-checked date and a reliability score. Info checked 8-30 days ago gets a freshness badge, and info not checked for over a month gets a caution badge."
      }
    },
    {
      ja: {
        q: "非公式(グレーゾーン)の情報とは何ですか？",
        a: "風俗営業関連施設など、公式な出典で裏付けが取りにくい場所には「⚠ 非公式情報」の注意書きを表示しています。利用は自己責任でお願いします。"
      },
      en: {
        q: "What does \"unofficial\" (gray-zone) information mean?",
        a: "Places that are hard to verify from official sources (e.g. adult-entertainment-adjacent venues) are shown with an \"⚠ Unofficial Information\" warning. Use at your own risk."
      }
    },
    {
      ja: {
        q: "歌舞伎町で24時間使えるトイレはどこですか？",
        a: "「西武新宿駅前公衆便所」「Haijia(東京都健康プラザ ハイジア)1階トイレ」「四季の路(新宿遊歩道公園)トイレ」など、「24h」タグ付きの数か所が24時間利用できます。それ以外の施設内トイレは営業時間内のみで、東急歌舞伎町タワーのトイレは認証式でテナント利用者限定です。カテゴリ「トイレ」からタグで絞り込んで確認してください。"
      },
      en: {
        q: "Which toilets in Kabukicho are open 24 hours?",
        a: "A handful of listings tagged \"24h\" -- including the public toilet in front of Seibu-Shinjuku Station, the 1F toilet at Haijia (Tokyo Health Plaza), and the Shiki-no-Michi park toilet -- are open around the clock. Other in-facility toilets are only open during business hours, and the Tokyu Kabukicho Tower toilet requires an authenticated tenant-store customer. Filter the \"Toilet\" category by tag to check."
      }
    },
    {
      ja: {
        q: "歌舞伎町で終電を逃したらどうすればいいですか？",
        a: "「朝まで過ごす」モードに切り替えると、宿泊・コンビニ・トイレを中心に、営業中の一部のカラオケ・シーシャバーも含めた候補を状況別に表示します。個別の営業時間・24時間対応かどうかは各POIカードのタグと最終確認日で確認してください(カラオケ・シーシャバーは店舗によって深夜営業時間が異なります)。"
      },
      en: {
        q: "What should I do if I miss the last train in Kabukicho?",
        a: "Switch to \"Until Morning\" mode to see lodging, convenience stores, and toilets, plus karaoke and shisha bars that happen to be open. Late-night hours vary by individual karaoke/shisha venue, so check each listing's tags and last-checked date rather than assuming category-wide 24-hour availability."
      }
    }
  ];

  function faqHtml() {
    var itemsHtml = FAQ_ITEMS.map(function (item) {
      var entry = item[CURRENT_LANG] || item.ja;
      return "<details><summary>" + escapeHtml(entry.q) + "</summary><p>" + escapeHtml(entry.a) + "</p></details>";
    }).join("");
    return "<h2>" + escapeHtml(tr(FAQ_HEADING)) + "</h2>" + itemsHtml;
  }

  function renderFaq() {
    if (typeof document === "undefined") return;
    var section = document.getElementById("faq-section");
    if (!section) return;
    section.innerHTML = faqHtml();
  }

  // Kabukicho's approximate centroid -- used as the map's default center
  // before (or in place of) a real geolocation fix.
  var KABUKICHO_CENTER = { lat: 35.6949, lng: 139.7028 };

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
    includeUnofficialSmoking: false,
    expandedCardKey: null,
    controlsOpen: false,
    focusedPoiKey: null,
    mapFailureReason: "loading"
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

  function trackEvent(eventName, params) {
    if (typeof window === "undefined" || typeof window.gtag !== "function") return;
    window.gtag("event", eventName, params || {});
  }

  function activeFilterCount() {
    return Object.keys(state.activeFilters).filter(function (tagId) {
      return !!state.activeFilters[tagId];
    }).length;
  }

  function analyticsContext(extra) {
    var payload = {};
    if (!extra) return payload;
    Object.keys(extra).forEach(function (key) {
      payload[key] = extra[key];
    });
    return payload;
  }

  function trackClick(params) {
    trackEvent("click", analyticsContext(Object.assign({
      ui_mode: state.activeMode,
      ui_category: state.activeCategory
    }, params || {})));
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
    if (poi && poi.category === "smoking" && poi.type === "unofficial" && !state.includeUnofficialSmoking) {
      return false;
    }
    var activeTags = Object.keys(state.activeFilters).filter(function (t) { return state.activeFilters[t]; });
    if (!activeTags.length) return true;
    var tags = poi.tags || [];
    return activeTags.every(function (t) { return tags.indexOf(t) !== -1; });
  }

  function isSmokingCategoryActive() {
    return state.activeCategory === "smoking";
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

    panel.style.setProperty("transform", "translateY(0)");
    panel.style.setProperty("opacity", "1");
    panel.style.setProperty("pointer-events", "auto");
    panel.style.setProperty("max-height", "84px");
  }

  // Focus trap state for the mobile control-panel modal. Desktop shows the
  // same panel inline (not as a modal -- see style.css's 1024px breakpoint),
  // so the trap and aria-modal flag only ever activate when isMobileViewport().
  var controlsFocusTrigger = null;

  function getFocusableElements(container) {
    if (!container) return [];
    var selector = 'a[href], button:not([disabled]), input:not([disabled]), ' +
      'select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
    return Array.prototype.slice.call(container.querySelectorAll(selector)).filter(function (el) {
      return !el.hidden && el.offsetParent !== null;
    });
  }

  function handleControlsPanelKeydown(event) {
    if (event.key === "Escape" || event.keyCode === 27) {
      setControlsOpen(false);
      return;
    }
    if (event.key !== "Tab" && event.keyCode !== 9) return;
    var panel = document.getElementById("control-panel");
    var focusable = getFocusableElements(panel);
    if (!focusable.length) return;
    var first = focusable[0];
    var last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function setControlsOpen(open) {
    state.controlsOpen = !!open;
    if (typeof document === "undefined") return;

    document.body.classList.toggle("controls-open", state.controlsOpen);

    var mapPane = document.getElementById("map-pane");
    if (mapPane) {
      if (state.controlsOpen) {
        mapPane.style.zIndex = "1";
        mapPane.style.pointerEvents = "none";
        mapPane.style.visibility = "hidden";
        mapPane.style.opacity = "0";
        mapPane.style.filter = "saturate(0.55) blur(0.8px)";
      } else {
        mapPane.style.removeProperty("z-index");
        mapPane.style.removeProperty("pointer-events");
        mapPane.style.removeProperty("visibility");
        mapPane.style.removeProperty("opacity");
        mapPane.style.removeProperty("filter");
      }
    }

    var backdrop = document.getElementById("controls-backdrop");
    if (backdrop) backdrop.hidden = !state.controlsOpen;

    ["controls-toggle", "reopen-controls"].forEach(function (id) {
      var button = document.getElementById(id);
      if (button) button.setAttribute("aria-expanded", state.controlsOpen ? "true" : "false");
    });

    var close = document.getElementById("controls-close");
    if (close) {
      var label = tr(state.controlsOpen ? { ja: "閉じる", en: "Close" } : { ja: "開く", en: "Open" });
      close.textContent = label;
      close.setAttribute("aria-label", tr({ ja: "条件パネルを" + label, en: "Filter panel: " + label }));
    }

    var panel = document.getElementById("control-panel");
    var isModalContext = isMobileViewport();
    if (panel) panel.setAttribute("aria-modal", isModalContext && state.controlsOpen ? "true" : "false");

    if (isModalContext) {
      if (state.controlsOpen) {
        controlsFocusTrigger = document.activeElement;
        document.addEventListener("keydown", handleControlsPanelKeydown, true);
        setTimeout(function () {
          var focusable = getFocusableElements(panel);
          if (focusable.length) focusable[0].focus();
          else if (panel) panel.focus();
        }, 0);
      } else {
        document.removeEventListener("keydown", handleControlsPanelKeydown, true);
        if (controlsFocusTrigger && typeof controlsFocusTrigger.focus === "function") {
          controlsFocusTrigger.focus();
        }
        controlsFocusTrigger = null;
      }
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
    scrollListToTop();
    trackClick({
      ui_area: "panel_controls",
      ui_action: "filter_apply",
      ui_label: "この条件で検索"
    });
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

  function countUnit(n) {
    return tr({ ja: n + "件", en: n + (n === 1 ? " place" : " places") });
  }

  function getVisibleCountLabel(pois, totalInCategory) {
    if (!pois.length) return countUnit(0);
    if (Object.keys(state.activeFilters).some(function (t) { return state.activeFilters[t]; })) {
      return pois.length + " / " + countUnit(totalInCategory);
    }
    return countUnit(pois.length);
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
    if (days <= 7) return null;
    if (days <= 30) return { cls: "freshness-month", text: { ja: "1ヶ月以内に確認", en: "Checked within 1 month" } };
    return { cls: "freshness-stale", text: { ja: "⚠ 情報が古い可能性あり", en: "⚠ Info may be outdated" } };
  }

  function freshnessWeight(lastUpdated) {
    var fresh = freshnessBadge(lastUpdated);
    if (!fresh) return 0;
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

  function mapsUrlForPoi(poi) {
    var pos = refinedPoiPosition(poi) || rawPoiPosition(poi);
    if (!pos) return "https://www.google.com/maps";
    return mapsUrl(pos.lat, pos.lng);
  }

  // Shared DOM escaping utility. In the browser it's loaded via a <script>
  // tag before this file (no bundler); in the Node test harness
  // (tests/test_app_logic.js), window is undefined, so require() the local
  // committed copy directly instead of reaching through a platform-only path.
  var escapeHtml = (typeof window !== "undefined" && window.AcipDomUtils)
    ? window.AcipDomUtils.escapeHtml
    : require("./dom_escape.js").escapeHtml;

  function modeSummaryHtml() {
    var mode = getModeDefinition(state.activeMode);
    if (mode.id === "nearby") return "";
    return (
      '<div class="mode-summary">' +
      '<span class="mode-summary-title">' + escapeHtml(tr(mode.label)) + '</span>' +
      '<span class="mode-summary-copy">' + escapeHtml(tr(mode.summary)) + '</span>' +
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
      categoryLabel = tr({ ja: "まとめ", en: "All" });
    } else {
      var category = getCategoryDefinition(state.activeCategory);
      categoryLabel = category ? tr(category.label) : tr({ ja: "カテゴリ", en: "Category" });
    }

    var pills = [
      '<span class="current-context-pill">' + escapeHtml(tr(mode.label)) + '</span>',
      '<span class="current-context-pill">' + escapeHtml(categoryLabel) + '</span>',
      '<span class="current-context-pill">' + escapeHtml(getVisibleCountLabel(pois, totalInCategory)) + '</span>'
    ];
    if (activeFilterCount) {
      pills.push('<span class="current-context-pill">' + escapeHtml(tr({ ja: "絞り込み ", en: "Filters " }) + activeFilterCount) + '</span>');
    }
    if (isSmokingCategoryActive() && state.includeUnofficialSmoking) {
      pills.push('<span class="current-context-pill">' + escapeHtml(tr({ ja: "非公式導線を含む", en: "Including unofficial spots" })) + '</span>');
    }

    var note = aggregateFailures.length
      ? tr({ ja: "一部カテゴリの読み込みに失敗しているため、結果は部分表示です。", en: "Some categories failed to load, so results are partial." })
      : (isSmokingCategoryActive() && state.includeUnofficialSmoking
        ? tr({ ja: "非公式導線を含めて表示しています。注意書きを確認し、自己責任で利用してください。", en: "Showing unofficial spots too. Read the warnings and use at your own risk." })
      : (mode.id === "nearby"
        ? tr({ ja: "必要な施設だけを短く見て、詳細はタップで展開できます。", en: "A quick view of what you need -- tap any card for details." })
        : tr(mode.summary)));

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
      if (poi.category === "lodging" && tags.indexOf("overnight_friendly") !== -1) return { ja: "朝まで滞在向き", en: "Good until morning" };
      if (poi.category === "lodging" && tags.indexOf("shower_available") !== -1) return { ja: "シャワーあり", en: "Has a shower" };
      if (poi.category === "convenience" && tags.indexOf("24h") !== -1) return { ja: "24時間の補給拠点", en: "24h supply stop" };
      if (poi.category === "karaoke" && tags.indexOf("free_drink_bar") !== -1) return { ja: "フリードリンクで長居しやすい", en: "Free drinks, easy to stay long" };
      if (poi.category === "karaoke" && tags.indexOf("one_person_ok") !== -1) return { ja: "一人でも入りやすい", en: "Solo-friendly" };
      if (poi.category === "shisha_bar" && tags.indexOf("group_friendly") !== -1) return { ja: "グループで時間つぶしやすい", en: "Good for killing time with a group" };
      if (poi.category === "toilet" && tags.indexOf("24h") !== -1) return { ja: "深夜でも使いやすい", en: "Usable late at night" };
      return { ja: "終電後に役立つ候補", en: "Useful after the last train" };
    }
    if (modeId === "toilet_now") {
      if (tags.indexOf("24h") !== -1 && tags.indexOf("free") !== -1) return { ja: "24時間・無料", en: "24h & free" };
      if (tags.indexOf("clean") !== -1) return { ja: "清潔寄り", en: "Tends to be clean" };
      return { ja: "今使いやすい候補", en: "Easy to use right now" };
    }
    if (modeId === "smoking_now") {
      if (tags.indexOf("indoor") !== -1) return { ja: "屋内で使いやすい", en: "Easy to use, indoor" };
      if (tags.indexOf("24h") !== -1) return { ja: "時間を気にしにくい", en: "No need to watch the clock" };
      return { ja: "喫煙しやすい候補", en: "Easy smoking option" };
    }
    return "";
  }

  function getJudgmentSignals(poi) {
    var tags = poi.tags || [];
    var categoryId = poi.category || state.activeCategory;
    var modeId = state.activeMode;
    var candidates = {
      "24h": { tag: "24h", label: { ja: "24時間", en: "24 hours" }, tone: "strong", base: 70 },
      free: { tag: "free", label: { ja: "無料", en: "Free" }, tone: "strong", base: 72 },
      clean: { tag: "clean", label: { ja: "清潔", en: "Clean" }, tone: "strong", base: 64 },
      gender_separated: { tag: "gender_separated", label: { ja: "男女別", en: "Gender-separated" }, tone: "neutral", base: 55 },
      indoor: { tag: "indoor", label: { ja: "屋内", en: "Indoor" }, tone: "strong", base: 66 },
      rain_ok: { tag: "rain_ok", label: { ja: "雨でも可", en: "OK in rain" }, tone: "neutral", base: 58 },
      overnight_friendly: { tag: "overnight_friendly", label: { ja: "朝まで可", en: "Good until morning" }, tone: "strong", base: 76 },
      shower_available: { tag: "shower_available", label: { ja: "シャワー", en: "Shower" }, tone: "strong", base: 73 },
      no_shower: { tag: "no_shower", label: { ja: "シャワーなし", en: "No shower" }, tone: "warn", base: 40 },
      suitcase_ok: { tag: "suitcase_ok", label: { ja: "スーツケース可", en: "Suitcase OK" }, tone: "strong", base: 71 },
      large: { tag: "large", label: { ja: "大型対応", en: "Large size OK" }, tone: "strong", base: 67 },
      medium: { tag: "medium", label: { ja: "中型対応", en: "Medium size OK" }, tone: "neutral", base: 48 },
      small: { tag: "small", label: { ja: "小型のみ", en: "Small only" }, tone: "neutral", base: 42 },
      suitcase_too_big: { tag: "suitcase_too_big", label: { ja: "大型不可", en: "No large luggage" }, tone: "warn", base: 38 },
      international_card_ok: { tag: "international_card_ok", label: { ja: "海外カード", en: "Intl. cards" }, tone: "neutral", base: 62 },
      atm_instore: { tag: "atm_instore", label: { ja: "ATMあり", en: "ATM inside" }, tone: "neutral", base: 54 },
      phone_charging: { tag: "phone_charging", label: { ja: "充電可", en: "Charging" }, tone: "neutral", base: 52 },
      price_band_budget: { tag: "price_band_budget", label: { ja: "低価格", en: "Budget" }, tone: "strong", base: 68 },
      price_band_mid: { tag: "price_band_mid", label: { ja: "標準価格", en: "Mid-range" }, tone: "neutral", base: 44 },
      price_band_high: { tag: "price_band_high", label: { ja: "高価格", en: "High-end" }, tone: "neutral", base: 28 },
      crowded: { tag: "crowded", label: { ja: "混雑注意", en: "Can be crowded" }, tone: "warn", base: 46 },
      long_wait: { tag: "long_wait", label: { ja: "待ち時間あり", en: "May have to wait" }, tone: "warn", base: 50 },
      dirty: { tag: "dirty", label: { ja: "清潔さ注意", en: "Cleanliness varies" }, tone: "warn", base: 48 },
      unsafe: { tag: "unsafe", label: { ja: "周辺注意", en: "Use caution" }, tone: "warn", base: 51 },
      hidden: { tag: "hidden", label: { ja: "見つけにくい", en: "Hard to find" }, tone: "warn", base: 43 },
      outdoor: { tag: "outdoor", label: { ja: "屋外", en: "Outdoor" }, tone: "neutral", base: 36 },
      free_drink_bar: { tag: "free_drink_bar", label: { ja: "フリードリンク", en: "Free drink bar" }, tone: "strong", base: 65 },
      one_person_ok: { tag: "one_person_ok", label: { ja: "一人カラオケ可", en: "Solo-friendly" }, tone: "neutral", base: 50 },
      group_friendly: { tag: "group_friendly", label: { ja: "グループ向け", en: "Group-friendly" }, tone: "neutral", base: 50 },
      reservation_recommended: { tag: "reservation_recommended", label: { ja: "予約推奨", en: "Reservation recommended" }, tone: "warn", base: 44 }
    };
    var categoryPriority = {
      toilet: ["free", "24h", "clean", "gender_separated", "long_wait", "dirty"],
      smoking: ["indoor", "rain_ok", "24h", "crowded", "unsafe", "hidden", "outdoor"],
      convenience: ["24h", "atm_instore", "phone_charging"],
      atm: ["24h", "international_card_ok"],
      coin_locker: ["suitcase_ok", "large", "24h", "medium", "small", "suitcase_too_big"],
      lodging: ["overnight_friendly", "shower_available", "24h", "price_band_budget", "price_band_mid", "price_band_high", "no_shower"],
      karaoke: ["free_drink_bar", "24h", "one_person_ok"],
      shisha_bar: ["24h", "group_friendly", "reservation_recommended"]
    };
    var modeBoosts = {
      toilet_now: { free: 30, "24h": 34, clean: 28, gender_separated: 18, long_wait: 8, dirty: 12 },
      smoking_now: { indoor: 34, rain_ok: 28, "24h": 24, crowded: 10, unsafe: 10, hidden: 8 },
      late_night: { overnight_friendly: 34, shower_available: 28, free_drink_bar: 22, group_friendly: 20, "24h": 20, price_band_budget: 16 }
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
    var freshness = freshnessBadge(poi.last_updated);
    var judgmentSignals = getJudgmentSignals(poi);
    var quickTagsHtml = judgmentSignals
      .map(function (signal) {
        return '<span class="signal-chip signal-chip-' + signal.tone + '">' + escapeHtml(tr(signal.label)) + "</span>";
      })
      .join("");
    var freshHtml = freshness
      ? '<span class="freshness-badge ' + freshness.cls + '">' + escapeHtml(tr(freshness.text)) + "</span>"
      : "";
    var distanceHtml =
      typeof poi._distanceMeters === "number"
        ? '<span class="distance-badge">📍 ' + escapeHtml(tr({ ja: "現在地から", en: "From you:" })) + " " + formatDistance(poi._distanceMeters) + "</span>"
        : "";
    var mode = getModeDefinition(state.activeMode);
    var modeBadgeHtml = mode.id !== "nearby"
      ? '<span class="mode-badge">' + escapeHtml(tr(mode.label)) + "</span>"
      : "";
    var category = getCategoryDefinition(poi.category || categoryId);
    var categoryBadgeHtml =
      mode.aggregateCategories && state.activeCategory === MODE_ALL_CATEGORY_ID && category
        ? '<span class="mode-badge">' + escapeHtml(category.icon + " " + tr(category.label)) + "</span>"
        : "";
    // reliability_score (1-5) is collected for every entry but was never
    // surfaced -- only flag the low end (<=2, ~8 of ~90 entries) rather
    // than showing a score on every card, matching how freshness/
    // gray-zone info only appears when there's actually something to
    // flag instead of cluttering every card with a routine "OK" signal.
    var lowReliabilityHtml =
      typeof poi.reliability_score === "number" && poi.reliability_score <= 2
        ? '<span class="reliability-badge">ℹ️ ' + escapeHtml(tr({ ja: "情報の確度: 参考程度", en: "Confidence: reference only" })) + "</span>"
        : "";
    var priorityLabel = modePriorityLabel(poi);
    var priorityHtml = priorityLabel
      ? '<div class="priority-line">' + escapeHtml(tr(priorityLabel)) + "</div>"
      : "";
    var featuredLabelHtml = options.featured
      ? '<div class="featured-kicker">' + escapeHtml(tr({ ja: "この条件で最初に見る候補", en: "Top pick for this filter" })) + "</div>"
      : "";
    var grayZoneHtml = isGrayZone
      ? '<div class="gray-zone-banner">' + DISCLAIMER_JA + "<br>" + DISCLAIMER_EN +
        (poi.gray_zone_note ? "<br>" + escapeHtml(poi.gray_zone_note) : "") + "</div>"
      : (poi.gray_zone_note ? '<div class="info-note">' + escapeHtml(poi.gray_zone_note) + "</div>" : "");
    var poiKey = getPoiKey(poi);
    var expanded = state.expandedCardKey === poiKey;
    var signalTagMap = {};
    judgmentSignals.forEach(function (signal) { signalTagMap[signal.tag] = true; });
    var detailTagsHtml = (poi.tags || [])
      .filter(function (tag) { return !signalTagMap[tag]; })
      .map(function (tag) {
        var caption = tr(tagCopy[tag]) || tag;
        return '<span class="tag-chip">' + escapeHtml(caption) + "</span>";
      })
      .join("");
    var collapsedMetaHtml = quickTagsHtml + freshHtml + lowReliabilityHtml;
    if (mode.aggregateCategories && state.activeCategory === MODE_ALL_CATEGORY_ID && categoryBadgeHtml) {
      collapsedMetaHtml += categoryBadgeHtml;
    }
    var supportingParts = [];
    if (collapsedMetaHtml) {
      supportingParts.push('<div class="poi-card-quick-tags">' + collapsedMetaHtml + '</div>');
    }
    var supportingHtml = supportingParts.length
      ? '<div class="poi-card-supporting">' + supportingParts.join("") + "</div>"
      : "";
    var detailMetaHtml = modeBadgeHtml + categoryBadgeHtml;

    return (
      '<article class="poi-card' + (options.featured ? ' poi-card-featured' : '') + '" data-poi-index="' + index + '" data-expanded="' + (expanded ? "true" : "false") + '">' +
      '<button class="poi-card-head" type="button" data-card-toggle="' + escapeHtml(poiKey) + '" aria-expanded="' + (expanded ? "true" : "false") + '">' +
      '<div class="poi-card-main">' +
      '<div class="poi-card-topline">' + featuredLabelHtml + priorityHtml + '</div>' +
      "<h3>" + escapeHtml(poi.name) + "</h3>" +
      supportingHtml +
      '</div>' +
      '<div class="poi-card-side">' + distanceHtml + '<span class="poi-card-toggle-text">' + escapeHtml(tr(expanded ? { ja: '閉じる', en: 'Close' } : { ja: '詳細', en: 'Details' })) + '</span><span class="poi-card-chevron">⌄</span></div>' +
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
        var wasExpanded = state.expandedCardKey === poiKey;
        var nextExpanded = state.expandedCardKey === poiKey ? null : poiKey;
        var targetPoi = pois.find(function (poi) { return getPoiKey(poi) === poiKey; });
        if (targetPoi) focusMarker(targetPoi);
        state.expandedCardKey = nextExpanded;
        if (targetPoi) {
          trackClick({
            ui_area: "list_poi_card",
            ui_action: wasExpanded ? "poi_card_collapse" : "poi_card_expand",
            ui_label: targetPoi.name,
            ui_category: targetPoi.category || state.activeCategory,
            ui_rank_index: pois.indexOf(targetPoi) + 1
          });
        }
        renderList();
      });
    });
    Array.prototype.forEach.call(container.querySelectorAll(".maps-link"), function (link) {
      link.addEventListener("click", function () {
        var article = link.closest(".poi-card");
        if (!article) return;
        var poiIndex = Number(article.getAttribute("data-poi-index"));
        var targetPoi = pois[poiIndex];
        if (!targetPoi) return;
        trackClick({
          ui_area: "list_poi_link",
          ui_action: "poi_open_maps",
          ui_label: targetPoi.name,
          ui_category: targetPoi.category || state.activeCategory,
          ui_rank_index: poiIndex + 1
        });
      });
    });
  }

  function inlineSponsoredHtml(index) {
    var slotNum = Math.floor(index / 7) + 1;
    var title;
    var copy;
    if (state.activeMode === "late_night") {
      title = { ja: "終電後サポート提携枠", en: "After-last-train partner slot" };
      copy = { ja: "朝まで利用しやすい宿泊・休憩・荷物預かりサービスの提携先を掲載します。", en: "Partner listings for lodging, rest, and luggage services good until morning." };
    } else if (state.activeMode === "toilet_now") {
      title = { ja: "周辺サービス提携枠", en: "Nearby service partner slot" };
      copy = { ja: "移動前後に使いやすい関連サービスの提携先を掲載します。", en: "Partner listings for services useful before or after moving on." };
    } else if (state.activeMode === "smoking_now") {
      title = { ja: "喫煙者向け提携枠", en: "Smoker-oriented partner slot" };
      copy = { ja: "休憩導線に合わせた周辺サービスをこの位置に表示します。", en: "Nearby services matched to your break, shown here." };
    } else {
      title = { ja: "関連サービス提携枠", en: "Related service partner slot" };
      copy = { ja: "一覧閲覧中に邪魔しない位置で、比較検討しやすい提携情報を掲載します。", en: "Partner info placed to compare without interrupting your browsing." };
    }

    return (
      '<aside class="inline-sponsored-card" aria-label="' + escapeHtml(tr({ ja: "スポンサー情報 ", en: "Sponsored " }) + slotNum) + '">' +
      '<span class="inline-sponsored-label">SPONSORED</span>' +
      '<strong>' + escapeHtml(tr(title)) + '</strong>' +
      '<p>' + escapeHtml(tr(copy)) + '</p>' +
      '</aside>'
    );
  }

  function cardsWithInlineSponsored(pois, categoryId, startIndex) {
    var html = "";
    var offset = startIndex || 0;
    pois.forEach(function (poi, localIndex) {
      var absoluteIndex = offset + localIndex;
      html += renderCard(poi, poi.category || categoryId, absoluteIndex);
      if ((localIndex + 1) % 7 === 0 && localIndex < pois.length - 1) {
        html += inlineSponsoredHtml(localIndex);
      }
    });
    return html;
  }

  function locationHintHtml() {
    if (state.locationStatus === "granted") return "";
    if (state.locationStatus === "requesting") {
      return '<div class="location-hint">📡 ' + escapeHtml(tr({ ja: "現在地を取得しています…", en: "Getting your location…" })) + '</div>';
    }
    if (state.locationStatus === "denied" || state.locationStatus === "unsupported") {
      return '<div class="location-hint">📍 ' + escapeHtml(tr({ ja: "現在地が取得できないため、標準の順番で表示しています。", en: "Couldn't get your location, so showing the default order." })) + '</div>';
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
        '<p class="no-results">⚠ ' + escapeHtml(tr({ ja: "データの読み込みに失敗しました。", en: "Failed to load data." })) +
        '<br>' + escapeHtml(tr({ ja: "通信環境をご確認のうえ、ページを再読み込みしてください。", en: "Check your connection and reload the page." })) + '</p>';
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
      ? '<div class="partial-load-note">⚠ ' + escapeHtml(tr({ ja: "一部カテゴリを読み込めなかったため、表示結果は完全ではありません。", en: "Some categories failed to load, so results are incomplete." })) + '</div>'
      : "";

    renderCurrentContext(pois, totalInCategory, aggregateFailures);

    if (!pois.length) {
      var emptyMessage = hasActiveFilter
        ? '<p class="no-results">' + escapeHtml(tr({ ja: "選択した条件では候補がありませんでした。", en: "No results for the selected filters." })) + '<br>' + escapeHtml(tr({ ja: "絞り込みを1つ外すか、別のモードに切り替えてください。", en: "Try removing a filter or switching modes." })) + '</p>'
        : '<p class="no-results">' + escapeHtml(tr(mode.emptyStateMessage) || tr({ ja: "このカテゴリに該当する場所が見つかりませんでした。別のカテゴリを選ぶか、条件を変えてみてください。", en: "No matching places found in this category. Try another category or change your filters." })) + '</p>';
      container.innerHTML = modeSummaryHtml() + locationHintHtml() + partialLoadHtml + emptyMessage;
      return;
    }
    var countNoteHtml =
      hasActiveFilter
        ? '<p class="filter-count-note">' + escapeHtml(tr({ ja: pois.length + " / " + totalInCategory + " 件を表示中", en: "Showing " + pois.length + " / " + totalInCategory })) + '</p>'
        : "";
    var cardsHtml;
    if (state.activeMode === "late_night" && state.activeCategory === MODE_ALL_CATEGORY_ID && pois.length > 1) {
      cardsHtml =
        '<section class="featured-result">' + renderCard(pois[0], pois[0].category || state.activeCategory, 0, { featured: true }) + '</section>' +
        '<section class="result-cluster">' +
        '<h3 class="result-cluster-title">' + escapeHtml(tr({ ja: "他の候補", en: "Other options" })) + '</h3>' +
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
    var noneActive = !hasActiveFilterSelections() && !(isSmokingCategoryActive() && state.includeUnofficialSmoking);
    var chips = [
      '<button class="filter-chip filter-chip-none" data-tag="' + NONE_FILTER_TAG_ID + '" aria-pressed="' + noneActive + '">' +
      '<span class="filter-chip-check" aria-hidden="true"></span>' +
      '<span class="filter-chip-label">' + escapeHtml(tr(FILTER_NONE_LABEL)) + '</span>' +
      '</button>'
    ];
    if (isSmokingCategoryActive()) {
      chips.push(
        '<button class="filter-chip filter-chip-unofficial" data-tag="' + SMOKING_UNOFFICIAL_TOGGLE_ID + '" aria-pressed="' + (state.includeUnofficialSmoking ? "true" : "false") + '">' +
        '<span class="filter-chip-check" aria-hidden="true"></span>' +
        '<span class="filter-chip-label">' + escapeHtml(tr(INCLUDE_UNOFFICIAL_LABEL)) + '</span>' +
        '</button>'
      );
    }
    chips = chips.concat(tagIds.map(function (tagId) {
      var active = !!state.activeFilters[tagId];
      return (
        '<button class="filter-chip" data-tag="' + tagId + '" aria-pressed="' + active + '">' +
        '<span class="filter-chip-check" aria-hidden="true"></span>' +
        '<span class="filter-chip-label">' + escapeHtml(tr(tagCopy[tagId])) + '</span>' +
        "</button>"
      );
    }));
    bar.innerHTML = chips.join("");

    Array.prototype.forEach.call(bar.querySelectorAll(".filter-chip"), function (btn) {
      btn.addEventListener("click", function () {
        var tagId = btn.getAttribute("data-tag");
        if (tagId === NONE_FILTER_TAG_ID) {
          state.activeFilters = {};
          state.includeUnofficialSmoking = false;
          trackClick({
            ui_area: "panel_filter",
            ui_action: "filter_toggle",
            ui_label: "条件指定なし",
            ui_filter_id: NONE_FILTER_TAG_ID,
            ui_selected: true
          });
        } else if (tagId === SMOKING_UNOFFICIAL_TOGGLE_ID) {
          state.includeUnofficialSmoking = !state.includeUnofficialSmoking;
          trackClick({
            ui_area: "panel_filter",
            ui_action: "filter_toggle",
            ui_label: "非公式導線を含む",
            ui_filter_id: SMOKING_UNOFFICIAL_TOGGLE_ID,
            ui_selected: state.includeUnofficialSmoking
          });
        } else {
          state.activeFilters[tagId] = !state.activeFilters[tagId];
          if (hasActiveFilterSelections()) {
            state.activeFilters[NONE_FILTER_TAG_ID] = false;
          }
          trackClick({
            ui_area: "panel_filter",
            ui_action: "filter_toggle",
            ui_label: (tagCopy[tagId] && tagCopy[tagId].ja) || tagId,
            ui_filter_id: tagId,
            ui_selected: !!state.activeFilters[tagId]
          });
        }
        // Reflect chip selection immediately so taps feel responsive.
        renderFilterBar();
        renderList();
        renderMarkers();
        scrollListToTop();
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
      navItems.push({ id: MODE_ALL_CATEGORY_ID, label: ALL_CATEGORIES_LABEL, icon: "🌙" });
    }
    navItems = navItems.concat(CATEGORIES.filter(function (cat) {
      return allowed.indexOf(cat.id) !== -1;
    }));
    nav.innerHTML = navItems.map(function (item) {
      var pressed = item.id === state.activeCategory ? "true" : "false";
      return (
        '<button class="nav-btn" data-category="' + item.id + '" aria-pressed="' + pressed + '">' +
        '<span class="nav-icon">' + item.icon + "</span>" +
        "<span>" + escapeHtml(tr(item.label)) + "</span>" +
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
        trackClick({
          ui_area: "panel_category",
          ui_action: "category_select",
          ui_label: btn.textContent ? btn.textContent.trim() : state.activeCategory,
          ui_category: state.activeCategory
        });
      });
    });
  }

  function renderModeBar() {
    // data-active-mode drives the desktop control panel's per-mode overlay
    // height in style.css (see [data-active-mode] rules) -- set here rather
    // than only in syncDesktopControlsInlineState so it also updates when
    // the mode changes while the panel is already open, not just on open/close.
    document.body.setAttribute("data-active-mode", state.activeMode);
    var bar = document.getElementById("mode-bar");
    if (!bar) return;
    bar.innerHTML = MODES.map(function (mode) {
      var pressed = mode.id === state.activeMode ? "true" : "false";
      return (
        '<button class="mode-chip" data-mode="' + mode.id + '" aria-pressed="' + pressed + '">' +
        '<span class="mode-chip-title">' + escapeHtml(tr(mode.label)) + '</span>' +
        '<span class="mode-chip-copy">' + escapeHtml(tr(mode.copy)) + '</span>' +
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
        trackClick({
          ui_area: "panel_mode",
          ui_action: "mode_select",
          ui_label: btn.querySelector(".mode-chip-title") ? btn.querySelector(".mode-chip-title").textContent.trim() : state.activeMode,
          ui_mode: state.activeMode
        });
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
        title: { ja: "地図APIは認証エラーです", en: "Map API authentication error" },
        note: {
          ja: "この端末のURLがGoogle Cloud側の許可リファラに入っていない可能性があります。下の簡易マップで位置関係は確認できます。",
          en: "This device's URL may not be in Google Cloud's allowed referrers. You can still check relative positions on the simple map below."
        }
      };
    }
    if (reason === "network") {
      return {
        kicker: "MAP FALLBACK",
        title: { ja: "地図APIの読み込みに失敗しました", en: "Map API failed to load" },
        note: {
          ja: "通信または外部APIの問題です。下の簡易マップで位置関係は確認できます。",
          en: "A network or external API issue. You can still check relative positions on the simple map below."
        }
      };
    }
    if (reason === "missing_key") {
      return {
        kicker: "MAP FALLBACK",
        title: { ja: "地図APIキーが未設定です", en: "Map API key not set" },
        note: {
          ja: "本番ではGoogle Mapsを表示しつつ、キーが無い環境でもこの簡易マップが残ります。",
          en: "Production shows Google Maps, but this simple map remains available even without a key."
        }
      };
    }
    return {
      kicker: "MAP OVERVIEW",
      title: { ja: "位置関係を簡易表示しています", en: "Showing a simplified layout" },
      note: {
        ja: "Google Mapsの読み込み前でも、カテゴリ内の位置関係を先に確認できます。",
        en: "You can check relative positions within a category even before Google Maps finishes loading."
      }
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
      ? '<span class="map-fallback-user-dot" style="left:' + normalize(state.userLocation.lng, minLng, lngRange) + '%;top:' + (90 - normalize(state.userLocation.lat, minLat, latRange)) + '%" title="' + escapeHtml(tr({ ja: "現在地", en: "Your location" })) + '"></span>'
      : "";

    fallback.hidden = false;
    if (mapCanvas) mapCanvas.style.visibility = "hidden";
    fallback.innerHTML =
      '<div class="map-fallback-surface">' +
      '<div class="map-fallback-header">' +
      '<span class="map-fallback-kicker">' + escapeHtml(copy.kicker) + '</span>' +
      '<strong class="map-fallback-title">' + escapeHtml(tr(copy.title)) + '</strong>' +
      '<span class="map-fallback-note">' + escapeHtml(tr(copy.note)) + '</span>' +
      '</div>' +
      '<div class="map-fallback-grid">' +
      '<div class="map-fallback-dots">' + dotsHtml + '</div>' +
      '<div class="map-fallback-user">' + userHtml + '</div>' +
      '</div>' +
      '<div class="map-fallback-legend">' +
      '<span class="map-fallback-legend-item"><span class="map-fallback-legend-swatch poi"></span>' + escapeHtml(tr({ ja: "候補", en: "Options" })) + '</span>' +
      (focusedKey ? '<span class="map-fallback-legend-item"><span class="map-fallback-legend-swatch focused"></span>' + escapeHtml(tr({ ja: "選択中", en: "Selected" })) + '</span>' : '') +
      (state.userLocation ? '<span class="map-fallback-legend-item"><span class="map-fallback-legend-swatch user"></span>' + escapeHtml(tr({ ja: "現在地", en: "You" })) + '</span>' : '') +
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
    var langToggle = document.getElementById("lang-toggle");

    if (langToggle) {
      langToggle.addEventListener("click", function () {
        var nextLang = CURRENT_LANG === "ja" ? "en" : "ja";
        setLanguage(nextLang);
        trackEvent("language_change", analyticsContext({ ui_action: "language_" + nextLang }));
      });
    }

    function openControls() { setControlsOpen(true); }
    function toggleControls() { setControlsOpen(!state.controlsOpen); }

    if (toggle) {
      toggle.addEventListener("click", function () {
        setControlsOpen(!state.controlsOpen);
        trackClick({
          ui_area: "panel_controls",
          ui_action: state.controlsOpen ? "controls_open" : "controls_close",
          ui_label: "条件",
          ui_trigger_id: "controls_toggle"
        });
      });
    }
    if (reopen) openControls && reopen.addEventListener("click", function () {
      openControls();
      trackClick({
        ui_area: "panel_controls",
        ui_action: "controls_open",
        ui_label: "条件を変更",
        ui_trigger_id: "reopen_controls"
      });
    });
    if (close) {
      close.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        toggleControls();
        trackClick({
          ui_area: "panel_controls",
          ui_action: state.controlsOpen ? "controls_open" : "controls_close",
          ui_label: close.textContent ? close.textContent.trim() : "閉じる",
          ui_trigger_id: "controls_close"
        });
      });
    }
    if (panelHead) {
      panelHead.addEventListener("click", function (event) {
        if (event.target && event.target.id === "controls-close") return;
        if (!state.controlsOpen && !isMobileViewport()) setControlsOpen(true);
      });
    }
    if (backdrop) backdrop.addEventListener("click", function () {
      setControlsOpen(false);
      trackClick({
        ui_area: "panel_controls",
        ui_action: "controls_close",
        ui_label: "backdrop",
        ui_trigger_id: "controls_backdrop"
      });
    });

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
      title: tr({ ja: "現在地", en: "Your location" }),
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
        trackEvent("geolocation_permission", analyticsContext({ ui_action: "geolocation_granted" }));
        renderUserMarker();
        renderMarkers();
        renderList();
        if (!state.map) renderMapFallback(state.mapFailureReason || "loading");
      },
      function () {
        state.locationStatus = "denied";
        trackEvent("geolocation_permission", analyticsContext({ ui_action: "geolocation_denied" }));
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
      state.map = new google.maps.Map(document.getElementById("map"), {
        center: state.userLocation || KABUKICHO_CENTER,
        zoom: mapDefaultZoom(),
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
      CURRENT_LANG = detectInitialLang();
      applyLanguageChrome();
      renderFaq();
      setupControlsSurface();
      renderMapFallback("loading");
      renderModeBar();
      renderNav();
      renderFilterBar();
      renderCurrentContext([], 0, []);
      loadAll().then(function () {
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
    module.exports = {
      haversineDistanceMeters: haversineDistanceMeters,
      formatDistance: formatDistance,
      freshnessBadge: freshnessBadge,
      sortPoisForMode: sortPoisForMode,
      getJudgmentSignals: getJudgmentSignals,
      passesActiveFilters: passesActiveFilters,
      ensureActiveCategoryAllowed: ensureActiveCategoryAllowed,
      renderCard: renderCard,
      MODE_ALL_CATEGORY_ID: MODE_ALL_CATEGORY_ID,
      tr: tr,
      faqHtml: faqHtml,
      // Test-only: flips CURRENT_LANG without the DOM-touching side effects
      // setLanguage() has (title/meta/render* calls that assume a real
      // document) -- setLanguage() itself is intentionally not exported,
      // same reason renderList/renderModeBar/etc. aren't: they're DOM
      // mutators, not the pure/string-building functions this test harness
      // targets (see the file comment below).
      setLangForTest: function (lang) { CURRENT_LANG = lang === "en" ? "en" : "ja"; },
      // Exposed only so tests can set up state (activeMode/activeCategory/
      // activeFilters/includeUnofficialSmoking) before calling the
      // functions above -- never mutated by browser code from outside
      // this file.
      state: state
    };
  }
})();
