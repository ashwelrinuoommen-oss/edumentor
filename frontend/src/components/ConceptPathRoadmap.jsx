import React, { useState } from 'react';
import { 
  GitFork, 
  Clock, 
  ArrowRight, 
  Plus, 
  Edit3, 
  Trash2, 
  Tag, 
  Layers, 
  CheckCircle, 
  AlertCircle, 
  Sparkles,
  HelpCircle,
  Play
} from 'lucide-react';

export default function ConceptPathRoadmap({ 
  deck, 
  onEditConcept, 
  onDeleteConcept, 
  onAddConcept,
  onStartRecallSession
}) {
  const concepts = deck?.concepts || [];
  const totalMinutes = concepts.reduce((acc, c) => acc + (c.estTimeMinutes || 3), 0);

  const getDifficultyBadge = (difficulty) => {
    switch (difficulty) {
      case 'Beginner':
        return <span className="diff-badge diff-beginner">Beginner</span>;
      case 'Intermediate':
        return <span className="diff-badge diff-intermediate">Intermediate</span>;
      case 'Advanced':
        return <span className="diff-badge diff-advanced">Advanced</span>;
      default:
        return <span className="diff-badge diff-beginner">Fundamental</span>;
    }
  };

  return (
    <div className="roadmap-container animate-fade-in">
      {/* Top Pathway Header */}
      <div className="roadmap-header-card">
        <div className="roadmap-header-main">
          <div className="roadmap-meta-badge">
            <GitFork size={14} className="text-purple" />
            <span>Topological Prerequisite Order</span>
          </div>
          <h2 className="roadmap-title">{deck?.title || 'Study Path'}</h2>
          <p className="roadmap-desc">
            Concepts have been ordered so that foundational principles are recalled first. 
            Mastering these early concepts unlocks dependent topics downstream.
          </p>
        </div>

        <div className="roadmap-summary-stats">
          <div className="summary-stat-box">
            <span className="summary-stat-val">{concepts.length}</span>
            <span className="summary-stat-label">Ordered Concepts</span>
          </div>
          <div className="summary-stat-box">
            <span className="summary-stat-val">~{totalMinutes} min</span>
            <span className="summary-stat-label">Estimated Recall Time</span>
          </div>
          <div className="summary-action-box">
            <button 
              className="btn-start-session"
              onClick={onStartRecallSession}
              id="btn-start-recall-session"
            >
              <Play size={16} fill="currentColor" />
              <span>Begin Socratic Recall</span>
            </button>
          </div>
        </div>
      </div>

      {/* Path Toolbar */}
      <div className="path-toolbar">
        <div className="path-toolbar-left">
          <span className="path-order-hint">
            <strong>Study Sequence:</strong> Concepts 1 through {concepts.length} in prerequisite dependency order.
          </span>
        </div>
        <div className="path-toolbar-right">
          <button 
            className="btn-add-concept"
            onClick={onAddConcept}
            id="btn-add-custom-concept"
          >
            <Plus size={15} />
            <span>Add Concept Node</span>
          </button>
        </div>
      </div>

      {/* Visual Roadmap Sequence */}
      <div className="roadmap-timeline">
        {concepts.length === 0 ? (
          <div className="empty-path-notice">
            <GitFork size={36} className="text-muted" />
            <h3>No concepts in this study path yet</h3>
            <p>Upload or paste notes in the Notes & Ingestion tab to generate an ordered path.</p>
          </div>
        ) : (
          concepts.map((concept, index) => {
            const hasPrereqs = concept.prerequisites && concept.prerequisites.length > 0;
            const hasKeyTerms = concept.keyTerms && concept.keyTerms.length > 0;

            return (
              <div 
                key={concept.id}
                className="path-node-card"
                id={`concept-node-${concept.id}`}
              >
                {/* Node Line & Step Indicator */}
                <div className="node-indicator-col">
                  <div className="node-number-circle">
                    {concept.orderIndex || index + 1}
                  </div>
                  {index < concepts.length - 1 && <div className="node-connector-line" />}
                </div>

                {/* Node Content Card */}
                <div className="node-card-body">
                  <div className="node-top-bar">
                    <div className="node-title-group">
                      <h3 className="node-title">{concept.title}</h3>
                      {getDifficultyBadge(concept.difficulty)}
                      <span className="node-est-time">
                        <Clock size={12} />
                        <span>~{concept.estTimeMinutes || 3} min</span>
                      </span>
                    </div>

                    <div className="node-actions-group">
                      <button 
                        className="btn-icon-action"
                        title="Edit Concept Details"
                        onClick={() => onEditConcept(concept)}
                      >
                        <Edit3 size={15} />
                      </button>
                      <button 
                        className="btn-icon-action danger"
                        title="Remove Concept"
                        onClick={() => {
                          if (confirm(`Remove concept "${concept.title}"?`)) {
                            onDeleteConcept(concept.id);
                          }
                        }}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>

                  {/* Definition / Core Summary */}
                  <p className="node-summary">
                    {concept.summary}
                  </p>

                  {/* Prerequisites indicator */}
                  <div className="node-prereq-row">
                    <span className="prereq-label">Prerequisites:</span>
                    {hasPrereqs ? (
                      <div className="prereq-pills-list">
                        {concept.prerequisites.map((p, pIdx) => (
                          <span key={pIdx} className="prereq-pill">
                            <GitFork size={11} />
                            <span>{p}</span>
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="prereq-none-pill">
                        Foundational (No prior dependencies)
                      </span>
                    )}
                  </div>

                  {/* Essential Key Terms Preview */}
                  {hasKeyTerms && (
                    <div className="node-terms-row">
                      <span className="terms-label">
                        <Tag size={12} />
                        <span>Key Terms:</span>
                      </span>
                      <div className="terms-pills-list">
                        {concept.keyTerms.map((term, tIdx) => (
                          <span key={tIdx} className="term-pill">
                            {term}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
