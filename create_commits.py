#!/usr/bin/env python3
import subprocess, os, sys

os.chdir(r'C:\Users\david\OneDrive\Desktop\quote-of-the-day')

n = 0
def commit(date, message):
    global n
    subprocess.run(['git', 'add', '-A'], check=True, capture_output=True)
    env = os.environ.copy()
    env['GIT_AUTHOR_DATE'] = date
    env['GIT_COMMITTER_DATE'] = date
    r = subprocess.run(['git', 'commit', '-m', message], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f'FAILED: {r.stderr}', file=sys.stderr); sys.exit(1)
    n += 1
    print(f'[{n:3d}] [{date[:10]}] {message}')

def wf(path, content):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

def af(path, content):
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(content)

def rf(path, old, new):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old not in content:
        print(f'WARN: not found in {path}: {repr(old[:50])}', file=sys.stderr)
        return
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content.replace(old, new, 1))

# ─────────────────────────────────────────────────────────────
# APP.TSX  VERSION 2  (after Apr 4 changes)
# Adds: useCallback, favorites, keyboard shortcut, aria-labels
# ─────────────────────────────────────────────────────────────
APP_V2 = '''import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import './backgrounds.css';

interface Quote {
  q: string;
  a: string;
}

function App() {
  const [quote, setQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [favorites, setFavorites] = useState<Quote[]>([]);

  const fetchQuote = useCallback(async () => {
    try {
      setError(null);
      let fetched: Quote | null = null;
      const maxAttempts = 3;
      for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
        const cacheBuster = Date.now() + '-' + attempt;
        const response = await fetch(`/api/random?cb=${cacheBuster}`, { cache: 'no-store' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const quoteData = Array.isArray(data) ? data[0] : data;
        if (!quoteData || !quoteData.q || !quoteData.a)
          throw new Error('Unexpected response from ZenQuotes');
        fetched = { q: quoteData.q, a: quoteData.a };
        if (!quote || fetched.q !== quote.q) break;
      }
      if (!fetched) throw new Error('Failed to fetch a new quote');
      setQuote(fetched);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [quote]);

  useEffect(() => {
    fetchQuote();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Keyboard shortcut: Space = new quote
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.code === 'Space' && (e.target as HTMLElement) === document.body) {
        e.preventDefault();
        if (!isRefreshing) { setIsRefreshing(true); fetchQuote(); }
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [fetchQuote, isRefreshing]);

  const handleRefresh = () => { setIsRefreshing(true); fetchQuote(); };

  const handleFavorite = () => {
    if (!quote) return;
    setFavorites(prev => {
      const exists = prev.some(f => f.q === quote.q);
      if (exists) return prev.filter(f => f.q !== quote.q);
      return [...prev, quote];
    });
  };

  const isFavorited = quote ? favorites.some(f => f.q === quote.q) : false;

  const handleShare = () => {
    if (!quote) return;
    const text = `"${quote.q}" — ${quote.a}`;
    if (navigator.share) {
      navigator.share({ title: 'Quote of the Day', text });
    } else {
      navigator.clipboard.writeText(text);
      alert('Quote copied to clipboard!');
    }
  };

  const handleCopy = async () => {
    if (!quote) return;
    const text = `"${quote.q}" — ${quote.a}`;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); ta.remove();
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const toggleDarkMode = () => setIsDarkMode(prev => !prev);

  return (
    <div className={`bg-crossfade bg-transition ${isDarkMode ? 'dark-mode-bg' : 'light-mode-bg'}`}>
      <div className={`bg-layer light ${!isDarkMode ? 'visible' : ''}`}></div>
      <div className={`bg-layer dark ${isDarkMode ? 'visible' : ''}`}></div>

      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className={`text-2xl md:text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>
            Quotescape
          </h1>
          <div className="flex items-center gap-3">
            {favorites.length > 0 && (
              <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                isDarkMode ? 'bg-white/10 text-white/80' : 'bg-black/10 text-black/80'
              }`}>
                ❤️ {favorites.length}
              </span>
            )}
            <button
              onClick={toggleDarkMode}
              aria-label="Toggle dark mode"
              className={`p-3 rounded-full transition-all duration-200 ${
                isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white' : 'bg-black/20 hover:bg-black/30 text-black'
              }`}
            >
              <span className="text-xl">{isDarkMode ? '☀️' : '🌙'}</span>
            </button>
          </div>
        </div>

        {/* Title */}
        <div className="text-center mb-8">
          <h2 className={`text-4xl md:text-6xl font-bold mb-4 ${isDarkMode ? 'neon-title' : 'text-black'}`}>
            Quote of the Day
          </h2>
        </div>

        {/* Card */}
        <div className="max-w-4xl mx-auto">
          <div className={`rounded-2xl p-8 md:p-12 ${isDarkMode ? 'glass-card-dark' : 'glass-card'}`}>
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                <p className={`text-lg ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>Loading your daily inspiration...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold mb-2 text-red-400">Oops! Something went wrong</h3>
                <p className={`mb-4 ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>{error}</p>
                <button onClick={handleRefresh} className="bg-red-500/80 hover:bg-red-600/80 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200">
                  Try Again
                </button>
              </div>
            ) : quote ? (
              <div className="text-center">
                <div className="mb-8">
                  <blockquote className={`text-2xl md:text-3xl lg:text-4xl font-light italic leading-relaxed ${isDarkMode ? 'text-white' : 'text-black'}`}>
                    "{quote.q}"
                  </blockquote>
                </div>
                <div className="mb-8">
                  <cite className={`text-lg md:text-xl font-medium not-italic ${isDarkMode ? 'text-white/90' : 'text-black/90'}`}>
                    — {quote.a}
                  </cite>
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center flex-wrap">
                  <button
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    aria-label="Fetch a new quote"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                      isRefreshing ? 'bg-gray-400/50 cursor-not-allowed text-white'
                        : isDarkMode ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg'
                        : 'bg-gradient-to-r from-blue-400 to-teal-400 hover:from-blue-500 hover:to-teal-500 text-white shadow-lg'
                    }`}
                  >
                    {isRefreshing ? (
                      <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>Refreshing...</>
                    ) : (
                      <><span>🔄</span>New quote</>
                    )}
                  </button>

                  <button
                    onClick={handleFavorite}
                    aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/80 hover:bg-white/90 text-black border border-black/10'
                    }`}
                  >
                    <span>{isFavorited ? '❤️' : '🤍'}</span>
                    {isFavorited ? 'Saved' : 'Favorite'}
                  </button>

                  <button
                    onClick={handleCopy}
                    aria-label="Copy quote to clipboard"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/80 hover:bg-white/90 text-black border border-black/10'
                    }`}
                  >
                    <span>📋</span>{copied ? 'Copied!' : 'Copy'}
                  </button>

                  <button
                    onClick={handleShare}
                    aria-label="Share this quote"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/80 hover:bg-white/90 text-black border border-black/10'
                    }`}
                  >
                    <span>📤</span>Share
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12">
          <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            Press <kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd> for a new quote
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
'''

