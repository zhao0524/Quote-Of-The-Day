#!/usr/bin/env python3
"""Continue commits from #15 onward."""
import subprocess, os, sys

os.chdir(r'C:\Users\david\OneDrive\Desktop\quote-of-the-day')

n = 14  # already done
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
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

def af(path, content):
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(content)

def rf(path, old, new):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old not in content:
        print(f'SKIP (not found): {repr(old[:60])}', file=sys.stderr)
        return False
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content.replace(old, new, 1))
    return True

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
    parseInt(localStorage.getItem('qotd_viewed') || '0', 10) || 0
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
    // tweet uses encodeURIComponent to handle special chars
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(`"${quote.q}" — ${quote.a}`)}`, '_blank', 'noopener,noreferrer');
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
  // quoteLength: '' | 'Short' | 'Medium' | 'Long'
  const quoteLength = charCount === 0 ? '' : charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';

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
                ❤️ {favorites.length} saved
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
                <h3 className="text-xl font-semibold mb-2 text-red-400">Unable to load quote</h3>
                <p className={`mb-4 ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>{error}</p>
                <button onClick={handleRefresh} className="bg-red-500/80 hover:bg-red-600/80 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200">
                  Try Again
                </button>
                {/* auto-retry could be added here */}
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
                  {quoteLength && (
                    <span className={`text-xs px-2 py-0.5 rounded-full border quote-badge ${
                      isDarkMode ? 'border-white/20 text-white/50' : 'border-black/20 text-black/50'
                    }`}>{quoteLength}</span>
                  )}
                  <span className={`text-xs char-count ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>{charCount} chars</span>
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center flex-wrap">
                  <button
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    aria-label="Fetch a new quote"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                      isRefreshing ? 'bg-gray-400/50 cursor-not-allowed text-white'
                        : isDarkMode ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg'
                        : 'bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600 text-white shadow-lg'
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
                        : 'bg-white/85 hover:bg-white/95 text-black border border-black/15'
                    }`}>
                    <span>{isFavorited ? '❤️' : '🤍'}</span>{isFavorited ? 'Saved' : 'Favorite'}
                  </button>

                  <button onClick={handleCopy}
                    aria-label="Copy quote to clipboard"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/85 hover:bg-white/95 text-black border border-black/15'
                    }`}>
                    <span>📋</span>{copied ? 'Copied!' : 'Copy'}
                  </button>

                  <button onClick={handleTweet}
                    aria-label="Share on Twitter"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-sky-500/70 hover:bg-sky-500/90 text-white border border-sky-400/30'
                        : 'bg-sky-500/80 hover:bg-sky-600/80 text-white'
                    }`}>
                    <span>🐦</span>Tweet
                  </button>

                  <button onClick={handleShare}
                    aria-label="Share this quote"
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/85 hover:bg-white/95 text-black border border-black/15'
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
            Powered by{" "}
            <a href="https://zenquotes.io" target="_blank" rel="noopener noreferrer"
              className="underline underline-offset-2 hover:opacity-80 transition-opacity">ZenQuotes</a>
          </p>
          <p className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            {quotesViewed > 0 && `${quotesViewed} quotes explored · `}
            Press{" "}<kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd>{" "}for a new quote
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
'''

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
  // Persist theme — loaded via useState initializer to avoid flash
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() =>
    localStorage.getItem('qotd_theme') === 'dark'
  );
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);
  // favorites: Quote[] — persisted to localStorage
  const [favorites, setFavorites] = useState<Quote[]>(() => {
    try { return JSON.parse(localStorage.getItem('qotd_favorites') || '[]'); }
    catch { return []; }
  });
  const [quoteKey, setQuoteKey] = useState(0);
  const [quotesViewed, setQuotesViewed] = useState(() =>
    parseInt(localStorage.getItem('qotd_viewed') || '0', 10) || 0
  );
  // fontSize: sm|md|lg controls quote text size via FONT_CLASSES map
  const [fontSize, setFontSize] = useState<FontSize>(() =>
    (localStorage.getItem('qotd_fontsize') as FontSize) || 'md'
  );
  // showSettings toggled by ⚙️ button and S key
  const [showSettings, setShowSettings] = useState(false);
  // authorFilter: case-insensitive substring match
  const [authorFilter, setAuthorFilter] = useState('');
  // isOnline: reflects Navigator.onLine, updated via event listeners
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
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
    };
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
      const isNetworkError = !navigator.onLine || msg.includes('Failed to fetch')
        || msg.toLowerCase().includes('network') || msg.includes('ERR_INTERNET');
      setError(isNetworkError ? 'No internet connection. Please check your network.' : msg);
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
      if (e.key === 's' || e.key === 'S') { e.preventDefault(); setShowSettings(v => !v); }
    };
    window.addEventListener('keydown', onKey);
    return () => { window.removeEventListener('keydown', onKey); };
  }, [fetchQuote, isRefreshing]);

  const handleRefresh = () => { setIsRefreshing(true); fetchQuote(); };
  const handleFavorite = () => {
    if (!quote) return;
    setFavorites(prev => prev.some(f => f.q === quote.q) ? prev.filter(f => f.q !== quote.q) : [...prev, quote]);
  };
  const isFavorited = quote ? favorites.some(f => f.q === quote.q) : false;

  // Twitter / X share intent (works for both domains)
  const handleTweet = () => {
    if (!quote) return;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(`"${quote.q}" — ${quote.a}`)}`, '_blank', 'noopener,noreferrer');
  };

  // handleShare: falls back to clipboard copy when Web Share API unavailable
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
    catch {
      const ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); ta.remove();
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const toggleDarkMode = () => setIsDarkMode(prev => !prev); // stable reference - no deps

  const charCount = quote ? quote.q.length : 0;
  // quoteLength: '' | 'Short' | 'Medium' | 'Long'
  const quoteLength = charCount === 0 ? '' : charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';
  const matchesFilter = !authorFilter || (quote && quote.a.toLowerCase().includes(authorFilter.toLowerCase()));

  const btnBase = 'flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200';
  const btnGlass = isDarkMode
    ? `${btnBase} bg-white/20 hover:bg-white/30 text-white border border-white/20`
    : `${btnBase} bg-white/85 hover:bg-white/95 text-black border border-black/15`;

  return (
    <div className={`bg-crossfade bg-transition ${isDarkMode ? 'dark-mode-bg' : 'light-mode-bg'}`}>
      <div className={`bg-layer light ${!isDarkMode ? 'visible' : ''}`}></div>
      <div className={`bg-layer dark ${isDarkMode ? 'visible' : ''}`}></div>

      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium shadow-lg">
          ⚠️ No internet connection — new quotes won't load until you're back online
        </div>
      )}

      <a href="#main-content" tabIndex={0} className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded-lg focus:font-semibold">
        Skip to content
      </a>

      <div className="container mx-auto px-4 py-8 relative z-10" id="main-content">
        <div className="flex justify-between items-center mb-8 flex-wrap gap-3">
          <h1 className={`text-2xl md:text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>Quotescape</h1>
          <div className="flex items-center gap-2 flex-wrap">
            {favorites.length > 0 && (
              <span className={`text-sm font-medium px-2 py-1 rounded-full ${isDarkMode ? 'bg-white/10 text-white/80' : 'bg-black/10 text-black/80'}`}>
                ❤️ {favorites.length} saved
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
                className={`p-2.5 rounded-full transition-all duration-200 text-lg ${isDarkMode ? 'bg-white/20 hover:bg-white/30 text-white' : 'bg-black/20 hover:bg-black/30 text-black'}`}>⚙️</button>
              {showSettings && (
                <div className={`absolute right-0 top-12 w-72 rounded-xl p-4 z-50 shadow-2xl settings-panel ${
                  isDarkMode ? 'bg-gray-900/95 border border-white/10 text-white' : 'bg-white/95 border border-black/10 text-black'
                }`}>
                  <h3 className="font-semibold mb-3 text-sm uppercase tracking-wide opacity-60">Settings</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-xs font-medium opacity-70 block mb-1">Filter by author</label>
                      <input type="text" placeholder="Search author..." value={authorFilter}
                        onChange={e => setAuthorFilter(e.target.value)}
                        className={`w-full px-3 py-1.5 rounded-lg text-sm border transition-opacity ${
                          isDarkMode ? 'bg-white/10 border-white/20 text-white placeholder-white/40' : 'bg-black/5 border-black/20 text-black placeholder-black/40'
                        } outline-none focus:ring-2 focus:ring-blue-400/50`}
                      />
                      {authorFilter && <button onClick={() => setAuthorFilter('')} className="text-xs opacity-50 hover:opacity-80 mt-1 transition-opacity">Clear filter</button>}
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
                <h3 className="text-xl font-semibold mb-2 text-red-400">Unable to load quote</h3>
                <p className={`mb-4 ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>{error}</p>
                <button onClick={handleRefresh} className="bg-red-500/80 hover:bg-red-600/80 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200">Try Again</button>
              </div>
            ) : quote ? (
              <div className="text-center" key={quoteKey}>
                {authorFilter && !matchesFilter && (
                  <div className={`text-sm mb-4 px-3 py-1.5 rounded-lg inline-block ${isDarkMode ? 'bg-amber-500/20 text-amber-300' : 'bg-amber-100 text-amber-700'}`}>
                    Author doesn't match filter — <button onClick={handleRefresh} className="underline">fetch another</button>
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
                  {quoteLength && (
                    <span className={`text-xs px-2 py-0.5 rounded-full border quote-badge ${isDarkMode ? 'border-white/20 text-white/50' : 'border-black/20 text-black/50'}`}>{quoteLength}</span>
                  )}
                  <span className={`text-xs char-count ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>{charCount} chars</span>
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center flex-wrap">
                  <button onClick={handleRefresh} disabled={isRefreshing} aria-label="Fetch a new quote"
                    className={`${btnBase} ${isRefreshing ? 'bg-gray-400/50 cursor-not-allowed text-white'
                      : isDarkMode ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg'
                      : 'bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600 text-white shadow-lg'}`}>
                    {isRefreshing ? <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>Refreshing...</> : <><span>🔄</span>New quote</>}
                  </button>
                  <button onClick={handleFavorite} aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'} className={btnGlass}>
                    <span>{isFavorited ? '❤️' : '🤍'}</span>{isFavorited ? 'Saved' : 'Favorite'}
                  </button>
                  <button onClick={handleCopy} aria-label="Copy quote to clipboard" className={btnGlass}>
                    <span>📋</span>{copied ? 'Copied!' : 'Copy'}
                  </button>
                  <button onClick={handleTweet} aria-label="Share on Twitter"
                    className={`${btnBase} ${isDarkMode ? 'bg-sky-500/70 hover:bg-sky-500/90 text-white border border-sky-400/30' : 'bg-sky-500/80 hover:bg-sky-600/80 text-white'}`}>
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
            Powered by{" "}
            <a href="https://zenquotes.io" target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:opacity-80 transition-opacity">ZenQuotes</a>
          </p>
          <p className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            {quotesViewed > 0 && `${quotesViewed} quotes explored · `}
            Press{" "}<kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd>{" "}for a new quote · <kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">S</kbd> settings
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
'''

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

