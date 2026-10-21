import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '../store/useAppStore';
import { sessionService, StudySession, Concept } from '../services/mockService';
import { 
  getDaysOverdue, 
  formatOverdueLabel, 
  getNextUpcomingReviewDate, 
  getUpcoming14DaysTimeline 
} from '../services/sm2Scheduler';
import { ActiveRecallFlow } from '../components/chat/ActiveRecallFlow';
import { DevDateSimulator } from '../components/ui/DevDateSimulator';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Tooltip } from '../components/ui/Tooltip';
import { 
  Clock, 
  CheckCircle2, 
  RotateCcw, 
  Sparkles, 
  ArrowRight, 
  Calendar, 
  Layers, 
  Flame, 
  BookOpen, 
  AlertCircle,
  HelpCircle,
  ChevronRight
} from 'lucide-react';
import { apiService, useApiCall } from '../services/api';
import { SkeletonListItem } from '../components/ui/Skeleton';
import { cn } from '../utils/cn';

export function ReviewPage() {
  const navigate = useNavigate();
  const { 
    sessions, 
    updateSession, 
    simulatedDaysOffset, 
    getSimulatedDate 
  } = useAppStore();

  const [isReviewActive, setIsReviewActive] = useState(false);
  const simulatedDate = getSimulatedDate();

  // Phase 11: Call backend GET /review/due with loading, error, and retry handling
  const { 
    data: apiDueData, 
    isLoading: isQueueLoading, 
    error: queueError, 
    retry: retryQueue 
  } = useApiCall(apiService.getDueReviews, {
    // Keep local simulated Date synced
  });

  React.useEffect(() => {
    apiService.getDueReviews(simulatedDate).catch(() => {});
  }, [simulatedDate]);

  const dueItems = sessionService.getDueReviewConcepts(simulatedDate);
  const dueCount = dueItems.length;

  // Next upcoming review date among non-due future concepts
  const nextReviewIso = getNextUpcomingReviewDate(sessions, simulatedDate);
  const formattedNextReviewDate = nextReviewIso 
    ? new Date(nextReviewIso).toLocaleDateString(undefined, {
        weekday: 'short',
        month: 'short',
        day: 'numeric'
      })
    : 'No upcoming reviews';

  // 14-day upcoming timeline
  const upcomingTimeline = getUpcoming14DaysTimeline(sessions, simulatedDate);

  // Build a synthetic StudySession containing only the due items for ActiveRecallFlow
  const reviewSession: StudySession = {
    id: `review-session-${Date.now()}`,
    title: `Spaced Recall Review (${dueItems.length} concepts due)`,
    category: 'Spaced Repetition',
    notes: 'Targeted active recall practice for concepts whose memory trace is decaying.',
    concepts: dueItems.map(item => item.concept),
    messages: [],
    currentConceptIndex: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  // Sync recall evaluation updates back to original parent sessions
  const handleUpdateReviewConcepts = (updatedReviewSession: StudySession) => {
    const conceptMap = new Map(updatedReviewSession.concepts.map(c => [c.id, c]));

    sessions.forEach(session => {
      let hasChanges = false;
      const updatedConcepts = (session.concepts || []).map(c => {
        if (conceptMap.has(c.id)) {
          hasChanges = true;
          return conceptMap.get(c.id)!;
        }
        return c;
      });

      if (hasChanges) {
        updateSession({
          ...session,
          concepts: updatedConcepts,
          updatedAt: new Date().toISOString()
        });
      }
    });
  };

  return (
    <div className="min-h-full bg-[#0A0A0A] p-4 sm:p-8 flex flex-col gap-6 max-w-4xl mx-auto">
      {/* Top Controls Row: Header Title & Dev Toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#262626]">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <Badge variant="caution" className="gap-1 text-[10px] font-mono">
              <Clock size={11} />
              <span>SM-2 Scheduler</span>
            </Badge>
            <span className="text-xs text-[#737373]">•</span>
            <span className="text-xs text-[#A3A3A3]">Spaced Repetition</span>
          </div>

          {/* Mandatory Header: "Due today: n" */}
          <h1 className="text-xl sm:text-2xl font-bold text-[#EDEDED] tracking-tight">
            Due today: {dueCount}
          </h1>
          <p className="text-xs text-[#737373]">
            Concepts scheduled right at memory decay thresholds. Queue ordered weakest first.
          </p>
        </div>

        {/* Embedded Dev Date Simulator */}
        <DevDateSimulator className="self-start sm:self-auto" />
      </div>

      {/* Error Callout with Retry Button */}
      {queueError && (
        <div className="p-4 rounded-[12px] bg-[#F87171]/10 border border-[#F87171]/30 flex items-center justify-between text-xs text-[#F87171] animate-fade-in">
          <div className="flex items-center gap-2">
            <AlertCircle size={15} />
            <span>{queueError.message || 'Error communicating with review endpoint.'}</span>
          </div>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => retryQueue()}
            className="text-xs gap-1 border-[#F87171]/40 text-[#F87171] hover:bg-[#F87171]/10"
            id="btn-retry-review-queue"
          >
            <RotateCcw size={12} />
            <span>Try again</span>
          </Button>
        </div>
      )}

      {/* Loading Skeleton Indicator */}
      {isQueueLoading && (
        <div className="flex flex-col gap-3 py-2">
          <SkeletonListItem />
          <SkeletonListItem />
          <SkeletonListItem />
        </div>
      )}

      {/* Active Recall Flow Mode (Runs when "Start review" is clicked) */}
      {isReviewActive && dueItems.length > 0 ? (
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between p-3 rounded-[12px] bg-[#171717] border border-[#262626]">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-[#2DD4BF] font-semibold">Active Review Session</span>
              <span className="text-[#737373]">•</span>
              <span className="text-[#A3A3A3]">{dueItems.length} concepts in queue</span>
            </div>
            <button
              type="button"
              onClick={() => setIsReviewActive(false)}
              className="text-xs text-[#737373] hover:text-[#EDEDED] transition-colors"
              id="btn-exit-review"
            >
              Back to queue
            </button>
          </div>

          <ActiveRecallFlow
            session={reviewSession}
            onUpdateSession={handleUpdateReviewConcepts}
            onFinish={() => {
              setIsReviewActive(false);
            }}
          />
        </div>
      ) : dueCount > 0 ? (
        /* Review Queue View (Ordered Weakest First) */
        <div className="flex flex-col gap-6" id="review-queue-container">
          {/* Action Callout with "Start review" button */}
          <div className="p-5 rounded-[16px] bg-[#171717] border border-[#262626] flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-full bg-[#2DD4BF]/15 border border-[#2DD4BF]/30 flex items-center justify-center text-[#2DD4BF] shrink-0">
                <Sparkles size={20} />
              </div>
              <div className="flex flex-col">
                <h3 className="text-sm font-semibold text-[#EDEDED]">
                  {dueCount} concept{dueCount === 1 ? '' : 's'} waiting for recall
                </h3>
                <p className="text-xs text-[#A3A3A3] mt-0.5">
                  Answering weak concepts now resets their decay curve and expands review intervals.
                </p>
              </div>
            </div>

            {/* Mandatory "Start review" button */}
            <Button
              size="sm"
              onClick={() => setIsReviewActive(true)}
              className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] font-semibold text-xs px-5 shrink-0"
              id="btn-start-review"
            >
              <span>Start review</span>
              <ArrowRight size={13} className="ml-1.5" />
            </Button>
          </div>

          {/* Ordered Queue List (Weakest First) */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between text-xs px-1 text-[#737373]">
              <span className="uppercase font-semibold tracking-wider text-[11px]">
                Recall Queue (Weakest First)
              </span>
              <span>{dueItems.length} items</span>
            </div>

            <div className="flex flex-col gap-2.5">
              {dueItems.map((item, idx) => {
                const daysOverdue = getDaysOverdue(item.concept, simulatedDate);
                const lastScore = item.concept.sm2?.lastScore ?? null;
                const scoreLabel = lastScore !== null ? `${lastScore.toFixed(1)} / 5.0` : 'Not tested';

                const isWeakScore = lastScore !== null && lastScore < 2.5;
                const isPartialScore = lastScore !== null && lastScore >= 2.5 && lastScore < 4.0;

                return (
                  <div
                    key={`${item.session.id}-${item.concept.id}-${idx}`}
                    className="p-4 rounded-[12px] bg-[#111111] border border-[#262626] hover:border-[#383838] transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm group"
                    id={`review-queue-item-${item.concept.id}`}
                  >
                    {/* Concept & Module Info */}
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="w-6 h-6 rounded-full bg-[#171717] border border-[#262626] flex items-center justify-center text-xs font-mono text-[#737373] shrink-0 mt-0.5">
                        {idx + 1}
                      </div>

                      <div className="flex flex-col min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-semibold text-[#EDEDED] group-hover:text-[#2DD4BF] transition-colors truncate">
                            {item.concept.title}
                          </h4>
                          {idx === 0 && (
                            <Badge variant="weak" className="text-[9px] py-0">Weakest</Badge>
                          )}
                        </div>

                        <div className="flex items-center gap-2 text-xs text-[#737373] mt-0.5">
                          <span className="text-[#A3A3A3] truncate max-w-[200px]">{item.session.title}</span>
                          <span>•</span>
                          <span className="line-clamp-1">{item.concept.summary}</span>
                        </div>
                      </div>
                    </div>

                    {/* Metadata Chips: Last Score & Days Overdue */}
                    <div className="flex items-center gap-2.5 shrink-0 self-end sm:self-auto">
                      {/* Last Score Badge */}
                      <div className="flex flex-col items-end">
                        <span className="text-[10px] text-[#737373] uppercase font-mono">Last Score</span>
                        <span
                          className={cn(
                            "text-xs font-bold font-mono px-2 py-0.5 rounded border",
                            isWeakScore
                              ? "bg-[#F87171]/15 text-[#F87171] border-[#F87171]/30"
                              : isPartialScore
                              ? "bg-[#FBBF24]/15 text-[#FBBF24] border-[#FBBF24]/30"
                              : "bg-[#34D399]/15 text-[#34D399] border-[#34D399]/30"
                          )}
                        >
                          {scoreLabel}
                        </span>
                      </div>

                      {/* Days Overdue Badge */}
                      <div className="flex flex-col items-end">
                        <span className="text-[10px] text-[#737373] uppercase font-mono">Status</span>
                        <span
                          className={cn(
                            "text-xs font-medium px-2 py-0.5 rounded border flex items-center gap-1",
                            daysOverdue > 0
                              ? "bg-[#F87171]/10 text-[#F87171] border-[#F87171]/30"
                              : "bg-[#FBBF24]/10 text-[#FBBF24] border-[#FBBF24]/30"
                          )}
                        >
                          <Clock size={11} />
                          <span>{formatOverdueLabel(daysOverdue)}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : (
        /* Empty State: "Nothing due today. Your next review is on {date}." with 14-day timeline */
        <div className="flex flex-col gap-6" id="review-empty-state-container">
          <div className="p-8 sm:p-10 rounded-[18px] bg-[#171717] border border-[#262626] text-center flex flex-col items-center justify-center gap-3.5 shadow-2xl">
            <div className="w-14 h-14 rounded-full bg-[#34D399]/15 border border-[#34D399]/30 flex items-center justify-center text-[#34D399]">
              <CheckCircle2 size={28} />
            </div>

            {/* Mandatory Empty State Headline */}
            <h2 className="text-lg sm:text-xl font-bold text-[#EDEDED] tracking-tight">
              Nothing due today. Your next review is on {formattedNextReviewDate}.
            </h2>

            <p className="text-xs text-[#A3A3A3] max-w-md leading-relaxed">
              All concepts are currently within their optimal retention intervals. Use the dev toggle in the header to simulate days passing and observe concepts returning when memory decays.
            </p>

            <div className="flex items-center gap-3 pt-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => navigate('/home')}
                className="text-xs"
              >
                Start a New Session
              </Button>
            </div>
          </div>

          {/* Small Upcoming-Reviews Timeline for the next 14 Days */}
          <div className="p-5 rounded-[16px] bg-[#111111] border border-[#262626] flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Calendar size={14} className="text-[#2DD4BF]" />
                <h3 className="text-xs font-semibold text-[#EDEDED]">
                  Upcoming Reviews Timeline (Next 14 Days)
                </h3>
              </div>
              <span className="text-[11px] text-[#737373]">
                Projected SM-2 Decay Schedule
              </span>
            </div>

            {/* 14-Day Timeline Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-7 lg:grid-cols-14 gap-2">
              {upcomingTimeline.map((item) => {
                const hasDue = item.count > 0;

                return (
                  <div
                    key={item.dayOffset}
                    className={cn(
                      "p-2.5 rounded-[10px] border flex flex-col items-center justify-between text-center transition-all min-h-[90px]",
                      hasDue
                        ? "bg-[#171717] border-[#2DD4BF]/40 shadow-sm"
                        : "bg-[#0E0E0E] border-[#262626]/70 opacity-60"
                    )}
                    title={
                      hasDue 
                        ? `${item.count} concept${item.count > 1 ? 's' : ''} scheduled for ${item.dateFormatted}: ${item.conceptTitles.join(', ')}`
                        : `No reviews scheduled for ${item.dateFormatted}`
                    }
                  >
                    <span className="text-[10px] font-mono text-[#737373] uppercase">
                      {item.dayOfWeek}
                    </span>
                    <span className="text-xs font-bold text-[#EDEDED] font-mono">
                      {item.date.getDate()}
                    </span>

                    {/* Count Indicator */}
                    <div className="mt-1">
                      {hasDue ? (
                        <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-[#2DD4BF]/20 text-[#2DD4BF] border border-[#2DD4BF]/30">
                          {item.count} due
                        </span>
                      ) : (
                        <span className="text-[10px] text-[#737373] font-mono">
                          -
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            <p className="text-[11px] text-[#737373] italic text-center">
              💡 As intervals expand past 21 days, concepts become fully Mastered.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