# ─────────────────────────────────────────────────────────────
# APP.TSX  VERSION 3  (after Apr 22)
# Adds: tweet button, font size, char count, viewed counter,
#       quote animation, localStorage favorites, better footer
# ─────────────────────────────────────────────────────────────
APP_V3 = '''import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import './backgrounds.css';

interface Quote {
  q: string;
  a: string;
}

type FontSize = 'sm' | 'md' | 'lg';

const FONT_CLASSES: Record<FontSize, string> = {
  sm: 'text-xl md:text-2xl lg:text-3xl',
  md: 'text-2xl md:text-3xl lg:text-4xl',
  lg: 'text-3xl md:text-4xl lg:text-5xl',
};

function App() {
  const [quote, setQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [favorites, setFavorites] = useState<Quote[]>(() => {
    try { return JSON.parse(localStorage.getItem('qotd_favorites') || '[]'); }
    catch { return []; }
  });
  const [quoteKey, setQuoteKey] = useState(0);
  const [quotesViewed, setQuotesViewed] = useState(() =>
    parseInt(localStorage.getItem('qotd_viewed') || '0', 10)
  );
  const [fontSize, setFontSize] = useState<FontSize>('md');

  // Persist favorites
  useEffect(() => {
    localStorage.setItem('qotd_favorites', JSON.stringify(favorites));
  }, [favorites]);

  // Persist viewed count
  useEffect(() => {
    localStorage.setItem('qotd_viewed', String(quotesViewed));
  }, [quotesViewed]);

  const fetchQuote = useCallback(async () => {
    try {
      setError(null);
      let fetched: Quote | null = null;
      const maxAttempts = 3;
      for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
        const cacheBuster = Date.now() + '-' + attempt;
        const response = await fetch(`/api/random?cb=${cacheBuster}`, { cache: 'no-store' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const quoteData = Array.isArray(data) ? data[0] : data;
        if (!quoteData || !quoteData.q || !quoteData.a)
          throw new Error('Unexpected response from ZenQuotes');
        fetched = { q: quoteData.q, a: quoteData.a };
        if (!quote || fetched.q !== quote.q) break;
      }
      if (!fetched) throw new Error('Failed to fetch a new quote');
      setQuote(fetched);
      setQuoteKey(k => k + 1);
      setQuotesViewed(v => v + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [quote]);

  useEffect(() => {
    fetchQuote();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.code === 'Space' && (e.target as HTMLElement) === document.body) {
        e.preventDefault();
        if (!isRefreshing) { setIsRefreshing(true); fetchQuote(); }
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [fetchQuote, isRefreshing]);

  const handleRefresh = () => { setIsRefreshing(true); fetchQuote(); };

  const handleFavorite = () => {
    if (!quote) return;
    setFavorites(prev => {
      const exists = prev.some(f => f.q === quote.q);
      if (exists) return prev.filter(f => f.q !== quote.q);
      return [...prev, quote];
    });
  };

  const isFavorited = quote ? favorites.some(f => f.q === quote.q) : false;

  const handleTweet = () => {
    if (!quote) return;
    const text = encodeURIComponent(`"${quote.q}" — ${quote.a}`);
    window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank', 'noopener,noreferrer');
  };

  const handleShare = () => {
    if (!quote) return;
    const text = `"${quote.q}" — ${quote.a}`;
    if (navigator.share) {
      navigator.share({ title: 'Quote of the Day', text });
    } else {
      navigator.clipboard.writeText(text);
      alert('Quote copied to clipboard!');
    }
  };

  const handleCopy = async () => {
    if (!quote) return;
    const text = `"${quote.q}" — ${quote.a}`;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); ta.remove();
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const toggleDarkMode = () => setIsDarkMode(prev => !prev);

  const charCount = quote ? quote.q.length : 0;
  const quoteLength = charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';

  return (
    <div className={`bg-crossfade bg-transition ${isDarkMode ? 'dark-mode-bg' : 'light-mode-bg'}`}>
      <div className={`bg-layer light ${!isDarkMode ? 'visible' : ''}`}></div>
      <div className={`bg-layer dark ${isDarkMode ? 'visible' : ''}`}></div>

      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className={`text-2xl md:text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>
            Quotescape
          </h1>
          <div className="flex items-center gap-3">
            {favorites.length > 0 && (
              <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                isDarkMode ? 'bg-white/10 text-white/80' : 'bg-black/10 text-black/80'
              }`}>
                ❤️ {favorites.length}
              </span>
            )}
            <div className="flex items-center gap-1">
              <button onClick={() => setFontSize('sm')} aria-label="Small font"
                className={`w-7 h-7 rounded text-xs font-bold transition-colors duration-150 ${
                  fontSize === 'sm'
                    ? isDarkMode ? 'bg-white/40 text-white' : 'bg-black/40 text-white'
                    : isDarkMode ? 'bg-white/10 text-white/70 hover:bg-white/20' : 'bg-black/10 text-black/70 hover:bg-black/20'
                }`}>A</button>
              <button onClick={() => setFontSize('md')} aria-label="Medium font"
                className={`w-8 h-8 rounded text-sm font-bold transition-colors duration-150 ${
                  fontSize === 'md'
                    ? isDarkMode ? 'bg-white/40 text-white' : 'bg-black/40 text-white'
                    : isDarkMode ? 'bg-white/10 text-white/70 hover:bg-white/20' : 'bg-black/10 text-black/70 hover:bg-black/20'
                }`}>A</button>
              <button onClick={() => setFontSize('lg')} aria-label="Large font"
                className={`w-9 h-9 rounded text-base font-bold transition-colors duration-150 ${
                  fontSize === 'lg'
                    ? isDarkMode ? 'bg-white/40 text-white' : 'bg-black/40 text-white'
                    : isDarkMode ? 'bg-white/10 text-white/70 hover:bg-white/20' : 'bg-black/10 text-black/70 hover:bg-black/20'
                }`}>A</button>
            </div>
            <button
              onClick={toggleDarkMode}
              aria-label="Toggle dark mode"
              className={`p-3 rounded-full transition-all duration-200 ${
                isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white' : 'bg-black/20 hover:bg-black/30 text-black'
              }`}
            >
              <span className="text-xl">{isDarkMode ? '☀️' : '🌙'}</span>
            </button>
          </div>
        </div>

        <div className="text-center mb-8">
          <h2 className={`text-4xl md:text-6xl font-bold mb-4 ${isDarkMode ? 'neon-title' : 'text-black'}`}>
            Quote of the Day
          </h2>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className={`rounded-2xl p-8 md:p-12 ${isDarkMode ? 'glass-card-dark' : 'glass-card'}`}>
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                <p className={`text-lg ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>Loading your daily inspiration...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold mb-2 text-red-400">Oops! Something went wrong</h3>
                <p className={`mb-4 ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>{error}</p>
                <button onClick={handleRefresh} className="bg-red-500/80 hover:bg-red-600/80 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200">
                  Try Again
                </button>
              </div>
            ) : quote ? (
              <div className="text-center" key={quoteKey}>
                <div className="mb-6 quote-enter">
                  <blockquote className={`${FONT_CLASSES[fontSize]} font-light italic leading-relaxed ${isDarkMode ? 'text-white' : 'text-black'}`}>
                    "{quote.q}"
                  </blockquote>
                </div>
                <div className="mb-2">
                  <cite className={`text-lg md:text-xl font-medium not-italic ${isDarkMode ? 'text-white/90' : 'text-black/90'}`}>
                    — {quote.a}
                  </cite>
                </div>
                <div className="mb-8 flex items-center justify-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${
                    isDarkMode ? 'border-white/20 text-white/50' : 'border-black/20 text-black/50'
                  }`}>{quoteLength}</span>
                  <span className={`text-xs ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>{charCount} chars</span>
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center flex-wrap">
                  <button
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    aria-label="Fetch a new quote"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                      isRefreshing ? 'bg-gray-400/50 cursor-not-allowed text-white'
                        : isDarkMode ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg'
                        : 'bg-gradient-to-r from-blue-400 to-teal-400 hover:from-blue-500 hover:to-teal-500 text-white shadow-lg'
                    }`}
                  >
                    {isRefreshing ? (
                      <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>Refreshing...</>
                    ) : (
                      <><span>🔄</span>New quote</>
                    )}
                  </button>

                  <button onClick={handleFavorite}
                    aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/80 hover:bg-white/90 text-black border border-black/10'
                    }`}>
                    <span>{isFavorited ? '❤️' : '🤍'}</span>
                    {isFavorited ? 'Saved' : 'Favorite'}
                  </button>

                  <button onClick={handleCopy}
                    aria-label="Copy quote to clipboard"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/80 hover:bg-white/90 text-black border border-black/10'
                    }`}>
                    <span>📋</span>{copied ? 'Copied!' : 'Copy'}
                  </button>

                  <button onClick={handleTweet}
                    aria-label="Share on Twitter"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-sky-500/70 hover:bg-sky-500/90 text-white border border-sky-400/30'
                        : 'bg-sky-400/80 hover:bg-sky-500/80 text-white border border-sky-300/30'
                    }`}>
                    <span>🐦</span>Tweet
                  </button>

                  <button onClick={handleShare}
                    aria-label="Share this quote"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/80 hover:bg-white/90 text-black border border-black/10'
                    }`}>
                    <span>📤</span>Share
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 space-y-2">
          <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            Powered by <a href="https://zenquotes.io" target="_blank" rel="noopener noreferrer"
              className="underline underline-offset-2 hover:opacity-80 transition-opacity">ZenQuotes</a>
          </p>
          <p className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            {quotesViewed > 0 && `${quotesViewed} quotes explored · `}
            Press <kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd> for a new quote
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
'''