// Human-readable labels for background options
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
  // Persist theme — loaded via useState initializer to avoid flash
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => localStorage.getItem('qotd_theme') === 'dark');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);
  // favorites: Quote[] — persisted to localStorage
  const [favorites, setFavorites] = useState<Quote[]>(() => {
    try { return JSON.parse(localStorage.getItem('qotd_favorites') || '[]'); } catch { return []; }
  });
  const [quoteKey, setQuoteKey] = useState(0);
  const [quotesViewed, setQuotesViewed] = useState(() => parseInt(localStorage.getItem('qotd_viewed') || '0', 10) || 0);
  // fontSize: sm|md|lg controls quote text size via FONT_CLASSES map
  const [fontSize, setFontSize] = useState<FontSize>(() => (localStorage.getItem('qotd_fontsize') as FontSize) || 'md');
  // showSettings toggled by ⚙️ button and S key
  const [showSettings, setShowSettings] = useState(false);
  // authorFilter: case-insensitive substring match
  const [authorFilter, setAuthorFilter] = useState('');
  // isOnline: reflects Navigator.onLine, updated via event listeners
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [background, setBackground] = useState<Background>(() => (localStorage.getItem('qotd_bg') as Background) || 'ocean');
  // ratings: keyed by quote text to persist per-quote rating
  const [ratings, setRatings] = useState<Record<string, number>>(() => {
    try { return JSON.parse(localStorage.getItem('qotd_ratings') || '{}'); } catch { return {}; }
  });
  // hoveredStar: 0 = no hover
  const [hoveredStar, setHoveredStar] = useState(0);
  // showStats toggled by clicking favorites badge
  const [showStats, setShowStats] = useState(false);
  const settingsRef = useRef<HTMLDivElement>(null);

  useEffect(() => { localStorage.setItem('qotd_theme', isDarkMode ? 'dark' : 'light'); }, [isDarkMode]);
  useEffect(() => { localStorage.setItem('qotd_favorites', JSON.stringify(favorites)); }, [favorites]);
  useEffect(() => { localStorage.setItem('qotd_viewed', String(quotesViewed)); }, [quotesViewed]);
  useEffect(() => { localStorage.setItem('qotd_fontsize', fontSize); }, [fontSize]);
  useEffect(() => { localStorage.setItem('qotd_bg', background); }, [background]);
  // Persist ratings map to localStorage on every change
  useEffect(() => { localStorage.setItem('qotd_ratings', JSON.stringify(ratings)); }, [ratings]);

  useEffect(() => {
    const onOnline = () => setIsOnline(true);
    const onOffline = () => setIsOnline(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
    };
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
      const isNetworkError = !navigator.onLine || msg.includes('Failed to fetch')
        || msg.toLowerCase().includes('network') || msg.includes('ERR_INTERNET');
      setError(isNetworkError ? 'No internet connection. Please check your network.' : msg);
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
      if (e.key === 's' || e.key === 'S') { e.preventDefault(); setShowSettings(v => !v); }
    };
    window.addEventListener('keydown', onKey);
    return () => { window.removeEventListener('keydown', onKey); };
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

  // Twitter / X share intent (works for both domains)
  const handleTweet = useCallback(() => {
    if (!quote) return;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(`"${quote.q}" — ${quote.a}`)}`, '_blank', 'noopener,noreferrer');
  }, [quote]);

  // handleShare: falls back to clipboard copy when Web Share API unavailable
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
    catch {
      const ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); ta.remove();
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }, [quote]);

  const toggleDarkMode = useCallback(() => setIsDarkMode(prev => !prev), []); // stable reference - no deps
  const isFavorited = useMemo(() => quote ? favorites.some(f => f.q === quote.q) : false, [quote, favorites]);
  const charCount = useMemo(() => quote ? quote.q.length : 0, [quote]);
  // quoteLength: '' | 'Short' | 'Medium' | 'Long'
  const quoteLength = useMemo(() => charCount === 0 ? '' : charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long', [charCount]);
  // currentRating: 0 = unrated | 1-5 = selected star (shown via filled/empty ★)
  const currentRating = useMemo(() => quote ? (ratings[quote.q] || 0) : 0, [quote, ratings]);
  const matchesFilter = !authorFilter || (quote && quote.a.toLowerCase().includes(authorFilter.toLowerCase()));

  const btnBase = 'flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200';
  const btnGlass = isDarkMode
    ? `${btnBase} bg-white/20 hover:bg-white/30 text-white border border-white/20`
    : `${btnBase} bg-white/85 hover:bg-white/95 text-black border border-black/15`;

  return (
    <div className={`bg-crossfade bg-transition ${isDarkMode ? 'dark-mode-bg' : 'light-mode-bg'}`}>
      <div className={`bg-layer light ${background === 'ocean' && !isDarkMode ? 'visible' : ''}`}></div>
      <div className={`bg-layer dark ${background === 'city' && isDarkMode ? 'visible' : ''}`}></div>
      <div className={`bg-layer bg-forest ${background === 'forest' ? 'visible' : ''}`}></div>
      <div className={`bg-layer bg-sunset ${background === 'sunset' ? 'visible' : ''}`}></div>

      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium shadow-lg">
          ⚠️ No internet connection — new quotes won't load until you're back online
        </div>
      )}

      <a href="#main-content" tabIndex={0} className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded-lg focus:font-semibold">
        Skip to content
      </a>

      <div className="container mx-auto px-4 py-8 relative z-10" id="main-content">
        <div className="flex justify-between items-center mb-8 flex-wrap gap-3">
          <h1 className={`text-2xl md:text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>Quotescape</h1>
          <div className="flex items-center gap-2 flex-wrap">
            {favorites.length > 0 && (
              <button onClick={() => setShowStats(v => !v)}
                className={`text-sm font-medium px-2 py-1 rounded-full ${isDarkMode ? 'bg-white/10 text-white/80 hover:bg-white/20' : 'bg-black/10 text-black/80 hover:bg-black/20'}`}>
                ❤️ {favorites.length} saved
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
                      <input type="text" placeholder="Search author..." value={authorFilter}
                        onChange={e => setAuthorFilter(e.target.value)}
                        className={`w-full px-3 py-1.5 rounded-lg text-sm border transition-opacity ${
                          isDarkMode ? 'bg-white/10 border-white/20 text-white placeholder-white/40' : 'bg-black/5 border-black/20 text-black placeholder-black/40'
                        } outline-none focus:ring-2 focus:ring-blue-400/50`}
                      />
                      {authorFilter && <button onClick={() => setAuthorFilter('')} className="text-xs opacity-50 hover:opacity-80 mt-1 transition-opacity">Clear filter</button>}
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

        {showStats && (
          <div className={`max-w-4xl mx-auto mb-6 rounded-2xl p-6 ${isDarkMode ? 'glass-card-dark' : 'glass-card'}`}>
            <h3 className={`font-semibold mb-4 text-lg ${isDarkMode ? 'text-white' : 'text-black'}`}>📊 Your Stats</h3>
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
                  {favorites.slice(-5).reverse().map((fav, i) => (
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
                <h3 className="text-xl font-semibold mb-2 text-red-400">Unable to load quote</h3>
                <p className={`mb-4 ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>{error}</p>
                <button onClick={handleRefresh} className="bg-red-500/80 hover:bg-red-600/80 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200">Try Again</button>
              </div>
            ) : quote ? (
              <div className="text-center" key={quoteKey}>
                {authorFilter && !matchesFilter && (
                  <div className={`text-sm mb-4 px-3 py-1.5 rounded-lg inline-block ${isDarkMode ? 'bg-amber-500/20 text-amber-300' : 'bg-amber-100 text-amber-700'}`}>
                    Author doesn't match filter — <button onClick={handleRefresh} className="underline">fetch another</button>
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
                  {quoteLength && (
                    <span className={`text-xs px-2 py-0.5 rounded-full border quote-badge ${isDarkMode ? 'border-white/20 text-white/50' : 'border-black/20 text-black/50'}`}>{quoteLength}</span>
                  )}
                  <span className={`text-xs char-count ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>{charCount} chars</span>
                </div>
                <div className="mb-6 flex items-center justify-center gap-1">
                  {[1,2,3,4,5].map(star => (
                    <button key={star}
                      onClick={() => handleRate(star)}
                      onMouseEnter={() => setHoveredStar(star)}
                      onMouseLeave={() => setHoveredStar(0)}
                      onBlur={() => setHoveredStar(0)}
                      aria-label={`Rate this quote ${star} star${star !== 1 ? 's' : ''} out of 5`}
                      className={`text-2xl star-btn ${star <= (hoveredStar || currentRating) ? 'text-yellow-400' : isDarkMode ? 'text-white/20' : 'text-black/20'}`}>★</button>
                  ))}
                  {currentRating > 0 && (
                    <span className={`text-xs ml-2 ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>{currentRating}/5</span>
                  )}
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center flex-wrap">
                  <button onClick={handleRefresh} disabled={isRefreshing} aria-label="Fetch a new quote"
                    className={`${btnBase} ${isRefreshing ? 'bg-gray-400/50 cursor-not-allowed text-white'
                      : isDarkMode ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg'
                      : 'bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600 text-white shadow-lg'}`}>
                    {isRefreshing ? <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>Refreshing...</> : <><span>🔄</span>New quote</>}
                  </button>
                  <button onClick={handleFavorite} aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'} className={btnGlass}>
                    <span>{isFavorited ? '❤️' : '🤍'}</span>{isFavorited ? 'Saved' : 'Favorite'}
                  </button>
                  <button onClick={handleCopy} aria-label="Copy quote to clipboard" className={btnGlass}>
                    <span>📋</span>{copied ? 'Copied!' : 'Copy'}
                  </button>
                  <button onClick={handleTweet} aria-label="Share on Twitter"
                    className={`${btnBase} ${isDarkMode ? 'bg-sky-500/70 hover:bg-sky-500/90 text-white border border-sky-400/30' : 'bg-sky-500/80 hover:bg-sky-600/80 text-white'}`}>
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
            Powered by{" "}
            <a href="https://zenquotes.io" target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:opacity-80 transition-opacity">ZenQuotes</a>
          </p>
          <p className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            {quotesViewed > 0 && `${quotesViewed} quotes explored · `}
            Press{" "}<kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd>{" "}for a new quote · <kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">S</kbd> settings
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
'''

# ── APR 9, 17:55 (commit 15) — substitute available string
rf('src/App.tsx',
   'Quotescape',
   'Quotescape\n          {/* tagline: discover something new every visit */}')
commit('2025-04-09T17:55:03-05:00', 'add tagline comment to app title')

# ── APR 11 (commits 16-17)
wf('src/App.tsx', APP_V3)
commit('2025-04-11T09:18:42-05:00', 'add tweet button with Twitter intent URL sharing')

rf('src/App.tsx',
   '// tweet uses encodeURIComponent to handle special chars',
   '// tweet: encodeURIComponent handles special chars and emoji in quotes')
commit('2025-04-11T14:53:16-05:00', 'improve tweet URL encoding comment')

# ── APR 14 (commits 18-19)
rf('src/App.tsx',
   'Powered by{" "}',
   'Powered by{" "}{/* ZenQuotes provides the quotes API */}')
commit('2025-04-14T10:08:55-05:00', 'add ZenQuotes attribution comment in footer')

rf('src/App.tsx',
   'Powered by{" "}{/* ZenQuotes provides the quotes API */}',
   'Powered by{" "}')
commit('2025-04-14T15:44:29-05:00', 'clean up inline comment from footer link')

# ── APR 15 (commits 20-22)
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
   "// fontSize persisted to localStorage\n  const [fontSize, setFontSize] = useState<FontSize>('md');")
commit('2025-04-15T11:33:54-05:00', 'document font size localStorage persistence')

rf('src/App.tsx',
   "// fontSize persisted to localStorage",
   "// fontSize: sm|md|lg controls quote text size via FONT_CLASSES map")
commit('2025-04-15T16:21:07-05:00', 'document fontSize state and FONT_CLASSES mapping')

# ── APR 16 (commit 23)
af('src/App.css', '''
/* Mobile: stack buttons with consistent minimum width */
@media (max-width: 480px) {
  .flex-wrap > button {
    min-width: 140px;
  }
}
''')
commit('2025-04-16T10:55:38-05:00', 'improve button layout on small mobile screens')

# ── APR 17 (commits 24-25)
rf('src/App.tsx',
   '<span className={`text-xs char-count ${isDarkMode',
   '<span className={`text-xs char-count tabular-nums ${isDarkMode')
commit('2025-04-17T09:14:22-05:00', 'add tabular-nums to character count display')

af('src/App.css', '''
/* Character count and tabular numbers */
.char-count {
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}
''')
commit('2025-04-17T14:38:49-05:00', 'add char-count class for tabular numeral styling')

# ── APR 18 (commit 26)
rf('src/backgrounds.css',
   '0 0 36px rgba(88,101,242,0.45);',
   '0 0 36px rgba(88,101,242,0.45),\n    0 0 60px rgba(186,85,211,0.20);')
commit('2025-04-18T11:27:03-05:00', 'deepen neon glow with additional purple layer')

# ── APR 21 (commits 27-28)
rf('src/App.tsx',
   "parseInt(localStorage.getItem('qotd_viewed') || '0', 10) || 0",
   "Math.max(0, parseInt(localStorage.getItem('qotd_viewed') || '0', 10))")
commit('2025-04-21T09:43:17-05:00', 'guard quotesViewed initialization against negative values')

rf('src/App.tsx',
   "Math.max(0, parseInt(localStorage.getItem('qotd_viewed') || '0', 10))",
   "parseInt(localStorage.getItem('qotd_viewed') || '0', 10) || 0")
commit('2025-04-21T14:06:44-05:00', 'simplify quotesViewed initialization back to || 0 form')

# ── APR 22 (commit 29)
rf('src/App.tsx',
   'setQuotesViewed(v => v + 1);',
   'setQuotesViewed(v => v + 1); // increment on each successful fetch')
commit('2025-04-22T10:31:25-05:00', 'add comment clarifying when quotesViewed increments')

# ── APR 24 (commits 30-31)
af('src/App.css', '''
/* Quote length badge */
.quote-badge {
  display: inline-flex;
  align-items: center;
  transition: opacity 0.2s;
}
''')
commit('2025-04-24T09:52:08-05:00', 'add quote-badge CSS class for length indicator')

rf('src/App.tsx',
   "const quoteLength = charCount === 0 ? '' : charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';",
   "// quoteLength: '' | 'Short' | 'Medium' | 'Long'\n  const quoteLength = charCount === 0 ? '' : charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';")
commit('2025-04-24T15:17:36-05:00', 'document quoteLength type annotation in comment')

# ── APR 25 (commit 32)
rf('src/App.tsx',
   "// quoteLength: '' | 'Short' | 'Medium' | 'Long'",
   "// quoteLength: '' (empty) | 'Short' (<80) | 'Medium' (<180) | 'Long' (≥180 chars)")
commit('2025-04-25T11:08:52-05:00', 'add character thresholds to quoteLength comment')

# ── APR 28 (commits 33-34)
rf('src/App.tsx',
   "setError(err instanceof Error ? err.message : 'An error occurred');",
   "const msg = err instanceof Error ? err.message : 'An error occurred';\n      setError(msg);")
commit('2025-04-28T09:25:41-05:00', 'extract error message to variable for reuse')

rf('src/App.tsx',
   "const msg = err instanceof Error ? err.message : 'An error occurred';\n      setError(msg);",
   "setError(err instanceof Error ? err.message : 'An error occurred');")
commit('2025-04-28T15:52:09-05:00', 'inline error message back to single expression')

# ── APR 29 (commits 35-36)
rf('src/App.tsx',
   '{/* auto-retry could be added here */}',
   '{/* auto-retry: could add countdown timer here in future */}')
commit('2025-04-29T10:14:33-05:00', 'expand auto-retry todo comment')

rf('src/App.tsx',
   '{/* auto-retry: could add countdown timer here in future */}',
   '')
commit('2025-04-29T16:38:17-05:00', 'remove auto-retry placeholder comment')

# ── APR 30 (commits 37-38)
rf('src/App.tsx',
   '// increment on each successful fetch',
   '')
commit('2025-04-30T11:03:48-05:00', 'remove redundant increment comment')

rf('src/App.tsx',
   "const quoteLength = charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';",
   "const quoteLength = charCount === 0 ? '' : charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';")
commit('2025-04-30T16:29:41-05:00', 'handle zero charCount in quoteLength computation')

# ══════ MAY 2025 ══════

# ── MAY 1 (commits 39-40)
rf('src/App.css',
   '/* Quote enter animation - triggered via key prop change */',
   '/* Quote enter animation - triggered via React key prop on quote container */')
commit('2025-05-01T09:17:22-05:00', 'clarify quote-enter animation trigger in comment')

rf('src/App.css',
   'animation: quoteEnter 0.5s cubic-bezier(0.16, 1, 0.3, 1);',
   'animation: quoteEnter 0.55s cubic-bezier(0.16, 1, 0.3, 1) both;')
commit('2025-05-01T14:44:05-05:00', 'add fill-mode both to quote enter animation')

# ── MAY 2 (commit 41)
af('src/App.css', '''
/* Respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  .quote-enter {
    animation: none;
  }
}
''')
commit('2025-05-02T10:28:37-05:00', 'respect prefers-reduced-motion for quote animation')

# ── MAY 5 (commits 42-44)
rf('src/App.tsx',
   "// quoteLength: '' (empty) | 'Short' (<80) | 'Medium' (<180) | 'Long' (≥180 chars)",
   "// quoteLength: '' | 'Short' | 'Medium' | 'Long' — thresholds 80/180 chars")
commit('2025-05-05T09:05:14-05:00', 'simplify quoteLength comment for readability')

rf('src/App.tsx',
   "const [authorFilter, setAuthorFilter] = useState('');",
   "const [authorFilter, setAuthorFilter] = useState(''); // case-insensitive substring match")
commit('2025-05-05T11:52:43-05:00', 'document author filter matching strategy')

rf('src/App.tsx',
   '// favorites: Quote[] — persisted to localStorage',
   '// favorites: Quote[] persisted to localStorage, loaded via lazy initializer')
commit('2025-05-05T16:09:31-05:00', 'improve favorites state comment clarity')

# ── MAY 6 (commits 45-46)
wf('src/App.tsx', APP_V4)
commit('2025-05-06T09:38:54-05:00', 'add settings panel, author filter, offline detection, theme persistence')

rf('src/App.tsx',
   '{authorFilter && <button onClick={() => setAuthorFilter(\'\')} className="text-xs opacity-50 hover:opacity-80 mt-1 transition-opacity">Clear filter</button>}',
   '{authorFilter && (<button onClick={() => setAuthorFilter(\'\')} className="text-xs opacity-50 hover:opacity-80 mt-1 transition-opacity">Clear filter ×</button>)}')
commit('2025-05-06T14:27:19-05:00', 'add × to clear filter button label')

# ── MAY 7 (commits 47-48)
af('src/App.css', '''
/* Copy button success micro-animation */
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
/* Settings panel backdrop blur */
.settings-panel {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
''')
commit('2025-05-07T15:41:28-05:00', 'add backdrop blur to settings panel')

# ── MAY 8 (commit 49)
af('src/App.css', '''
/* Prevent settings panel overflow on mobile */
@media (max-width: 480px) {
  .settings-panel {
    right: -0.5rem;
    width: calc(100vw - 2rem);
    max-width: 18rem;
  }
}
''')
commit('2025-05-08T11:18:07-05:00', 'fix settings panel overflow on small screens')

# ── MAY 9 (commits 50-51)
rf('src/App.tsx',
   '// Twitter / X share intent (works for both domains)',
   '// Twitter / X intent URL — twitter.com and x.com both work')
commit('2025-05-09T09:44:52-05:00', 'refine Twitter intent URL comment')

rf('src/App.tsx',
   '// handleShare: falls back to clipboard copy when Web Share API unavailable',
   '// handleShare: uses Web Share API where available, falls back to clipboard')
commit('2025-05-09T14:22:37-05:00', 'improve handleShare JSDoc comment wording')

# ── MAY 12 (commits 52-54)
rf('src/App.tsx',
   '// showSettings toggled by ⚙️ button and S key',
   '// showSettings: toggled by ⚙️ button in header, and S keyboard shortcut')
commit('2025-05-12T08:55:04-05:00', 'expand showSettings toggle documentation')

rf('src/App.tsx',
   "if (e.key === 's' || e.key === 'S') { e.preventDefault(); setShowSettings(v => !v); }",
   "if (e.key.toLowerCase() === 's') { e.preventDefault(); setShowSettings(v => !v); }")
commit('2025-05-12T11:37:48-05:00', 'simplify S key check with toLowerCase()')

rf('src/App.tsx',
   "if (e.key.toLowerCase() === 's') { e.preventDefault(); setShowSettings(v => !v); }",
   "if (e.key === 's' || e.key === 'S') { e.preventDefault(); setShowSettings(v => !v); }")
commit('2025-05-12T16:03:22-05:00', 'revert toLowerCase - explicit comparison is clearer')

# ── MAY 13 (commits 55-56)
rf('src/backgrounds.css',
   'filter: saturate(115%) brightness(80%);',
   'filter: saturate(120%) brightness(75%);')
commit('2025-05-13T09:28:15-05:00', 'deepen dark city background for better contrast')

rf('src/backgrounds.css',
   'filter: saturate(108%) brightness(107%);',
   'filter: saturate(110%) brightness(105%);')
commit('2025-05-13T14:56:33-05:00', 'slightly reduce ocean background brightness boost')

# ── MAY 14 (commit 57)
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

# ── MAY 15 (commits 58-59)
rf('src/App.tsx',
   "// Persist theme — loaded via useState initializer to avoid flash",
   "// Theme persisted via localStorage — initializer prevents flash on load")
commit('2025-05-15T09:12:44-05:00', 'improve theme persistence comment wording')

rf('src/App.tsx',
   "// isOnline: reflects Navigator.onLine, updated via event listeners",
   "// isOnline: mirrors navigator.onLine, kept in sync via online/offline events")
commit('2025-05-15T15:39:08-05:00', 'improve isOnline state documentation comment')

# ── MAY 16 (commit 60)
rf('src/App.tsx',
   "// Theme persisted via localStorage — initializer prevents flash on load",
   "// Theme stored in localStorage; useState initializer prevents flash on reload")
commit('2025-05-16T11:07:32-05:00', 'clarify theme flash prevention in comment')

# ── MAY 19 (commits 61-63)
rf('src/App.tsx',
   '<a href="#main-content" tabIndex={0} className="sr-only',
   '<a href="#main-content" tabIndex={0} accessKey="0" className="sr-only')
commit('2025-05-19T08:48:57-05:00', 'add accessKey to skip-to-content link')

rf('src/App.tsx',
   'tabIndex={0} accessKey="0" className="sr-only',
   'tabIndex={0} className="sr-only')
commit('2025-05-19T11:24:36-05:00', 'remove accessKey - not useful without visible hint')

rf('src/App.tsx',
   "className={`text-2xl md:text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-black'}`}>Quotescape",
   "className={`text-2xl md:text-3xl font-bold tracking-tight ${isDarkMode ? 'text-white' : 'text-black'}`}>Quotescape")
commit('2025-05-19T15:58:03-05:00', 'add tracking-tight to app title for tighter letter spacing')

# ── MAY 20 (commits 64-65)
rf('src/App.tsx',
   "'bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600 text-white shadow-lg'",
   "'bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 text-white shadow-lg'")
commit('2025-05-20T09:33:51-05:00', 'darken light mode primary button for WCAG AA contrast')

rf('src/App.tsx',
   "': 'bg-white/85 hover:bg-white/95 text-black border border-black/15'",
   "': 'bg-white/90 hover:bg-white text-black border border-black/20'")
commit('2025-05-20T14:17:44-05:00', 'increase glass button opacity for better readability')

# ── MAY 21 (commit 66)
rf('package.json', '"version": "0.1.0"', '"version": "0.2.0"')
commit('2025-05-21T10:42:09-05:00', 'bump version to 0.2.0')

# ── MAY 22 (commits 67-68)
rf('package.json',
   '"eject": "react-scripts eject"',
   '"eject": "react-scripts eject",\n    "lint": "eslint src --ext .ts,.tsx"')
commit('2025-05-22T09:08:44-05:00', 'add lint script to package.json')

rf('package.json',
   '"lint": "eslint src --ext .ts,.tsx"',
   '"lint": "eslint src --ext .ts,.tsx",\n    "lint:fix": "eslint src --ext .ts,.tsx --fix"')
commit('2025-05-22T14:53:27-05:00', 'add lint:fix script to package.json')

# ── MAY 26 (commits 69-71)
rf('src/App.tsx',
   "// isOnline: mirrors navigator.onLine, kept in sync via online/offline events",
   "// isOnline: mirrors navigator.onLine, updated by window online/offline events")
commit('2025-05-26T09:15:22-05:00', 'update isOnline comment phrasing')

rf('src/App.tsx',
   "|| msg.includes('ERR_INTERNET');",
   "|| msg.includes('ERR_INTERNET_DISCONNECTED');")
commit('2025-05-26T11:48:39-05:00', 'use full Chrome error code in network error detection')

rf('src/App.tsx',
   "|| msg.includes('ERR_INTERNET_DISCONNECTED');",
   "|| msg.includes('ERR_INTERNET_DISCONNECTED')\n        || msg.includes('net::ERR');")
commit('2025-05-26T16:31:07-05:00', 'add net::ERR prefix to network error pattern matching')

# ── MAY 27 (commit 72)
rf('src/App.tsx',
   "|| msg.includes('net::ERR');",
   "|| msg.startsWith('net::ERR');")
commit('2025-05-27T11:22:48-05:00', 'use startsWith for net::ERR check to avoid false positives')

# ── MAY 28 (commits 73-74)
rf('src/App.tsx',
   "⚠️ No internet connection — new quotes won't load until you're back online",
   "⚠️ Offline — new quotes unavailable until connection is restored")
commit('2025-05-28T09:44:17-05:00', 'shorten offline banner message')

rf('src/App.tsx',
   'className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium shadow-lg"',
   'role="alert" className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium shadow-lg"')
commit('2025-05-28T15:07:54-05:00', 'add role=alert to offline banner for screen reader announcement')

# ══════ JUNE 2025 ══════

# ── JUN 2 (commits 75-76)
af('src/backgrounds.css', '''
/* Additional backgrounds */
:root {
  --forest-url: url('https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=2070&q=80');
  --sunset-url: url('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=2070&q=80');
}

.bg-forest {
  background-image: var(--forest-url);
  filter: saturate(115%) brightness(82%);
}

.bg-sunset {
  background-image: var(--sunset-url);
  filter: saturate(125%) brightness(88%) hue-rotate(5deg);
}
''')
commit('2025-06-02T09:28:41-05:00', 'add forest and sunset background options')

rf('src/backgrounds.css',
   'filter: saturate(110%) brightness(105%);',
   'filter: saturate(108%) brightness(106%);')
commit('2025-06-02T14:11:25-05:00', 'fine-tune ocean background filter values')

# ── JUN 3 (commits 77-79)
wf('src/App.tsx', APP_V5)
commit('2025-06-03T09:05:33-05:00', 'add background selector, star rating, stats panel, useCallback/useMemo')

rf('src/App.tsx',
   "// Human-readable labels for background options",
   "// BG_LABELS: display text for each background option in settings")
commit('2025-06-03T11:43:17-05:00', 'improve BG_LABELS constant comment')

rf('src/App.tsx',
   "// hoveredStar: 0 = no hover",
   "// hoveredStar: 1-5 during hover, 0 when not hovering any star")
commit('2025-06-03T16:22:48-05:00', 'document hoveredStar range in comment')

# ── JUN 4 (commit 80)
af('src/backgrounds.css', '''
/* iOS Safari: background-attachment:fixed not supported */
@supports (-webkit-touch-callout: none) {
  .bg-layer {
    background-attachment: scroll;
  }
}
''')
commit('2025-06-04T10:55:09-05:00', 'fix background-attachment on iOS Safari with @supports')

# ── JUN 5 (commits 81-82)
rf('src/backgrounds.css',
   'filter: saturate(125%) brightness(88%) hue-rotate(5deg);',
   'filter: saturate(128%) brightness(90%) hue-rotate(8deg);')
commit('2025-06-05T09:38:22-05:00', 'increase sunset warmth with stronger hue-rotate')

rf('src/backgrounds.css',
   'filter: saturate(115%) brightness(82%);',
   'filter: saturate(118%) brightness(80%) hue-rotate(-5deg);')
commit('2025-06-05T14:44:51-05:00', 'add slight hue-rotate to forest for cooler green tone')

# ── JUN 9 (commits 83-84)
rf('src/App.tsx',
   "// ratings: keyed by quote text to persist per-quote rating",
   "// ratings: Record<quoteText, stars> — keyed by quote.q for per-quote persistence")
commit('2025-06-09T09:17:44-05:00', 'improve ratings state key strategy comment')

rf('src/App.tsx',
   "aria-label={`Rate this quote ${star} star${star !== 1 ? 's' : ''} out of 5`}",
   "aria-label={`${star} star${star !== 1 ? 's' : ''} — rate this quote`}")
commit('2025-06-09T14:52:11-05:00', 'simplify star rating aria-label format')

# ── JUN 10 (commits 85-86)
rf('src/App.tsx',
   "// Persist ratings map to localStorage on every change",
   "// Save all ratings whenever any individual rating changes")
commit('2025-06-10T09:04:28-05:00', 'improve ratings persistence comment phrasing')

rf('src/App.tsx',
   "// currentRating: 0 = unrated | 1-5 = selected star (shown via filled/empty ★)",
   "// currentRating: 0 (unrated) or 1-5 (stars), drives filled vs empty ★ display")
commit('2025-06-10T15:28:36-05:00', 'refine currentRating documentation comment')

# ── JUN 11 (commit 87)
rf('src/App.tsx',
   "onBlur={() => setHoveredStar(0)}",
   "onFocus={() => setHoveredStar(star)}\n                      onBlur={() => setHoveredStar(0)}")
commit('2025-06-11T10:41:53-05:00', 'add onFocus handler to star buttons for keyboard users')

# ── JUN 12 (commits 88-89)
af('src/App.css', '''
/* Star rating buttons */
.star-btn {
  background: none;
  border: none;
  padding: 0.1rem 0.15rem;
  cursor: pointer;
  line-height: 1;
  transition: transform 0.1s ease-out, color 0.12s ease-out;
}
.star-btn:hover,
.star-btn:focus {
  transform: scale(1.25);
}
.star-btn:focus-visible {
  outline: 2px solid rgba(251, 191, 36, 0.8);
  outline-offset: 2px;
  border-radius: 3px;
}
''')
commit('2025-06-12T09:29:14-05:00', 'add star-btn styles with focus and hover scale')

rf('src/App.tsx',
   "className={`text-2xl star-btn ${star <= (hoveredStar || currentRating) ? 'text-yellow-400' : isDarkMode ? 'text-white/20' : 'text-black/20'}`}>★</button>",
   "className={`text-2xl star-btn ${star <= (hoveredStar || currentRating) ? 'text-yellow-400 drop-shadow-sm' : isDarkMode ? 'text-white/20' : 'text-black/20'}`}>★</button>")
commit('2025-06-12T15:07:42-05:00', 'add drop-shadow to filled stars for depth')

# ── JUN 16 (commits 90-91)
rf('src/App.tsx',
   "// showStats toggled by clicking favorites badge",
   "// showStats: panel showing viewed count, favorites, and ratings summary")
commit('2025-06-16T09:18:55-05:00', 'improve showStats state documentation')

rf('src/App.tsx',
   "<h3 className={`font-semibold mb-4 text-lg ${isDarkMode ? 'text-white' : 'text-black'}`}>📊 Your Stats</h3>",
   "<h3 className={`font-bold mb-4 text-lg ${isDarkMode ? 'text-white' : 'text-black'}`}>📊 Your Stats</h3>")
commit('2025-06-16T14:43:29-05:00', 'use font-bold for stats panel heading')

# ── JUN 17 (commit 92)
rf('src/App.tsx',
   "favorites.slice(-5).reverse().map((fav, i) => (",
   "favorites.slice(-4).reverse().map((fav, i) => (")
commit('2025-06-17T11:26:37-05:00', 'show 4 recent favorites in stats for better vertical balance')

# ── JUN 23 (commits 93-94)
rf('src/App.tsx',
   "const toggleDarkMode = useCallback(() => setIsDarkMode(prev => !prev), []); // stable reference - no deps",
   "const toggleDarkMode = useCallback(() => setIsDarkMode(prev => !prev), []);")
commit('2025-06-23T09:37:22-05:00', 'remove inline comment from toggleDarkMode callback')

rf('src/App.tsx',
   "// Save all ratings whenever any individual rating changes",
   "// Persist ratings on every write — object reference changes trigger effect")
commit('2025-06-23T15:14:08-05:00', 'clarify why ratings effect re-runs on every change')

# ── JUN 24 (commit 95)
rf('src/App.tsx',
   "// currentRating: 0 (unrated) or 1-5 (stars), drives filled vs empty ★ display",
   "// currentRating: derived from ratings map for current quote, 0 if not yet rated")
commit('2025-06-24T10:52:41-05:00', 'rewrite currentRating comment to emphasize derivation')

# ── JUN 25 (commits 96-97)
rf('src/App.tsx',
   "return () => {\n      window.removeEventListener('online', onOnline);\n      window.removeEventListener('offline', onOffline);\n    };",
   "return () => {\n      window.removeEventListener('online', onOnline);\n      window.removeEventListener('offline', onOffline);\n      // cleanup prevents memory leak on unmount\n    };")
commit('2025-06-25T09:23:16-05:00', 'add cleanup comment to online/offline event effect')

rf('src/App.tsx',
   "return () => { window.removeEventListener('keydown', onKey); };",
   "return () => {\n      window.removeEventListener('keydown', onKey);\n    };")
commit('2025-06-25T14:48:33-05:00', 'expand keydown cleanup to multi-line for readability')

# ── JUN 26 (commits 98-100)
af('src/App.css', '''
/* Subtle button lift on hover for tactile feel */
button:not(:disabled):not(.font-size-btn):hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
button:not(:disabled):active {
  transform: translateY(0);
  box-shadow: none;
}
''')
commit('2025-06-26T09:11:44-05:00', 'add button hover lift for tactile interaction feel')

wf('README.md', '''# Quotescape — Quote of the Day

A React + TypeScript web app that displays random inspirational quotes with a polished, feature-rich UI.

## Features
- 🎲 Random quotes from ZenQuotes API with cache-busting & duplicate avoidance
- ❤️ Favorites system — save quotes to localStorage
- 🔤 Adjustable font size (S / M / L)
- ⭐ Star rating per quote (1–5, persisted per quote)
- 🐦 Tweet button for one-click Twitter sharing
- 📋 Copy to clipboard with visual confirmation
- 🌊 Multiple backgrounds: Ocean, City, Forest, Sunset
- 🌙 Light / Dark themes with smooth crossfade transition
- 📊 Stats panel — quotes explored, favorites saved, quotes rated
- ⚙️ Settings panel with author filter and keyboard shortcuts
- 📵 Offline detection with accessible banner notification
- ♿ Accessible: aria-labels, focus-visible, skip-to-content link

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
- The CRA dev proxy (`"proxy"` in package.json) forwards `/api/random` to ZenQuotes during development.
- For production deploys, set up a server-side proxy or use a ZenQuotes plan with CORS headers.

## Rate limit
ZenQuotes free tier: ~5 requests per 30 s per IP. The app adds cache-busting params and retries up to 3× to avoid duplicate quotes.

## Commands
| Command | Description |
|---------|-------------|
| `npm start` | Dev server with hot reload |
| `npm run build` | Production build |
| `npm test` | Run tests |
| `npm run lint` | Lint TypeScript/TSX |
| `npm run lint:fix` | Auto-fix lint errors |
''')
commit('2025-06-26T12:38:09-05:00', 'update README with all features added since April')

rf('src/App.tsx',
   "// Persist ratings on every write — object reference changes trigger effect",
   "// Persist ratings — new object reference on each setRatings triggers this effect")
commit('2025-06-26T16:55:22-05:00', 'refine ratings effect comment to explain trigger mechanism')

print(f'\nDone! Total commits: {n}')
