import React, { useState, useRef } from 'react';
import { 
  Sparkles, 
  Upload, 
  FileText, 
  ArrowRight, 
  RefreshCw, 
  Check, 
  Cpu, 
  Brain, 
  Activity, 
  AlertCircle,
  FileCode,
  Zap
} from 'lucide-react';
import { SAMPLE_NOTE_SETS } from '../data/sampleNotes';

export default function NotesIngestion({ 
  initialTitle = '', 
  initialContent = '', 
  onGeneratePath, 
  isAnalyzing = false 
}) {
  const [deckTitle, setDeckTitle] = useState(initialTitle || 'My Study Notes');
  const [content, setContent] = useState(initialContent || '');
  const [selectedCategory, setSelectedCategory] = useState('General');
  const [dragActive, setDragActive] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState(null);
  const fileInputRef = useRef(null);

  // Sync state if initialTitle changes
  React.useEffect(() => {
    if (initialTitle) setDeckTitle(initialTitle);
    if (initialContent) setContent(initialContent);
  }, [initialTitle, initialContent]);

  // Compute live stats
  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
  const charCount = content.length;
  // Estimated concepts: roughly count markdown headers and numbered lists
  const estimatedConceptCount = Math.max(
    1,
    (content.match(/^(?:#{1,3}\s+|\d+[\.\)]\s+)/gm) || []).length || Math.ceil(wordCount / 120)
  );

  const handleLoadSample = (sample) => {
    setDeckTitle(sample.title);
    setContent(sample.content);
    setSelectedCategory(sample.category);
    setFeedbackMsg(`Loaded "${sample.title}" sample notes.`);
    setTimeout(() => setFeedbackMsg(null), 3000);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    readFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      readFile(e.dataTransfer.files[0]);
    }
  };

  const readFile = (file) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result;
      if (typeof text === 'string') {
        const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
        setDeckTitle(cleanName);
        setContent(text);
        setFeedbackMsg(`Successfully imported ${file.name}`);
        setTimeout(() => setFeedbackMsg(null), 3000);
      }
    };
    reader.readAsText(file);
  };

  const handleTriggerAnalysis = () => {
    if (!content.trim()) {
      alert('Please paste some study notes or load a sample note set first!');
      return;
    }
    onGeneratePath(deckTitle.trim() || 'Untitled Session', content, selectedCategory);
  };

  return (
    <div className="ingestion-container animate-fade-in">
      {/* Top Banner & Value Proposition */}
      <div className="ingestion-header-card">
        <div className="ingestion-header-content">
          <div className="badge-pill">
            <Zap size={13} className="text-purple" />
            <span>Phase 1 • Ingestion & Prerequisite Extraction</span>
          </div>
          <h2 className="ingestion-hero-title">Paste Notes. Discover Concepts. Build Path.</h2>
          <p className="ingestion-hero-subtitle">
            EduMentor extracts essential concepts from your lecture slides, textbooks, or personal notes,
            identifies prerequisite dependencies, and structures an ordered study path for active recall.
          </p>
        </div>

        {/* Quick Sample Notes Pills */}
        <div className="sample-picker-bar">
          <span className="sample-label">Try instant sample deck:</span>
          <div className="sample-buttons-row">
            {SAMPLE_NOTE_SETS.map(sample => (
              <button 
                key={sample.id}
                type="button"
                className="sample-btn"
                onClick={() => handleLoadSample(sample)}
                title={sample.description}
              >
                {sample.icon === 'Cpu' && <Cpu size={14} className="text-cyan" />}
                {sample.icon === 'Brain' && <Brain size={14} className="text-purple" />}
                {sample.icon === 'Activity' && <Activity size={14} className="text-emerald" />}
                <span>{sample.title.split(':')[0]}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {feedbackMsg && (
        <div className="feedback-toast animate-fade-in">
          <Check size={16} className="text-emerald" />
          <span>{feedbackMsg}</span>
        </div>
      )}

      {/* Main Form Box */}
      <div className="ingestion-form-grid">
        {/* Left / Top: Title & Controls */}
        <div className="ingestion-meta-row">
          <div className="meta-field-group">
            <label className="field-label" htmlFor="deck-title-input">Deck / Topic Title</label>
            <input 
              id="deck-title-input"
              className="input-text-dark"
              value={deckTitle}
              onChange={(e) => setDeckTitle(e.target.value)}
              placeholder="e.g. Operating Systems: Virtual Memory"
            />
          </div>

          <div className="meta-stats-group">
            <div className="stat-pill" title="Total Words">
              <span className="stat-num">{wordCount}</span>
              <span className="stat-lbl">words</span>
            </div>
            <div className="stat-pill" title="Characters">
              <span className="stat-num">{charCount}</span>
              <span className="stat-lbl">chars</span>
            </div>
            <div className="stat-pill highlight" title="Estimated Concepts Detected">
              <span className="stat-num">~{estimatedConceptCount}</span>
              <span className="stat-lbl">concepts</span>
            </div>
          </div>
        </div>

        {/* Dropzone & Text Area Area */}
        <div 
          className={`editor-drop-container ${dragActive ? 'drag-over' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
        >
          <div className="editor-toolbar">
            <div className="toolbar-left">
              <FileText size={15} className="text-muted" />
              <span className="toolbar-title">Raw Notes Editor (Markdown / Plain Text)</span>
            </div>

            <div className="toolbar-actions">
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
                accept=".txt,.md,.markdown,.json" 
                style={{ display: 'none' }} 
              />
              <button 
                type="button" 
                className="btn-toolbar"
                onClick={() => fileInputRef.current?.click()}
                title="Upload .txt or .md file"
                id="btn-upload-file"
              >
                <Upload size={14} />
                <span>Upload File</span>
              </button>
              {content.length > 0 && (
                <button 
                  type="button" 
                  className="btn-toolbar danger"
                  onClick={() => setContent('')}
                  title="Clear text"
                >
                  <span>Clear</span>
                </button>
              )}
            </div>
          </div>

          <textarea 
            className="notes-textarea"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your lecture notes, textbook chapters, or summary here...

Tip: You can use markdown headers (e.g. ## Concept Name) or numbered topics (e.g. 1. Concept Name). Explicit lines like 'Prerequisites: ...' and 'Keywords: ...' are automatically detected to organize your prerequisite study path."
            rows={14}
            id="notes-content-textarea"
          />

          <div className="editor-footer-info">
            <span>Supports standard Markdown, plaintext lectures, or syllabus outlines.</span>
            <span>Shortcut: Press Extract below to construct the topological study graph.</span>
          </div>
        </div>

        {/* Action Button Row */}
        <div className="ingestion-action-bar">
          <button 
            type="button" 
            className="btn-primary-glow"
            onClick={handleTriggerAnalysis}
            disabled={isAnalyzing || !content.trim()}
            id="btn-extract-study-path"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw size={18} className="spin-icon" />
                <span>Analyzing Prerequisites & Sorting Graph...</span>
              </>
            ) : (
              <>
                <Sparkles size={18} />
                <span>Extract Concepts & Generate Study Path</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
