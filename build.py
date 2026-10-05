"""Builds the Deep Time Archive website from content/ into plain HTML pages (GitHub Pages serves them as-is).

    python build.py            (needs Pillow for image thumbnails: the history_factory venv has it)

content/stories.json      stories, categories, hero slides
content/articles/<slug>.html   the article text for published stories
content/pages/*.html      privacy and terms bodies
assets/img/source/        full-size images (story pictures and section art) -> resized into assets/img/
"""
import html
import json
import shutil
from datetime import date
from pathlib import Path

SITE = Path(__file__).resolve().parent
CONTENT = SITE / "content"
BASE_URL = "https://deeptimearchive.github.io"
EMAIL = "thedeeptimearchive1@gmail.com"
SOCIAL = {"youtube": "https://www.youtube.com/@DeepTimeArchiveHistory",
          "instagram": "https://www.instagram.com/thedeeptimearchive",
          "facebook": "https://www.facebook.com/thedeeptimearchive"}
CONTINENTS = {"africa": "Africa", "asia": "Asia", "europe": "Europe", "north-america": "North America",
              "south-america": "South America", "oceania": "Oceania"}
QUICK_SEARCHES = ["Nigeria", "Libya", "Egypt", "Mali", "Morocco", "United Kingdom", "United States", "Japan",
                  "ghost ship", "impostor", "smuggling", "empire"]
e = html.escape

ICON = {
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "left": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>',
    "right": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "play": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.5-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5Z"/></svg>',
    "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5Z"/><path d="M4 19a2 2 0 0 1 2-2h13"/></svg>',
    "youtube": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8ZM9.7 15.1V8.9l5.8 3.1-5.8 3.1Z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 21v-7.5H16l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4a21 21 0 0 0-2.3-.1c-2.3 0-3.9 1.4-3.9 4v2.2H8v3h2.4V21h3.1Z"/></svg>',
    "x": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.8 3h3.1l-6.8 7.8L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.3-8.3L2 3h6.4l4.4 5.8L17.8 3Zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5Z"/></svg>',
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.8 14.2c-.2.7-1.4 1.3-2 1.4-.5.1-1.2.1-1.9-.1-.4-.1-1-.3-1.7-.6a13 13 0 0 1-5-4.4c-.4-.5-1-1.5-1-2.8s.7-2 1-2.3a1 1 0 0 1 .7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.1 1 2.1 1.3 2.4 1.5.3.1.5.1.6-.1l.9-1.1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.2.1.8-.1 1.4Z"/></svg>',
    "link": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s7-6.1 7-11.5A7 7 0 0 0 5 9.5C5 14.9 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
}


# ---------------------------------------------------------------- data
def dashes(text):
    """' - ' typed as a dash becomes a real en dash."""
    return text.replace(" - ", " – ")


def load():
    data = json.loads(dashes((CONTENT / "stories.json").read_text(encoding="utf-8")))
    countries = json.loads((SITE / "assets" / "data" / "countries.json").read_text(encoding="utf-8"))
    by_code = {c["code"]: c for c in countries}
    cats = {c["slug"]: c for c in data["categories"]}
    for s in data["stories"]:
        unknown = [c for c in s["countries"] if c not in by_code]
        if unknown:
            raise SystemExit(f"{s['slug']}: unknown country code(s) {unknown} - see assets/data/countries.json")
        s["url"] = f"/stories/{s['slug']}/"
        s["country_names"] = [by_code[c]["name"] for c in s["countries"]]
        s["cat_names"] = [cats[c]["name"] for c in s["categories"]]
        s["thumb"] = thumb_of(s["image"]["src"])
        art = CONTENT / "articles" / f"{s['slug']}.html"
        s["body"] = dashes(art.read_text(encoding="utf-8")) if art.exists() else None
        if s["status"] == "published" and not s["body"]:
            raise SystemExit(f"{s['slug']} is published but content/articles/{s['slug']}.html is missing")
    # published first (newest first), then coming soon
    data["stories"].sort(key=lambda s: (s["status"] != "published", s.get("date", "") and -int(s["date"].replace("-", ""))))
    return data, countries, by_code, cats


def thumb_of(src):
    return src.replace("/assets/img/", "/assets/img/thumbs/")


def prepare_images():
    """assets/img/source/<folder>/<name>.jpg -> assets/img/<folder>/<name>.jpg (max 1600 wide) + thumbs (640 wide)."""
    from PIL import Image
    src_root = SITE / "assets" / "img" / "source"
    for src in src_root.rglob("*.jpg"):
        rel = src.relative_to(src_root)
        for out, width, q in ((SITE / "assets" / "img" / rel, 1600, 84), (SITE / "assets" / "img" / "thumbs" / rel, 640, 80)):
            if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            im = Image.open(src).convert("RGB")
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            im.save(out, "JPEG", quality=q, optimize=True, progressive=True)