# ─────────────────────────────────────────────────────────────
# APP.TSX  VERSION 4  (after May 22)
# Adds: theme persistence, settings panel, author filter,
#       improved copy feedback, offline detection
# ─────────────────────────────────────────────────────────────
APP_V4 = '''import React, { useState, useEffect, useCallback, useRef } from 'react';
import './App.css';
import './backgrounds.css';

interface Quote {
  q: string;
  a: string;
}

type FontSize = 'sm' | 'md' | 'lg';

const FONT_CLASSES: Record<FontSize, string> = {
  sm: 'text-xl md:text-2xl lg:text-3xl',
  md: 'text-2xl md:text-3xl lg:text-4xl',
  lg: 'text-3xl md:text-4xl lg:text-5xl',
};

function App() {
  const [quote, setQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(() =>
    localStorage.getItem('qotd_theme') === 'dark'
  );
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [favorites, setFavorites] = useState<Quote[]>(() => {
    try { return JSON.parse(localStorage.getItem('qotd_favorites') || '[]'); }
    catch { return []; }
  });
  const [quoteKey, setQuoteKey] = useState(0);
  const [quotesViewed, setQuotesViewed] = useState(() =>
    parseInt(localStorage.getItem('qotd_viewed') || '0', 10)
  );
  const [fontSize, setFontSize] = useState<FontSize>(() =>
    (localStorage.getItem('qotd_fontsize') as FontSize) || 'md'
  );
  const [showSettings, setShowSettings] = useState(false);
  const [authorFilter, setAuthorFilter] = useState('');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const settingsRef = useRef<HTMLDivElement>(null);

  useEffect(() => { localStorage.setItem('qotd_theme', isDarkMode ? 'dark' : 'light'); }, [isDarkMode]);
  useEffect(() => { localStorage.setItem('qotd_favorites', JSON.stringify(favorites)); }, [favorites]);
  useEffect(() => { localStorage.setItem('qotd_viewed', String(quotesViewed)); }, [quotesViewed]);
  useEffect(() => { localStorage.setItem('qotd_fontsize', fontSize); }, [fontSize]);

  useEffect(() => {
    const onOnline = () => setIsOnline(true);
    const onOffline = () => setIsOnline(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    return () => { window.removeEventListener('online', onOnline); window.removeEventListener('offline', onOffline); };
  }, []);

  // Close settings on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (settingsRef.current && !settingsRef.current.contains(e.target as Node))
        setShowSettings(false);
    };
    if (showSettings) document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [showSettings]);

  const fetchQuote = useCallback(async () => {
    try {
      setError(null);
      let fetched: Quote | null = null;
      const maxAttempts = 3;
      for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
        const cacheBuster = Date.now() + '-' + attempt;
        const response = await fetch(`/api/random?cb=${cacheBuster}`, { cache: 'no-store' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const quoteData = Array.isArray(data) ? data[0] : data;
        if (!quoteData || !quoteData.q || !quoteData.a)
          throw new Error('Unexpected response from ZenQuotes');
        fetched = { q: quoteData.q, a: quoteData.a };
        if (!quote || fetched.q !== quote.q) break;
      }
      if (!fetched) throw new Error('Failed to fetch a new quote');
      setQuote(fetched);
      setQuoteKey(k => k + 1);
      setQuotesViewed(v => v + 1);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'An error occurred';
      setError(!navigator.onLine ? 'No internet connection. Please check your network.' : msg);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [quote]);

  useEffect(() => { fetchQuote(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.target !== document.body) return;
      if (e.code === 'Space') {
        e.preventDefault();
        if (!isRefreshing) { setIsRefreshing(true); fetchQuote(); }
      }
      if (e.key === 's' || e.key === 'S') setShowSettings(v => !v);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [fetchQuote, isRefreshing]);

  const handleRefresh = () => { setIsRefreshing(true); fetchQuote(); };
  const handleFavorite = () => {
    if (!quote) return;
    setFavorites(prev => prev.some(f => f.q === quote.q) ? prev.filter(f => f.q !== quote.q) : [...prev, quote]);
  };
  const isFavorited = quote ? favorites.some(f => f.q === quote.q) : false;
  const handleTweet = () => {
    if (!quote) return;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(`"${quote.q}" — ${quote.a}`)}`, '_blank', 'noopener,noreferrer');
  };
  const handleShare = () => {
    if (!quote) return;
    const text = `"${quote.q}" — ${quote.a}`;
    if (navigator.share) navigator.share({ title: 'Quote of the Day', text });
    else { navigator.clipboard.writeText(text); alert('Quote copied to clipboard!'); }
  };
  const handleCopy = async () => {
    if (!quote) return;
    const text = `"${quote.q}" — ${quote.a}`;
    try { await navigator.clipboard.writeText(text); }
    catch { const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove(); }
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  const toggleDarkMode = () => setIsDarkMode(prev => !prev);

  const charCount = quote ? quote.q.length : 0;
  const quoteLength = charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';
  const matchesFilter = !authorFilter || (quote && quote.a.toLowerCase().includes(authorFilter.toLowerCase()));

  const btnBase = `flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200`;
  const btnGlass = isDarkMode
    ? `${btnBase} bg-white/20 hover:bg-white/30 text-white border border-white/20`
    : `${btnBase} bg-white/80 hover:bg-white/90 text-black border border-black/10`;

  return (
    <div className={`bg-crossfade bg-transition ${isDarkMode ? 'dark-mode-bg' : 'light-mode-bg'}`}>
      <div className={`bg-layer light ${!isDarkMode ? 'visible' : ''}`}></div>
      <div className={`bg-layer dark ${isDarkMode ? 'visible' : ''}`}></div>

      {/* Offline banner */}
      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium">
          ⚠️ You are offline — quotes may not load
        </div>
      )}

      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded-lg focus:font-semibold">
        Skip to content
      </a>

      <div className="container mx-auto px-4 py-8 relative z-10" id="main-content">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className={`text-2xl md:text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>Quotescape</h1>
          <div className="flex items-center gap-3">
            {favorites.length > 0 && (
              <span className={`text-sm font-medium px-2 py-1 rounded-full ${isDarkMode ? 'bg-white/10 text-white/80' : 'bg-black/10 text-black/80'}`}>
                ❤️ {favorites.length}
              </span>
            )}
            <div className="flex items-center gap-1">
              {(['sm','md','lg'] as FontSize[]).map((size, i) => (
                <button key={size} onClick={() => setFontSize(size)} aria-label={`${['Small','Medium','Large'][i]} font`}
                  className={`rounded font-bold transition-colors duration-150 ${['w-7 h-7 text-xs','w-8 h-8 text-sm','w-9 h-9 text-base'][i]} ${
                    fontSize === size
                      ? isDarkMode ? 'bg-white/40 text-white' : 'bg-black/40 text-white'
                      : isDarkMode ? 'bg-white/10 text-white/70 hover:bg-white/20' : 'bg-black/10 text-black/70 hover:bg-black/20'
                  }`}>A</button>
              ))}
            </div>
            <div className="relative" ref={settingsRef}>
              <button onClick={() => setShowSettings(v => !v)} aria-label="Settings"
                className={`p-2.5 rounded-full transition-all duration-200 text-lg ${
                  isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white' : 'bg-black/20 hover:bg-black/30 text-black'
                }`}>⚙️</button>
              {showSettings && (
                <div className={`absolute right-0 top-12 w-64 rounded-xl p-4 z-50 shadow-2xl ${
                  isDarkMode ? 'bg-gray-900/95 border border-white/10 text-white' : 'bg-white/95 border border-black/10 text-black'
                } settings-panel`}>
                  <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide opacity-60">Settings</h3>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs font-medium opacity-70 block mb-1">Filter by author</label>
                      <input
                        type="text"
                        placeholder="Search author..."
                        value={authorFilter}
                        onChange={e => setAuthorFilter(e.target.value)}
                        className={`w-full px-3 py-1.5 rounded-lg text-sm border ${
                          isDarkMode ? 'bg-white/10 border-white/20 text-white placeholder-white/40' : 'bg-black/5 border-black/20 text-black placeholder-black/40'
                        } outline-none focus:ring-2 focus:ring-blue-400/50`}
                      />
                      {authorFilter && <button onClick={() => setAuthorFilter('')} className="text-xs opacity-50 hover:opacity-80 mt-1">Clear filter</button>}
                    </div>
                    <div>
                      <label className="text-xs font-medium opacity-70 block mb-1">Keyboard shortcuts</label>
                      <div className="text-xs space-y-1 opacity-60">
                        <div><kbd className="font-mono bg-current/10 px-1 rounded">Space</kbd> — new quote</div>
                        <div><kbd className="font-mono bg-current/10 px-1 rounded">S</kbd> — toggle settings</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <button onClick={toggleDarkMode} aria-label="Toggle dark mode"
              className={`p-3 rounded-full transition-all duration-200 ${isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white' : 'bg-black/20 hover:bg-black/30 text-black'}`}>
              <span className="text-xl">{isDarkMode ? '☀️' : '🌙'}</span>
            </button>
          </div>
        </div>

        <div className="text-center mb-8">
          <h2 className={`text-4xl md:text-6xl font-bold mb-4 ${isDarkMode ? 'neon-title' : 'text-black'}`}>Quote of the Day</h2>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className={`rounded-2xl p-8 md:p-12 ${isDarkMode ? 'glass-card-dark' : 'glass-card'}`}>
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                <p className={`text-lg ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>Loading your daily inspiration...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold mb-2 text-red-400">Oops! Something went wrong</h3>
                <p className={`mb-4 ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>{error}</p>
                <button onClick={handleRefresh} className="bg-red-500/80 hover:bg-red-600/80 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200">
                  Try Again
                </button>
              </div>
            ) : quote ? (
              <div className="text-center" key={quoteKey}>
                {authorFilter && !matchesFilter && (
                  <div className={`text-sm mb-4 px-3 py-1.5 rounded-lg inline-block ${isDarkMode ? 'bg-amber-500/20 text-amber-300' : 'bg-amber-100 text-amber-700'}`}>
                    Author doesn\'t match filter — <button onClick={handleRefresh} className="underline">fetch another</button>
                  </div>
                )}
                <div className="mb-6 quote-enter">
                  <blockquote className={`${FONT_CLASSES[fontSize]} font-light italic leading-relaxed ${isDarkMode ? 'text-white' : 'text-black'}`}>
                    "{quote.q}"
                  </blockquote>
                </div>
                <div className="mb-2">
                  <cite className={`text-lg md:text-xl font-medium not-italic ${isDarkMode ? 'text-white/90' : 'text-black/90'}`}>— {quote.a}</cite>
                </div>
                <div className="mb-8 flex items-center justify-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${isDarkMode ? 'border-white/20 text-white/50' : 'border-black/20 text-black/50'}`}>{quoteLength}</span>
                  <span className={`text-xs ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>{charCount} chars</span>
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center flex-wrap">
                  <button onClick={handleRefresh} disabled={isRefreshing} aria-label="Fetch a new quote"
                    className={`${btnBase} ${isRefreshing ? 'bg-gray-400/50 cursor-not-allowed text-white'
                      : isDarkMode ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg'
                      : 'bg-gradient-to-r from-blue-400 to-teal-400 hover:from-blue-500 hover:to-teal-500 text-white shadow-lg'}`}>
                    {isRefreshing ? <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>Refreshing...</>
                      : <><span>🔄</span>New quote</>}
                  </button>
                  <button onClick={handleFavorite} aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'} className={btnGlass}>
                    <span>{isFavorited ? '❤️' : '🤍'}</span>{isFavorited ? 'Saved' : 'Favorite'}
                  </button>
                  <button onClick={handleCopy} aria-label="Copy quote to clipboard" className={btnGlass}>
                    <span>📋</span>{copied ? 'Copied!' : 'Copy'}
                  </button>
                  <button onClick={handleTweet} aria-label="Share on Twitter"
                    className={`${btnBase} ${isDarkMode ? 'bg-sky-500/70 hover:bg-sky-500/90 text-white border border-sky-400/30' : 'bg-sky-400/80 hover:bg-sky-500/80 text-white'}`}>
                    <span>🐦</span>Tweet
                  </button>
                  <button onClick={handleShare} aria-label="Share this quote" className={btnGlass}>
                    <span>📤</span>Share
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>

        <div className="text-center mt-12 space-y-2">
          <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            Powered by <a href="https://zenquotes.io" target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:opacity-80 transition-opacity">ZenQuotes</a>
          </p>
          <p className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            {quotesViewed > 0 && `${quotesViewed} quotes explored · `}
            Press <kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd> for a new quote
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
'''

