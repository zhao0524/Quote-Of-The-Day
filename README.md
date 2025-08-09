# Quotescape — Quote of the Day

A small React + TypeScript app that shows a random quote from ZenQuotes with a polished UI. Light mode features an ocean/beach scene; dark mode features a dark background. Styled with Tailwind CSS.

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


## Rate limit
- ZenQuotes free tier is rate limited (~5 requests per 30 seconds per IP). The app adds a cache-busting param and retries to avoid duplicates, but you should still avoid spamming the button.
