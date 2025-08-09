# Quotescape — Quote of the Day

A small React + TypeScript app that shows a random quote from ZenQuotes with a polished UI. Light mode features an ocean/beach scene; dark mode features a cyberpunk city scene with neon accents. Styled with Tailwind CSS.

## Features
- Random quote from ZenQuotes (`/api/random`)
- New quote button with cache-busting and duplicate-avoidance
- Copy to clipboard + Share
- Light/Dark themes with smooth cross-fade background images (ocean ↔ cyberpunk)
- Glassmorphism card, responsive layout

## Tech
- React (CRA) + TypeScript
- Tailwind CSS
- ZenQuotes API

## Getting started
1) Install dependencies
```
npm install
```
2) Start the dev server
```
npm start
```
3) Open `http://localhost:3000`

## ZenQuotes and CORS (dev proxy)
- This project uses CRA’s built-in dev proxy to avoid CORS during local development.
- `package.json` contains:
```
"proxy": "https://zenquotes.io"
```
- The app calls ZenQuotes via relative paths, e.g. `fetch('/api/random')`. CRA forwards that to `https://zenquotes.io/api/random` while you run `npm start`.
- Note: The CRA dev proxy only works in development. For production, use a tiny proxy endpoint or a ZenQuotes plan that enables CORS.

## Commands
- `npm start` — run locally with hot reload
- `npm run build` — production build
- `npm test` — run tests (if any)

## File map (key files)
```
src/
├── App.tsx            # App logic + UI (fetch, copy/share, theme toggle)
├── backgrounds.css    # Crossfade image layers + neon overlays + glass styles
├── index.css          # Tailwind directives
├── index.tsx          # App entry
tailwind.config.js     # Tailwind setup
postcss.config.js      # PostCSS setup
```

## Rate limit
- ZenQuotes free tier is rate limited (~5 requests per 30 seconds per IP). The app adds a cache-busting param and retries to avoid duplicates, but you should still avoid spamming the button.

## Troubleshooting
- Seeing CORS errors? Make sure you:
  - Run via `npm start` (not opening `public/index.html` directly)
  - Restart the dev server after changing `package.json` proxy
- Getting repeated quotes? That can happen due to API randomness and limits; the app retries a few times. We can also switch to `/api/quotes` (batch) and pick a random item locally if needed.

## Attribution
- Quotes: ZenQuotes (`https://zenquotes.io`)
- Photos: Unsplash (ocean and city background images)