# ---------------------------------------------------------------- layout
def head(title, desc, path, image="/images/brand/og-image.jpg", kind="website", extra=""):
    full = title if "Deep Time Archive" in title else f"{title} | The Deep Time Archive"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(full)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{BASE_URL}{path}">
  <meta property="og:site_name" content="The Deep Time Archive">
  <meta property="og:type" content="{kind}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{BASE_URL}{path}">
  <meta property="og:image" content="{BASE_URL}{image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#091321">
  <link rel="icon" href="/images/brand/icon-32.png" sizes="32x32" type="image/png">
  <link rel="apple-touch-icon" href="/images/brand/icon-180.png">
  <link rel="preload" href="/fonts/Cinzel.ttf" as="font" type="font/ttf" crossorigin>
  <link rel="stylesheet" href="/assets/css/site.css">
  {extra}
</head>"""


NAV = [("/stories/", "Stories"), ("/category/crime/", "Crime"), ("/category/politics/", "Politics"),
       ("/category/military/", "Military"), ("/category/strange/", "Strange"), ("/explore/", "Explore the world")]


def header(active=""):
    links = "".join(f'<a href="{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a>'
                    for href, label in NAV)
    return f"""<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="The Deep Time Archive - home">
      <img src="/images/brand/emblem-on-dark.png" alt="" width="40" height="40">
      <span>Deep Time<small>Archive</small></span>
    </a>
    <nav class="nav" id="nav" aria-label="Main">{links}</nav>
    <div class="header-actions">
      <button class="icon-btn" type="button" data-open-search aria-label="Search stories and countries (press /)">{ICON['search']}</button>
      <a class="btn gold" href="/submit/">Submit a story</a>
      <button class="icon-btn menu-btn" type="button" aria-controls="nav" aria-expanded="false" aria-label="Menu">{ICON['menu']}</button>
    </div>
  </div>
</header>
<div class="search-overlay" role="dialog" aria-modal="true" aria-label="Search">
  <div class="search-panel">
    <label class="search-field">{ICON['search']}<span class="sr-only">Search</span>
      <input type="search" placeholder="Search a country, a story, a name..." autocomplete="off"></label>
    <div class="search-results" aria-live="polite"></div>
    <div class="search-hints"><b>Try:</b>{''.join(f'<button class="chip" type="button" data-search-term="{e(q)}">{e(q)}</button>' for q in QUICK_SEARCHES[:8])}</div>
  </div>
</div>
<main id="main">"""


def footer(cats):
    cat_links = "".join(f'<li><a href="/category/{c["slug"]}/">{e(c["name"])}</a></li>' for c in cats.values())
    cont_links = "".join(f'<li><a href="/explore/?continent={k}">{v}</a></li>' for k, v in CONTINENTS.items())
    socials = "".join(f'<a href="{url}" rel="noopener" aria-label="{name.title()}">{ICON[name]}</a>' for name, url in SOCIAL.items())
    return f"""</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <img class="footer-logo" src="/images/brand/logo-full-on-dark.png" alt="The Deep Time Archive - True stories history almost forgot" width="260" loading="lazy">
        <p>Strange-but-true stories, crime, power and war from every corner of the world - researched, sourced and told for people who can't stop at one.</p>
        <div class="socials">{socials}</div>
      </div>
      <div><h4>Categories</h4><ul>{cat_links}</ul></div>
      <div><h4>Explore</h4><ul>{cont_links}</ul></div>
      <div><h4>The Archive</h4><ul>
        <li><a href="/stories/">All stories</a></li>
        <li><a href="/submit/">Submit a story</a></li>
        <li><a href="/partner/">For brands</a></li>
        <li><a href="/about/">How we work</a></li>
        <li><a href="mailto:{EMAIL}">Contact</a></li>
      </ul></div>
    </div>
    <div class="footer-base">
      <span>© {date.today().year} The Deep Time Archive · AI reconstructions are labelled</span>
      <span><a href="/privacy.html">Privacy policy</a> · <a href="/terms.html">Terms of use</a></span>
    </div>
  </div>
</footer>
<script src="/assets/js/config.js"></script>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def page(title, desc, path, body, cats, active="", image="/images/brand/og-image.jpg", kind="website", extra=""):
    return head(title, desc, path, image, kind, extra) + "\n" + header(active) + body + footer(cats)


def write(rel, text):
    out = SITE / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- components
def label_for(img):
    if img.get("ai"):
        return '<span class="ai-label">AI reconstruction</span>'
    return ""


