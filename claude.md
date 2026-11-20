# CLAUDE.md

Guidance for AI coding agents (Claude Code and similar) working in this repository.

## Project

ReviewLens is a Chrome extension (Manifest V3) plus a FastAPI backend that analyses the customer reviews visible on an Amazon India product page and shows a short assessment card. See README.md for the full overview.

## Layout

- `extension/` Chrome extension. `content.js` extracts reviews and renders the card. `background.js` forwards the payload to the backend. `manifest.json` lists the matched sites.
- `backend/main.py` FastAPI app with a single `POST /analyze` endpoint.
- `ml/analyze.py` the analysis pipeline. `ml/aspects.py` sentence splitting, universal aspects and aspect discovery. `ml/sentiment.joblib` is the trained sentiment model.

## Run and test

Run the backend from the project root (not from `backend/`), otherwise `import ml` fails:

```bash
uvicorn backend.main:app --reload
```

- Health check: open http://127.0.0.1:8000/docs
- Load the extension: `chrome://extensions` -> Developer mode -> Load unpacked -> `extension/`
- After any extension change: click Reload on the extension, then refresh the Amazon tab. The old content script keeps running otherwise.
- Manual test: open an amazon.in product page, open DevTools Console, and look for `ReviewLens: attempt N found M reviews` and the `backend response` object.

## Conventions

- Python 3.11+ style, type hints on API models, small functions.
- Keep the API response shape stable: `analyzed`, `verdict`, `summary`, `strengths` (list of strings), `weaknesses` (list of strings), `red_flags` (list of objects with `issue`), plus an `error` key when nothing could be analysed. `content.js` renders these fields directly.
- Escape any review text before putting it into the page (`escapeHtml` in `content.js`).
- Aspects must stay category-independent. Do not add product-specific hard-coded lists. Extend `UNIVERSAL` or the `STOP` list in `ml/aspects.py` instead.

## Rules for this project

- Analyse only reviews that are visible through normal page access. Do not bypass logins, captchas or rate limits, and do not add scraping of "See all reviews" pages.
- Always show how many reviews were analysed. Never present a small sample as all customers.
- Suspicious-review signals are hints, not proof. Do not label a review or reviewer as fake.
- Do not commit secrets, `.env` files, raw datasets or large model files.
- Do not retrain or replace `ml/sentiment.joblib` without recording the dataset, metrics (precision, recall, F1, confusion matrix) in the README.

## Known issues

- Only amazon.in selectors are supported (`data-hook="review"`, `cmps-review`, `review-body`). Amazon can change its markup.
- Aspect names such as "life" come from noun discovery and can be incomplete ("battery life").
- Hinglish reviews are weakly handled by the sentiment model.

## Good next tasks

1. Show "N of total reviews analysed" using the total ratings count on the page.
2. Add a leave-one-category-out evaluation of the sentiment model.
3. Add personalised priorities and the two-product comparison.