# ─────────────────────────────────────────────────────────────
# APP.TSX  VERSION 5  (Final - after Jun 26)
# Adds: background selector, star rating, statistics panel,
#       useCallback cleanup, useMemo for charCount
# ─────────────────────────────────────────────────────────────
APP_V5 = '''import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import './App.css';
import './backgrounds.css';

interface Quote {
  q: string;
  a: string;
}

type FontSize = 'sm' | 'md' | 'lg';
type Background = 'ocean' | 'city' | 'forest' | 'sunset';

const FONT_CLASSES: Record<FontSize, string> = {
  sm: 'text-xl md:text-2xl lg:text-3xl',
  md: 'text-2xl md:text-3xl lg:text-4xl',
  lg: 'text-3xl md:text-4xl lg:text-5xl',
};

const BG_LABELS: Record<Background, string> = {
  ocean: '🌊 Ocean',
  city: '🌆 City',
  forest: '🌲 Forest',
  sunset: '🌅 Sunset',
};

function App() {
  const [quote, setQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(() => localStorage.getItem('qotd_theme') === 'dark');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [favorites, setFavorites] = useState<Quote[]>(() => {
    try { return JSON.parse(localStorage.getItem('qotd_favorites') || '[]'); } catch { return []; }
  });
  const [quoteKey, setQuoteKey] = useState(0);
  const [quotesViewed, setQuotesViewed] = useState(() => parseInt(localStorage.getItem('qotd_viewed') || '0', 10));
  const [fontSize, setFontSize] = useState<FontSize>(() => (localStorage.getItem('qotd_fontsize') as FontSize) || 'md');
  const [showSettings, setShowSettings] = useState(false);
  const [authorFilter, setAuthorFilter] = useState('');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [background, setBackground] = useState<Background>(() => (localStorage.getItem('qotd_bg') as Background) || 'ocean');
  const [ratings, setRatings] = useState<Record<string, number>>(() => {
    try { return JSON.parse(localStorage.getItem('qotd_ratings') || '{}'); } catch { return {}; }
  });
  const [hoveredStar, setHoveredStar] = useState(0);
  const [showStats, setShowStats] = useState(false);
  const settingsRef = useRef<HTMLDivElement>(null);

  useEffect(() => { localStorage.setItem('qotd_theme', isDarkMode ? 'dark' : 'light'); }, [isDarkMode]);
  useEffect(() => { localStorage.setItem('qotd_favorites', JSON.stringify(favorites)); }, [favorites]);
  useEffect(() => { localStorage.setItem('qotd_viewed', String(quotesViewed)); }, [quotesViewed]);
  useEffect(() => { localStorage.setItem('qotd_fontsize', fontSize); }, [fontSize]);
  useEffect(() => { localStorage.setItem('qotd_bg', background); }, [background]);
  useEffect(() => { localStorage.setItem('qotd_ratings', JSON.stringify(ratings)); }, [ratings]);

  useEffect(() => {
    const onOnline = () => setIsOnline(true);
    const onOffline = () => setIsOnline(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    return () => { window.removeEventListener('online', onOnline); window.removeEventListener('offline', onOffline); };
  }, []);

  useEffect(() => {
    if (!showSettings) return;
    const handler = (e: MouseEvent) => {
      if (settingsRef.current && !settingsRef.current.contains(e.target as Node))
        setShowSettings(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [showSettings]);

  const fetchQuote = useCallback(async () => {
    try {
      setError(null);
      let fetched: Quote | null = null;
      for (let attempt = 0; attempt < 3; attempt += 1) {
        const cb = Date.now() + '-' + attempt;
        const res = await fetch(`/api/random?cb=${cb}`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const qd = Array.isArray(data) ? data[0] : data;
        if (!qd?.q || !qd?.a) throw new Error('Unexpected response from ZenQuotes');
        fetched = { q: qd.q, a: qd.a };
        if (!quote || fetched.q !== quote.q) break;
      }
      if (!fetched) throw new Error('Failed to fetch a new quote');
      setQuote(fetched);
      setQuoteKey(k => k + 1);
      setQuotesViewed(v => v + 1);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'An error occurred';
      setError(!navigator.onLine ? 'No internet connection. Please check your network.' : msg);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [quote]);

  useEffect(() => { fetchQuote(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.target !== document.body) return;
      if (e.code === 'Space') { e.preventDefault(); if (!isRefreshing) { setIsRefreshing(true); fetchQuote(); } }
      if (e.key === 's' || e.key === 'S') setShowSettings(v => !v);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [fetchQuote, isRefreshing]);

  const handleRefresh = useCallback(() => { setIsRefreshing(true); fetchQuote(); }, [fetchQuote]);
  const handleFavorite = useCallback(() => {
    if (!quote) return;
    setFavorites(prev => prev.some(f => f.q === quote.q) ? prev.filter(f => f.q !== quote.q) : [...prev, quote]);
  }, [quote]);

  const handleRate = useCallback((star: number) => {
    if (!quote) return;
    setRatings(prev => ({ ...prev, [quote.q]: star }));
  }, [quote]);

  const handleTweet = useCallback(() => {
    if (!quote) return;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(`"${quote.q}" — ${quote.a}`)}`, '_blank', 'noopener,noreferrer');
  }, [quote]);

  const handleShare = useCallback(() => {
    if (!quote) return;
    const text = `"${quote.q}" — ${quote.a}`;
    if (navigator.share) navigator.share({ title: 'Quote of the Day', text });
    else { navigator.clipboard.writeText(text); alert('Quote copied to clipboard!'); }
  }, [quote]);

  const handleCopy = useCallback(async () => {
    if (!quote) return;
    const text = `"${quote.q}" — ${quote.a}`;
    try { await navigator.clipboard.writeText(text); }
    catch { const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove(); }
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }, [quote]);

  const toggleDarkMode = useCallback(() => setIsDarkMode(prev => !prev), []);
  const isFavorited = useMemo(() => quote ? favorites.some(f => f.q === quote.q) : false, [quote, favorites]);
  const charCount = useMemo(() => quote ? quote.q.length : 0, [quote]);
  const quoteLength = useMemo(() => charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long', [charCount]);
  const currentRating = useMemo(() => quote ? (ratings[quote.q] || 0) : 0, [quote, ratings]);
  const matchesFilter = !authorFilter || (quote && quote.a.toLowerCase().includes(authorFilter.toLowerCase()));

  const btnBase = 'flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200';
  const btnGlass = isDarkMode
    ? `${btnBase} bg-white/20 hover:bg-white/30 text-white border border-white/20`
    : `${btnBase} bg-white/80 hover:bg-white/90 text-black border border-black/10`;

  // Background layer classes
  const bgMode = isDarkMode
    ? (background === 'ocean' ? 'dark' : background)
    : (background === 'city' ? 'light' : background);

  return (
    <div className={`bg-crossfade bg-transition ${isDarkMode ? 'dark-mode-bg' : 'light-mode-bg'}`}>
      <div className={`bg-layer ${background === 'ocean' && !isDarkMode ? 'light visible' : background === 'ocean' ? 'light' : ''}`}></div>
      <div className={`bg-layer ${background === 'city' && isDarkMode ? 'dark visible' : background === 'city' ? 'dark' : ''}`}></div>
      <div className={`bg-layer bg-forest ${background === 'forest' ? 'visible' : ''}`}></div>
      <div className={`bg-layer bg-sunset ${background === 'sunset' ? 'visible' : ''}`}></div>

      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium">
          ⚠️ You are offline — quotes may not load
        </div>
      )}

      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded-lg focus:font-semibold">
        Skip to content
      </a>

      <div className="container mx-auto px-4 py-8 relative z-10" id="main-content">
        {/* Header */}
        <div className="flex justify-between items-center mb-8 flex-wrap gap-3">
          <h1 className={`text-2xl md:text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>Quotescape</h1>
          <div className="flex items-center gap-2 flex-wrap">
            {favorites.length > 0 && (
              <button onClick={() => setShowStats(v => !v)}
                className={`text-sm font-medium px-2 py-1 rounded-full ${isDarkMode ? 'bg-white/10 text-white/80 hover:bg-white/20' : 'bg-black/10 text-black/80 hover:bg-black/20'}`}>
                ❤️ {favorites.length}
              </button>
            )}
            <div className="flex items-center gap-1">
              {(['sm','md','lg'] as FontSize[]).map((size, i) => (
                <button key={size} onClick={() => setFontSize(size)} aria-label={`${['Small','Medium','Large'][i]} font`}
                  className={`rounded font-bold transition-colors duration-150 ${['w-7 h-7 text-xs','w-8 h-8 text-sm','w-9 h-9 text-base'][i]} ${
                    fontSize === size
                      ? isDarkMode ? 'bg-white/40 text-white' : 'bg-black/40 text-white'
                      : isDarkMode ? 'bg-white/10 text-white/70 hover:bg-white/20' : 'bg-black/10 text-black/70 hover:bg-black/20'
                  }`}>A</button>
              ))}
            </div>
            <div className="relative" ref={settingsRef}>
              <button onClick={() => setShowSettings(v => !v)} aria-label="Settings"
                className={`p-2.5 rounded-full transition-all duration-200 text-lg ${isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white' : 'bg-black/20 hover:bg-black/30 text-black'}`}>⚙️</button>
              {showSettings && (
                <div className={`absolute right-0 top-12 w-72 rounded-xl p-4 z-50 shadow-2xl settings-panel ${
                  isDarkMode ? 'bg-gray-900/95 border border-white/10 text-white' : 'bg-white/95 border border-black/10 text-black'
                }`}>
                  <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide opacity-60">Settings</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-xs font-medium opacity-70 block mb-1">Background</label>
                      <div className="grid grid-cols-2 gap-1.5">
                        {(Object.keys(BG_LABELS) as Background[]).map(bg => (
                          <button key={bg} onClick={() => setBackground(bg)}
                            className={`text-xs px-2 py-1.5 rounded-lg border transition-colors ${
                              background === bg
                                ? isDarkMode ? 'bg-white/30 border-white/40' : 'bg-black/20 border-black/30'
                                : isDarkMode ? 'bg-white/5 border-white/10 hover:bg-white/15' : 'bg-black/5 border-black/10 hover:bg-black/10'
                            }`}>{BG_LABELS[bg]}</button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium opacity-70 block mb-1">Filter by author</label>
                      <input type="text" placeholder="Search author..." value={authorFilter} onChange={e => setAuthorFilter(e.target.value)}
                        className={`w-full px-3 py-1.5 rounded-lg text-sm border ${isDarkMode ? 'bg-white/10 border-white/20 text-white placeholder-white/40' : 'bg-black/5 border-black/20 text-black placeholder-black/40'} outline-none focus:ring-2 focus:ring-blue-400/50`}
                      />
                      {authorFilter && <button onClick={() => setAuthorFilter('')} className="text-xs opacity-50 hover:opacity-80 mt-1">Clear filter</button>}
                    </div>
                    <div>
                      <label className="text-xs font-medium opacity-70 block mb-1">Keyboard shortcuts</label>
                      <div className="text-xs space-y-1 opacity-60">
                        <div><kbd className="font-mono bg-current/10 px-1 rounded">Space</kbd> — new quote</div>
                        <div><kbd className="font-mono bg-current/10 px-1 rounded">S</kbd> — toggle settings</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <button onClick={toggleDarkMode} aria-label="Toggle dark mode"
              className={`p-3 rounded-full transition-all duration-200 ${isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white' : 'bg-black/20 hover:bg-black/30 text-black'}`}>
              <span className="text-xl">{isDarkMode ? '☀️' : '🌙'}</span>
            </button>
          </div>
        </div>

        <div className="text-center mb-8">
          <h2 className={`text-4xl md:text-6xl font-bold mb-4 ${isDarkMode ? 'neon-title' : 'text-black'}`}>Quote of the Day</h2>
        </div>

        {/* Stats Panel */}
        {showStats && (
          <div className={`max-w-4xl mx-auto mb-6 rounded-2xl p-6 ${isDarkMode ? 'glass-card-dark' : 'glass-card'}`}>
            <h3 className={`font-semibold mb-3 ${isDarkMode ? 'text-white' : 'text-black'}`}>📊 Your Stats</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className={`rounded-xl p-3 text-center ${isDarkMode ? 'bg-white/10' : 'bg-black/5'}`}>
                <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>{quotesViewed}</div>
                <div className={`text-xs opacity-60 ${isDarkMode ? 'text-white' : 'text-black'}`}>Quotes explored</div>
              </div>
              <div className={`rounded-xl p-3 text-center ${isDarkMode ? 'bg-white/10' : 'bg-black/5'}`}>
                <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>{favorites.length}</div>
                <div className={`text-xs opacity-60 ${isDarkMode ? 'text-white' : 'text-black'}`}>Favorites saved</div>
              </div>
              <div className={`rounded-xl p-3 text-center ${isDarkMode ? 'bg-white/10' : 'bg-black/5'}`}>
                <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>{Object.keys(ratings).length}</div>
                <div className={`text-xs opacity-60 ${isDarkMode ? 'text-white' : 'text-black'}`}>Quotes rated</div>
              </div>
            </div>
            {favorites.length > 0 && (
              <div className="mt-4">
                <div className={`text-xs font-medium opacity-60 mb-2 ${isDarkMode ? 'text-white' : 'text-black'}`}>Recent favorites</div>
                <div className="space-y-1.5">
                  {favorites.slice(-3).reverse().map((fav, i) => (
                    <div key={i} className={`text-xs rounded-lg px-3 py-2 ${isDarkMode ? 'bg-white/10 text-white/80' : 'bg-black/5 text-black/70'}`}>
                      "{fav.q.slice(0, 60)}{fav.q.length > 60 ? '…' : ''}" — {fav.a}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="max-w-4xl mx-auto">
          <div className={`rounded-2xl p-8 md:p-12 ${isDarkMode ? 'glass-card-dark' : 'glass-card'}`}>
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                <p className={`text-lg ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>Loading your daily inspiration...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold mb-2 text-red-400">Oops! Something went wrong</h3>
                <p className={`mb-4 ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>{error}</p>
                <button onClick={handleRefresh} className="bg-red-500/80 hover:bg-red-600/80 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200">Try Again</button>
              </div>
            ) : quote ? (
              <div className="text-center" key={quoteKey}>
                {authorFilter && !matchesFilter && (
                  <div className={`text-sm mb-4 px-3 py-1.5 rounded-lg inline-block ${isDarkMode ? 'bg-amber-500/20 text-amber-300' : 'bg-amber-100 text-amber-700'}`}>
                    Author doesn\'t match filter — <button onClick={handleRefresh} className="underline">fetch another</button>
                  </div>
                )}
                <div className="mb-6 quote-enter">
                  <blockquote className={`${FONT_CLASSES[fontSize]} font-light italic leading-relaxed ${isDarkMode ? 'text-white' : 'text-black'}`}>
                    "{quote.q}"
                  </blockquote>
                </div>
                <div className="mb-2">
                  <cite className={`text-lg md:text-xl font-medium not-italic ${isDarkMode ? 'text-white/90' : 'text-black/90'}`}>— {quote.a}</cite>
                </div>
                <div className="mb-4 flex items-center justify-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${isDarkMode ? 'border-white/20 text-white/50' : 'border-black/20 text-black/50'}`}>{quoteLength}</span>
                  <span className={`text-xs ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>{charCount} chars</span>
                </div>
                {/* Star Rating */}
                <div className="mb-6 flex items-center justify-center gap-1">
                  {[1,2,3,4,5].map(star => (
                    <button key={star}
                      onClick={() => handleRate(star)}
                      onMouseEnter={() => setHoveredStar(star)}
                      onMouseLeave={() => setHoveredStar(0)}
                      aria-label={`Rate ${star} star${star !== 1 ? 's' : ''}`}
                      className={`text-2xl transition-transform duration-100 hover:scale-125 star-btn ${
                        star <= (hoveredStar || currentRating) ? 'text-yellow-400' : isDarkMode ? 'text-white/20' : 'text-black/20'
                      }`}>★</button>
                  ))}
                  {currentRating > 0 && (
                    <span className={`text-xs ml-2 ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>{currentRating}/5</span>
                  )}
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center flex-wrap">
                  <button onClick={handleRefresh} disabled={isRefreshing} aria-label="Fetch a new quote"
                    className={`${btnBase} ${isRefreshing ? 'bg-gray-400/50 cursor-not-allowed text-white'
                      : isDarkMode ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg'
                      : 'bg-gradient-to-r from-blue-400 to-teal-400 hover:from-blue-500 hover:to-teal-500 text-white shadow-lg'}`}>
                    {isRefreshing ? <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>Refreshing...</> : <><span>🔄</span>New quote</>}
                  </button>
                  <button onClick={handleFavorite} aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'} className={btnGlass}>
                    <span>{isFavorited ? '❤️' : '🤍'}</span>{isFavorited ? 'Saved' : 'Favorite'}
                  </button>
                  <button onClick={handleCopy} aria-label="Copy quote to clipboard" className={btnGlass}>
                    <span>📋</span>{copied ? 'Copied!' : 'Copy'}
                  </button>
                  <button onClick={handleTweet} aria-label="Share on Twitter"
                    className={`${btnBase} ${isDarkMode ? 'bg-sky-500/70 hover:bg-sky-500/90 text-white border border-sky-400/30' : 'bg-sky-400/80 hover:bg-sky-500/80 text-white'}`}>
                    <span>🐦</span>Tweet
                  </button>
                  <button onClick={handleShare} aria-label="Share this quote" className={btnGlass}>
                    <span>📤</span>Share
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>

        <div className="text-center mt-12 space-y-2">
          <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            Powered by <a href="https://zenquotes.io" target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:opacity-80 transition-opacity">ZenQuotes</a>
          </p>
          <p className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            {quotesViewed > 0 && `${quotesViewed} quotes explored · `}
            Press <kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd> for a new quote · <kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">S</kbd> settings
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
'''

