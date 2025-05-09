import React, { useState, useEffect, useCallback, useRef } from 'react';
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
  // Theme persisted; initializer reads localStorage to avoid flash on reload
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() =>
    localStorage.getItem('qotd_theme') === 'dark'
  );
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);
  // favorites: Quote[] persisted to localStorage, loaded via lazy initializer
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
  // showSettings: toggled by gear button in header, and S keyboard shortcut
  const [showSettings, setShowSettings] = useState(false);
  // authorFilter: case-insensitive substring match
  const [authorFilter, setAuthorFilter] = useState('');
  // isOnline: mirrors navigator.onLine, kept in sync via online/offline events
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
      for (let attempt = 0; attempt < 3; attempt += 1) {
        const cb = Date.now() + '-' + attempt;
        const response = await fetch(`/api/random?cb=${cb}`, { cache: 'no-store' });
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
        || msg.toLowerCase().includes('network')
        || msg.startsWith('net::ERR');
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
    setFavorites(prev =>
      prev.some(f => f.q === quote.q) ? prev.filter(f => f.q !== quote.q) : [...prev, quote]
    );
  };

  const isFavorited = quote ? favorites.some(f => f.q === quote.q) : false;

  // Twitter / X share — intent URL works on twitter.com and x.com
  const handleTweet = () => {
    if (!quote) return;
    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(`"${quote.q}" — ${quote.a}`)}`,
      '_blank', 'noopener,noreferrer'
    );
  };

  // handleShare: uses Web Share API where available, falls back to clipboard
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

  const toggleDarkMode = () => setIsDarkMode(prev => !prev);

  const charCount = quote ? quote.q.length : 0;
  // quoteLength: '' | 'Short' | 'Medium' | 'Long' — thresholds 80/180 chars
  const quoteLength = charCount === 0 ? '' : charCount < 80 ? 'Short' : charCount < 180 ? 'Medium' : 'Long';
  const matchesFilter = !authorFilter || (quote && quote.a.toLowerCase().includes(authorFilter.toLowerCase()));

  const btnBase = 'flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200';
  const btnGlass = isDarkMode
    ? `${btnBase} bg-white/20 hover:bg-white/30 text-white border border-white/20`
    : `${btnBase} bg-white/90 hover:bg-white text-black border border-black/20`;

  return (
    <div className={`bg-crossfade bg-transition ${isDarkMode ? 'dark-mode-bg' : 'light-mode-bg'}`}>
      <div className={`bg-layer light ${!isDarkMode ? 'visible' : ''}`}></div>
      <div className={`bg-layer dark ${isDarkMode ? 'visible' : ''}`}></div>

      {!isOnline && (
        <div role="alert" className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium shadow-lg">
          ⚠️ Offline — new quotes unavailable until connection is restored
        </div>
      )}

      <a href="#main-content" tabIndex={0} className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded-lg focus:font-semibold">
        Skip to content
      </a>

      <div className="container mx-auto px-4 py-8 relative z-10" id="main-content">
        <div className="flex justify-between items-center mb-8 flex-wrap gap-3">
          <h1 className={`text-2xl md:text-3xl font-bold tracking-tight ${isDarkMode ? 'text-white' : 'text-black'}`}>
            Quotescape
            {/* tagline: discover something new every visit */}
          </h1>
          <div className="flex items-center gap-2 flex-wrap">
            {favorites.length > 0 && (
              <span className={`text-sm font-medium px-2 py-1 rounded-full ${isDarkMode ? 'bg-white/10 text-white/80' : 'bg-black/10 text-black/80'}`}>
                ❤️ {favorites.length} saved
              </span>
            )}
            <div className="flex items-center gap-1">
              {(['sm','md','lg'] as FontSize[]).map((size, i) => (
                <button key={size} onClick={() => setFontSize(size)}
                  aria-label={`${['Small','Medium','Large'][i]} font`}
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
                      {authorFilter && (
                        <button onClick={() => setAuthorFilter('')}
                          className="text-xs opacity-50 hover:opacity-80 mt-1 transition-opacity">
                          Clear filter ×
                        </button>
                      )}
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
          <h2 className={`text-4xl md:text-6xl font-bold mb-4 ${isDarkMode ? 'neon-title' : 'text-black'}`}>
            Quote of the Day
          </h2>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className={`rounded-2xl p-8 md:p-12 ${isDarkMode ? 'glass-card-dark' : 'glass-card'}`}>
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                <p className={`text-lg ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>
                  Finding your next great quote...
                </p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold mb-2 text-red-400">Unable to load quote</h3>
                <p className={`mb-4 ${isDarkMode ? 'text-white/80' : 'text-black/80'}`}>{error}</p>
                <button onClick={handleRefresh}
                  className="bg-red-500/80 hover:bg-red-600/80 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200">
                  Try Again
                </button>
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
                  <cite className={`text-lg md:text-xl font-medium not-italic ${isDarkMode ? 'text-white/90' : 'text-black/90'}`}>
                    — {quote.a}
                  </cite>
                </div>
                <div className="mb-8 flex items-center justify-center gap-2">
                  {quoteLength && (
                    <span className={`text-xs px-2 py-0.5 rounded-full border quote-badge ${isDarkMode ? 'border-white/20 text-white/50' : 'border-black/20 text-black/50'}`}>
                      {quoteLength}
                    </span>
                  )}
                  <span className={`text-xs char-count tabular-nums ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>
                    {charCount} chars
                  </span>
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center flex-wrap">
                  <button onClick={handleRefresh} disabled={isRefreshing} aria-label="Fetch a new quote"
                    className={`${btnBase} ${isRefreshing ? 'bg-gray-400/50 cursor-not-allowed text-white'
                      : isDarkMode ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg'
                      : 'bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 text-white shadow-lg'}`}>
                    {isRefreshing
                      ? <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>Refreshing...</>
                      : <><span>🔄</span>New quote</>}
                  </button>

                  <button onClick={handleFavorite}
                    aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
                    className={btnGlass}>
                    <span>{isFavorited ? '❤️' : '🤍'}</span>
                    {isFavorited ? 'Saved' : 'Favorite'}
                  </button>

                  <button onClick={handleCopy} aria-label="Copy quote to clipboard" className={btnGlass}>
                    <span>📋</span>{copied ? 'Copied!' : 'Copy'}
                  </button>

                  <button onClick={handleTweet} aria-label="Share on Twitter"
                    className={`${btnBase} ${isDarkMode ? 'bg-sky-500/70 hover:bg-sky-500/90 text-white border border-sky-400/30' : 'bg-sky-600/80 hover:bg-sky-700/80 text-white'}`}>
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
            <a href="https://zenquotes.io" target="_blank" rel="noopener noreferrer"
              className="underline underline-offset-2 hover:opacity-80 transition-opacity">ZenQuotes</a>
          </p>
          <p className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            {quotesViewed > 0 && `${quotesViewed} quotes explored · `}
            Press{" "}<kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">Space</kbd>{" "}for a new quote
            {" "}· <kbd className="px-1 py-0.5 rounded text-xs font-mono border border-current opacity-70">S</kbd> settings
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
