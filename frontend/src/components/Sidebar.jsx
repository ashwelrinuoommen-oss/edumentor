import React from 'react';
import { 
  BookOpen, 
  Plus, 
  Sparkles, 
  Clock, 
  Trash2, 
  Cpu, 
  Brain, 
  Activity, 
  Layers, 
  ChevronRight,
  Database,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function Sidebar({ 
  decks = [], 
  activeDeckId, 
  onSelectDeck, 
  onNewDeck, 
  onDeleteDeck,
  reviewDueCount = 0,
  activeView,
  onNavigateView
}) {
  const getDeckIcon = (iconName) => {
    switch (iconName) {
      case 'Cpu': return <Cpu size={16} className="deck-icon text-cyan" />;
      case 'Brain': return <Brain size={16} className="deck-icon text-purple" />;
      case 'Activity': return <Activity size={16} className="deck-icon text-emerald" />;
      default: return <BookOpen size={16} className="deck-icon text-purple" />;
    }
  };

  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-logo-wrap">
          <div className="brand-icon-pulse">
            <Sparkles size={18} className="brand-icon" />
          </div>
          <div>
            <h1 className="brand-title">EduMentor</h1>
            <p className="brand-tagline">Study. Recall. Master.</p>
          </div>
        </div>
      </div>

      {/* New Deck Action */}
      <div className="sidebar-actions">
        <button 
          className="btn-new-deck"
          onClick={onNewDeck}
          id="btn-new-study-deck"
        >
          <Plus size={18} />
          <span>New Study Deck</span>
        </button>
      </div>

      {/* Navigation Sections */}
      <div className="sidebar-scrollable">
        {/* Spaced Repetition Due Queue Indicator */}
        <div className="sidebar-section">
          <div className="section-label">RETENTION & SPACED REPETITION</div>
          <button 
            className={`nav-pill-item ${activeView === 'review' ? 'active' : ''}`}
            onClick={() => onNavigateView('review')}
            id="nav-review-queue"
          >
            <div className="nav-item-left">
              <Clock size={16} className={reviewDueCount > 0 ? "text-amber" : "text-muted"} />
              <span>Review Due Queue</span>
            </div>
            {reviewDueCount > 0 ? (
              <span className="badge-due-count">{reviewDueCount}</span>
            ) : (
              <span className="badge-clear">0</span>
            )}
          </button>
        </div>

        {/* Saved Study Decks */}
        <div className="sidebar-section">
          <div className="section-label">
            <span>STUDY DECKS ({decks.length})</span>
          </div>

          <div className="deck-list">
            {decks.length === 0 ? (
              <div className="empty-deck-notice">
                <BookOpen size={24} className="text-muted" />
                <p>No study decks yet. Paste notes or select a sample deck to begin.</p>
              </div>
            ) : (
              decks.map(deck => {
                const isActive = deck.id === activeDeckId;
                const conceptCount = deck.concepts ? deck.concepts.length : 0;
                const masteredCount = deck.concepts ? deck.concepts.filter(c => c.status === 'mastered').length : 0;

                return (
                  <div 
                    key={deck.id}
                    className={`deck-item ${isActive ? 'active' : ''}`}
                    onClick={() => onSelectDeck(deck.id)}
                    id={`deck-item-${deck.id}`}
                  >
                    <div className="deck-item-icon">
                      {getDeckIcon(deck.icon)}
                    </div>
                    <div className="deck-item-content">
                      <span className="deck-title" title={deck.title}>
                        {deck.title}
                      </span>
                      <div className="deck-meta">
                        <span className="deck-category">{deck.category || 'General'}</span>
                        <span className="meta-dot">•</span>
                        <span className="deck-count">{conceptCount} concepts</span>
                      </div>
                    </div>

                    <button 
                      className="btn-deck-delete"
                      title="Delete deck"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm(`Delete "${deck.title}"?`)) {
                          onDeleteDeck(deck.id);
                        }
                      }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="sidebar-footer">
        <div className="storage-status">
          <Database size={13} className="text-emerald" />
          <span>Local Storage Synced</span>
        </div>
      </div>
    </aside>
  );
}
