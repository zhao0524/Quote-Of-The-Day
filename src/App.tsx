import React, { useState, useEffect, useCallback } from 'react';
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
  // fontSize: sm|md|lg controls quote text size via FONT_CLASSES map
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
      setQuotesViewed(v => v + 1); // increment on each successful fetch
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'An error occurred';
      setError(msg);
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
    // tweet: encodeURIComponent handles special chars and emoji in quotes
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
  // quoteLength: '' (empty) | 'Short' (<80) | 'Medium' (<180) | 'Long' (≥180 chars)
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
                  <span className={`text-xs char-count tabular-nums ${isDarkMode ? 'text-white/40' : 'text-black/40'}`}>{charCount} chars</span>
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
