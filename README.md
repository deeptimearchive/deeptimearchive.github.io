# Deep Time Archive - website

Static site (no build step, no JavaScript, no cookies): `index.html`, `privacy.html`, `terms.html`, `styles.css`,
self-hosted fonts in `fonts/` (SIL Open Font License, licence files included), `favicon.svg`.

## Why it exists
- Google OAuth "Publish app" needs a homepage + privacy policy URL (otherwise the YouTube login expires every 7 days).
- YouTube's API compliance audit (needed for automatic *public* uploads) asks for a privacy policy that covers
  YouTube API Services - `privacy.html` is written to those requirements (YouTube ToS link, Google Privacy Policy
  link, what is accessed/stored/shared, revocation via Google security settings, deletion within 7 days).
- Meta asks for a privacy policy URL for apps too - same page.

## Preview locally
From the history_factory venv: `python -m http.server 8123 --directory .` then open http://localhost:8123

## Publish (GitHub Pages, free)
1. Create a GitHub repository and push these files to it.
2. Repository -> Settings -> Pages -> Source: "Deploy from a branch" -> Branch `main`, folder `/ (root)` -> Save.
3. The site appears at `https://<username>.github.io/<repo>/` (or `https://<username>.github.io/` for a repo named
   `<username>.github.io`).

## After it's live
- Google Cloud -> Google Auth Platform -> Branding: Application home page = the site URL; Privacy policy = `/privacy.html`;
  Terms of service = `/terms.html`; Authorized domain = `<username>.github.io`. Then Audience -> **Publish app**.
- Meta app -> App settings -> Basic: Privacy Policy URL + Terms of Service URL.
- When updating the Joyita card or adding stories, keep image credits under each image.
