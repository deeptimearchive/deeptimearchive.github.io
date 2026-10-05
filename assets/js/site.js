/* Deep Time Archive - site behaviour. No frameworks, no trackers. */
(function () {
  "use strict";
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var params = new URLSearchParams(location.search);

  /* ---------- shared data (search index) ---------- */
  var dataPromise = null;
  function data() {
    if (!dataPromise) {
      dataPromise = fetch("/assets/data/search.json").then(function (r) { return r.json(); });
    }
    return dataPromise;
  }
  function norm(s) {
    return (s || "").toString().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9 ]+/g, " ");
  }
  function esc(s) {
    return (s || "").toString().replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* ---------- search ---------- */
  function search(d, q) {
    var words = norm(q).split(" ").filter(function (w) { return w.length > 1 || /\d/.test(w); });
    if (!words.length) return [];
    var out = [];
    d.stories.forEach(function (s) {
      var fields = [[s.title, 6], [s.countryNames.join(" "), 5], [s.place, 4], [s.keywords.join(" "), 3],
                    [s.catNames.join(" "), 3], [s.era, 2], [s.hook + " " + s.summary, 1]];
      var score = 0, all = true;
      words.forEach(function (w) {
        var best = 0;
        fields.forEach(function (f) {
          var t = " " + norm(f[0]) + " ";
          if (t.indexOf(" " + w) !== -1) best = Math.max(best, f[1]);
        });
        if (!best) all = false;
        score += best;
      });
      if (score && all) out.push({ kind: "story", item: s, score: score + (s.status === "published" ? 1 : 0) });
    });
    var q2 = norm(q).trim();
    d.countries.forEach(function (c) {
      var n = norm(c.name);
      if (n.indexOf(q2) === 0 || (q2.length > 3 && n.indexOf(q2) !== -1)) {
        out.push({ kind: "country", item: c, score: n === q2 ? 9 : 4 });
        if (n === q2 && !d.counts[c.code]) out.push({ kind: "suggest", item: c, score: 8.5 });
      }
    });
    d.categories.forEach(function (c) {
      if (norm(c.name).indexOf(q2) !== -1 || norm(c.slug).indexOf(q2) === 0) out.push({ kind: "category", item: c, score: 5 });
    });
    return out.sort(function (a, b) { return b.score - a.score; }).slice(0, 9);
  }
  function resultHTML(r, d) {
    if (r.kind === "story") {
      var s = r.item;
      return '<a class="result" href="' + s.url + '"><img src="' + s.thumb + '" alt="" loading="lazy">' +
        '<div><strong>' + esc(s.title) + '</strong><span>' + esc(s.catNames[0] || "") + " · " + esc(s.place) +
        (s.status === "coming" ? " · Coming soon" : "") + "</span></div></a>";
    }
    if (r.kind === "country") {
      var c = r.item, n = d.counts[c.code] || 0;
      return '<a class="result" href="/explore/?country=' + c.code + '"><div class="r-icon">' + esc(c.code.toUpperCase()) +
        '</div><div><strong>' + esc(c.name) + '</strong><span>' +
        (n ? n + " stor" + (n === 1 ? "y" : "ies") : "No stories yet - suggest one") + " · " + esc(d.continentNames[c.continent]) +
        "</span></div></a>";
    }
    if (r.kind === "suggest") {
      return '<a class="result" href="/submit/?country=' + encodeURIComponent(r.item.name) + '"><div class="r-icon">+</div><div><strong>Suggest a story from ' +
        esc(r.item.name) + "</strong><span>Know something history forgot? We'll credit you.</span></div></a>";
    }
    var cat = r.item;
    return '<a class="result" href="/category/' + cat.slug + '/"><div class="r-icon">✦</div><div><strong>' + esc(cat.name) +
      "</strong><span>Category</span></div></a>";
  }
  function attachSearch(input, box) {
    var active = -1;
    function render() {
      var q = input.value.trim();
      if (!q) { box.innerHTML = ""; return; }
      data().then(function (d) {
        var res = search(d, q);
        active = -1;
        box.innerHTML = res.length ? res.map(function (r) { return resultHTML(r, d); }).join("") :
          '<div class="result-empty">Nothing yet for "<b>' + esc(q) + '</b>". <a href="/submit/?topic=' +
          encodeURIComponent(q) + '">Suggest this story</a> - if we make it, we will credit you.</div>';
      });
    }
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      var items = $$(".result", box);
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!items.length) return;
        active = (active + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items.forEach(function (it, i) { it.classList.toggle("active", i === active); });
        items[active].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter" && active >= 0 && items[active]) {
        e.preventDefault();
        location.href = items[active].getAttribute("href");
      }
    });
    if (input.value) render();
  }

  var overlay = $(".search-overlay");
  function openSearch(prefill) {
    if (!overlay) return;
    overlay.classList.add("open");
    var inp = $("input", overlay);
    if (prefill != null) { inp.value = prefill; inp.dispatchEvent(new Event("input")); }
    setTimeout(function () { inp.focus(); }, 30);
    document.body.style.overflow = "hidden";
  }
  function closeSearch() {
    if (!overlay) return;
    overlay.classList.remove("open");
    document.body.style.overflow = "";
  }
  if (overlay) {
    attachSearch($("input", overlay), $(".search-results", overlay));
    overlay.addEventListener("click", function (e) { if (e.target === overlay) closeSearch(); });
    $$("[data-open-search]").forEach(function (b) { b.addEventListener("click", function () { openSearch(); }); });
    $$("[data-search-term]").forEach(function (b) {
      b.addEventListener("click", function (e) { e.preventDefault(); openSearch(b.getAttribute("data-search-term")); });
    });
    document.addEventListener("keydown", function (e) {
      var typing = /input|textarea|select/i.test((document.activeElement || {}).tagName || "");
      if (e.key === "Escape") closeSearch();
      if (!typing && (e.key === "/" || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k"))) { e.preventDefault(); openSearch(); }
    });
  }
  var bandInput = $("#home-search");
  if (bandInput) {
    $("#home-search-form").addEventListener("submit", function (e) { e.preventDefault(); openSearch(bandInput.value); });
    bandInput.addEventListener("focus", function () { openSearch(bandInput.value); bandInput.blur(); });
  }

  /* ---------- mobile menu ---------- */
  var menuBtn = $(".menu-btn"), nav = $(".nav");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- hero slider ---------- */
  var hero = $(".hero[data-slider]");
  if (hero) {
    var slides = $$(".slide", hero), dots = $$(".dot", hero), texts = $$(".hero-text", hero);
    var labels = $$("[data-slide-label]", hero);
    var i = 0, timer = null, ms = 7000;
    hero.style.setProperty("--slide-ms", ms + "ms");
    function show(n) {
      var prev = i;
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle("active", k === i); s.setAttribute("aria-hidden", k === i ? "false" : "true"); });
      dots.forEach(function (d, k) {
        d.classList.remove("active", "done");
        if (k < i) d.classList.add("done");
        void d.offsetWidth;                               // restart the progress animation
        if (k === i) d.classList.add("active");
        d.setAttribute("aria-current", k === i ? "true" : "false");
      });
      labels.forEach(function (l) { l.hidden = l.getAttribute("data-slide-label") !== String(i); });
      if (prev !== i && texts[prev]) {
        texts[prev].classList.add("leaving");
        setTimeout(function () {
          texts.forEach(function (t, k) { t.hidden = k !== i; t.classList.remove("leaving"); });
        }, 420);
      } else {
        texts.forEach(function (t, k) { t.hidden = k !== i; });
      }
    }
    function play() { stop(); if (!reduceMotion) timer = setInterval(function () { show(i + 1); }, ms); hero.classList.remove("paused"); }
    function stop() { clearInterval(timer); timer = null; hero.classList.add("paused"); }
    dots.forEach(function (d, k) { d.addEventListener("click", function () { show(k); play(); }); });
    var prevBtn = $("[data-prev]", hero), nextBtn = $("[data-next]", hero);
    if (prevBtn) prevBtn.addEventListener("click", function () { show(i - 1); play(); });
    if (nextBtn) nextBtn.addEventListener("click", function () { show(i + 1); play(); });
    hero.addEventListener("mouseenter", stop);
    hero.addEventListener("mouseleave", play);
    hero.addEventListener("focusin", stop);
    document.addEventListener("visibilitychange", function () { document.hidden ? stop() : play(); });
    var x0 = null;
    hero.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    hero.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) { show(i + (dx < 0 ? 1 : -1)); play(); }
      x0 = null;
    });
    // lazy-load the other slides' images after the first one is shown
    window.addEventListener("load", function () {
      $$("img[data-src]", hero).forEach(function (img) { img.src = img.getAttribute("data-src"); });
    });
    show(0);
    play();
  }

  /* ---------- listing filters (stories & category pages) ---------- */
  var listing = $("[data-listing]");
  if (listing) {
    var cards = $$("[data-card]", listing), chips = $$("[data-filter-cat]"), qInput = $("#filter-q");
    var contSel = $("#filter-continent"), emptyBox = $("[data-empty]");
    var state = { cat: params.get("cat") || "all", q: params.get("q") || "", cont: params.get("continent") || "all" };
    if (qInput) qInput.value = state.q;
    if (contSel) contSel.value = state.cont;
    function apply() {
      var words = norm(state.q).split(" ").filter(Boolean), shown = 0;
      cards.forEach(function (c) {
        var ok = (state.cat === "all" || c.getAttribute("data-cats").split(" ").indexOf(state.cat) !== -1) &&
          (state.cont === "all" || c.getAttribute("data-continent") === state.cont) &&
          words.every(function (w) { return c.getAttribute("data-text").indexOf(w) !== -1; });
        c.hidden = !ok;
        if (ok) shown++;
      });
      chips.forEach(function (ch) { ch.setAttribute("aria-pressed", ch.getAttribute("data-filter-cat") === state.cat ? "true" : "false"); });
      if (emptyBox) emptyBox.hidden = shown > 0;
      var u = new URL(location.href);
      ["cat", "q", "continent"].forEach(function (k) { u.searchParams.delete(k); });
      if (state.cat !== "all") u.searchParams.set("cat", state.cat);
      if (state.q) u.searchParams.set("q", state.q);
      if (state.cont !== "all") u.searchParams.set("continent", state.cont);
      history.replaceState(null, "", u);
    }
    chips.forEach(function (ch) { ch.addEventListener("click", function () { state.cat = ch.getAttribute("data-filter-cat"); apply(); }); });
    if (qInput) qInput.addEventListener("input", function () { state.q = qInput.value; apply(); });
    if (contSel) contSel.addEventListener("change", function () { state.cont = contSel.value; apply(); });
    apply();
  }

  /* ---------- explore map ---------- */
  var explore = $("[data-explore]");
  if (explore) {
    var mapWrap = $(".map-wrap", explore), panel = $(".country-panel", explore), tip = $(".map-tip", explore);
    var tabs = $$(".continent-tabs button", explore);
    Promise.all([fetch("/assets/img/world-map.svg").then(function (r) { return r.text(); }), data()]).then(function (res) {
      var d = res[1];
      mapWrap.insertAdjacentHTML("afterbegin", res[0]);
      var svg = $("svg", mapWrap), current = { continent: null, country: null };
      Object.keys(d.counts).forEach(function (code) { var p = $("#c-" + code, svg); if (p) p.classList.add("has"); });
      function byCode(code) { return d.countries.filter(function (c) { return c.code === code; })[0]; }
      function storiesIn(code) { return d.stories.filter(function (s) { return s.countries.indexOf(code) !== -1; }); }
      function setContinent(cont, keepPanel) {
        current.continent = cont;
        tabs.forEach(function (t) { t.setAttribute("aria-pressed", t.getAttribute("data-continent") === (cont || "all") ? "true" : "false"); });
        $$("g.continent", svg).forEach(function (g) {
          var c = g.getAttribute("data-continent");
          g.classList.toggle("on", !cont || c === cont);
          g.classList.toggle("dim", !!cont && c !== cont);
        });
        if (!keepPanel) listCountries(cont);
      }
      function listCountries(cont) {
        var list = d.countries.filter(function (c) { return !cont || c.continent === cont; });
        list.sort(function (a, b) { return (d.counts[b.code] || 0) - (d.counts[a.code] || 0) || a.name.localeCompare(b.name); });
        var title = cont ? d.continentNames[cont] : "The whole world";
        var codes = {}; list.forEach(function (c) { codes[c.code] = 1; });
        var total = d.stories.filter(function (s) { return s.countries.some(function (k) { return codes[k]; }); }).length;
        panel.innerHTML = "<h3>" + esc(title) + '</h3><p class="muted">' + list.length + " countries · " +
          (total ? total + " stor" + (total === 1 ? "y" : "ies") : "first stories coming") + "</p>" +
          '<input class="country-filter" type="search" placeholder="Find a country..." aria-label="Find a country">' +
          '<ul class="country-list">' + list.map(function (c) {
            var n = d.counts[c.code] || 0;
            return '<li><button data-code="' + c.code + '"><span>' + esc(c.name) + "</span>" + (n ? '<span class="n">' + n + "</span>" : "") + "</button></li>";
          }).join("") + "</ul>";
        var filt = $(".country-filter", panel);
        filt.addEventListener("input", function () {
          var w = norm(filt.value);
          $$(".country-list li", panel).forEach(function (li) { li.hidden = norm(li.textContent).indexOf(w) === -1; });
        });
        $$(".country-list button", panel).forEach(function (b) { b.addEventListener("click", function () { showCountry(b.getAttribute("data-code")); }); });
      }
      function showCountry(code) {
        var c = byCode(code);
        if (!c) return;
        $$("path.sel", svg).forEach(function (p) { p.classList.remove("sel"); });
        var p = $("#c-" + code, svg);
        if (p) p.classList.add("sel");
        if (current.continent !== c.continent) setContinent(c.continent, true);
        var list = storiesIn(code);
        panel.innerHTML = '<button class="back-link" type="button">← All of ' + esc(d.continentNames[c.continent]) + "</button>" +
          "<h3>" + esc(c.name) + "</h3>" +
          (list.length ? '<p class="muted">' + list.length + " stor" + (list.length === 1 ? "y" : "ies") + "</p>" +
            '<div class="country-stories">' + list.map(function (s) {
              return '<a class="mini" href="' + s.url + '"><img src="' + s.thumb + '" alt=""><div><strong>' + esc(s.title) +
                "</strong><span>" + (s.status === "coming" ? "Coming soon" : (s.video ? "Watch · Read" : "Read")) + " · " + esc(s.era) + "</span></div></a>";
            }).join("") + "</div>" :
            '<p class="muted">No stories from ' + esc(c.name) + " yet. Know a true story from here that the world forgot?</p>") +
          '<a class="btn gold" href="/submit/?country=' + encodeURIComponent(c.name) + '">Suggest a story from ' + esc(c.name) + "</a>";
        $(".back-link", panel).addEventListener("click", function () { listCountries(c.continent); });
        var u = new URL(location.href); u.searchParams.set("country", code); history.replaceState(null, "", u);
      }
      svg.addEventListener("click", function (e) {
        var p = e.target.closest("path");
        if (p) showCountry(p.id.slice(2));
      });
      svg.addEventListener("mousemove", function (e) {
        var p = e.target.closest("path");
        if (!p) { tip.style.display = "none"; return; }
        var r = mapWrap.getBoundingClientRect(), n = d.counts[p.id.slice(2)] || 0;
        tip.textContent = p.getAttribute("data-name") + (n ? " · " + n + " stor" + (n === 1 ? "y" : "ies") : "");
        tip.style.left = (e.clientX - r.left) + "px";
        tip.style.top = (e.clientY - r.top) + "px";
        tip.style.display = "block";
      });
      svg.addEventListener("mouseleave", function () { tip.style.display = "none"; });
      tabs.forEach(function (t) {
        t.addEventListener("click", function () {
          var c = t.getAttribute("data-continent");
          setContinent(c === "all" ? null : c);
        });
      });
      var startCountry = params.get("country"), startCont = params.get("continent");
      if (startCountry && byCode(startCountry)) { setContinent(byCode(startCountry).continent, true); showCountry(startCountry); }
      else setContinent(startCont || explore.getAttribute("data-start") || null);
    });
  }

  /* ---------- video facade (YouTube loads only after a click) ---------- */
  $$("[data-youtube]").forEach(function (box) {
    var btn = $("button", box);
    btn.addEventListener("click", function () {
      var id = box.getAttribute("data-youtube");
      box.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0" title="' +
        esc(box.getAttribute("data-title")) + '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    });
  });

  /* ---------- share ---------- */
  $$("[data-copy-link]").forEach(function (b) {
    b.addEventListener("click", function () {
      var done = function () { b.setAttribute("aria-label", "Link copied"); b.title = "Link copied"; b.classList.add("copied"); };
      if (navigator.share && window.matchMedia("(pointer: coarse)").matches) {
        navigator.share({ title: document.title, url: location.href }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(location.href).then(done);
      }
    });
  });

  /* ---------- story submission (Web3Forms) ---------- */
  var form = $("#submit-form");
  if (form) {
    var status = $(".form-status", form);
    ["country", "topic", "type"].forEach(function (k) {
      var v = params.get(k), el = form.elements[k === "topic" ? "story_title" : k];
      if (v && el) el.value = v;
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var key = (window.DTA_CONFIG || {}).web3formsKey || "";
      status.className = "form-status";
      if (!key || key.indexOf("PASTE") === 0) {
        status.textContent = "The form isn't switched on yet. Please email thedeeptimearchive1@gmail.com instead.";
        status.classList.add("err");
        return;
      }
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var fd = new FormData(form);
      fd.append("access_key", key);
      fd.append("subject", "[" + (fd.get("type") || "Story") + "] " + (fd.get("story_title") || "New submission") + " - " + (fd.get("country") || ""));
      fd.append("from_name", "Deep Time Archive website");
      var btn = $("button[type=submit]", form);
      btn.disabled = true; btn.textContent = "Sending...";
      fetch("https://api.web3forms.com/submit", { method: "POST", body: fd })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (!j.success) throw new Error(j.message || "failed");
          form.reset();
          status.textContent = "Thank you! Your story is on its way to us. If we turn it into a video, we'll be in touch.";
          status.classList.add("ok");
        })
        .catch(function () {
          status.textContent = "Sorry - it didn't send. Please try again, or email thedeeptimearchive1@gmail.com.";
          status.classList.add("err");
        })
        .then(function () { btn.disabled = false; btn.textContent = "Send my story"; status.scrollIntoView({ block: "center" }); });
    });
  }

  /* ---------- reveal on scroll ---------- */
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal").forEach(function (el) { el.classList.add("in"); });
  }
})();
