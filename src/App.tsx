import React, { useState, useEffect } from 'react';
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

  const fetchQuote = async () => {
    try {
      setError(null);

      // ZenQuotes 
      const response = await fetch(
        'https://api.allorigins.win/raw?url=https://zenquotes.io/api/random'
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();

      // make sure this is an array of quote and author
      const quoteData = Array.isArray(data) ? data[0] : data;
      if (!quoteData || !quoteData.q || !quoteData.a) {
        throw new Error('Unexpected response from ZenQuotes');
      }

      setQuote({ q: quoteData.q, a: quoteData.a });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchQuote();
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    fetchQuote();
  };

  const handleShare = () => {
    if (quote) {
      const text = `"${quote.q}" - ${quote.a}`;
      if (navigator.share) {
        navigator.share({
          title: 'Quote of the Day',
          text: text,
        });
      } else {
        navigator.clipboard.writeText(text);
        alert('Quote copied to clipboard!');
      }
    }
  };
// copy the quote
  const handleCopy = async () => {
    if (!quote) return;
    const text = `"${quote.q}" - ${quote.a}`;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch (err) {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      textarea.remove();
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className={`min-h-screen bg-transition ${
      isDarkMode ? 'dark-mode-bg' : 'light-mode-bg'
    }`}>
      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className={`text-2xl md:text-3xl font-bold ${
            isDarkMode ? 'text-white' : 'text-black'
          }`}>
            Quotescape
          </h1>
          <button
            onClick={toggleDarkMode}
            className={`p-3 rounded-full transition-all duration-200 ${
              isDarkMode 
                ? 'bg-white/20 hover:bg-white/30 text-white' 
                : 'bg-black/20 hover:bg-black/30 text-black'
            }`}
          >
            <span className="text-xl">{isDarkMode ? '☀️' : '🌙'}</span>
          </button>
        </div>

        {/* Main Content */}
        <div className="text-center mb-8">
          <h2 className={`text-4xl md:text-6xl font-bold mb-4 ${
            isDarkMode ? 'neon-title' : 'text-black'
          }`}>
            Quote of the Day
          </h2>
          <p className={`text-lg ${
            isDarkMode ? 'text-white/80' : 'text-black/80'
          }`}>
            A delightful daily dose of wisdom — tuned for neon nights and ocean light.
          </p>
        </div>

        {/* Main Quote Card */}
        <div className="max-w-4xl mx-auto">
          <div className={`rounded-2xl p-8 md:p-12 ${
            isDarkMode ? 'glass-card-dark' : 'glass-card'
          }`}>
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                <p className={`text-lg ${
                  isDarkMode ? 'text-white/80' : 'text-black/80'
                }`}>
                  Loading your daily inspiration...
                </p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-red-400 text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold mb-2 text-red-400">Oops! Something went wrong</h3>
                <p className={`mb-4 ${
                  isDarkMode ? 'text-white/80' : 'text-black/80'
                }`}>
                  {error}
                </p>
                <button
                  onClick={handleRefresh}
                  className="bg-red-500/80 hover:bg-red-600/80 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200"
                >
                  Try Again
                </button>
              </div>
            ) : quote ? (
              <div className="text-center">
                {/* Quote Text */}
                <div className="mb-8">
                  <blockquote className={`text-2xl md:text-3xl lg:text-4xl font-light italic leading-relaxed ${
                    isDarkMode ? 'text-white' : 'text-black'
                  }`}>
                    "{quote.q}"
                  </blockquote>
                </div>

                {/* Author */}
                <div className="mb-8">
                  <cite className={`text-lg md:text-xl font-medium not-italic ${
                    isDarkMode ? 'text-white/90' : 'text-black/90'
                  }`}>
                    — {quote.a}
                  </cite>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                  <button
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                      isRefreshing
                        ? 'bg-gray-400/50 cursor-not-allowed text-white'
                        : isDarkMode
                        ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg'
                        : 'bg-gradient-to-r from-blue-400 to-teal-400 hover:from-blue-500 hover:to-teal-500 text-white shadow-lg'
                    }`}
                  >
                    {isRefreshing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Refreshing...
                      </>
                    ) : (
                      <>
                        <span>🔄</span>
                        New quote
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleCopy}
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode
                        ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/80 hover:bg-white/90 text-black border border-black/10'
                    }`}
                  >
                    <span>📋</span>
                    {copied ? 'Copied!' : 'Copy'}
                  </button>

                  <button
                    onClick={handleShare}
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode
                        ? 'bg-white/20 hover:bg-white/30 text-white border border-white/20'
                        : 'bg-white/80 hover:bg-white/90 text-black border border-black/10'
                    }`}
                  >
                    <span>📤</span>
                    Share
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12">
          <p className={`text-sm ${
            isDarkMode ? 'text-gray-400' : 'text-gray-500'
          }`}>
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
