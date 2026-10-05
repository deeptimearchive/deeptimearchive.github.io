# The Deep Time Archive – website

Live at **https://deeptimearchive.github.io** (GitHub Pages, free). Static pages, no cookies, no analytics, no
third-party scripts. Brand: the owner's hourglass logo, parchment/navy/gold.

## What's on it
- **Home** – moving hero slideshow, instant search (countries, stories, categories), trending stories, category
  tiles, an interactive world map, shorts, "submit a story" and "for brands".
- **/stories/** – every story with filters (category, continent, text). **/category/<name>/** – one page per category.
- **/stories/<slug>/** – the article (blog read), the video (YouTube loads only on click), sources, sharing.
- **/explore/** – continent → country → stories. Countries without a story invite a submission.
- **/submit/** – story submissions, delivered by email through Web3Forms.
- **/partner/** (brands), **/about/** (standards), **privacy.html**, **terms.html** (same URLs Google has on file).

## How to add or change a story
1. Edit `content/stories.json` (title, hook, summary, categories, continent, country codes, image, video).
   Country codes are in `assets/data/countries.json` (e.g. `nga` Nigeria, `lby` Libya).
2. For a published story, write the article in `content/articles/<slug>.html`.
3. Put the full-size picture in `assets/img/source/stories/<slug>.jpg`.
4. Run `python build.py` (with the history_factory venv: it has Pillow), check locally, then commit and push.

Status `"coming"` shows a story as *Coming soon*; `"published"` needs an article.

## Settings the owner can change
- `assets/js/config.js` – the **Web3Forms access key** for the submission form (free: web3forms.com, sent to
  thedeeptimearchive1@gmail.com). Without it the form asks people to email instead.

## Rules this site follows
- Every AI picture shows **"AI reconstruction"** and never depicts a real person's face; real photos are credited.
- Articles use only fact-checked claims; what couldn't be confirmed is left out or said to be uncertain.
- Privacy policy sections 2–3 (YouTube API Services, Meta) are required by Google's audit – keep them.

## Preview locally
`python -m http.server 8123` in this folder, then open http://localhost:8123 (root-relative links need a server).

## Tools
- `tools/make_world_map.py` – rebuilds the world map from Natural Earth (public domain).