def card(s, lazy=True):
    status = '<span class="badge gold">Coming soon</span>' if s["status"] == "coming" else ""
    if s["status"] == "published" and s.get("video"):
        status += f'<span class="badge">{ICON["play"].replace("<svg", "<svg width=10 height=10")} Watch</span>'
    meta = (f'<span>{e(s["era"])}</span><span>{e(s["place"])}</span>' +
            (f'<span>{s["read_minutes"]} min read</span>' if s.get("read_minutes") else ""))
    text = " ".join([s["title"], s["hook"], s["summary"], s["place"], s["era"], *s["country_names"], *s["cat_names"],
                     *s.get("keywords", [])]).lower()
    import unicodedata
    text = "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")
    return f"""<a class="card{' coming' if s['status'] == 'coming' else ''}" href="{s['url']}" data-card data-cats="{' '.join(s['categories'])}" data-continent="{s['continent']}" data-text="{e(text)}">
  <div class="card-media"><img src="{s['thumb']}" alt="{e(s['image']['alt'])}" width="640" height="360"{' loading="lazy"' if lazy else ''}>
    <div class="badges">{status}</div>{label_for(s['image'])}</div>
  <div class="card-body"><span class="tag">{e(' · '.join(s['cat_names'][:2]))}</span><h3>{e(s['title'])}</h3><p>{e(s['hook'])}</p>
    <div class="card-meta">{meta}</div></div>
</a>"""


def empty_state(what):
    return f"""<div class="empty" data-empty hidden><h3>No stories here yet</h3>
  <p>We're working on {e(what)}. Know a true story the world forgot? Tell us - if we make it, we'll credit you.</p>
  <a class="btn gold" href="/submit/">Suggest a story</a></div>"""


def submit_band():
    return f"""<section class="section tight"><div class="wrap">
  <div class="cta-band reveal">
    <img class="emblem" src="/images/brand/emblem-on-dark.png" alt="" loading="lazy">
    <div><p class="eyebrow">Your story, our next video</p>
      <h2>Know a story the world forgot?</h2>
      <p>A strange crime from your hometown. A coup your grandparents lived through. A legend that turned out to be true.
        Send it in - if we make it into a video, we'll credit you on screen.</p></div>
    <div class="actions"><a class="btn gold" href="/submit/">Submit a story {ICON['arrow']}</a>
      <a class="btn light" href="/explore/">Browse by country</a></div>
  </div></div></section>"""


def explore_block(start=""):
    tabs = '<button type="button" data-continent="all" aria-pressed="true">World</button>' + "".join(
        f'<button type="button" data-continent="{k}" aria-pressed="false">{v}</button>' for k, v in CONTINENTS.items())
    return f"""<div class="explore" data-explore data-start="{start}">
  <div><div class="continent-tabs" role="group" aria-label="Choose a continent">{tabs}</div>
    <div class="map-wrap"><div class="map-tip" aria-hidden="true"></div></div></div>
  <div class="country-panel" aria-live="polite"><p class="muted">Loading the map...</p></div>
</div>"""


