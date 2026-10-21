import React from 'react';
import { 
  FileText, 
  GitFork, 
  MessageSquare, 
  RotateCw, 
  CheckCircle2, 
  Sparkles,
  ChevronRight,
  TrendingUp
} from 'lucide-react';

export default function Header({ 
  activeDeck, 
  activeView, 
  onNavigateView, 
  reviewDueCount = 0 
}) {
  const concepts = activeDeck ? (activeDeck.concepts || []) : [];
  const totalConcepts = concepts.length;
  const masteredCount = concepts.filter(c => c.status === 'mastered').length;
  const progressPercent = totalConcepts > 0 ? Math.round((masteredCount / totalConcepts) * 100) : 0;

  return (
    <header className="app-header">
      <div className="header-breadcrumbs">
        <span className="crumb-brand">EduMentor</span>
        <ChevronRight size={14} className="crumb-separator" />
        <span className="crumb-deck">
          {activeDeck ? activeDeck.title : 'New Study Session'}
        </span>
      </div>

      {/* Center View Switcher */}
      <nav className="header-view-nav">
        <button 
          className={`view-tab-btn ${activeView === 'ingestion' ? 'active' : ''}`}
          onClick={() => onNavigateView('ingestion')}
          id="tab-notes-ingestion"
        >
          <FileText size={15} />
          <span>Notes & Ingestion</span>
        </button>

        <button 
          className={`view-tab-btn ${activeView === 'roadmap' ? 'active' : ''}`}
          onClick={() => onNavigateView('roadmap')}
          id="tab-study-path-roadmap"
        >
          <GitFork size={15} />
          <span>Prerequisite Roadmap</span>
          {totalConcepts > 0 && <span className="tab-badge">{totalConcepts}</span>}
        </button>
      </nav>

      {/* Right Stats & Status */}
      <div className="header-stats">
        {totalConcepts > 0 && (
          <div className="mastery-mini-pill" title={`${masteredCount} of ${totalConcepts} concepts mastered`}>
            <div className="progress-ring-label">
              <TrendingUp size={14} className="text-purple" />
              <span>{progressPercent}% Mastered</span>
            </div>
            <div className="mini-progress-track">
              <div 
                className="mini-progress-fill"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
