// App.tsx
import React, { useState, useCallback, useRef, useEffect } from 'react';
import './App.css';

// Types
interface ReelData {
  reel: string;
  transcription: string;
}

// Icons
const Icons = {
  Search: () => (<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>),
  PlayCircle: () => (<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>),
  FileText: () => (<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>),
  AlertCircle: () => (<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>),
  ExternalLink: () => (<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>),
  Loader2: () => (<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="spin"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/></svg>),
  Calendar: () => (<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>),
  ArrowLeft: () => (<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>),
  Copy: () => (<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>),
  Check: () => (<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>),
};

// Reel Card Component for Homepage
const ReelCard: React.FC<{ reel: ReelData; index: number; onClick: () => void }> = ({ reel, index, onClick }) => {
  // Extract shortcode for thumbnail (optional)
  const shortcode = reel.reel.split('/').filter(Boolean).pop();
  const thumbnailUrl = `https://img.youtube.com/vi/${shortcode}/mqdefault.jpg`; // Fallback, Instagram doesn't have direct thumbnails

  return (
    <div className="reel-card" onClick={onClick}>
      <div className="reel-card-preview">
        <div className="thumbnail-placeholder">
          <Icons.PlayCircle />
        </div>
        <div className="play-overlay">
          <Icons.PlayCircle />
        </div>
      </div>
      <div className="reel-card-content">
        <div className="reel-card-header">
          <span className="reel-number">Reel #{index + 1}</span>
          <a 
            href={reel.reel} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="external-link-icon"
            onClick={(e) => e.stopPropagation()}
          >
            <Icons.ExternalLink />
          </a>
        </div>
        <p className="reel-transcription-preview">
          {reel.transcription.substring(0, 120)}...
        </p>
        <div className="reel-card-footer">
          <span className="read-more">Click to view full transcription →</span>
        </div>
      </div>
    </div>
  );
};