# ---------------------------------------------------------------- pages
def home(data, cats):
    stories, by_slug = data["stories"], {s["slug"]: s for s in data["stories"]}
    slides, texts, dots, labels, first_img = [], [], [], [], None
    for i, h in enumerate(data["hero"]):
        if "story" in h:
            s = by_slug[h["story"]]
            img, link = s["image"], s["url"]
            if s["status"] == "published":
                btns = (f'<a class="btn gold" href="{link}#watch">{ICON["play"]} Watch the story</a>' if s.get("video") else "") + \
                       f'<a class="btn light" href="{link}">{ICON["book"]} Read in {s.get("read_minutes", 4)} min</a>'
            else:
                btns = f'<a class="btn gold" href="{link}">{ICON["arrow"]} First look</a>' \
                       f'<a class="btn light" href="{SOCIAL["youtube"]}" rel="noopener">Follow to get it first</a>'
        else:
            c = cats[h["category"]]
            img = {"src": c["image"], "alt": c["name"], "ai": c.get("image_ai")}
            btns = f'<a class="btn gold" href="/category/{c["slug"]}/">{ICON["arrow"]} Explore {e(c["name"])}</a>'
        src = img["src"]
        first_img = first_img or src
        attr = f'src="{src}" fetchpriority="high"' if i == 0 else f'data-src="{src}" src="{thumb_of(src)}"'
        slides.append(f'<div class="slide{" active" if i == 0 else ""}"><div class="slide-media"><img {attr} alt="{e(img["alt"])}"></div></div>')
        texts.append(f'<div class="hero-text"{" hidden" if i else ""}><p class="eyebrow">{e(h["eyebrow"])}</p>'
                     f'<h1>{h["headline"]}</h1><p class="sub">{e(h["sub"])}</p><div class="buttons">{btns}</div></div>')
        dots.append(f'<button class="dot{" active" if i == 0 else ""}" type="button" aria-label="Slide {i + 1}"><span></span></button>')
        lab = '<span class="ai-label">AI reconstruction</span>' if img.get("ai") else \
            (f'<span class="photo-credit">{e(img.get("credit", ""))}</span>' if img.get("credit") else "")
        if lab:
            labels.append(f'<div data-slide-label="{i}"{" hidden" if i else ""}>{lab}</div>')

    trending = [s for s in stories if s.get("trending")] + [s for s in stories if not s.get("trending")]
    published = [s for s in stories if s["status"] == "published"]
    feature = next((s for s in published if not s.get("video")), published[0] if published else None)
    counts = {c: sum(1 for s in stories if c in s["categories"]) for c in cats}
    cat_tiles = "".join(f"""<a class="cat reveal" href="/category/{c['slug']}/"><img src="{thumb_of(c['image']) if i else c['image']}" alt="" loading="lazy">
  {'<span class="ai-label">AI reconstruction</span>' if c.get('image_ai') else ''}
  <div class="cat-body"><h3>{e(c['name'])}</h3><p>{e(c['tagline'])}</p>
  <span class="count">{f"{counts[c['slug']]} stor{'y' if counts[c['slug']] == 1 else 'ies'}" if counts[c['slug']] else 'First stories coming'} →</span></div></a>"""
                        for i, c in enumerate(cats.values()))
    shorts = []
    for s in stories:
        for platform, url in (s.get("short") or {}).items():
            shorts.append(f"""<a class="short" href="{url}" rel="noopener"><img src="{s['thumb']}" alt="" loading="lazy">
  <span class="play">{ICON['play']}</span><div class="s-body"><span class="tag" style="color:var(--gold-2)">{'Instagram' if platform == 'instagram' else 'YouTube Shorts'}</span>
  <strong>{e(s['hook'])}</strong></div></a>""")
    shorts += [f"""<a class="short platform" href="{SOCIAL[p]}" rel="noopener"><div class="s-body"><span class="play" style="position:static;transform:none;margin:0 auto 14px">{ICON[p]}</span>
  <strong>Follow on {name}</strong><span style="font-size:14px;color:rgba(245,238,223,.75)">New strange-but-true stories every week</span></div></a>"""
               for p, name in (("youtube", "YouTube"), ("instagram", "Instagram"), ("facebook", "Facebook"))]

    body = f"""
<section class="hero" data-slider aria-roledescription="carousel" aria-label="Featured stories">
  {''.join(slides)}
  <div class="hero-content"><div class="wrap"><div class="hero-copy">{''.join(texts)}</div></div></div>
  {''.join(labels)}
  <div class="hero-controls"><div class="wrap"><div class="dots">{''.join(dots)}</div>
    <div class="hero-arrows"><button class="icon-btn" type="button" data-prev aria-label="Previous story">{ICON['left']}</button>
    <button class="icon-btn" type="button" data-next aria-label="Next story">{ICON['right']}</button></div></div></div>
</section>

<div class="search-band"><div class="wrap">
  <form class="search-box" id="home-search-form" role="search">{ICON['search']}
    <label class="sr-only" for="home-search">Search</label>
    <input id="home-search" type="search" placeholder="Search a country, a story, a name..." autocomplete="off">
    <button class="btn gold" type="submit"><span>Search</span>{ICON['arrow']}</button></form>
  <div class="quick">{''.join(f'<button class="chip" type="button" data-search-term="{e(q)}">{e(q)}</button>' for q in QUICK_SEARCHES)}</div>
</div></div>

<section class="section"><div class="wrap">
  <div class="section-head reveal"><div><p class="eyebrow">Trending on the Archive</p><h2>Strange. True. Unforgettable.</h2>
    <p>The stories people can't stop reading - from ghost ships to impossible conquests.</p></div>
    <a class="link-more" href="/stories/">All stories {ICON['arrow']}</a></div>
  <div class="rail">{''.join(card(s) for s in trending)}</div>
</div></section>

{f'''<section class="section tight"><div class="wrap">
  <a class="feature-card reveal" href="{feature['url']}"><div class="card-media"><img src="{feature['image']['src']}" alt="{e(feature['image']['alt'])}" loading="lazy">{label_for(feature['image'])}</div>
  <div class="fc-body"><span class="tag">Long read · {e(feature['cat_names'][0])}</span><h3>{e(feature['title'])}</h3><p>{e(feature['summary'])}</p>
  <span class="btn gold" style="align-self:flex-start;margin-top:8px">{ICON['book']} Read the story</span></div></a>
</div></section>''' if feature else ''}

<section class="section"><div class="wrap">
  <div class="section-head reveal"><div><p class="eyebrow">Choose your obsession</p><h2>Crime, power, war - and the truly strange</h2></div></div>
  <div class="cats">{cat_tiles}</div>
</div></section>

<section class="section dark map-band"><div class="wrap">
  <div class="section-head reveal"><div><p class="eyebrow">Explore the world</p><h2>Pick a continent. Pick a country.</h2>
    <p>Every country has a story history almost forgot. Gold countries already have one on the Archive - click any other to suggest the first.</p></div>
    <a class="link-more" href="/explore/" style="color:var(--gold-2)">Full map {ICON['arrow']}</a></div>
  {explore_block()}
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head reveal"><div><p class="eyebrow">Short on time?</p><h2>Stories in under three minutes</h2>
    <p>Vertical shorts for the scroll - then the full story on YouTube.</p></div></div>
  <div class="shorts">{''.join(shorts)}</div>
</div></section>

{submit_band()}

<section class="section"><div class="wrap split">
  <div class="panel reveal"><p class="eyebrow">For brands</p><h3>Reach the people who stay for the whole story</h3>
    <p>True crime, power and strange-but-true history hold attention like little else online. Partner with a channel built for curious 18-34-year-olds on YouTube, Instagram and Facebook.</p>
    <a class="btn" href="/partner/">Work with us {ICON['arrow']}</a></div>
  <div class="panel reveal"><p class="eyebrow">How we work</p><h3>Wild stories. Real sources.</h3>
    <p>Every claim is checked against independent sources. Legends are called legends, AI pictures are labelled, and a person approves every video.</p>
    <a class="btn" href="/about/">Our standards {ICON['arrow']}</a></div>
</div></section>
"""
    return page("The Deep Time Archive - True stories history almost forgot",
                "Strange-but-true stories, true crime, coups, dictators and military history from every country - "
                "watch the videos or read the stories. Search by country or continent.",
                "/", body, cats, extra=f'<link rel="preload" as="image" href="{first_img}">')


