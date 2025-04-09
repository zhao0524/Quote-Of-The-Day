import React, { useState, useEffect, useCallback } from 'react';
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
  // favorites persisted to localStorage via useEffect

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
      // quoteKey increments to trigger re-animation; quotesViewed counts total fetches
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
  // prevents duplicate favorites via .some() check

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
          {/* tagline: discover something new every visit */}
          </h1>
          <div className="flex items-center gap-3">
            {favorites.length > 0 && (
              <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                isDarkMode ? 'bg-white/10 text-white/80' : 'bg-black/10 text-black/80'
              }`}>
                ❤️ {favorites.length} saved
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
