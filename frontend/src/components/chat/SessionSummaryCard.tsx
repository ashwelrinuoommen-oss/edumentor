import React from 'react';
import { motion } from 'framer-motion';
import { 
  Trophy, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Calendar, 
  ArrowRight, 
  RotateCcw, 
  Home, 
  TrendingUp,
  Clock
} from 'lucide-react';
import { Concept } from '../../services/mockService';
import { EvaluationResult } from '../../services/evaluationEngine';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { cn } from '../../utils/cn';

export interface ConceptEvaluationRecord {
  concept: Concept;
  evaluation: EvaluationResult;
}

export interface SessionSummaryCardProps {
  records: ConceptEvaluationRecord[];
  sessionTitle: string;
  onReviewWeakNow: () => void;
  onFinishForToday: () => void;
}

export function SessionSummaryCard({
  records,
  sessionTitle,
  onReviewWeakNow,
  onFinishForToday
}: SessionSummaryCardProps) {
  if (!records || records.length === 0) return null;

  // Compute average score
  const totalScore = records.reduce((sum, r) => sum + r.evaluation.score, 0);
  const averageScore = Number((totalScore / records.length).toFixed(1));

  // Determine strongest and weakest concepts
  const sortedByScore = [...records].sort((a, b) => b.evaluation.score - a.evaluation.score);
  const strongest = sortedByScore[0];
  const weakest = sortedByScore[sortedByScore.length - 1];

  const hasWeak = records.some(r => r.evaluation.score < 3.5 || r.concept.status === 'weak');

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="p-5 sm:p-7 rounded-[18px] bg-[#171717] border border-[#262626] text-sm text-[#EDEDED] shadow-2xl flex flex-col gap-6 max-w-2xl w-full"
      id="session-summary-card"
    >
      {/* Header: Trophy & Completion Title */}
      <div className="flex items-start gap-4 pb-4 border-b border-[#262626]">
        <div className="w-12 h-12 rounded-[12px] bg-[#2DD4BF]/15 border border-[#2DD4BF]/30 flex items-center justify-center text-[#2DD4BF] shrink-0">
          <Trophy size={24} />
        </div>
        <div className="flex flex-col gap-1 min-w-0">
          <div className="flex items-center gap-2">
            <Badge variant="teal" className="text-[10px] uppercase font-semibold">
              Session Complete
            </Badge>
            <span className="text-xs text-[#737373] font-mono">• All concepts recalled</span>
          </div>
          <h2 className="text-lg sm:text-xl font-bold text-[#EDEDED] truncate">
            {sessionTitle}
          </h2>
          <p className="text-xs text-[#A3A3A3]">
            You recalled all {records.length} concepts. Answers have been calibrated into your SM-2 spaced repetition queue.
          </p>
        </div>
      </div>

      {/* Centerpiece Stat: Average Score */}
      <div className="p-4 rounded-[14px] bg-[#111111] border border-[#262626] flex items-center justify-between">
        <div className="flex flex-col gap-0.5">
          <span className="text-[11px] font-medium text-[#737373] uppercase tracking-wider">
            Average Session Score
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-[#EDEDED] font-mono">
              {averageScore.toFixed(1)}
            </span>
            <span className="text-xs text-[#737373] font-mono">/ 5.0</span>
          </div>
        </div>

        <Badge
          variant={averageScore >= 4.0 ? 'success' : averageScore >= 2.5 ? 'caution' : 'weak'}
          className="text-xs py-1 px-3 uppercase font-semibold"
        >
          {averageScore >= 4.0 ? 'Strong Retention' : averageScore >= 2.5 ? 'Partial Retention' : 'Needs Practice'}
        </Badge>
      </div>

      {/* Strongest and Weakest Concepts Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Strongest Concept */}
        {strongest && (
          <div className="p-3.5 rounded-[12px] bg-[#34D399]/10 border border-[#34D399]/30 flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-[#34D399] uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 size={13} />
                Strongest Concept
              </span>
              <span className="font-mono text-xs font-bold text-[#34D399]">
                {strongest.evaluation.score.toFixed(1)}/5.0
              </span>
            </div>
            <span className="text-xs font-semibold text-[#EDEDED] truncate">
              {strongest.concept.title}
            </span>
            <span className="text-[11px] text-[#A3A3A3] line-clamp-1">
              {strongest.concept.summary || strongest.concept.rawContent}
            </span>
          </div>
        )}

        {/* Weakest Concept */}
        {weakest && (
          <div className="p-3.5 rounded-[12px] bg-[#F87171]/10 border border-[#F87171]/30 flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-[#F87171] uppercase tracking-wider flex items-center gap-1.5">
                <AlertCircle size={13} />
                Weakest Concept
              </span>
              <span className="font-mono text-xs font-bold text-[#F87171]">
                {weakest.evaluation.score.toFixed(1)}/5.0
              </span>
            </div>
            <span className="text-xs font-semibold text-[#EDEDED] truncate">
              {weakest.concept.title}
            </span>
            <span className="text-[11px] text-[#A3A3A3] line-clamp-1">
              {weakest.concept.summary || weakest.concept.rawContent}
            </span>
          </div>
        )}
      </div>

      {/* "Concepts coming back soon" with their dates */}
      <div className="flex flex-col gap-2 p-4 rounded-[12px] bg-[#111111] border border-[#262626]">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-[#EDEDED]">
          <Calendar size={13} className="text-[#2DD4BF]" />
          <span>Concepts coming back soon (Spaced Repetition Schedule)</span>
        </div>
        <p className="text-[11px] text-[#737373]">
          Weaker answers come back sooner to prevent forgetting curves.
        </p>

        <div className="flex flex-col divide-y divide-[#262626] mt-1">
          {records.map((r, idx) => (
            <div key={idx} className="flex items-center justify-between py-2 text-xs">
              <div className="flex items-center gap-2 min-w-0">
                <span className="w-4 h-4 rounded-full bg-[#171717] text-[10px] text-[#737373] flex items-center justify-center font-mono shrink-0">
                  {idx + 1}
                </span>
                <span className="font-medium text-[#EDEDED] truncate">
                  {r.concept.title}
                </span>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span className="text-[11px] text-[#2DD4BF] font-medium">
                  {r.evaluation.nextReviewLabel === 'tomorrow' ? 'Tomorrow' : r.evaluation.nextReviewLabel}
                </span>
                <span className="text-[10px] font-mono text-[#737373]">
                  ({r.evaluation.score.toFixed(1)}/5)
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons: "Review weak concepts now" and "Finish for today" */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-end gap-3 pt-3 border-t border-[#262626]">
        {hasWeak && (
          <Button
            variant="secondary"
            size="sm"
            onClick={onReviewWeakNow}
            className="text-xs"
            id="btn-review-weak-now"
          >
            <RotateCcw size={13} className="mr-1.5 text-[#F87171]" />
            <span>Review weak concepts now</span>
          </Button>
        )}

        <Button
          size="sm"
          onClick={onFinishForToday}
          className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] text-xs font-semibold px-4"
          id="btn-finish-for-today"
        >
          <span>Finish for today</span>
          <ArrowRight size={13} className="ml-1.5" />
        </Button>
      </div>
    </motion.div>
  );
}