def listing_page(title, eyebrow, intro, path, stories, cats, active, bg=None, cat_filter=True, empty_what="these stories"):
    chips = ""
    if cat_filter:
        chips = '<button class="chip" type="button" data-filter-cat="all" aria-pressed="true">All</button>' + "".join(
            f'<button class="chip" type="button" data-filter-cat="{c["slug"]}">{e(c["name"])}</button>' for c in cats.values())
    conts = '<option value="all">Every continent</option>' + "".join(f'<option value="{k}">{v}</option>' for k, v in CONTINENTS.items())
    body = f"""
<section class="page-hero">{f'<img class="bg" src="{bg}" alt="">' if bg else ''}<div class="wrap">
  <div class="crumbs"><a href="/">Home</a> / {e(title)}</div>
  <p class="eyebrow">{e(eyebrow)}</p><h1>{e(title)}</h1><p>{e(intro)}</p></div></section>
<section class="section tight"><div class="wrap" data-listing>
  <div class="filters">
    <label class="search-inline">{ICON['search']}<span class="sr-only">Filter stories</span><input id="filter-q" type="search" placeholder="Filter by name, country, year..."></label>
    <select id="filter-continent" class="chip" aria-label="Continent">{conts}</select>
  </div>
  {f'<div class="filters">{chips}</div>' if chips else ''}
  <div class="grid-cards">{''.join(card(s) for s in stories)}</div>
  {empty_state(empty_what)}
</div></section>
{submit_band()}"""
    return page(title, intro, path, body, cats, active=active, image=(bg or "/images/brand/og-image.jpg"))