// Detail View Component
const DetailView: React.FC<{ reel: ReelData; onBack: () => void }> = ({ reel, onBack }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(reel.transcription);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="detail-view">
      <button className="back-button" onClick={onBack}>
        <Icons.ArrowLeft />
        Back to all reels
      </button>

      <div className="detail-container">
        {/* Left side - Iframe */}
        <div className="detail-left">
          <div className="iframe-wrapper">
            <iframe
              src={`${reel.reel}/embed`}
              className="detail-iframe"
              allowFullScreen
              title="Instagram Reel"
              sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
            />
          </div>
          <div className="reel-link">
            <a href={reel.reel} target="_blank" rel="noopener noreferrer">
              Open in Instagram <Icons.ExternalLink />
            </a>
          </div>
        </div>

        {/* Right side - Transcription */}
        <div className="detail-right">
          <div className="transcription-header-detail">
            <div className="transcription-title">
              <Icons.FileText />
              <h2>Full Transcription</h2>
            </div>
            <button className="copy-button" onClick={handleCopy}>
              {copied ? <Icons.Check /> : <Icons.Copy />}
              {copied ? 'Copied!' : 'Copy text'}
            </button>
          </div>
          <div className="transcription-content-detail">
            <p>{reel.transcription}</p>
          </div>
          <div className="transcription-meta">
            <span>Source: Instagram Reel</span>
            <span>Character count: {reel.transcription.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App: React.FC = () => {
  const [username, setUsername] = useState('');
  const [days, setDays] = useState(1);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [reels, setReels] = useState<ReelData[]>([]);
  const [selectedReel, setSelectedReel] = useState<ReelData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  
  const abortControllerRef = useRef<AbortController | null>(null);

  const runPipeline = async () => {
    if (!username.trim()) {
      alert('Please enter a username');
      return;
    }

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    
    setLoading(true);
    setStreaming(true);
    setReels([]);
    setError(null);
    setSelectedReel(null);
    setProgress({ current: 0, total: 0 });

    const params = new URLSearchParams({
      username: username.trim(),
      days: days.toString(),
    });

    try {
      const response = await fetch(`https://reeltranscript-backend-8z7v.onrender.com/response?${params}`, {
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      let buffer = '';
      let reelCount = 0;

      while (reader) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete JSON objects
        let start = buffer.indexOf('{');
        let end = buffer.indexOf('}', start);
        
        while (start !== -1 && end !== -1) {
          const objStr = buffer.substring(start, end + 1);
          
          try {
            const obj = JSON.parse(objStr);
            if (obj.reel && obj.transcription) {
              setReels(prev => [...prev, obj]);
              reelCount++;
              setProgress({ current: reelCount, total: reelCount });
            }
          } catch (e) {
            console.error('JSON parse error:', e);
          }
          
          buffer = buffer.substring(end + 1);
          start = buffer.indexOf('{');
          end = buffer.indexOf('}', start);
        }
      }
      
      if (reelCount === 0) {
        setError('No reels found for this username and timeframe.');
      }
      
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Pipeline error:', err);
        setError('Failed to fetch reels. Make sure the server is running on http://127.0.0.1:8000');
      }
    } finally {
      setLoading(false);
      setStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setLoading(false);
      setStreaming(false);
    }
  };

  const handleReelClick = (reel: ReelData) => {
    setSelectedReel(reel);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleBack = () => {
    setSelectedReel(null);
  };

  // Format transcription preview
  const getPreview = (text: string) => {
    return text.length > 120 ? text.substring(0, 120) + '...' : text;
  };

  return (
    <div className="app">
      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="logo-wrapper">
            <div className="logo-icon"><Icons.PlayCircle /></div>
          </div>
          <h1 className="title">Reel Pipeline</h1>
          <div className="badge-group">
            <span className="tech-badge">STREAMING</span>
            <span className="tech-badge">REAL-TIME</span>
            <span className="tech-badge">AI TRANSCRIPT</span>
          </div>
          <p className="subtitle">
            Stream Instagram Reels with AI-powered transcription in real-time
          </p>
        </header>

        {/* Input Card */}
        <div className="card input-card">
          <div className="input-grid">
            <div className="input-field">
              <label className="input-label">
                <Icons.Search />
                Instagram Username
              </label>
              <input
                type="text"
                className="input"
                placeholder="e.g., samantharuthprabhuoffl"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div className="input-field">
              <label className="input-label">
                <Icons.Calendar />
                Days to look back
              </label>
              <input
                type="number"
                className="input"
                placeholder="Days"
                value={days}
                onChange={(e) => setDays(parseInt(e.target.value) || 1)}
                min="1"
                max="30"
              />
            </div>
          </div>

          <div className="button-group">
            <button
              className="btn-primary"
              onClick={runPipeline}
              disabled={loading}
            >
              {loading ? (
                <>
                  <Icons.Loader2 />
                  Streaming Reels...
                </>
              ) : (
                <>
                  <Icons.PlayCircle />
                  Start Streaming
                </>
              )}
            </button>
            
            {loading && (
              <button className="btn-secondary" onClick={handleCancel}>
                Cancel
              </button>
            )}
          </div>
        </div>

        {/* Streaming Progress */}
        {streaming && reels.length > 0 && (
          <div className="streaming-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: '100%' }}
              />
            </div>
            <p>Streaming reels... {reels.length} received so far</p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-banner">
            <Icons.AlertCircle />
            <span>{error}</span>
          </div>
        )}

        {/* Content - Either Detail View or Home View */}
        {selectedReel ? (
          <DetailView reel={selectedReel} onBack={handleBack} />
        ) : (
          <>
            {/* Results Summary */}
            {reels.length > 0 && (
              <div className="results-summary">
                <h2>Found {reels.length} Reel{reels.length !== 1 ? 's' : ''}</h2>
                <p>Click on any reel to view full transcription and video</p>
              </div>
            )}

            {/* Reels Grid */}
            {reels.length > 0 && (
              <div className="reels-grid">
                {reels.map((reel, idx) => (
                  <ReelCard
                    key={`${reel.reel}-${idx}`}
                    reel={reel}
                    index={idx}
                    onClick={() => handleReelClick(reel)}
                  />
                ))}
              </div>
            )}

            {/* Empty State */}
            {!loading && !streaming && reels.length === 0 && !error && (
              <div className="welcome-state">
                <div className="welcome-icon">
                  <Icons.PlayCircle />
                </div>
                <h3 className="welcome-title">Ready to stream reels</h3>
                <p className="welcome-text">
                  Enter an Instagram username and click "Start Streaming" to begin
                </p>
              </div>
            )}

            {/* Loading State */}
            {loading && reels.length === 0 && (
              <div className="loading-state">
                <Icons.Loader2 />
                <p>Waiting for reels from server...</p>
                <small>This may take a few moments</small>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default App;