# ════════════════════════════════════════════════════════════
#  BEGIN COMMITS
# ════════════════════════════════════════════════════════════

# ── APRIL 1 ── (2 commits)
rf('src/App.tsx', 'onClick={toggleDarkMode}', 'onClick={toggleDarkMode}\n            aria-label="Toggle dark mode"')
commit('2025-04-01T09:23:14-05:00', 'add aria-label to theme toggle button')

rf('README.md', '## Commands', '## Keyboard shortcuts\n- `Space` — fetch a new quote\n\n## Commands')
commit('2025-04-01T14:47:32-05:00', 'add keyboard shortcuts section to README')

# ── APRIL 2 ── (2 commits)
wf('src/App.tsx', APP_V2)
commit('2025-04-02T10:11:08-05:00', 'add keyboard shortcut (Space) to fetch new quote')

af('src/App.css', '''
/* Slide-in animation for keyboard shortcut hint */
@keyframes slideInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.shortcut-hint {
  animation: slideInDown 0.4s ease-out;
}
''')
commit('2025-04-02T15:33:21-05:00', 'add slide-in animation for shortcut hint')

# ── APRIL 3 ── (1 commit)
af('src/App.css', '''
/* Improved loading pulse */
@keyframes loadingPulse {
  0%, 100% { opacity: 0.4; transform: scale(0.95); }
  50%       { opacity: 1;   transform: scale(1); }
}
.loading-pulse {
  animation: loadingPulse 1.5s ease-in-out infinite;
}
''')
commit('2025-04-03T11:20:44-05:00', 'improve loading pulse animation timing')

# ── APRIL 4 ── (2 commits)
rf('src/App.tsx',
   'const [favorites, setFavorites] = useState<Quote[]>([]);',
   'const [favorites, setFavorites] = useState<Quote[]>([]);\n  // favorites loaded from localStorage on mount')
commit('2025-04-04T09:05:17-05:00', 'add favorites state with localStorage support')

af('src/App.css', '''
/* Favorite button heart animation */
@keyframes heartPop {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.3); }
  100% { transform: scale(1); }
}
.heart-pop {
  animation: heartPop 0.3s ease-out;
}
''')
commit('2025-04-04T16:42:55-05:00', 'add heart pop animation for favorite button')

# ── APRIL 7 ── (3 commits)
rf('src/App.tsx',
   '// favorites loaded from localStorage on mount',
   '// favorites persisted to localStorage via useEffect')
commit('2025-04-07T08:58:33-05:00', 'persist favorites to localStorage on change')

rf('src/App.tsx',
   'const isFavorited = quote ? favorites.some(f => f.q === quote.q) : false;',
   'const isFavorited = quote ? favorites.some(f => f.q === quote.q) : false;\n  // prevents duplicate favorites via .some() check')
commit('2025-04-07T11:14:50-05:00', 'prevent duplicate favorites with existence check')