def story_page(s, data, cats):
    img = s["image"]
    chips = "".join(f'<a class="chip" href="/category/{c}/">{e(cats[c]["name"])}</a>' for c in s["categories"])
    places = ", ".join(f'<a href="/explore/?country={code}" style="color:inherit">{e(name)}</a>'
                       for code, name in zip(s["countries"], s["country_names"]))
    credit = '<span class="ai-label">AI reconstruction - not a photograph</span>' if img.get("ai") else \
        f'<span class="photo-credit">{e(img.get("credit", ""))}</span>'
    if s.get("video"):
        vid = s["video"]["youtube"]
        media = f"""<div class="video-embed" id="watch" data-youtube="{vid}" data-title="{e(s['title'])}">
  <button type="button" aria-label="Play the video: {e(s['title'])}"><img src="{img['src']}" alt="" loading="lazy">
  <span class="play">{ICON['play']}</span><span class="note">Plays from YouTube (privacy-enhanced mode) when you press play.</span></button></div>"""
    elif s["status"] == "published":
        media = f"""<div class="coming-box" id="watch"><h3>The video is in production</h3><p>Read the story now - and follow us to see it first when it lands.</p>
  <a class="btn gold" href="{SOCIAL['youtube']}" rel="noopener">{ICON['youtube']} Follow on YouTube</a></div>"""
    else:
        media = ""
    if s["status"] == "published":
        main = s["body"]
    else:
        main = f"""<p class="dropcap">{e(s['summary'])}</p>
<div class="coming-box"><h3>Coming soon to the Archive</h3><p>We're researching and fact-checking this story now. Follow us and be the first to watch it.</p>
<div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn gold" href="{SOCIAL['youtube']}" rel="noopener">{ICON['youtube']} YouTube</a>
<a class="btn light" href="{SOCIAL['instagram']}" rel="noopener">{ICON['instagram']} Instagram</a></div></div>"""
    url = BASE_URL + s["url"]
    share = f"""<div class="share">
  <a href="https://wa.me/?text={e(s['title'])}%20{url}" rel="noopener" aria-label="Share on WhatsApp">{ICON['whatsapp']}</a>
  <a href="https://twitter.com/intent/tweet?text={e(s['title'])}&url={url}" rel="noopener" aria-label="Share on X">{ICON['x']}</a>
  <a href="https://www.facebook.com/sharer/sharer.php?u={url}" rel="noopener" aria-label="Share on Facebook">{ICON['facebook']}</a>
  <button type="button" data-copy-link aria-label="Copy link">{ICON['link']}</button></div>"""
    sources = ""
    if s.get("sources"):
        sources = '<div class="side-box"><h4>Sources</h4><ol class="sources">' + "".join(
            f'<li><a href="{e(x["url"])}" rel="noopener">{e(x["label"])}</a></li>' for x in s["sources"]) + "</ol></div>"
    related = [r for r in data["stories"] if r["slug"] != s["slug"] and
               (set(r["categories"]) & set(s["categories"]) or r["continent"] == s["continent"])][:3] or \
              [r for r in data["stories"] if r["slug"] != s["slug"]][:3]
    body = f"""
<article>
<header class="article-hero"><img class="bg" src="{img['src']}" alt="{e(img['alt'])}">{credit}
  <div class="wrap"><div class="crumbs"><a href="/">Home</a> / <a href="/stories/">Stories</a> / {e(s['cat_names'][0])}</div>
    <h1>{e(s['title'])}</h1><p class="hook">{e(s['hook'])}</p>
    <div class="article-meta">{chips}<span>{ICON['pin'].replace('<svg', '<svg width=15 height=15')} {places}</span><span>{e(s['era'])}</span>
    {f"<span>{s['read_minutes']} min read</span>" if s.get('read_minutes') else '<span>Coming soon</span>'}</div></div>
</header>
<div class="article-layout">
  <div>{media}<div class="prose">{main}</div></div>
  <aside class="sidebar"><div class="sticky-side">
    <div class="side-box"><h4>At a glance</h4><ul class="facts">
      <li><span>Where</span><span>{e(s['place'])}</span></li><li><span>When</span><span>{e(s['era'])}</span></li>
      <li><span>Category</span><span>{e(', '.join(s['cat_names']))}</span></li>
      <li><span>Status</span><span>{'Fact-checked' if s['status'] == 'published' else 'In research'}</span></li></ul></div>
    <div class="side-box"><h4>Share this story</h4>{share}</div>
    {sources}
    <div class="side-box"><h4>Got a story like this?</h4><p style="font-size:15px;color:var(--ink-2);margin:0 0 12px">Tell us a true story from your country.</p>
      <a class="btn gold" href="/submit/?country={e(s['country_names'][0])}">Submit a story</a></div>
  </div></aside>
</div>
</article>
<section class="section tight" style="background:var(--paper-2)"><div class="wrap">
  <div class="section-head"><div><p class="eyebrow">Keep going</p><h2>You might also like</h2></div></div>
  <div class="grid-cards">{''.join(card(r) for r in related)}</div></div></section>"""
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": s["title"], "description": s["summary"],
          "image": BASE_URL + img["src"], "author": {"@type": "Organization", "name": "The Deep Time Archive"},
          "publisher": {"@type": "Organization", "name": "The Deep Time Archive",
                        "logo": {"@type": "ImageObject", "url": BASE_URL + "/images/brand/icon-512.png"}}}
    if s.get("date"):
        ld["datePublished"] = s["date"]
    extra = f'<script type="application/ld+json">{json.dumps(ld)}</script>'
    return page(s["title"], s["summary"], s["url"], body, cats, image=img["src"], kind="article", extra=extra)


def explore_page(data, cats):
    body = f"""
<section class="page-hero"><img class="bg" src="/assets/img/art/explore.jpg" alt=""><span class="ai-label">AI reconstruction</span><div class="wrap">
  <div class="crumbs"><a href="/">Home</a> / Explore the world</div>
  <p class="eyebrow">Explore the world</p><h1>History, country by country</h1>
  <p>Choose a continent, then a country, to find its stories. No story yet? Be the one who suggests it.</p></div></section>
<section class="section dark map-band"><div class="wrap">{explore_block()}</div></section>
{submit_band()}"""
    return page("Explore the world", "Find strange-but-true stories, crime and history by continent and country.",
                "/explore/", body, cats, active="/explore/", image="/assets/img/art/explore.jpg")


