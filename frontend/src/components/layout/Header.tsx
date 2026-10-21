import React, { useState, useEffect } from 'react';
import { useLocation, useParams, useNavigate } from 'react-router-dom';
import { 
  Menu, 
  PanelRightClose, 
  PanelRight, 
  Clock, 
  Edit2, 
  Check, 
  X,
  Layers,
  Sparkles
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { sessionService } from '../../services/mockService';
import { Badge } from '../ui/Badge';
import { DevDateSimulator } from '../ui/DevDateSimulator';
import { cn } from '../../utils/cn';

export function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { id } = useParams<{ id?: string }>();
  
  const { 
    sessions, 
    renameSession, 
    studyPathOpen, 
    toggleStudyPath, 
    setMobileSidebarOpen,
    simulatedDaysOffset,
    getSimulatedDate
  } = useAppStore();

  const currentSession = sessions.find(s => s.id === id);

  // Inline editing state for session title
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState('');

  useEffect(() => {
    if (currentSession) {
      setEditedTitle(currentSession.title);
    }
  }, [currentSession]);

  const simulatedDate = getSimulatedDate();
  const dueItems = sessionService.getDueReviewConcepts(simulatedDate);
  const dueCount = dueItems.length;

  const handleSaveTitle = (e: React.FormEvent) => {
    e.preventDefault();
    if (currentSession && editedTitle.trim()) {
      renameSession(currentSession.id, editedTitle.trim());
    }
    setIsEditingTitle(false);
  };

  const getPageTitle = () => {
    if (location.pathname === '/home') return 'New Study Session';
    if (location.pathname === '/review') return 'Spaced Repetition Review';
    if (location.pathname === '/progress') return 'Progress & Retention Matrix';
    if (location.pathname === '/settings') return 'Application Settings';
    if (location.pathname === '/styleguide') return 'Design System Styleguide';
    if (currentSession) return currentSession.title;
    return 'EduMentor';
  };

  return (
    <header className="h-14 min-h-[56px] bg-[#111111] border-b border-[#262626] px-4 md:px-6 flex items-center justify-between z-10 select-none">
      {/* Left: Mobile Hamburger & Current Title (Editable Inline) */}
      <div className="flex items-center gap-3 min-w-0">
        {/* Mobile Sidebar Hamburger Toggle */}
        <button
          type="button"
          onClick={() => setMobileSidebarOpen(true)}
          className="md:hidden p-1.5 rounded-md text-[#A3A3A3] hover:text-[#EDEDED] hover:bg-[#1F1F1F] transition-colors focus-visible:ring-2 focus-visible:ring-[#2DD4BF]"
          title="Open menu"
        >
          <Menu size={18} />
        </button>

        {/* Inline Editable Title or Section Name */}
        {currentSession && location.pathname.startsWith('/session/') ? (
          isEditingTitle ? (
            <form onSubmit={handleSaveTitle} className="flex items-center gap-1.5">
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                autoFocus
                onBlur={handleSaveTitle}
                className="text-sm font-medium bg-[#171717] border border-[#2DD4BF] rounded-md px-2.5 py-1 text-[#EDEDED] outline-none max-w-xs md:max-w-md"
              />
              <button
                type="submit"
                className="p-1 text-[#34D399] hover:bg-[#171717] rounded"
                title="Save title"
              >
                <Check size={14} />
              </button>
              <button
                type="button"
                onClick={() => {
                  setEditedTitle(currentSession.title);
                  setIsEditingTitle(false);
                }}
                className="p-1 text-[#737373] hover:bg-[#171717] rounded"
                title="Cancel"
              >
                <X size={14} />
              </button>
            </form>
          ) : (
            <div 
              onClick={() => setIsEditingTitle(true)}
              className="group flex items-center gap-2 cursor-pointer py-1 px-1.5 -ml-1.5 rounded-md hover:bg-[#171717] transition-colors max-w-xs sm:max-w-md truncate"
              title="Click to rename session title"
            >
              <h2 className="text-sm font-medium text-[#EDEDED] truncate">
                {currentSession.title}
              </h2>
              <Edit2 size={12} className="opacity-0 group-hover:opacity-100 text-[#737373] transition-opacity shrink-0" />
            </div>
          )
        ) : (
          <h2 className="text-sm font-medium text-[#EDEDED] truncate">
            {getPageTitle()}
          </h2>
        )}
      </div>

      {/* Right: Due Status Chip & Study Path Panel Toggle */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Phase 7 Dev Toggle for Date Simulation */}
        <DevDateSimulator className="hidden md:inline-flex" />

        {/* Small Status Chip: e.g. "3 due today" */}
        <button
          type="button"
          onClick={() => navigate('/review')}
          className={cn(
            'inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full border transition-colors cursor-pointer',
            'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none',
            dueCount > 0 
              ? 'bg-[#FBBF24]/10 text-[#FBBF24] border-[#FBBF24]/30 hover:bg-[#FBBF24]/20' 
              : 'bg-[#2DD4BF]/10 text-[#2DD4BF] border-[#2DD4BF]/30 hover:bg-[#2DD4BF]/20'
          )}
          id="chip-due-today-header"
          title="View spaced repetition queue"
        >
          <Clock size={12} />
          <span>{dueCount} due today</span>
        </button>

        {/* Keyboard Shortcuts Trigger Button */}
        <button
          type="button"
          onClick={() => useAppStore.getState().setShortcutsModalOpen(true)}
          className="p-1.5 rounded-md text-[#737373] hover:text-[#EDEDED] hover:bg-[#1F1F1F] transition-colors focus-visible:ring-2 focus-visible:ring-[#2DD4BF]"
          title="Keyboard shortcuts (?)"
          aria-label="Open keyboard shortcuts cheat sheet"
          id="btn-keyboard-shortcuts-header"
        >
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono font-bold bg-[#1A1A1A] border border-[#262626] rounded text-[#A3A3A3]">
            ?
          </kbd>
        </button>

        {/* Study Path Panel Toggle Button (Bottom sheet on mobile, aside on desktop) */}
        <button
          type="button"
          onClick={toggleStudyPath}
          className={cn(
            'inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-[8px] border transition-colors',
            'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none',
            studyPathOpen
              ? 'bg-[#171717] text-[#2DD4BF] border-[#2DD4BF]/40'
              : 'bg-transparent text-[#737373] border-[#262626] hover:text-[#EDEDED] hover:bg-[#171717]'
          )}
          id="btn-toggle-study-path-header"
          title={studyPathOpen ? "Hide Study Path Tracker" : "Show Study Path Tracker"}
          aria-label="Toggle study path tracker panel"
        >
          <Layers size={14} />
          <span className="hidden md:inline">Study path</span>
          {studyPathOpen ? <PanelRightClose size={14} /> : <PanelRight size={14} />}
        </button>
      </div>
    </header>
  );
}