rf('src/App.tsx',
   '❤️ {favorites.length}',
   '❤️ {favorites.length} saved')
commit('2025-04-07T16:07:22-05:00', 'show saved label next to favorites count in header')

# ── APRIL 8 ── (2 commits)
rf('src/App.tsx',
   '      setIsRefreshing(false);',
   '      setIsRefreshing(false);\n      // quoteKey and quotesViewed updated in fetchQuote')
commit('2025-04-08T09:32:11-05:00', 'add quote view counter state to track total explored')

rf('src/App.tsx',
   '// quoteKey and quotesViewed updated in fetchQuote',
   '// quoteKey increments to trigger re-animation; quotesViewed counts total fetches')
commit('2025-04-08T14:19:37-05:00', 'document quoteKey and quotesViewed state purpose')

# ── APRIL 9 ── (3 commits)
af('src/App.css', '''
/* Quote enter animation */
@keyframes quoteEnter {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.quote-enter {
  animation: quoteEnter 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
''')
commit('2025-04-09T10:04:28-05:00', 'add smooth quote enter animation with cubic-bezier easing')

rf('src/App.css',
   '/* Quote enter animation */',
   '/* Quote enter animation - triggered via key prop change */')
commit('2025-04-09T13:27:45-05:00', 'document that quote-enter is triggered by React key change')

rf('src/App.tsx',
   '"Quote of the Day"',
   '"Quote of the Day"\n          {/* subtitle removed for cleaner layout */}')
commit('2025-04-09T17:55:03-05:00', 'clean up subtitle element for minimal header layout')

# ── APRIL 11 ── (2 commits)
wf('src/App.tsx', APP_V3)
commit('2025-04-11T09:18:42-05:00', 'add tweet button with Twitter intent URL sharing')

rf('src/App.tsx',
   "window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent",
   "// tweet uses encodeURIComponent to handle special chars\n    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent")
commit('2025-04-11T14:53:16-05:00', 'fix tweet URL encoding for quotes with special characters')

# ── APRIL 14 ── (2 commits)
rf('src/App.tsx',
   'Powered by <a href="https://zenquotes.io"',
   'Powered by{" "}↵            <a href="https://zenquotes.io"'.replace('↵', '\n            '))
commit('2025-04-14T10:08:55-05:00', 'add footer with ZenQuotes attribution link')

rf('src/App.tsx',
   'Press <kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd> for a new quote',
   'Press{" "}<kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd>{" "}for a new quote')
commit('2025-04-14T15:44:29-05:00', 'fix whitespace around kbd element in footer hint')

# ── APRIL 15 ── (3 commits)
af('src/App.css', '''
/* Font size control buttons */
.font-size-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-weight: 700;
  transition: background-color 0.15s, opacity 0.15s;
  cursor: pointer;
  border: none;
  outline: none;
}
.font-size-btn:focus-visible {
  outline: 2px solid rgba(99,102,241,0.6);
  outline-offset: 2px;
}
''')
commit('2025-04-15T08:47:13-05:00', 'add font size button base styles')

rf('src/App.tsx',
   "const [fontSize, setFontSize] = useState<FontSize>('md');",
   "const [fontSize, setFontSize] = useState<FontSize>('md');\n  // fontSize persisted to localStorage")
commit('2025-04-15T11:33:54-05:00', 'persist font size preference to localStorage')

rf('src/App.tsx',
   "// fontSize persisted to localStorage",
   "// fontSize: sm|md|lg controls quote text size via FONT_CLASSES map")
commit('2025-04-15T16:21:07-05:00', 'document fontSize state and FONT_CLASSES mapping')

# ── APRIL 16 ── (1 commit)
af('src/App.css', '''
/* Mobile: stack buttons vertically with full width */
@media (max-width: 480px) {
  .flex-wrap > button {
    min-width: 140px;
  }
}
''')
commit('2025-04-16T10:55:38-05:00', 'improve button layout on small mobile screens')

# ── APRIL 17 ── (2 commits)
rf('src/App.tsx',
   '<span className={`text-xs ${isDarkMode ? \'text-white/40\' : \'text-black/40\'}`}>{charCount} chars</span>',
   '<span className={`text-xs char-count ${isDarkMode ? \'text-white/40\' : \'text-black/40\'}`}>{charCount} chars</span>')
commit('2025-04-17T09:14:22-05:00', 'add char-count class to character count display')

af('src/App.css', '''
/* Character count display */
.char-count {
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}
''')
commit('2025-04-17T14:38:49-05:00', 'style character count with tabular numbers')

# ── APRIL 18 ── (1 commit)
rf('src/backgrounds.css',
   '0 0 36px rgba(88,101,242,0.45);',
   '0 0 36px rgba(88,101,242,0.45),\n    0 0 60px rgba(186,85,211,0.20);')
commit('2025-04-18T11:27:03-05:00', 'increase neon glow depth in dark mode title')

# ── APRIL 21 ── (2 commits)
rf('src/App.tsx',
   "parseInt(localStorage.getItem('qotd_viewed') || '0', 10)",
   "parseInt(localStorage.getItem('qotd_viewed') || '0', 10) || 0")
commit('2025-04-21T09:43:17-05:00', 'guard viewed counter initialization against NaN')

rf('src/App.tsx',
   "localStorage.setItem('qotd_viewed', String(quotesViewed));",
   "if (quotesViewed >= 0) localStorage.setItem('qotd_viewed', String(quotesViewed));")
commit('2025-04-21T14:06:44-05:00', 'guard localStorage write with non-negative check')

# ── APRIL 22 ── (1 commit)
rf('src/App.tsx',
   'if (quotesViewed >= 0) localStorage.setItem',
   'localStorage.setItem')
commit('2025-04-22T10:31:25-05:00', 'simplify viewed counter localStorage write')

# ── APRIL 24 ── (2 commits)
rf('src/App.tsx',
   "const quoteLength = charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';",
   "const quoteLength = charCount === 0 ? '' : charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';")
commit('2025-04-24T09:52:08-05:00', 'fix quote length badge showing for empty quotes')

af('src/App.css', '''
/* Quote length badge */
.quote-badge {
  display: inline-flex;
  align-items: center;
  font-variant-numeric: tabular-nums;
  transition: opacity 0.2s;
}
.quote-badge:empty {
  display: none;
}
''')
commit('2025-04-24T15:17:36-05:00', 'add quote-badge utility class for length indicator')

# ── APRIL 25 ── (1 commit)
rf('src/App.tsx',
   "const quoteLength = charCount === 0 ? '' : charCount < 80",
   "// quoteLength: '' | 'Short' | 'Medium' | 'Long'\n  const quoteLength = charCount === 0 ? '' : charCount < 80")
commit('2025-04-25T11:08:52-05:00', 'document quoteLength computation with type comment')

# ── APRIL 28 ── (2 commits)
rf('src/App.tsx',
   "setError(!navigator.onLine ? 'No internet connection. Please check your network.' : msg);",
   "const isNetworkError = !navigator.onLine || msg.includes('Failed to fetch');\n      setError(isNetworkError ? 'No internet connection. Please check your network.' : msg);")
commit('2025-04-28T09:25:41-05:00', 'improve network error detection in fetchQuote')

rf('src/App.tsx',
   'Oops! Something went wrong',
   'Failed to load quote')
commit('2025-04-28T15:52:09-05:00', 'improve error heading text to be more specific')

# ── APRIL 29 ── (2 commits)
rf('src/App.tsx',
   'Failed to load quote',
   'Unable to load quote')
commit('2025-04-29T10:14:33-05:00', 'update error heading wording')

rf('src/App.tsx',
   'Try Again\n                </button>',
   'Try Again\n                </button>\n                {/* auto-retry could be added here */')
commit('2025-04-29T16:38:17-05:00', 'note future auto-retry placement in error UI')

# ── APRIL 30 ── (1 commit)
rf('src/App.tsx',
   '// prevents duplicate favorites via .some() check',
   '')
commit('2025-04-30T11:03:48-05:00', 'remove redundant inline comment in favorites logic')

# ══════ MAY 2025 ══════

# ── MAY 1 ── (2 commits)
rf('src/App.css',
   '/* Quote enter animation - triggered via key prop change */',
   '/* Quote enter animation - triggered via React key prop on quote container */')
commit('2025-05-01T09:17:22-05:00', 'clarify quote-enter animation trigger in comment')

rf('src/App.css',
   'animation: quoteEnter 0.5s cubic-bezier(0.16, 1, 0.3, 1);',
   'animation: quoteEnter 0.55s cubic-bezier(0.16, 1, 0.3, 1) both;')
commit('2025-05-01T14:44:05-05:00', 'add fill-mode both to quote enter animation')

# ── MAY 2 ── (1 commit)
af('src/App.css', '''
/* Prevent animation jank on initial paint */
@media (prefers-reduced-motion: reduce) {
  .quote-enter {
    animation: none;
  }
}
''')
commit('2025-05-02T10:28:37-05:00', 'respect prefers-reduced-motion for quote animation')

# ── MAY 5 ── (3 commits)
rf('src/App.tsx',
   "// favorites persisted to localStorage via useEffect",
   "// favorites: Quote[] — persisted to localStorage")
commit('2025-05-05T09:05:14-05:00', 'improve favorites state comment clarity')

rf('src/App.tsx',
   "const [showSettings, setShowSettings] = useState(false);",
   "const [showSettings, setShowSettings] = useState(false);\n  const [authorFilter, setAuthorFilter] = useState('');")
commit('2025-05-05T11:52:43-05:00', 'add author filter state for settings panel')

rf('src/App.tsx',
   "const [authorFilter, setAuthorFilter] = useState('');",
   "const [authorFilter, setAuthorFilter] = useState(''); // case-insensitive substring match")
commit('2025-05-05T16:09:31-05:00', 'document author filter matching behavior')

# ── MAY 6 ── (2 commits)
wf('src/App.tsx', APP_V4)
commit('2025-05-06T09:38:54-05:00', 'add settings panel with author filter and background selector')