def submit_page(cats, countries):
    opts = '<option value="">Choose a country</option>' + "".join(f'<option>{e(c["name"])}</option>' for c in countries) + \
        '<option>Several countries / at sea</option>'
    body = f"""
<section class="page-hero"><img class="bg" src="/assets/img/art/strange.jpg" alt=""><span class="ai-label">AI reconstruction</span><div class="wrap">
  <div class="crumbs"><a href="/">Home</a> / Submit a story</div>
  <p class="eyebrow">Your story, our next video</p><h1>Tell us a story history almost forgot</h1>
  <p>A crime nobody believes. A coup your family lived through. A legend from your town that turned out to be true. If we make it, we'll credit you.</p></div></section>
<section class="section tight"><div class="wrap split" style="align-items:start">
  <form class="panel form" id="submit-form" novalidate>
    <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
    <div class="field"><label for="f-type">What are you sending?</label>
      <select id="f-type" name="type"><option>Story idea</option><option>Correction</option><option>Brand partnership</option><option>Other</option></select></div>
    <div class="row">
      <div class="field"><label for="f-name">Your name <span class="hint">(as you'd like to be credited)</span></label><input id="f-name" name="name" required maxlength="80" autocomplete="name"></div>
      <div class="field"><label for="f-email">Email <span class="hint">(so we can reply)</span></label><input id="f-email" name="email" type="email" required maxlength="120" autocomplete="email"></div>
    </div>
    <div class="row">
      <div class="field"><label for="f-country">Country</label><select id="f-country" name="country">{opts}</select></div>
      <div class="field"><label for="f-title">Story title</label><input id="f-title" name="story_title" required maxlength="120" placeholder="e.g. The bank robbery that..."></div>
    </div>
    <div class="field"><label for="f-story">The story <span class="hint">(what happened, when, who - the stranger the better)</span></label>
      <textarea id="f-story" name="message" required maxlength="5000"></textarea></div>
    <div class="field"><label for="f-source">Where can we check it? <span class="hint">(optional: a link, book, newspaper)</span></label><input id="f-source" name="source" maxlength="300"></div>
    <label class="check"><input type="checkbox" name="credit_ok" value="yes" checked> Credit me by name if you make a video from my story.</label>
    <label class="check"><input type="checkbox" name="consent" value="yes" required> I agree that The Deep Time Archive may use this idea for its videos and articles, and I've read the <a href="/privacy.html#submissions">privacy policy</a>.</label>
    <div class="form-status" role="status"></div>
    <button class="btn gold" type="submit" style="justify-self:start">Send my story</button>
  </form>
  <div class="panel"><h3>What happens next</h3><ol class="steps-mini">
    <li><b>1</b><div><strong>We read every story.</strong><p>Your message goes straight to our inbox.</p></div></li>
    <li><b>2</b><div><strong>We check the facts.</strong><p>We look for independent sources. Rumours and accusations against people never found guilty stay out.</p></div></li>
    <li><b>3</b><div><strong>It becomes a video.</strong><p>If the story holds up, we research it fully and make it - and credit you if you'd like.</p></div></li>
  </ol>
  <p style="margin-top:22px;font-size:15px;color:var(--ink-3)">Prefer email? <a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
</div></section>"""
    return page("Submit a story", "Send The Deep Time Archive a true story from your country - crime, politics, war or the strangely true.",
                "/submit/", body, cats)


def partner_page(cats):
    body = f"""
<section class="page-hero"><img class="bg" src="/assets/img/art/politics.jpg" alt=""><span class="ai-label">AI reconstruction</span><div class="wrap">
  <div class="crumbs"><a href="/">Home</a> / For brands</div>
  <p class="eyebrow">For brands &amp; partners</p><h1>Stories people stay for</h1>
  <p>True crime, power and strange-but-true history are some of the most watched - and most finished - stories online. Put your brand where the attention is.</p></div></section>
<section class="section"><div class="wrap split">
  <div class="panel"><h3>Who watches</h3>
    <p>Curious 18-34-year-olds who live on YouTube, Instagram and Facebook - the audience that binges documentaries, shares the wildest stories with friends and comes back for the next one.</p>
    <div class="stats"><div class="stat"><b>3</b><span>platforms</span></div><div class="stat"><b>8+ min</b><span>main videos</span></div><div class="stat"><b>Weekly</b><span>new stories</span></div></div>
    <p>Every story ships as a full YouTube documentary plus vertical shorts - so your message travels across long-form and the scroll.</p></div>
  <div class="panel"><h3>Ways to work together</h3><ul style="margin:0;padding-left:20px;color:var(--ink-2)">
    <li><strong>Integrated sponsorship</strong> - a read in the main video, plus links in descriptions.</li>
    <li><strong>Story series</strong> - sponsor a run of stories around a country, era or theme.</li>
    <li><strong>Shorts packages</strong> - placements across YouTube Shorts, Reels and Facebook.</li>
    <li><strong>Education &amp; tourism</strong> - history-led stories for museums, travel and learning brands.</li></ul>
    <p style="margin-top:16px">Brand-safe by design: fact-checked, no gore, no accusations beyond the court record.</p>
    <a class="btn gold" href="/submit/?type=Brand%20partnership">Request our media kit {ICON['arrow']}</a></div>
</div></section>"""
    return page("For brands", "Partner with The Deep Time Archive - true crime, power and strange-but-true history for a curious 18-34 audience.",
                "/partner/", body, cats)


