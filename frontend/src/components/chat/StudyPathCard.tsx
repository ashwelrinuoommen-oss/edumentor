import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Layers, 
  List, 
  Network, 
  Clock, 
  ArrowRight, 
  RotateCcw, 
  Download, 
  Info, 
  ChevronRight,
  GitFork,
  BookOpen,
  CheckCircle2
} from 'lucide-react';
import { StudySession, Concept } from '../../services/mockService';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { ConceptFlowGraph } from '../graph/ConceptFlowGraph';
import { ConceptDetailDrawer } from './ConceptDetailDrawer';
import { useToast } from '../ui/Toast';
import { cn } from '../../utils/cn';

export interface StudyPathCardProps {
  session: StudySession;
  onUpdateSession: (updatedSession: StudySession) => void;
  onRegeneratePath?: () => void;
  onStartRecall?: () => void;
}

export function StudyPathCard({
  session,
  onUpdateSession,
  onRegeneratePath,
  onStartRecall
}: StudyPathCardProps) {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [viewMode, setViewMode] = useState<'list' | 'graph'>('list');
  const [selectedConceptId, setSelectedConceptId] = useState<string | null>(null);

  const concepts = session.concepts || [];
  const selectedConcept = concepts.find(c => c.id === selectedConceptId) || null;

  // Calculate estimated study time
  const totalMinutes = concepts.reduce((sum, c) => sum + (c.estTimeMinutes || 3), 0);

  // Handle drawer update of concepts
  const handleUpdateConcepts = (updatedConcepts: Concept[]) => {
    const updatedSession: StudySession = {
      ...session,
      concepts: updatedConcepts,
      updatedAt: new Date().toISOString()
    };
    onUpdateSession(updatedSession);

    toast({
      title: 'Study Path Updated',
      description: 'Prerequisite order and concept definitions synchronized.',
      type: 'success'
    });
  };

  // Mock Export as PDF
  const handleExportPdf = () => {
    toast({
      title: 'Exporting Study Path',
      description: `Generating offline PDF study guide for "${session.title}"...`,
      type: 'info'
    });
  };

  return (
    <div className="flex flex-col items-start gap-1.5 self-start max-w-3xl w-full">
      {/* Mentor Identity Row */}
      <div className="flex items-center gap-2 text-[11px] text-[#737373] px-1">
        <div className="w-5 h-5 rounded-full bg-[#2DD4BF]/15 border border-[#2DD4BF]/30 flex items-center justify-center text-[#2DD4BF]">
          <Sparkles size={11} />
        </div>
        <span className="text-[#2DD4BF] font-semibold">EduMentor</span>
        <span>•</span>
        <span>Just now</span>
      </div>

      {/* Main "Your study path" Card */}
      <div 
        className="w-full rounded-[16px] bg-[#171717] border border-[#262626] p-4 sm:p-6 text-sm text-[#EDEDED] shadow-xl flex flex-col gap-5"
        id="study-path-card"
      >
        {/* Card Header: Module Name, Concept Count, Est Time, and Segmented Toggle */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#262626]">
          <div className="flex flex-col gap-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[#2DD4BF] text-xs font-semibold tracking-wide uppercase">
                Your study path
              </span>
              <Badge variant="teal" className="text-[10px] py-0 px-2 font-mono">
                {concepts.length} concepts
              </Badge>
              <span className="text-xs text-[#737373] flex items-center gap-1 font-mono">
                <Clock size={12} />
                Est. {totalMinutes} mins
              </span>
            </div>

            <h3 className="text-base sm:text-lg font-semibold text-[#EDEDED] truncate" title={session.title}>
              {session.title}
            </h3>
          </div>

          {/* Segmented View Toggle: List vs Graph */}
          <div className="inline-flex items-center p-1 rounded-full bg-[#111111] border border-[#262626] shrink-0 self-start sm:self-auto">
            <button
              type="button"
              onClick={() => setViewMode('list')}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all duration-150',
                viewMode === 'list'
                  ? 'bg-[#171717] text-[#2DD4BF] shadow-sm border border-[#262626]'
                  : 'text-[#737373] hover:text-[#EDEDED]'
              )}
              id="toggle-view-list"
            >
              <List size={13} />
              <span>List view</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('graph')}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all duration-150',
                viewMode === 'graph'
                  ? 'bg-[#171717] text-[#2DD4BF] shadow-sm border border-[#262626]'
                  : 'text-[#737373] hover:text-[#EDEDED]'
              )}
              id="toggle-view-graph"
            >
              <Network size={13} />
              <span>Graph view</span>
            </button>
          </div>
        </div>

        {/* View Mode 1: List View */}
        {viewMode === 'list' && (
          <div className="flex flex-col gap-0 relative py-1" id="study-path-list-view">
            {concepts.map((concept, idx) => {
              const isLast = idx === concepts.length - 1;
              const prereqNames = (concept.prerequisiteIds || []).map(pId => {
                const found = concepts.find(c => c.id === pId);
                return found ? found.title : null;
              }).filter(Boolean);

              const isMastered = concept.status === 'mastered';
              const isWeak = concept.status === 'weak' || concept.status === 'review_due';
              const isInProgress = concept.status === 'in_progress';

              return (
                <div key={concept.id} className="relative flex items-start gap-3.5 group">
                  {/* Left Column: Number Node + Vertical Connector Line */}
                  <div className="flex flex-col items-center shrink-0 self-stretch">
                    <div 
                      className={cn(
                        "w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all z-10",
                        isMastered 
                          ? "bg-[#34D399]/20 text-[#34D399] border border-[#34D399]/40" 
                          : isInProgress
                          ? "bg-[#2DD4BF]/20 text-[#2DD4BF] border border-[#2DD4BF]/50"
                          : isWeak
                          ? "bg-[#F87171]/20 text-[#F87171] border border-[#F87171]/50"
                          : "bg-[#111111] text-[#A3A3A3] border border-[#262626] group-hover:border-[#2DD4BF] group-hover:text-[#2DD4BF]"
                      )}
                    >
                      {concept.orderIndex}
                    </div>

                    {/* Vertical Connector Line linking cards in sequence */}
                    {!isLast && (
                      <div className="w-0.5 flex-1 bg-[#262626] group-hover:bg-[#2DD4BF]/40 transition-colors my-1" />
                    )}
                  </div>

                  {/* Right Column: Numbered Concept Card */}
                  <div
                    onClick={() => setSelectedConceptId(concept.id)}
                    className={cn(
                      "flex-1 p-3.5 sm:p-4 rounded-[12px] bg-[#111111] border border-[#262626] mb-3 transition-all cursor-pointer shadow-sm text-left",
                      "hover:bg-[#1A1A1A] hover:border-[#383838] hover:ring-1 hover:ring-[#2DD4BF]/30",
                      "focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none"
                    )}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === 'Enter' && setSelectedConceptId(concept.id)}
                    id={`concept-item-${concept.id}`}
                    title="Click to view details and edit concept"
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-xs font-semibold text-[#EDEDED] group-hover:text-[#2DD4BF] transition-colors truncate">
                          {concept.title}
                        </span>
                      </div>

                      {/* Status Badge */}
                      <Badge
                        variant={
                          isMastered 
                            ? 'success' 
                            : isWeak 
                            ? 'weak' 
                            : isInProgress 
                            ? 'teal' 
                            : 'neutral'
                        }
                        className="text-[10px] py-0 px-2 uppercase tracking-wide font-semibold shrink-0"
                      >
                        {concept.status === 'unstudied' ? 'Unstudied' : (concept.status || 'Unstudied').replace('_', ' ')}
                      </Badge>
                    </div>

                    {/* One-line Definition Clamped */}
                    <p className="text-xs text-[#A3A3A3] line-clamp-1 leading-relaxed mb-2.5">
                      {concept.summary || concept.rawContent}
                    </p>

                    {/* Prerequisite Chips & Footer Row */}
                    <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-[#262626]/60 text-[11px]">
                      <div className="flex flex-wrap items-center gap-1.5">
                        {prereqNames.length > 0 ? (
                          prereqNames.map((name, pIdx) => (
                            <span
                              key={pIdx}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#171717] border border-[#262626] text-[10px] text-[#2DD4BF]"
                            >
                              <span className="text-[#737373]">needs:</span>
                              <span className="font-medium truncate max-w-[120px]">{name}</span>
                            </span>
                          ))
                        ) : (
                          <span className="text-[10px] text-[#737373] italic">
                            Foundation concept
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-1 text-[10px] text-[#737373] group-hover:text-[#2DD4BF] transition-colors">
                        <span>Details & edit</span>
                        <ChevronRight size={12} />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* View Mode 2: Graph View */}
        {viewMode === 'graph' && (
          <div className="w-full flex flex-col gap-2" id="study-path-graph-view">
            <ConceptFlowGraph
              concepts={concepts}
              activeConceptId={selectedConceptId || undefined}
              onSelectConcept={(conceptId) => setSelectedConceptId(conceptId)}
              height="430px"
            />
            <p className="text-[11px] text-[#737373] italic text-center">
              💡 Tip: Drag to pan, scroll to zoom, hover for definition, or click any node to open the concept drawer.
            </p>
          </div>
        )}

        {/* Card Actions & Note Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-[#262626]">
          {/* Mandatory small note */}
          <div className="flex items-center gap-1.5 text-xs text-[#737373]">
            <Info size={13} className="shrink-0 text-[#2DD4BF]" />
            <span>Definitions come only from your notes.</span>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            {onRegeneratePath && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onRegeneratePath}
                className="text-xs"
                id="btn-regenerate-path"
              >
                <RotateCcw size={12} className="mr-1.5" />
                <span>Regenerate path</span>
              </Button>
            )}

            <Button
              variant="secondary"
              size="sm"
              onClick={handleExportPdf}
              className="text-xs"
              id="btn-export-pdf"
            >
              <Download size={12} className="mr-1.5" />
              <span>Export as PDF</span>
            </Button>

            <Button
              size="sm"
              onClick={() => onStartRecall ? onStartRecall() : navigate(`/session/${session.id}`)}
              className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] text-xs font-semibold px-4"
              id="btn-start-recall"
            >
              <span>Start recall</span>
              <ArrowRight size={13} className="ml-1.5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Concept Drawer (Right side) */}
      <ConceptDetailDrawer
        isOpen={Boolean(selectedConceptId)}
        concept={selectedConcept}
        allConcepts={concepts}
        onClose={() => setSelectedConceptId(null)}
        onUpdateConcepts={handleUpdateConcepts}
      />
    </div>
  );
}
