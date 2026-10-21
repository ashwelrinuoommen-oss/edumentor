import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Layers, 
  PanelRightClose, 
  X,
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  HelpCircle,
  GitFork,
  ChevronRight
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { Progress } from '../ui/Progress';
import { Badge } from '../ui/Badge';
import { cn } from '../../utils/cn';

export function StudyPathTracker() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const { 
    sessions, 
    activeSessionId,
    studyPathOpen, 
    toggleStudyPath, 
    setScrollToConceptId 
  } = useAppStore();

  const currentSession = sessions.find(s => s.id === id) || 
                         (activeSessionId ? sessions.find(s => s.id === activeSessionId) : null) || 
                         sessions[0] || 
                         null;

  if (!studyPathOpen) return null;

  const concepts = currentSession?.concepts || [];
  const totalConcepts = concepts.length;
  const masteredCount = concepts.filter(c => c.status === 'mastered').length;
  const progressPercent = totalConcepts > 0 ? Math.round((masteredCount / totalConcepts) * 100) : 0;

  const handleConceptClick = (conceptId: string, index: number) => {
    setScrollToConceptId(conceptId);

    // If not currently on this session's page, navigate to it
    if (currentSession && id !== currentSession.id) {
      navigate(`/session/${currentSession.id}`);
    }

    // Scroll chat / view to concept card or message
    setTimeout(() => {
      const element = document.getElementById(`concept-node-${conceptId}`) || 
                      document.getElementById(`concept-message-${conceptId}`) ||
                      document.getElementById(`concept-item-${conceptId}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);

    // If on mobile, close bottom sheet on item selection
    if (window.innerWidth < 1024) {
      toggleStudyPath();
    }
  };

  // Status Dot helper: not started (grey), in progress (teal), weak (red), mastered (green)
  const getStatusDot = (status: string, index: number, currentIndex: number) => {
    if (status === 'mastered') {
      return (
        <span 
          className="w-2.5 h-2.5 rounded-full bg-[#34D399] shrink-0 ring-2 ring-[#34D399]/20" 
          title="Mastered"
        />
      );
    }
    if (status === 'review_due') {
      return (
        <span 
          className="w-2.5 h-2.5 rounded-full bg-[#F87171] shrink-0 ring-2 ring-[#F87171]/20" 
          title="Weak / Due for Review"
        />
      );
    }
    if (index === currentIndex || status === 'in_progress') {
      return (
        <span 
          className="w-2.5 h-2.5 rounded-full bg-[#2DD4BF] shrink-0 ring-2 ring-[#2DD4BF]/20 animate-pulse" 
          title="In Progress"
        />
      );
    }
    return (
      <span 
        className="w-2.5 h-2.5 rounded-full bg-[#737373] shrink-0" 
        title="Not Started"
      />
    );
  };

  const trackerBody = (
    <div className="flex-1 flex flex-col min-h-0 select-none">
      {/* Header */}
      <div className="p-4 border-b border-[#262626] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers size={15} className="text-[#2DD4BF]" />
          <h3 className="text-xs font-semibold text-[#EDEDED] tracking-tight">
            Study path tracker
          </h3>
        </div>

        <button
          type="button"
          onClick={toggleStudyPath}
          className="p-1 rounded-md text-[#737373] hover:text-[#EDEDED] hover:bg-[#1F1F1F] transition-colors focus-visible:ring-2 focus-visible:ring-[#2DD4BF]"
          title="Close study path tracker"
          aria-label="Close study path tracker"
        >
          <X size={15} className="lg:hidden" />
          <PanelRightClose size={15} className="hidden lg:block" />
        </button>
      </div>

      {/* Overall Progress Bar */}
      <div className="p-4 border-b border-[#262626] bg-[#0A0A0A]/50 flex flex-col gap-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-[#A3A3A3] font-medium">Path Completion</span>
          <span className="text-[#2DD4BF] font-semibold">{progressPercent}%</span>
        </div>
        <Progress value={progressPercent} size="sm" variant="teal" />
        <div className="flex items-center justify-between text-[11px] text-[#737373] mt-0.5">
          <span>{masteredCount} of {totalConcepts} mastered</span>
          <span>{totalConcepts - masteredCount} remaining</span>
        </div>
      </div>

      {/* Status Legend */}
      <div className="px-4 py-2 border-b border-[#262626] flex items-center justify-between text-[10px] text-[#737373]">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#737373]" />
          <span>Not started</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#2DD4BF]" />
          <span>In progress</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#F87171]" />
          <span>Weak</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#34D399]" />
          <span>Mastered</span>
        </div>
      </div>

      {/* Vertical List of Ordered Concepts */}
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-1.5">
        {concepts.length === 0 ? (
          <div className="p-6 text-center text-xs text-[#737373] flex flex-col items-center gap-2">
            <GitFork size={20} className="text-[#383838]" />
            <p>No concepts in active study path.</p>
          </div>
        ) : (
          concepts.map((concept, index) => {
            const isCurrent = currentSession && currentSession.currentConceptIndex === index;

            return (
              <div
                key={concept.id}
                id={`concept-item-${concept.id}`}
                onClick={() => handleConceptClick(concept.id, index)}
                className={cn(
                  'group flex items-start gap-2.5 p-2.5 rounded-[10px] border cursor-pointer transition-all duration-150 text-left',
                  'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none',
                  isCurrent
                    ? 'bg-[#171717] border-[#2DD4BF]/50 shadow-sm'
                    : 'bg-[#141414] border-[#262626] hover:bg-[#1A1A1A] hover:border-[#383838]'
                )}
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleConceptClick(concept.id, index);
                }}
              >
                {/* Dot */}
                <div className="mt-1">
                  {getStatusDot(concept.status, index, currentSession?.currentConceptIndex ?? 0)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 flex flex-col gap-0.5">
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-xs font-medium text-[#EDEDED] truncate" title={concept.title}>
                      {index + 1}. {concept.title}
                    </span>
                  </div>

                  <p className="text-[11px] text-[#737373] line-clamp-1">
                    {concept.summary}
                  </p>

                  {/* Prerequisite preview tag if any */}
                  {concept.prerequisites && concept.prerequisites.length > 0 && (
                    <div className="flex items-center gap-1 text-[10px] text-[#737373] truncate mt-0.5">
                      <span className="text-[#A3A3A3]">Prereq:</span>
                      <span className="truncate">{concept.prerequisites[0]}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Meta */}
      <div className="p-3 border-t border-[#262626] bg-[#0A0A0A] flex items-center justify-between text-[11px] text-[#737373]">
        <span>Click concept to scroll</span>
        <Badge variant="teal" className="text-[10px] py-0 px-1.5">Topological</Badge>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Aside (>= 1024px) */}
      <aside 
        aria-label="Study Path Tracker"
        className="w-[280px] min-w-[280px] h-full bg-[#111111] border-l border-[#262626] hidden lg:flex flex-col z-10 animate-fade-in"
      >
        {trackerBody}
      </aside>

      {/* Mobile Bottom Sheet (< 1024px) */}
      <div className="lg:hidden">
        {/* Backdrop overlay */}
        <div 
          className="fixed inset-0 bg-black/75 backdrop-blur-sm z-40 transition-opacity"
          onClick={toggleStudyPath}
          aria-hidden="true"
        />

        {/* Bottom Sheet Modal Container */}
        <div 
          role="dialog"
          aria-label="Study Path Tracker Bottom Sheet"
          aria-modal="true"
          className="fixed inset-x-0 bottom-0 z-50 max-h-[82vh] h-[82vh] bg-[#111111] border-t border-[#262626] rounded-t-[20px] shadow-2xl flex flex-col animate-slide-up"
        >
          {/* Draggable grab bar handle */}
          <div className="w-12 h-1.5 bg-[#333333] rounded-full mx-auto my-2.5 shrink-0" />
          {trackerBody}
        </div>
      </div>
    </>
  );
}
