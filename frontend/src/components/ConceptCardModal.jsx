import React, { useState } from 'react';
import { X, Check, GitFork, Tag, Clock, Layers } from 'lucide-react';

export default function ConceptCardModal({ 
  concept, 
  allConcepts = [], 
  onSave, 
  onClose,
  isNew = false 
}) {
  const [title, setTitle] = useState(concept?.title || '');
  const [summary, setSummary] = useState(concept?.summary || '');
  const [keyTermsInput, setKeyTermsInput] = useState(
    concept?.keyTerms ? concept.keyTerms.join(', ') : ''
  );
  const [prereqInput, setPrereqInput] = useState(
    concept?.prerequisites ? concept.prerequisites.join(', ') : ''
  );
  const [difficulty, setDifficulty] = useState(concept?.difficulty || 'Intermediate');
  const [estTime, setEstTime] = useState(concept?.estTimeMinutes || 3);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert('Concept title is required.');
      return;
    }

    const keyTerms = keyTermsInput
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0);

    const prerequisites = prereqInput
      .split(',')
      .map(p => p.trim())
      .filter(p => p.length > 0);

    const updated = {
      ...(concept || {}),
      id: concept?.id || `concept-${Date.now()}`,
      title: title.trim(),
      summary: summary.trim(),
      keyTerms,
      prerequisites,
      difficulty,
      estTimeMinutes: Number(estTime) || 3,
      status: concept?.status || 'unstudied'
    };

    onSave(updated);
  };

  return (
    <div className="modal-backdrop animate-fade-in" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title">
            <Layers size={18} className="text-purple" />
            <h3>{isNew ? 'Add Concept Node' : 'Edit Concept Details'}</h3>
          </div>
          <button className="btn-modal-close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label className="form-label">Concept Title</label>
            <input 
              className="input-text-dark"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Translation Lookaside Buffer (TLB)"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Core Definition / Summary</label>
            <textarea 
              className="input-text-dark"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="Explain the foundational principle and mechanism..."
              rows={3}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Key Terms (Comma-separated)</label>
            <input 
              className="input-text-dark"
              value={keyTermsInput}
              onChange={(e) => setKeyTermsInput(e.target.value)}
              placeholder="e.g. MMU, cache, page table walk, TLB hit"
            />
            <span className="form-hint">These terms are evaluated during active recall scoring.</span>
          </div>

          <div className="form-group">
            <label className="form-label">Prerequisites (Comma-separated)</label>
            <input 
              className="input-text-dark"
              value={prereqInput}
              onChange={(e) => setPrereqInput(e.target.value)}
              placeholder="e.g. Paging and Page Tables"
            />
            <span className="form-hint">EduMentor places prerequisite concepts earlier in the study path.</span>
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label className="form-label">Difficulty Level</label>
              <select 
                className="input-select-dark"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Est. Recall Time (min)</label>
              <input 
                type="number" 
                min={1} 
                max={30}
                className="input-text-dark"
                value={estTime}
                onChange={(e) => setEstTime(e.target.value)}
              />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary-glow">
              <Check size={16} />
              <span>{isNew ? 'Create Concept' : 'Save Changes'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