def about_page(cats):
    body = f"""
<section class="page-hero"><img class="bg" src="/assets/img/art/explore.jpg" alt=""><span class="ai-label">AI reconstruction</span><div class="wrap">
  <div class="crumbs"><a href="/">Home</a> / How we work</div>
  <p class="eyebrow">Our standards</p><h1>Wild stories. Real sources.</h1>
  <p>Every story starts with research. If a detail isn't supported by the sources, it doesn't go in.</p></div></section>
<section class="section"><div class="wrap" style="max-width:860px"><ol class="steps-mini">
  <li><b>1</b><div><strong>Sources first.</strong><p>We work from credible sources - scholarship, archives, contemporary reporting and recorded oral history - and list them with every story.</p></div></li>
  <li><b>2</b><div><strong>Claims are checked one by one.</strong><p>Each fact is checked against independent sources. Legends are called legends; disputed or uncertain details are described that way - and what we couldn't confirm, we say.</p></div></li>
  <li><b>3</b><div><strong>True crime with care.</strong><p>We state guilt only where a court found it, we don't cover cases still in the courts, and we remember victims as people, not plot points.</p></div></li>
  <li><b>4</b><div><strong>Open about our tools.</strong><p>We use AI tools to help draft scripts, to narrate (the voice in our videos is an AI voice) and to paint scenes where no photograph exists. AI pictures are always labelled "AI reconstruction" and never show a real person's face. A person reviews and approves every video before it is published.</p></div></li>
  <li><b>5</b><div><strong>Corrections are welcome.</strong><p>If we got something wrong, <a href="/submit/?type=Correction">tell us</a> - we correct the record and say so.</p></div></li>
</ol></div></section>
{submit_band()}"""
    return page("How we work", "How The Deep Time Archive researches, fact-checks and makes its stories - and how we use AI.",
                "/about/", body, cats)


def legal_page(name, title, desc, cats):
    body = '<div class="doc"><div class="wrap">' + dashes((CONTENT / "pages" / f"{name}.html").read_text(encoding="utf-8")) + "</div></div>"
    return page(title, desc, f"/{name}.html", body, cats)


def not_found(cats):
    body = f"""<section class="section"><div class="wrap" style="text-align:center;max-width:640px">
  <img src="/images/brand/emblem.png" alt="" width="140" style="margin:0 auto 20px">
  <h1>Lost to history</h1><p>This page has vanished - like the crew of the Joyita. Try a search, or start from the beginning.</p>
  <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap"><button class="btn gold" type="button" data-open-search>{ICON['search']} Search</button>
  <a class="btn" href="/">Home</a></div></div></section>"""
    return page("Page not found", "This page doesn't exist.", "/404.html", body, cats)


# ---------------------------------------------------------------- build
def main():
    prepare_images()
    data, countries, by_code, cats = load()
    stories = data["stories"]
    write("index.html", home(data, cats))
    write("stories/index.html", listing_page("All stories", "The Archive", "Crime, power, war and the strangely true - from every continent. Filter by category, continent or name.",
                                            "/stories/", stories, cats, "/stories/", bg="/assets/img/art/mysteries.jpg"))
    for c in cats.values():
        in_cat = [s for s in stories if c["slug"] in s["categories"]]
        write(f"category/{c['slug']}/index.html",
              listing_page(c["name"], "Category", c["tagline"], f"/category/{c['slug']}/", in_cat, cats,
                           f"/category/{c['slug']}/", bg=c["image"], cat_filter=False, empty_what=c["name"].lower() + " stories"))
    for s in stories:
        write(f"stories/{s['slug']}/index.html", story_page(s, data, cats))
    write("explore/index.html", explore_page(data, cats))
    write("submit/index.html", submit_page(cats, countries))
    write("partner/index.html", partner_page(cats))
    write("about/index.html", about_page(cats))
    write("privacy.html", legal_page("privacy", "Privacy Policy", "How The Deep Time Archive, its website and its publishing tool handle data, including YouTube API Services and Meta.", cats))
    write("terms.html", legal_page("terms", "Terms of Use", "Terms of use for The Deep Time Archive website and content.", cats))
    write("404.html", not_found(cats))

    counts = {}
    for s in stories:
        for code in s["countries"]:
            counts[code] = counts.get(code, 0) + 1
    index = {"stories": [{"slug": s["slug"], "title": s["title"], "hook": s["hook"], "summary": s["summary"],
                          "url": s["url"], "thumb": s["thumb"], "status": s["status"], "era": s["era"], "place": s["place"],
                          "continent": s["continent"], "countries": s["countries"], "countryNames": s["country_names"],
                          "categories": s["categories"], "catNames": s["cat_names"], "keywords": s.get("keywords", []),
                          "video": bool(s.get("video"))} for s in stories],
             "countries": countries, "counts": counts, "continentNames": CONTINENTS,
             "categories": [{"slug": c["slug"], "name": c["name"]} for c in cats.values()]}
    write("assets/data/search.json", json.dumps(index, ensure_ascii=False, separators=(",", ":")))

    urls = ["/", "/stories/", "/explore/", "/submit/", "/partner/", "/about/", "/privacy.html", "/terms.html"] + \
        [f"/category/{c}/" for c in cats] + [s["url"] for s in stories]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"  <url><loc>{BASE_URL}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    print(f"built {len(urls)} pages, {len(stories)} stories, {len(counts)} countries with stories")


if __name__ == "__main__":
    main()
