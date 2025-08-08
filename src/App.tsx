import React, { useState, useEffect } from 'react';
import './App.css';

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

  const fetchQuote = async () => {
    try {
      setError(null);
      
      // Try multiple quote APIs with fallback
      const apis = [
        'https://api.quotable.io/random',
        'https://api.allorigins.win/raw?url=https://zenquotes.io/api/random',
        'https://quotes.rest/qod'
      ];
      
      let quoteData = null;
      let lastError = null;
      
      for (const api of apis) {
        try {
          const response = await fetch(api);
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }
          
          const data = await response.json();
          
          // Handle different API response formats
          if (api.includes('quotable.io')) {
            quoteData = { q: data.content, a: data.author };
          } else if (api.includes('zenquotes.io')) {
            quoteData = data[0];
          } else if (api.includes('quotes.rest')) {
            quoteData = { q: data.contents.quotes[0].quote, a: data.contents.quotes[0].author };
          }
          
          if (quoteData) break;
        } catch (err) {
          lastError = err;
          continue;
        }
      }
      
      if (quoteData) {
        setQuote(quoteData);
      } else {
        throw lastError || new Error('All quote APIs failed');
      }
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

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      isDarkMode 
        ? 'bg-gray-900 text-white' 
        : 'bg-gradient-to-br from-blue-50 to-indigo-100 text-gray-800'
    }`}>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className={`text-4xl md:text-6xl font-bold mb-4 ${
            isDarkMode ? 'text-white' : 'text-gray-800'
          }`}>
            Quote of the Day
          </h1>
          <p className={`text-lg ${
            isDarkMode ? 'text-gray-300' : 'text-gray-600'
          }`}>
            Daily inspiration at your fingertips
          </p>
        </div>

        {/* Main Quote Card */}
        <div className="max-w-4xl mx-auto">
          <div className={`rounded-2xl shadow-2xl p-8 md:p-12 ${
            isDarkMode 
              ? 'bg-gray-800 border border-gray-700' 
              : 'bg-white border border-gray-200'
          }`}>
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className={`text-lg ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-600'
                }`}>
                  Loading your daily inspiration...
                </p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-red-500 text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold mb-2 text-red-500">Oops! Something went wrong</h3>
                <p className={`mb-4 ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-600'
                }`}>
                  {error}
                </p>
                <button
                  onClick={handleRefresh}
                  className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200"
                >
                  Try Again
                </button>
              </div>
            ) : quote ? (
              <div className="text-center">
                {/* Quote Text */}
                <div className="mb-8">
                  <blockquote className="text-2xl md:text-3xl lg:text-4xl font-light italic leading-relaxed">
                    "{quote.q}"
                  </blockquote>
                </div>

                {/* Author */}
                <div className="mb-8">
                  <cite className={`text-lg md:text-xl font-medium not-italic ${
                    isDarkMode ? 'text-blue-400' : 'text-blue-600'
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
                        ? 'bg-gray-400 cursor-not-allowed'
                        : isDarkMode
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-blue-500 hover:bg-blue-600 text-white'
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
                        New Quote
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleShare}
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                      isDarkMode
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-green-500 hover:bg-green-600 text-white'
                    }`}
                  >
                    <span>📤</span>
                    Share Quote
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>

        {/* Dark Mode Toggle */}
        <div className="text-center mt-8">
          <button
            onClick={toggleDarkMode}
            className={`flex items-center gap-2 mx-auto px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
              isDarkMode
                ? 'bg-gray-700 hover:bg-gray-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
            }`}
          >
            <span>{isDarkMode ? '☀️' : '🌙'}</span>
            {isDarkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>

        {/* Footer */}
        <div className="text-center mt-12">
          <p className={`text-sm ${
            isDarkMode ? 'text-gray-400' : 'text-gray-500'
          }`}>
            Powered by Multiple Quote APIs • Built with React, TypeScript & Tailwind CSS
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