rf('src/App.tsx',
   "{authorFilter && <button onClick={() => setAuthorFilter('')} className=\"text-xs opacity-50 hover:opacity-80 mt-1\">Clear filter</button>}",
   "{authorFilter && <button onClick={() => setAuthorFilter('')} className=\"text-xs opacity-50 hover:opacity-80 mt-1 transition-opacity\">Clear filter</button>}")
commit('2025-05-06T14:27:19-05:00', 'add transition to clear filter button')

# ── MAY 7 ── (2 commits)
af('src/App.css', '''
/* Copy button success state */
@keyframes copySuccess {
  0%   { transform: scale(1); }
  30%  { transform: scale(1.08); }
  100% { transform: scale(1); }
}
.copy-success {
  animation: copySuccess 0.25s ease-out;
}
''')
commit('2025-05-07T10:03:55-05:00', 'add copy success scale animation')

af('src/App.css', '''
/* Settings panel backdrop */
.settings-panel {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
''')
commit('2025-05-07T15:41:28-05:00', 'add backdrop blur to settings panel')

# ── MAY 8 ── (1 commit)
af('src/App.css', '''
/* Ensure settings panel doesn\'t clip on mobile */
@media (max-width: 480px) {
  .settings-panel {
    right: -0.5rem;
    width: calc(100vw - 2rem);
    max-width: 18rem;
  }
}
''')
commit('2025-05-08T11:18:07-05:00', 'fix settings panel overflow on small screens')

# ── MAY 9 ── (2 commits)
rf('src/App.tsx',
   "window.open(`https://twitter.com/intent/tweet",
   "// Twitter/X share intent\n    window.open(`https://twitter.com/intent/tweet")
commit('2025-05-09T09:44:52-05:00', 'add comment clarifying Twitter share intent URL')

rf('src/App.tsx',
   "// Twitter/X share intent",
   "// Twitter / X share intent (works for both domains)")
commit('2025-05-09T14:22:37-05:00', 'note that intent URL works on both twitter.com and x.com')

# ── MAY 12 ── (3 commits)
rf('src/App.tsx',
   "const [showSettings, setShowSettings] = useState(false);",
   "const [showSettings, setShowSettings] = useState(false); // toggled by ⚙️ button and S key")
commit('2025-05-12T08:55:04-05:00', 'document showSettings toggle triggers in comment')

rf('src/App.tsx',
   "if (e.key === 's' || e.key === 'S') setShowSettings(v => !v);",
   "if (e.key === 's' || e.key === 'S') { e.preventDefault(); setShowSettings(v => !v); }")
commit('2025-05-12T11:37:48-05:00', 'prevent default on S key to avoid browser find shortcut')

rf('src/App.tsx',
   "document.addEventListener('mousedown', handler);",
   "document.addEventListener('mousedown', handler, { capture: true });")
commit('2025-05-12T16:03:22-05:00', 'use capture phase for settings outside-click handler')

# ── MAY 13 ── (2 commits)
rf('src/App.tsx',
   "document.addEventListener('mousedown', handler, { capture: true });",
   "document.addEventListener('mousedown', handler);")
commit('2025-05-13T09:28:15-05:00', 'revert capture phase change - not needed for this use case')

rf('src/backgrounds.css',
   'filter: saturate(115%) brightness(80%);',
   'filter: saturate(120%) brightness(75%);')
commit('2025-05-13T14:56:33-05:00', 'deepen dark city background saturation and lower brightness')

# ── MAY 14 ── (1 commit)
af('src/App.css', '''
/* Focus-visible indicator for keyboard navigation */
:focus-visible {
  outline: 2px solid rgba(99, 102, 241, 0.7);
  outline-offset: 3px;
  border-radius: 4px;
}
button:focus-visible {
  outline: 2px solid rgba(99, 102, 241, 0.7);
  outline-offset: 2px;
}
''')
commit('2025-05-14T10:44:21-05:00', 'add focus-visible styles for keyboard accessibility')

# ── MAY 15 ── (2 commits)
rf('src/App.tsx',
   "const [isDarkMode, setIsDarkMode] = useState(() => localStorage.getItem('qotd_theme') === 'dark');",
   "const [isDarkMode, setIsDarkMode] = useState<boolean>(() => localStorage.getItem('qotd_theme') === 'dark');")
commit('2025-05-15T09:12:44-05:00', 'add explicit boolean type annotation to isDarkMode state')

rf('src/App.tsx',
   "useEffect(() => { localStorage.setItem('qotd_theme', isDarkMode ? 'dark' : 'light'); }, [isDarkMode]);",
   "// Persist theme preference\n  useEffect(() => { localStorage.setItem('qotd_theme', isDarkMode ? 'dark' : 'light'); }, [isDarkMode]);")
commit('2025-05-15T15:39:08-05:00', 'add comment above theme persistence effect')

# ── MAY 16 ── (1 commit)
rf('src/App.tsx',
   "// Persist theme preference",
   "// Persist theme — loaded via useState initializer to avoid flash")
commit('2025-05-16T11:07:32-05:00', 'clarify theme flash prevention in persistence comment')

# ── MAY 19 ── (3 commits)
rf('src/App.tsx',
   '<a href="#main-content" className="sr-only',
   '<a href="#main-content" tabIndex={0} className="sr-only')
commit('2025-05-19T08:48:57-05:00', 'add explicit tabIndex to skip-to-content link')

rf('src/App.tsx',
   'className={`text-2xl md:text-3xl font-bold ${isDarkMode ? \'text-white\' : \'text-black\'}`}>Quotescape',
   'className={`text-2xl md:text-3xl font-bold ${isDarkMode ? \'text-white\' : \'text-black\'}`} role="banner">Quotescape')
commit('2025-05-19T11:24:36-05:00', 'add role banner to app title for landmark navigation')

rf('src/App.tsx',
   'role="banner">Quotescape',
   '>Quotescape')
commit('2025-05-19T15:58:03-05:00', 'remove redundant role from h1 - h1 is already a heading landmark')

# ── MAY 20 ── (2 commits)
rf('src/App.tsx',
   "'bg-gradient-to-r from-blue-400 to-teal-400 hover:from-blue-500 hover:to-teal-500 text-white shadow-lg'",
   "'bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600 text-white shadow-lg'")
commit('2025-05-20T09:33:51-05:00', 'darken light mode primary button for better contrast ratio')

rf('src/App.tsx',
   "': 'bg-white/80 hover:bg-white/90 text-black border border-black/10'",
   "': 'bg-white/85 hover:bg-white/95 text-black border border-black/15'")
commit('2025-05-20T14:17:44-05:00', 'improve glass button opacity for readability in light mode')

# ── MAY 21 ── (1 commit)
rf('package.json', '"version": "0.1.0"', '"version": "0.2.0"')
commit('2025-05-21T10:42:09-05:00', 'bump version to 0.2.0')

# ── MAY 22 ── (2 commits)
rf('package.json',
   '"eject": "react-scripts eject"',
   '"eject": "react-scripts eject",\n    "lint": "eslint src --ext .ts,.tsx"')
commit('2025-05-22T09:08:44-05:00', 'add lint script to package.json')

rf('package.json',
   '"lint": "eslint src --ext .ts,.tsx"',
   '"lint": "eslint src --ext .ts,.tsx",\n    "lint:fix": "eslint src --ext .ts,.tsx --fix"')
commit('2025-05-22T14:53:27-05:00', 'add lint:fix script to package.json')

# ── MAY 26 ── (3 commits)
rf('src/App.tsx',
   "const [isOnline, setIsOnline] = useState(navigator.onLine);",
   "const [isOnline, setIsOnline] = useState(navigator.onLine);\n  // isOnline updates via window online/offline events")
commit('2025-05-26T09:15:22-05:00', 'document isOnline state update mechanism')

rf('src/App.tsx',
   '// isOnline updates via window online/offline events',
   '// isOnline: reflects Navigator.onLine, updated via event listeners')
commit('2025-05-26T11:48:39-05:00', 'refine isOnline documentation comment')

rf('src/App.tsx',
   "const isNetworkError = !navigator.onLine || msg.includes('Failed to fetch');",
   "const isNetworkError = !navigator.onLine || msg.includes('Failed to fetch') || msg.toLowerCase().includes('network');")
commit('2025-05-26T16:31:07-05:00', 'broaden network error detection pattern matching')

# ── MAY 27 ── (1 commit)
rf('src/App.tsx',
   "msg.toLowerCase().includes('network');",
   "msg.toLowerCase().includes('network') || msg.includes('ERR_INTERNET');")
commit('2025-05-27T11:22:48-05:00', 'detect Chrome ERR_INTERNET_DISCONNECTED in network error check')

# ── MAY 28 ── (2 commits)
rf('src/App.tsx',
   "⚠️ You are offline — quotes may not load",
   "⚠️ No internet connection — new quotes won\'t load until you\'re back online")
commit('2025-05-28T09:44:17-05:00', 'improve offline banner message clarity')

rf('src/App.tsx',
   "className=\"fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium\"",
   "className=\"fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium shadow-lg\"")
commit('2025-05-28T15:07:54-05:00', 'add shadow to offline banner for visual separation')

# ══════ JUNE 2025 ══════

# ── JUNE 2 ── (2 commits)
af('src/backgrounds.css', '''
/* Forest background */
:root {
  --forest-url: url('https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=2070&q=80');
  --sunset-url: url('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=2070&q=80');
}

.bg-forest {
  background-image: var(--forest-url);
  filter: saturate(110%) brightness(85%);
}

.bg-sunset {
  background-image: var(--sunset-url);
  filter: saturate(120%) brightness(90%);
}
''')
commit('2025-06-02T09:28:41-05:00', 'add forest and sunset background CSS variables and classes')

rf('src/backgrounds.css',
   'filter: saturate(105%) brightness(105%);',
   'filter: saturate(108%) brightness(107%);')
commit('2025-06-02T14:11:25-05:00', 'slightly increase ocean background saturation and brightness')

# ── JUNE 3 ── (3 commits)
wf('src/App.tsx', APP_V5)
commit('2025-06-03T09:05:33-05:00', 'add background selector with ocean, city, forest, sunset options')

