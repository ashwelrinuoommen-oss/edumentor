import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { ConceptFlowGraph } from '../components/graph/ConceptFlowGraph';
import { TrendingUp } from 'lucide-react';
import { cn } from '../utils/cn';
import { InitialNotesContent } from '../components/chat/InitialNotesContent';
import { StudyPathCard } from '../components/chat/StudyPathCard';
import { ActiveRecallFlow } from '../components/chat/ActiveRecallFlow';

export function SessionPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { sessions, updateSession, scrollToConceptId, setScrollToConceptId } = useAppStore();

  const [activeTab, setActiveTab] = useState<'chat' | 'graph'>('chat');
  const session = sessions.find(s => s.id === id);

  // Scroll to target concept when clicked from StudyPathTracker
  useEffect(() => {
    if (scrollToConceptId) {
      setActiveTab('chat');
      setTimeout(() => {
        const el = document.getElementById(`concept-item-${scrollToConceptId}`);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        setScrollToConceptId(null);
      }, 100);
    }
  }, [scrollToConceptId, setScrollToConceptId]);

  if (!session) {
    return (
      <div className="p-8 text-center flex flex-col items-center justify-center h-full gap-3">
        <h3 className="text-base font-semibold text-[#EDEDED]">Session not found</h3>
        <p className="text-xs text-[#737373]">This study thread may have been removed.</p>
        <Button variant="secondary" size="sm" onClick={() => navigate('/home')}>
          Return to Home
        </Button>
      </div>
    );
  }

  const currentConcept = session.concepts[session.currentConceptIndex] || session.concepts[0];
  const totalConcepts = session.concepts.length;
  const masteredCount = session.concepts.filter(c => c.status === 'mastered').length;
  const progressPercent = totalConcepts > 0 ? Math.round((masteredCount / totalConcepts) * 100) : 0;

  // Extract initial student notes message if available
  const initialMessage = session.messages.find(m => m.isInitialNotes || m.role === 'student');

  return (
    <div className="flex h-full flex-col bg-[#0A0A0A] overflow-hidden select-text">
      {/* Session Top Bar */}
      <div className="px-6 py-3 border-b border-[#262626] bg-[#111111] flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex flex-col min-w-0">
            <h2 className="text-sm font-semibold text-[#EDEDED] truncate">
              {session.title}
            </h2>
            <div className="flex items-center gap-2 text-[11px] text-[#737373]">
              <span>Concept {session.currentConceptIndex + 1} of {totalConcepts}:</span>
              <span className="text-[#2DD4BF] font-medium truncate">
                {currentConcept?.title || 'Review'}
              </span>
            </div>
          </div>
        </div>

        {/* View Switcher & Progress */}
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-[#171717] p-1 rounded-[8px] border border-[#262626]">
            <button
              onClick={() => setActiveTab('chat')}
              className={cn(
                'px-3 py-1 text-xs rounded-md font-medium transition-colors',
                activeTab === 'chat' ? 'bg-[#242424] text-[#EDEDED]' : 'text-[#737373] hover:text-[#EDEDED]'
              )}
            >
              Mentor Chat
            </button>
            <button
              onClick={() => setActiveTab('graph')}
              className={cn(
                'px-3 py-1 text-xs rounded-md font-medium transition-colors',
                activeTab === 'graph' ? 'bg-[#242424] text-[#EDEDED]' : 'text-[#737373] hover:text-[#EDEDED]'
              )}
            >
              Concept Graph
            </button>
          </div>

          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-[8px] bg-[#171717] border border-[#262626] text-xs">
            <TrendingUp size={13} className="text-[#2DD4BF]" />
            <span className="text-[#A3A3A3]">{progressPercent}% Mastered</span>
          </div>
        </div>
      </div>

      {/* Main Workspace Body */}
      {activeTab === 'graph' ? (
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-5xl mx-auto flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-[#EDEDED]">Prerequisite Concept Graph</h3>
                <p className="text-xs text-[#737373]">
                  Interactive DAG showing the knowledge graph and prerequisite flow.
                </p>
              </div>
              <Badge variant="teal">Step {session.currentConceptIndex + 1} of {totalConcepts}</Badge>
            </div>
            <ConceptFlowGraph 
              concepts={session.concepts} 
              activeConceptId={currentConcept?.id} 
            />
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-4 sm:p-6">
          <div className="max-w-3xl mx-auto w-full flex flex-col gap-6">
            {/* 1. Restored User Message: Initial Notes */}
            <div className="flex flex-col items-end gap-1.5 self-end max-w-2xl w-full">
              <div className="flex items-center gap-2 text-[11px] text-[#737373] px-1">
                <span>You</span>
                <span>•</span>
                <span>{new Date(session.createdAt || Date.now()).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
              </div>

              <div className="p-4 rounded-[14px] bg-[#171717] border border-[#262626] text-sm text-[#EDEDED] shadow-md w-full">
                {/* Attached Files if present */}
                {initialMessage?.attachments && initialMessage.attachments.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3 pb-2.5 border-b border-[#262626]">
                    {initialMessage.attachments.map((file, fIdx) => (
                      <div
                        key={fIdx}
                        className="inline-flex items-center gap-2 px-2.5 py-1 rounded-[8px] bg-[#111111] border border-[#262626] text-xs text-[#EDEDED]"
                      >
                        <span className="text-[#2DD4BF] font-mono text-[10px] uppercase font-bold">
                          {file.type}
                        </span>
                        <span className="font-medium truncate max-w-[160px]">{file.name}</span>
                        <span className="text-[10px] text-[#737373]">{file.size}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Notes Text with Show More Toggle */}
                <InitialNotesContent 
                  content={session.notes} 
                  isInitial={true} 
                />
              </div>
            </div>

            {/* 2. Restored Study Path Card */}
            <StudyPathCard
              session={session}
              onUpdateSession={(updatedSession) => {
                updateSession(updatedSession);
              }}
            />

            {/* 3. Restored Active Recall Flow */}
            <ActiveRecallFlow
              session={session}
              onUpdateSession={(updatedSession) => {
                updateSession(updatedSession);
              }}
              onFinish={() => {
                navigate('/progress');
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
