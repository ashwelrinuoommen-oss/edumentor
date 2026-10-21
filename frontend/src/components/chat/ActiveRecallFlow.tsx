import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Lightbulb, 
  Send, 
  HelpCircle, 
  RotateCcw, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle, 
  BookOpen, 
  Layers,
  ChevronRight,
  Info
} from 'lucide-react';
import { Concept, StudySession } from '../../services/mockService';
import { 
  evaluateStudentAnswer, 
  checkIfCopiedAnswer, 
  getFirstSentenceHint, 
  EvaluationResult 
} from '../../services/evaluationEngine';
import { EvaluationCard } from './EvaluationCard';
import { SessionSummaryCard, ConceptEvaluationRecord } from './SessionSummaryCard';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { useAppStore } from '../../store/useAppStore';
import { apiService } from '../../services/api';
import { cn } from '../../utils/cn';

export interface ActiveRecallFlowProps {
  session: StudySession;
  onUpdateSession: (updatedSession: StudySession) => void;
  onFinish?: () => void;
}

interface CompletedItem {
  concept: Concept;
  studentAnswer: string;
  evaluation: EvaluationResult;
}

export function ActiveRecallFlow({
  session,
  onUpdateSession,
  onFinish
}: ActiveRecallFlowProps) {
  const navigate = useNavigate();
  const { getSimulatedDate } = useAppStore();
  const simulatedDate = getSimulatedDate();

  const concepts = session.concepts || [];
  const totalConcepts = concepts.length;

  // Active recall step state
  const [currentConceptIndex, setCurrentConceptIndex] = useState<number>(0);
  const [completedItems, setCompletedItems] = useState<CompletedItem[]>([]);
  const [isSessionComplete, setIsSessionComplete] = useState<boolean>(false);

  // Current concept answering state
  const [inputText, setInputText] = useState<string>('');
  const [showHint, setShowHint] = useState<boolean>(false);
  const [isHinted, setIsHinted] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [copiedWarning, setCopiedWarning] = useState<string | null>(null);

  // Current active evaluation for the current concept
  const [currentEvaluation, setCurrentEvaluation] = useState<EvaluationResult | null>(null);

  const threadEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const currentConcept = concepts[currentConceptIndex] || concepts[0];

  // Auto-scroll when new question or evaluation arrives
  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConceptIndex, isSubmitting, currentEvaluation, isSessionComplete]);

  // Calculate progress percent
  const progressPercent = totalConcepts > 0 
    ? Math.round((currentConceptIndex / totalConcepts) * 100) 
    : 0;

  // Auto-grow textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 160);
    textarea.style.height = `${Math.max(48, newHeight)}px`;
  }, [inputText]);

  // Handle Submit Answer
  const handleCheckAnswer = () => {
    if (!inputText.trim() || isSubmitting) return;

    // Rule: Check if copied word-for-word from notes
    const isCopied = checkIfCopiedAnswer(currentConcept, inputText);
    if (isCopied) {
      setCopiedWarning("That looks copied. Try putting it in your own words.");
      return;
    }

    setCopiedWarning(null);
    setIsSubmitting(true);

    // Short typing indicator simulation (450ms)
    setTimeout(() => {
      const evalResult = evaluateStudentAnswer(currentConcept, inputText, isHinted, false, simulatedDate);
      setCurrentEvaluation(evalResult);
      setIsSubmitting(false);

      // Phase 11: Call POST /recall/evaluate
      apiService.evaluateRecall({
        concept_id: currentConcept.id,
        answer: inputText,
        hinted: isHinted
      }).catch(console.error);

      // Persist updated concept in session
      syncConceptUpdate(evalResult.updatedConcept);
    }, 450);
  };

  // Handle "I do not remember"
  const handleIDoNotRemember = () => {
    if (isSubmitting) return;
    setIsSubmitting(true);

    setTimeout(() => {
      const evalResult = evaluateStudentAnswer(currentConcept, 'I do not remember.', isHinted, true, simulatedDate);
      setCurrentEvaluation(evalResult);
      setIsSubmitting(false);

      // Phase 11: Call POST /recall/evaluate
      apiService.evaluateRecall({
        concept_id: currentConcept.id,
        answer: 'I do not remember.',
        hinted: isHinted
      }).catch(console.error);

      syncConceptUpdate(evalResult.updatedConcept);
    }, 350);
  };

  // Handle "Skip for now"
  const handleSkipForNow = () => {
    if (currentConceptIndex + 1 < totalConcepts) {
      advanceToNextConcept();
    } else {
      setIsSessionComplete(true);
    }
  };

  // Sync concept status and SM-2 update into parent session
  const syncConceptUpdate = (updatedConcept: Concept) => {
    const updatedConcepts = concepts.map(c => 
      c.id === updatedConcept.id ? updatedConcept : c
    );
    const updatedSession: StudySession = {
      ...session,
      concepts: updatedConcepts,
      currentConceptIndex: Math.min(currentConceptIndex + 1, totalConcepts - 1),
      updatedAt: new Date().toISOString()
    };
    onUpdateSession(updatedSession);
  };

  // Advance to Next Concept
  const advanceToNextConcept = () => {
    if (currentEvaluation) {
      setCompletedItems(prev => [
        ...prev,
        {
          concept: currentConcept,
          studentAnswer: inputText || (currentEvaluation.isDidNotRemember ? 'I do not remember.' : 'Skipped'),
          evaluation: currentEvaluation
        }
      ]);
    }

    // Reset current concept question state
    setInputText('');
    setShowHint(false);
    setIsHinted(false);
    setCopiedWarning(null);
    setCurrentEvaluation(null);

    if (currentConceptIndex + 1 < totalConcepts) {
      setCurrentConceptIndex(prev => prev + 1);
    } else {
      setIsSessionComplete(true);
    }
  };

  // "Try again" (Practice only, does not alter saved SM-2 schedule)
  const handleTryAgain = () => {
    setCurrentEvaluation(null);
    setInputText('');
    setCopiedWarning(null);
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 50);
  };

  // Final summary actions
  const handleReviewWeakNow = () => {
    // Find weak concepts (< 3.5 score)
    const weakConcepts = concepts.filter(c => c.status === 'weak' || c.status === 'review_due');
    if (weakConcepts.length > 0) {
      const weakIds = new Set(weakConcepts.map(c => c.id));
      const firstWeakIndex = concepts.findIndex(c => weakIds.has(c.id));
      if (firstWeakIndex >= 0) {
        setCurrentConceptIndex(firstWeakIndex);
        setIsSessionComplete(false);
        setCurrentEvaluation(null);
        setCompletedItems([]);
        return;
      }
    }
    // Fallback: restart from beginning
    setCurrentConceptIndex(0);
    setIsSessionComplete(false);
    setCurrentEvaluation(null);
  };

  const handleFinishForToday = () => {
    if (onFinish) {
      onFinish();
    } else {
      navigate('/progress');
    }
  };

  return (
    <div className="w-full flex flex-col gap-6" id="active-recall-flow">
      {/* Thread-Top Progress Bar */}
      <div className="sticky top-0 z-20 bg-[#0A0A0A]/95 backdrop-blur-md pt-2 pb-3 border-b border-[#262626] flex flex-col gap-2">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Badge variant="teal" className="text-[10px] font-mono">
              Recall Mode
            </Badge>
            <span className="text-[#EDEDED] font-semibold">
              {!isSessionComplete 
                ? `Concept ${currentConceptIndex + 1} of ${totalConcepts}: ${currentConcept?.title}`
                : 'Session Complete!'}
            </span>
          </div>

          <span className="text-xs font-mono text-[#A3A3A3]">
            {isSessionComplete ? '100%' : `${progressPercent}% complete`}
          </span>
        </div>

        {/* Teal Progress Bar */}
        <div className="w-full h-1.5 rounded-full bg-[#171717] border border-[#262626] overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: isSessionComplete ? '100%' : `${progressPercent}%` }}
            transition={{ duration: 0.3 }}
            className="h-full bg-[#2DD4BF] rounded-full"
          />
        </div>
      </div>

      {/* Previously Completed Concepts in this Session */}
      {completedItems.map((item, idx) => (
        <div key={idx} className="flex flex-col gap-4 opacity-75 hover:opacity-100 transition-opacity">
          {/* Question Message */}
          <div className="flex items-start gap-2.5 max-w-2xl">
            <div className="w-6 h-6 rounded-full bg-[#2DD4BF]/15 border border-[#2DD4BF]/30 flex items-center justify-center text-[#2DD4BF] shrink-0 mt-0.5">
              <Sparkles size={12} />
            </div>
            <div className="p-3.5 rounded-[14px] bg-[#111111] border border-[#262626] text-xs text-[#EDEDED]">
              <span className="font-semibold text-[#2DD4BF]">Concept {item.concept.orderIndex} of {totalConcepts}:</span>{' '}
              In your own words, what is {item.concept.title}?
            </div>
          </div>

          {/* Student Answer */}
          <div className="self-end max-w-xl p-3.5 rounded-[14px] bg-[#171717] border border-[#262626] text-xs text-[#EDEDED]">
            {item.studentAnswer}
          </div>

          {/* Evaluation Card Summary */}
          <div className="max-w-2xl">
            <EvaluationCard
              evaluation={item.evaluation}
              conceptTitle={item.concept.title}
              isLastConcept={idx === totalConcepts - 1}
              onNextConcept={() => {}}
              onTryAgain={() => {}}
            />
          </div>
        </div>
      ))}

      {/* Active Question & Active Answering Sequence (if not finished) */}
      {!isSessionComplete && (
        <div className="flex flex-col gap-5">
          {/* Mentor Question Message */}
          <motion.div
            key={`question-${currentConcept.id}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-start gap-1.5 self-start max-w-2xl w-full"
          >
            <div className="flex items-center gap-2 text-[11px] text-[#737373] px-1">
              <span className="text-[#2DD4BF] font-semibold">EduMentor</span>
              <span>•</span>
              <span>Recall question</span>
            </div>

            <div className="p-4 sm:p-5 rounded-[16px] bg-[#111111] border border-[#262626] text-sm text-[#EDEDED] shadow-lg flex flex-col gap-3.5 w-full">
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-[#2DD4BF] font-semibold uppercase tracking-wider">
                  Concept {currentConceptIndex + 1} of {totalConcepts}
                </span>
                <span className="text-[11px] text-[#737373]">
                  Definition is hidden
                </span>
              </div>

              {/* Mandatory Prompt Copy: "Concept X of Y: In your own words, what is a {concept}?" */}
              <h3 className="text-base sm:text-lg font-semibold text-[#EDEDED] leading-snug">
                In your own words, what is {currentConcept.title}?
              </h3>

              {/* Hint System: Button reveals first sentence only and marks attempt as 'hinted' */}
              <div className="pt-2 border-t border-[#262626]/70 flex flex-col gap-2">
                {!showHint ? (
                  <button
                    type="button"
                    onClick={() => {
                      setShowHint(true);
                      setIsHinted(true);
                    }}
                    className="inline-flex items-center gap-1.5 text-xs text-[#2DD4BF] hover:text-[#14B8A6] self-start transition-colors p-1"
                    id="btn-show-hint"
                  >
                    <Lightbulb size={13} />
                    <span>Need a hint? (reveals first sentence)</span>
                  </button>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="p-3 rounded-[8px] bg-[#2DD4BF]/10 border border-[#2DD4BF]/25 text-xs text-[#EDEDED] flex flex-col gap-1"
                    id="box-hint-revealed"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold text-[#2DD4BF] uppercase flex items-center gap-1">
                        <Lightbulb size={11} />
                        First sentence from your notes (Hinted):
                      </span>
                      <Badge variant="caution" className="text-[9px] py-0">Hinted attempt</Badge>
                    </div>
                    <p className="text-xs text-[#EDEDED] italic leading-relaxed">
                      "{getFirstSentenceHint(currentConcept)}"
                    </p>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>

          {/* Student Answering / Evaluation Display */}
          {currentEvaluation ? (
            /* Evaluation Card Displayed After Submit */
            <div className="max-w-2xl w-full">
              {/* Echoed Student Answer */}
              <div className="flex items-center justify-end mb-3">
                <div className="p-3.5 rounded-[14px] bg-[#171717] border border-[#262626] text-xs text-[#EDEDED] max-w-xl">
                  {inputText || (currentEvaluation.isDidNotRemember ? 'I do not remember.' : 'Skipped')}
                </div>
              </div>

              <EvaluationCard
                evaluation={currentEvaluation}
                conceptTitle={currentConcept.title}
                isLastConcept={currentConceptIndex === totalConcepts - 1}
                onNextConcept={advanceToNextConcept}
                onTryAgain={handleTryAgain}
              />
            </div>
          ) : isSubmitting ? (
            /* Short Typing Indicator */
            <div className="flex items-center gap-2 p-3 rounded-[12px] bg-[#111111] border border-[#262626] text-xs text-[#A3A3A3] w-fit">
              <div className="w-4 h-4 rounded-full bg-[#2DD4BF]/20 flex items-center justify-center text-[#2DD4BF]">
                <Sparkles size={11} className="animate-spin" />
              </div>
              <span>EduMentor is evaluating your explanation...</span>
            </div>
          ) : (
            /* Active Composer in Recall Mode */
            <div className="sticky bottom-4 w-full bg-[#171717] rounded-[24px] border border-[#262626] p-3 sm:p-4 flex flex-col gap-2.5 shadow-2xl focus-within:border-[#2DD4BF]">
              {/* Copied Answer Warning Notice */}
              {copiedWarning && (
                <div className="p-2.5 rounded-[8px] bg-[#FBBF24]/15 border border-[#FBBF24]/30 text-xs text-[#FBBF24] flex items-center gap-2 animate-shake">
                  <AlertCircle size={14} className="shrink-0" />
                  <span>{copiedWarning}</span>
                </div>
              )}

              {/* Textarea: Placeholder becomes "Explain it from memory..." */}
              <textarea
                ref={textareaRef}
                value={inputText}
                onChange={(e) => {
                  setInputText(e.target.value);
                  setCopiedWarning(null);
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleCheckAnswer();
                  }
                }}
                placeholder="Explain it from memory..."
                className="w-full bg-transparent text-[#EDEDED] text-sm placeholder-[#737373] outline-none resize-none leading-relaxed px-1 min-h-[50px]"
                id="recall-composer-textarea"
              />

              {/* Composer Controls Row: "Skip for now", "I do not remember", and "Check my answer" */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-[#262626]/70">
                <div className="flex items-center gap-3">
                  {/* Skip for now text button */}
                  <button
                    type="button"
                    onClick={handleSkipForNow}
                    className="text-xs text-[#737373] hover:text-[#EDEDED] transition-colors"
                    id="btn-skip-concept"
                  >
                    Skip for now
                  </button>

                  {/* "I do not remember" button: scores zero, non-shaming */}
                  <button
                    type="button"
                    onClick={handleIDoNotRemember}
                    className="text-xs text-[#FBBF24] hover:text-[#f59e0b] px-2.5 py-1 rounded-full bg-[#FBBF24]/10 border border-[#FBBF24]/20 transition-colors"
                    id="btn-i-do-not-remember"
                  >
                    I do not remember
                  </button>
                </div>

                {/* Send Button: Label becomes "Check my answer" (teal) */}
                <Button
                  size="sm"
                  disabled={!inputText.trim() || isSubmitting}
                  onClick={handleCheckAnswer}
                  className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] text-xs font-semibold px-4 disabled:opacity-30 disabled:cursor-not-allowed"
                  id="btn-check-my-answer"
                >
                  <span>Check my answer</span>
                  <Send size={12} className="ml-1.5" />
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Final Summary Card (After Last Concept) */}
      {isSessionComplete && (
        <div className="flex flex-col gap-4">
          <SessionSummaryCard
            records={completedItems.map(item => ({
              concept: item.concept,
              evaluation: item.evaluation
            }))}
            sessionTitle={session.title}
            onReviewWeakNow={handleReviewWeakNow}
            onFinishForToday={handleFinishForToday}
          />
        </div>
      )}

      <div ref={threadEndRef} />
    </div>
  );
}