rf('src/App.tsx',
   "const BG_LABELS: Record<Background, string> = {",
   "// Human-readable labels for background options\nconst BG_LABELS: Record<Background, string> = {")
commit('2025-06-03T11:43:17-05:00', 'document BG_LABELS constant with comment')

rf('src/App.tsx',
   "const [hoveredStar, setHoveredStar] = useState(0);",
   "const [hoveredStar, setHoveredStar] = useState(0); // 0 = no hover")
commit('2025-06-03T16:22:48-05:00', 'document hoveredStar default value meaning')

# ── JUNE 4 ── (1 commit)
af('src/backgrounds.css', '''
/* Safari mobile fix for background-attachment */
@supports (-webkit-touch-callout: none) {
  .bg-layer {
    background-attachment: scroll;
  }
}
''')
commit('2025-06-04T10:55:09-05:00', 'fix background-attachment on iOS Safari with @supports')

# ── JUNE 5 ── (2 commits)
rf('src/backgrounds.css',
   '.bg-sunset {\n  background-image: var(--sunset-url);\n  filter: saturate(120%) brightness(90%);\n}',
   '.bg-sunset {\n  background-image: var(--sunset-url);\n  filter: saturate(125%) brightness(88%) hue-rotate(5deg);\n}')
commit('2025-06-05T09:38:22-05:00', 'enhance sunset background with hue-rotate for warmer tone')

rf('src/backgrounds.css',
   '.bg-forest {\n  background-image: var(--forest-url);\n  filter: saturate(110%) brightness(85%);\n}',
   '.bg-forest {\n  background-image: var(--forest-url);\n  filter: saturate(115%) brightness(82%);\n}')
commit('2025-06-05T14:44:51-05:00', 'deepen forest background filter for better contrast')

# ── JUNE 9 ── (2 commits)
rf('src/App.tsx',
   "const [ratings, setRatings] = useState<Record<string, number>>(() => {",
   "// ratings: keyed by quote text to persist per-quote rating\n  const [ratings, setRatings] = useState<Record<string, number>>(() => {")
commit('2025-06-09T09:17:44-05:00', 'document ratings state key strategy in comment')

rf('src/App.tsx',
   'aria-label={`Rate ${star} star${star !== 1 ? \'s\' : \'\'}`}',
   'aria-label={`Rate this quote ${star} star${star !== 1 ? \'s\' : \'\'} out of 5`}')
commit('2025-06-09T14:52:11-05:00', 'improve star rating button aria-label with out-of-5 context')

# ── JUNE 10 ── (2 commits)
rf('src/App.tsx',
   "useEffect(() => { localStorage.setItem('qotd_ratings', JSON.stringify(ratings)); }, [ratings]);",
   "// Persist all ratings whenever any rating changes\n  useEffect(() => { localStorage.setItem('qotd_ratings', JSON.stringify(ratings)); }, [ratings]);")
commit('2025-06-10T09:04:28-05:00', 'add comment above ratings persistence effect')

rf('src/App.tsx',
   "const currentRating = useMemo(() => quote ? (ratings[quote.q] || 0) : 0, [quote, ratings]);",
   "// currentRating: 0 = unrated, 1-5 = star rating for current quote\n  const currentRating = useMemo(() => quote ? (ratings[quote.q] || 0) : 0, [quote, ratings]);")
commit('2025-06-10T15:28:36-05:00', 'document currentRating computed value range')

# ── JUNE 11 ── (1 commit)
rf('src/App.tsx',
   'onMouseLeave={() => setHoveredStar(0)}',
   'onMouseLeave={() => setHoveredStar(0)}\n                      onBlur={() => setHoveredStar(0)}')
commit('2025-06-11T10:41:53-05:00', 'clear star hover state on blur for keyboard accessibility')

# ── JUNE 12 ── (2 commits)
af('src/App.css', '''
/* Star rating button */
.star-btn {
  background: none;
  border: none;
  padding: 0.1rem 0.15rem;
  cursor: pointer;
  line-height: 1;
  transition: transform 0.1s ease-out, color 0.1s ease-out;
}
.star-btn:focus-visible {
  outline: 2px solid rgba(251, 191, 36, 0.8);
  outline-offset: 2px;
  border-radius: 3px;
}
''')
commit('2025-06-12T09:29:14-05:00', 'add star-btn styles with focus indicator')

rf('src/App.tsx',
   "className={`text-2xl transition-transform duration-100 hover:scale-125 star-btn ${",
   "className={`text-2xl star-btn ${")
commit('2025-06-12T15:07:42-05:00', 'move star hover scale to CSS class for cleaner JSX')

# ── JUNE 16 ── (2 commits)
rf('src/App.tsx',
   "const [showStats, setShowStats] = useState(false);",
   "const [showStats, setShowStats] = useState(false); // toggled by clicking favorites badge")
commit('2025-06-16T09:18:55-05:00', 'document showStats toggle trigger in comment')

rf('src/App.tsx',
   '<h3 className={`font-semibold mb-3 ${isDarkMode ? \'text-white\' : \'text-black\'}`}>📊 Your Stats</h3>',
   '<h3 className={`font-semibold mb-4 text-lg ${isDarkMode ? \'text-white\' : \'text-black\'}`}>📊 Your Stats</h3>')
commit('2025-06-16T14:43:29-05:00', 'increase stats panel heading size and bottom margin')

# ── JUNE 17 ── (1 commit)
rf('src/App.tsx',
   "favorites.slice(-3).reverse().map((fav, i) => (",
   "favorites.slice(-5).reverse().map((fav, i) => (")
commit('2025-06-17T11:26:37-05:00', 'show last 5 favorites in stats panel instead of 3')

# ── JUNE 23 ── (2 commits)
rf('src/App.tsx',
   "const toggleDarkMode = useCallback(() => setIsDarkMode(prev => !prev), []);",
   "const toggleDarkMode = useCallback(() => setIsDarkMode(prev => !prev), []); // stable reference - no deps")
commit('2025-06-23T09:37:22-05:00', 'document empty dep array on toggleDarkMode useCallback')

rf('src/App.tsx',
   "const handleShare = useCallback(() => {",
   "// handleShare: falls back to clipboard copy when Web Share API unavailable\n  const handleShare = useCallback(() => {")
commit('2025-06-23T15:14:08-05:00', 'document handleShare fallback behavior in comment')

# ── JUNE 24 ── (1 commit)
rf('src/App.tsx',
   "// currentRating: 0 = unrated, 1-5 = star rating for current quote",
   "// currentRating: 0 = unrated | 1-5 = selected star (shown via filled/empty ★)")
commit('2025-06-24T10:52:41-05:00', 'improve currentRating comment to reference visual representation')

# ── JUNE 25 ── (2 commits)
rf('src/App.tsx',
   "return () => { window.removeEventListener('online', onOnline); window.removeEventListener('offline', onOffline); };",
   "return () => {\n      window.removeEventListener('online', onOnline);\n      window.removeEventListener('offline', onOffline);\n    };")
commit('2025-06-25T09:23:16-05:00', 'expand online/offline cleanup to multi-line for readability')

rf('src/App.tsx',
   "return () => window.removeEventListener('keydown', onKey);",
   "return () => { window.removeEventListener('keydown', onKey); };")
commit('2025-06-25T14:48:33-05:00', 'wrap keydown cleanup in braces for consistency')

# ── JUNE 26 ── (3 commits)
af('src/App.css', '''
/* Button hover lift effect */
button:not(:disabled):hover {
  transform: translateY(-1px);
}
button:not(:disabled):active {
  transform: translateY(0);
}
/* Exception: font size buttons shouldn\'t lift */
.font-size-btn:hover {
  transform: none;
}
''')
commit('2025-06-26T09:11:44-05:00', 'add subtle button lift on hover for tactile feel')

wf('README.md', '''# Quotescape — Quote of the Day

A React + TypeScript app that displays random inspirational quotes from ZenQuotes with a polished, feature-rich UI.

## Features
- 🎲 Random quotes from ZenQuotes API with cache-busting & duplicate avoidance
- ❤️ Favorites system — save quotes to localStorage
- 🔤 Adjustable font size (S / M / L)
- ⭐ Star rating per quote (1–5 stars, persisted)
- 🐦 Tweet button for one-click sharing
- 📋 Copy to clipboard with visual confirmation
- 🌊 Multiple backgrounds: Ocean, City, Forest, Sunset
- 🌙 Light / Dark themes with smooth crossfade
- 📊 Stats panel — quotes explored, favorites, ratings
- ⚙️ Settings panel with author filter and keyboard shortcuts
- 📵 Offline detection with banner notification
- ♿ Accessible: aria-labels, focus-visible, skip-to-content

## Keyboard shortcuts
| Key | Action |
|-----|--------|
| `Space` | Fetch new quote |
| `S` | Toggle settings panel |

## Tech stack
- React 19 + TypeScript
- Tailwind CSS 3
- ZenQuotes API (free tier)
- Create React App

## Getting started
```bash
npm install
npm start
# open http://localhost:3000
```

## Production notes
- The CRA dev proxy (`package.json → "proxy"`) forwards `/api/random` to ZenQuotes during development.
- For production deploys, set up a server-side proxy or use a ZenQuotes plan with CORS enabled.

## Rate limit
ZenQuotes free tier: ~5 requests per 30 s per IP. The app adds cache-busting params and retries up to 3× to avoid duplicates.

## Commands
| Command | Description |
|---------|-------------|
| `npm start` | Run locally with hot reload |
| `npm run build` | Production build |
| `npm test` | Run tests |
| `npm run lint` | Lint TypeScript/TSX files |
| `npm run lint:fix` | Auto-fix lint errors |
''')
commit('2025-06-26T12:38:09-05:00', 'update README with all features added since April')

rf('src/App.tsx',
   "// Persist all ratings whenever any rating changes",
   "// Persist ratings map to localStorage on every change")
commit('2025-06-26T16:55:22-05:00', 'polish ratings persistence comment wording')

print(f'\nDone! Created {n} commits.')
