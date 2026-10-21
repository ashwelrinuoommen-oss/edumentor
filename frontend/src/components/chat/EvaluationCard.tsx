import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle2, 
  AlertCircle, 
  Info, 
  ChevronDown, 
  ChevronUp, 
  RotateCcw, 
  ArrowRight, 
  Calendar, 
  Flag, 
  Sparkles,
  HelpCircle
} from 'lucide-react';
import { EvaluationResult } from '../../services/evaluationEngine';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Tooltip } from '../ui/Tooltip';
import { useToast } from '../ui/Toast';
import { cn } from '../../utils/cn';

export interface EvaluationCardProps {
  evaluation: EvaluationResult;
  conceptTitle: string;
  isLastConcept: boolean;
  onNextConcept: () => void;
  onTryAgain: () => void;
}

export function EvaluationCard({
  evaluation,
  conceptTitle,
  isLastConcept,
  onNextConcept,
  onTryAgain
}: EvaluationCardProps) {
  const { toast } = useToast();
  const [showNotesComparison, setShowNotesComparison] = useState(false);
  const [flagged, setFlagged] = useState(false);

  // Score metrics
  const score = evaluation.score;
  const gradeLabel = evaluation.gradeLabel;
  const isStrong = gradeLabel === 'Strong';
  const isPartial = gradeLabel === 'Partial';
  const isNeedsWork = gradeLabel === 'Needs work';

  // SVG Circular Score Ring constants
  const radius = 38;
  const circumference = 2 * Math.PI * radius; // ~238.76
  const strokeDashoffset = circumference - (Math.min(score, 5.0) / 5.0) * circumference;

  const ringColor = isStrong 
    ? '#34D399' 
    : isPartial 
    ? '#FBBF24' 
    : '#F87171';

  // Highlighting matched keywords in source definition
  const renderHighlightedDefinition = (text: string, matched: string[]) => {
    if (!matched || matched.length === 0) return text;

    // Build regex to match any of the matched keywords (case-insensitive)
    const escaped = matched.map(m => m.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
    const regex = new RegExp(`(${escaped})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, i) => {
      const isMatched = matched.some(m => m.toLowerCase() === part.toLowerCase());
      if (isMatched) {
        return (
          <mark key={i} className="bg-[#2DD4BF]/25 text-[#2DD4BF] px-1 py-0.5 rounded font-medium">
            {part}
          </mark>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  const handleFlagUnfair = () => {
    setFlagged(true);
    toast({
      title: 'Feedback Recorded',
      description: 'Flagged evaluation for review. Our AI scoring model calibrates based on your feedback.',
      type: 'info'
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      role="region"
      aria-live="polite"
      aria-label={`Recall evaluation for ${conceptTitle}: Score ${score.toFixed(1)} out of 5, ${gradeLabel}`}
      className="p-5 sm:p-6 rounded-[16px] bg-[#171717] border border-[#262626] text-sm text-[#EDEDED] shadow-xl flex flex-col gap-5 w-full"
      id="evaluation-card"
    >
      {/* Header: Concept & Evaluation Notice */}
      <div className="flex items-center justify-between pb-3 border-b border-[#262626]">
        <div className="flex items-center gap-2">
          <Badge variant="teal" className="text-[10px] uppercase font-semibold">
            Recall Evaluation
          </Badge>
          <span className="text-xs font-semibold text-[#EDEDED] truncate">
            {conceptTitle}
          </span>
        </div>

        {evaluation.isHinted && (
          <Badge variant="caution" className="text-[10px]">
            Hint used
          </Badge>
        )}
      </div>

      {/* Centerpiece: Score Ring (0 to 5) & 3 Component Bars */}
      <div className="grid grid-cols-1 sm:grid-cols-12 gap-5 items-center py-2">
        {/* Left / Center: Score Ring from 0 to 5 with Grade Label */}
        <div className="sm:col-span-5 flex flex-col items-center justify-center gap-2">
          <div className="relative w-28 h-28 flex items-center justify-center">
            {/* Background Ring */}
            <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 96 96">
              <circle
                cx="48"
                cy="48"
                r={radius}
                className="stroke-[#262626]"
                strokeWidth="7"
                fill="transparent"
              />
              {/* Animated Progress Ring */}
              <circle
                cx="48"
                cy="48"
                r={radius}
                stroke={ringColor}
                strokeWidth="7"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                style={{ transition: 'stroke-dashoffset 0.8s ease-out' }}
              />
            </svg>

            {/* Score Text in Center */}
            <div className="absolute inset-0 flex flex-col items-center justify-center select-none">
              <span className="text-2xl font-bold tracking-tight text-[#EDEDED] font-mono leading-none">
                {score.toFixed(1)}
              </span>
              <span className="text-[11px] text-[#737373] font-mono mt-0.5">
                / 5.0
              </span>
            </div>
          </div>

          {/* Qualitative Grade Label Badge: Strong, Partial, or Needs work */}
          <span
            className={cn(
              "px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border",
              isStrong && "bg-[#34D399]/15 text-[#34D399] border-[#34D399]/30",
              isPartial && "bg-[#FBBF24]/15 text-[#FBBF24] border-[#FBBF24]/30",
              isNeedsWork && "bg-[#F87171]/15 text-[#F87171] border-[#F87171]/30"
            )}
            id="evaluation-grade-label"
          >
            {gradeLabel}
          </span>
        </div>

        {/* Right: Three Small Bars with Explanatory Tooltips */}
        <div className="sm:col-span-7 flex flex-col gap-3 justify-center pl-0 sm:pl-4 sm:border-l border-[#262626]">
          {/* Bar 1: Meaning match (semantic similarity) */}
          <div className="flex flex-col gap-1">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-[#A3A3A3]">
                <span>Meaning match</span>
                <Tooltip content="Measures conceptual alignment with your notes regardless of exact phrasing.">
                  <span className="text-[#737373] hover:text-[#EDEDED] cursor-help">
                    <Info size={11} />
                  </span>
                </Tooltip>
              </div>
              <span className="font-mono text-xs text-[#EDEDED] font-medium">
                {evaluation.meaningMatchScore}%
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-[#111111] border border-[#262626] overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${evaluation.meaningMatchScore}%` }}
                transition={{ duration: 0.6, delay: 0.1 }}
                className="h-full bg-[#2DD4BF] rounded-full"
              />
            </div>
          </div>

          {/* Bar 2: Key terms covered (keyword coverage) */}
          <div className="flex flex-col gap-1">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-[#A3A3A3]">
                <span>Key terms covered</span>
                <Tooltip content="Measures which essential vocabulary words from your notes were correctly mentioned.">
                  <span className="text-[#737373] hover:text-[#EDEDED] cursor-help">
                    <Info size={11} />
                  </span>
                </Tooltip>
              </div>
              <span className="font-mono text-xs text-[#EDEDED] font-medium">
                {evaluation.keyTermsCoveredScore}%
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-[#111111] border border-[#262626] overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${evaluation.keyTermsCoveredScore}%` }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="h-full bg-[#34D399] rounded-full"
              />
            </div>
          </div>

          {/* Bar 3: Tutor judgement (AI judge) */}
          <div className="flex flex-col gap-1">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-[#A3A3A3]">
                <span>Tutor judgement</span>
                <Tooltip content="Evaluates technical depth, causal relationships, and absence of misconceptions.">
                  <span className="text-[#737373] hover:text-[#EDEDED] cursor-help">
                    <Info size={11} />
                  </span>
                </Tooltip>
              </div>
              <span className="font-mono text-xs text-[#EDEDED] font-medium">
                {evaluation.tutorJudgementScore}%
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-[#111111] border border-[#262626] overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${evaluation.tutorJudgementScore}%` }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="h-full bg-[#FBBF24] rounded-full"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Three Qualitative Text Blocks (Calm wording; hidden if empty) */}
      <div className="flex flex-col gap-2.5 pt-2 border-t border-[#262626]">
        {/* Block 1: What you got right */}
        {evaluation.whatYouGotRight.length > 0 && (
          <div className="p-3 rounded-[10px] bg-[#34D399]/10 border border-[#34D399]/30 flex flex-col gap-1 text-xs text-[#EDEDED]">
            <div className="flex items-center gap-1.5 font-semibold text-[#34D399]">
              <CheckCircle2 size={14} className="shrink-0" />
              <span>What you got right</span>
            </div>
            <ul className="list-disc list-inside space-y-0.5 text-[#EDEDED] text-[12px] pl-1">
              {evaluation.whatYouGotRight.map((item, idx) => (
                <li key={idx} className="leading-relaxed">{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Block 2: What was missing */}
        {evaluation.whatWasMissing.length > 0 && (
          <div className="p-3 rounded-[10px] bg-[#FBBF24]/10 border border-[#FBBF24]/30 flex flex-col gap-1 text-xs text-[#EDEDED]">
            <div className="flex items-center gap-1.5 font-semibold text-[#FBBF24]">
              <AlertCircle size={14} className="shrink-0" />
              <span>What was missing</span>
            </div>
            <ul className="list-disc list-inside space-y-0.5 text-[#EDEDED] text-[12px] pl-1">
              {evaluation.whatWasMissing.map((item, idx) => (
                <li key={idx} className="leading-relaxed">{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Block 3: What was off */}
        {evaluation.whatWasOff.length > 0 && (
          <div className="p-3 rounded-[10px] bg-[#F87171]/10 border border-[#F87171]/30 flex flex-col gap-1 text-xs text-[#EDEDED]">
            <div className="flex items-center gap-1.5 font-semibold text-[#F87171]">
              <HelpCircle size={14} className="shrink-0" />
              <span>What was off</span>
            </div>
            <ul className="list-disc list-inside space-y-0.5 text-[#EDEDED] text-[12px] pl-1">
              {evaluation.whatWasOff.map((item, idx) => (
                <li key={idx} className="leading-relaxed">{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Collapsible "Compare with your notes" Section */}
      <div className="border border-[#262626] rounded-[10px] overflow-hidden bg-[#111111]">
        <button
          type="button"
          onClick={() => setShowNotesComparison(!showNotesComparison)}
          className="w-full px-3.5 py-2.5 flex items-center justify-between text-xs font-medium text-[#A3A3A3] hover:text-[#EDEDED] transition-colors"
          id="btn-toggle-compare-notes"
        >
          <span className="flex items-center gap-1.5">
            <span>Compare with your notes</span>
            <span className="text-[10px] text-[#737373]">
              ({evaluation.matchedKeywords.length} key term{evaluation.matchedKeywords.length === 1 ? '' : 's'} matched)
            </span>
          </span>
          {showNotesComparison ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>

        <AnimatePresence>
          {showNotesComparison && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-t border-[#262626] p-3.5 text-xs text-[#A3A3A3] leading-relaxed whitespace-pre-wrap bg-[#0E0E0E]"
            >
              <div className="text-[10px] text-[#737373] uppercase font-semibold tracking-wider mb-1.5">
                Source definition from notes:
              </div>
              <p className="text-xs text-[#EDEDED] leading-relaxed">
                {renderHighlightedDefinition(evaluation.sourceDefinition, evaluation.matchedKeywords)}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Schedule Line: "Next review: tomorrow" or "in 6 days" with tooltip */}
      <div className="flex items-center justify-between text-xs px-1 text-[#A3A3A3]">
        <div className="flex items-center gap-1.5">
          <Calendar size={13} className="text-[#2DD4BF]" />
          <span>Next review:</span>
          <strong className="text-[#EDEDED] font-semibold">{evaluation.nextReviewLabel}</strong>
          <Tooltip content="Weaker answers come back sooner.">
            <span className="text-[#737373] hover:text-[#EDEDED] cursor-help ml-0.5">
              <Info size={11} />
            </span>
          </Tooltip>
        </div>

        {/* Flag as unfair mock action */}
        {!flagged ? (
          <button
            type="button"
            onClick={handleFlagUnfair}
            className="text-[11px] text-[#737373] hover:text-[#EDEDED] flex items-center gap-1 transition-colors"
            title="Flag score as unfair or inaccurate"
          >
            <Flag size={11} />
            <span>Flag as unfair</span>
          </button>
        ) : (
          <span className="text-[10px] text-[#2DD4BF]">Feedback logged</span>
        )}
      </div>

      {/* Action Buttons: Next concept (primary), Try again (practice only) */}
      <div className="flex items-center justify-between pt-3 border-t border-[#262626]">
        <Button
          variant="secondary"
          size="sm"
          onClick={onTryAgain}
          className="text-xs"
          title="Try again (practice only, does not change the schedule)"
          id="btn-try-again-concept"
        >
          <RotateCcw size={12} className="mr-1.5" />
          <span>Try again</span>
          <span className="hidden sm:inline text-[10px] text-[#737373] ml-1">(practice)</span>
        </Button>

        <Button
          size="sm"
          onClick={onNextConcept}
          className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] text-xs font-semibold px-4"
          id="btn-next-concept"
        >
          <span>{isLastConcept ? 'View Session Summary' : 'Next concept'}</span>
          <ArrowRight size={13} className="ml-1.5" />
        </Button>
      </div>
    </motion.div>
  );
}
