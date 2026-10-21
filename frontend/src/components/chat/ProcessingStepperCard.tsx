import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  CheckCircle2, 
  Loader2, 
  AlertCircle, 
  RotateCcw, 
  X, 
  Edit3, 
  Clock, 
  ArrowRight,
  BookOpen,
  Layers,
  FileText
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { cn } from '../../utils/cn';

export interface StepItem {
  id: number;
  label: string;
  sublabel?: string;
  durationMs: number;
}

export const DEFAULT_PROCESSING_STEPS: StepItem[] = [
  { 
    id: 1, 
    label: 'Reading your notes', 
    sublabel: 'Tokenizing text and scanning structural sections',
    durationMs: 1100 
  },
  { 
    id: 2, 
    label: 'Finding key concepts', 
    sublabel: 'Identifying core definitions and terminology',
    durationMs: 1600 
  },
  { 
    id: 3, 
    label: 'Mapping what depends on what', 
    sublabel: 'Constructing topological dependency graph',
    durationMs: 1400 
  },
  { 
    id: 4, 
    label: 'Building your study path', 
    sublabel: 'Sequencing concepts into adaptive recall queue',
    durationMs: 1100 
  }
];

export interface ProcessingStepperCardProps {
  onComplete: () => void;
  onCancel: () => void;
  onEditNotes: () => void;
  /**
   * Simulation overrides for testing edge cases
   */
  simulateErrorStep?: number | null; // 1 to 4
  simulateZeroConcepts?: boolean;
  notesTitle?: string;
}

export function ProcessingStepperCard({
  onComplete,
  onCancel,
  onEditNotes,
  simulateErrorStep = null,
  simulateZeroConcepts = false,
  notesTitle = 'Study Session'
}: ProcessingStepperCardProps) {
  // Step states: 0 = not started, 1..4 = active step, 5 = all complete
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(1);
  const [stepStatuses, setStepStatuses] = useState<Record<number, 'pending' | 'running' | 'done' | 'failed'>>({
    1: 'running',
    2: 'pending',
    3: 'pending',
    4: 'pending'
  });
  
  // Elapsed timer in milliseconds
  const [elapsedMs, setElapsedMs] = useState<number>(0);
  const [isCancelled, setIsCancelled] = useState<boolean>(false);
  const [failedStep, setFailedStep] = useState<number | null>(null);
  const [zeroConceptsError, setZeroConceptsError] = useState<boolean>(false);
  const [stepDurations, setStepDurations] = useState<Record<number, number>>({});

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const stepTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(Date.now());
  const pausedElapsedRef = useRef<number>(0);

  // Live timer interval
  useEffect(() => {
    if (isCancelled || failedStep !== null || zeroConceptsError || currentStepIndex > 4) {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }

    startTimeRef.current = Date.now() - pausedElapsedRef.current;
    timerRef.current = setInterval(() => {
      setElapsedMs(Date.now() - startTimeRef.current);
    }, 50);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isCancelled, failedStep, zeroConceptsError, currentStepIndex]);

  // Stepper state machine execution
  useEffect(() => {
    if (isCancelled || failedStep !== null || zeroConceptsError) {
      if (stepTimeoutRef.current) clearTimeout(stepTimeoutRef.current);
      return;
    }

    // If all 4 steps completed
    if (currentStepIndex > 4) {
      const finishTimeout = setTimeout(() => {
        onComplete();
      }, 400);
      return () => clearTimeout(finishTimeout);
    }

    // Set current step to running
    setStepStatuses(prev => ({
      ...prev,
      [currentStepIndex]: 'running'
    }));

    const stepConfig = DEFAULT_PROCESSING_STEPS.find(s => s.id === currentStepIndex);
    const duration = stepConfig ? stepConfig.durationMs : 1200;

    stepTimeoutRef.current = setTimeout(() => {
      // Check for zero concepts trigger (typically occurs at step 2 when finding concepts)
      if (simulateZeroConcepts && currentStepIndex === 2) {
        setStepStatuses(prev => ({
          ...prev,
          [currentStepIndex]: 'failed'
        }));
        setZeroConceptsError(true);
        return;
      }

      // Check for step error simulation
      if (simulateErrorStep && currentStepIndex === simulateErrorStep) {
        setStepStatuses(prev => ({
          ...prev,
          [currentStepIndex]: 'failed'
        }));
        setFailedStep(currentStepIndex);
        return;
      }

      // Mark current step as done and record duration
      setStepStatuses(prev => ({
        ...prev,
        [currentStepIndex]: 'done'
      }));
      setStepDurations(prev => ({
        ...prev,
        [currentStepIndex]: duration
      }));

      // Advance to next step
      setCurrentStepIndex(prev => prev + 1);
    }, duration);

    return () => {
      if (stepTimeoutRef.current) clearTimeout(stepTimeoutRef.current);
    };
  }, [currentStepIndex, isCancelled, failedStep, zeroConceptsError, simulateErrorStep, simulateZeroConcepts]);

  // Format timer display: e.g. "2.4s"
  const formattedSeconds = (elapsedMs / 1000).toFixed(1) + 's';

  // Handle Cancel
  const handleCancelClick = () => {
    setIsCancelled(true);
    pausedElapsedRef.current = elapsedMs;
    if (stepTimeoutRef.current) clearTimeout(stepTimeoutRef.current);
    if (timerRef.current) clearInterval(timerRef.current);
    onCancel();
  };

  // Handle Resume after cancel
  const handleResumeClick = () => {
    setIsCancelled(false);
  };

  // Handle Retry / Try Again
  const handleRetryClick = () => {
    setFailedStep(null);
    setZeroConceptsError(false);
    setIsCancelled(false);
    setElapsedMs(0);
    pausedElapsedRef.current = 0;
    setCurrentStepIndex(1);
    setStepStatuses({
      1: 'running',
      2: 'pending',
      3: 'pending',
      4: 'pending'
    });
  };

  return (
    <div className="flex flex-col items-start gap-1.5 self-start max-w-2xl w-full">
      {/* Mentor Identity Row */}
      <div className="flex items-center gap-2 text-[11px] text-[#737373] px-1">
        <div className="w-5 h-5 rounded-full bg-[#2DD4BF]/15 border border-[#2DD4BF]/30 flex items-center justify-center text-[#2DD4BF]">
          <Sparkles size={11} />
        </div>
        <span className="text-[#2DD4BF] font-semibold">EduMentor</span>
        <span>•</span>
        <span className="flex items-center gap-1">
          {currentStepIndex <= 4 && !isCancelled && !failedStep && !zeroConceptsError ? (
            <span className="text-[#2DD4BF] flex items-center gap-1 font-mono text-[10px]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#2DD4BF] animate-pulse" />
              Processing notes
            </span>
          ) : zeroConceptsError || failedStep ? (
            <span className="text-[#F87171] font-mono text-[10px]">Processing error</span>
          ) : isCancelled ? (
            <span className="text-[#FBBF24] font-mono text-[10px]">Paused</span>
          ) : (
            <span>Ready</span>
          )}
        </span>
      </div>

      {/* Main Live Stepper Card */}
      <div 
        className={cn(
          "p-4 sm:p-5 rounded-[14px] bg-[#171717] border border-[#262626] text-sm text-[#EDEDED] shadow-xl w-full transition-all",
          failedStep !== null && "border-[#F87171]/40 bg-[#171717]",
          zeroConceptsError && "border-[#F87171]/40 bg-[#171717]"
        )}
        id="processing-stepper-card"
      >
        {/* Card Header: Title, Live Elapsed Timer & Cancel Button */}
        <div className="flex items-center justify-between pb-3.5 mb-3.5 border-b border-[#262626]">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-[8px] bg-[#111111] border border-[#262626] flex items-center justify-center text-[#2DD4BF]">
              <Layers size={15} />
            </div>
            <div>
              <h3 className="text-xs sm:text-sm font-semibold text-[#EDEDED]">
                {zeroConceptsError 
                  ? 'Concept Extraction Alert' 
                  : failedStep 
                  ? 'Processing Interrupted' 
                  : currentStepIndex > 4 
                  ? 'Study Path Complete' 
                  : 'Analyzing Notes & Generating Path'}
              </h3>
              <p className="text-[11px] text-[#737373]">
                {notesTitle}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Live Elapsed Timer */}
            <div 
              className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium border transition-colors",
                failedStep || zeroConceptsError
                  ? "bg-[#F87171]/10 text-[#F87171] border-[#F87171]/30"
                  : currentStepIndex > 4
                  ? "bg-[#34D399]/10 text-[#34D399] border-[#34D399]/30"
                  : "bg-[#111111] text-[#2DD4BF] border-[#262626]"
              )}
              title="Elapsed Processing Time"
              id="processing-timer"
            >
              <Clock size={12} className={currentStepIndex <= 4 && !isCancelled && !failedStep && !zeroConceptsError ? "animate-spin" : ""} />
              <span>{formattedSeconds}</span>
            </div>

            {/* Cancel Button (Visible while processing) */}
            {currentStepIndex <= 4 && !isCancelled && !failedStep && !zeroConceptsError && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancelClick}
                className="text-xs h-7 px-2.5 text-[#A3A3A3] hover:text-[#EDEDED] border-[#262626] hover:bg-[#1F1F1F]"
                id="btn-cancel-processing"
              >
                <X size={12} className="mr-1" />
                <span>Cancel</span>
              </Button>
            )}
          </div>
        </div>

        {/* Four Sequential Stepper Items */}
        <div className="flex flex-col gap-2 relative">
          {DEFAULT_PROCESSING_STEPS.map((step, idx) => {
            const status = stepStatuses[step.id];
            const isLast = idx === DEFAULT_PROCESSING_STEPS.length - 1;
            const isRunning = status === 'running';
            const isDone = status === 'done';
            const isFailed = status === 'failed';
            const isPending = status === 'pending';

            return (
              <div
                key={step.id}
                className={cn(
                  "relative rounded-[10px] p-3 border transition-all flex items-center justify-between overflow-hidden",
                  // Running State with subtle shimmer
                  isRunning && "bg-[#111111] border-[#2DD4BF]/40 shadow-sm animate-shimmer",
                  // Done State
                  isDone && "bg-[#111111]/60 border-[#262626]",
                  // Failed State
                  isFailed && "bg-[#F87171]/10 border-[#F87171]/40 text-[#F87171]",
                  // Pending State
                  isPending && "bg-transparent border-transparent opacity-50"
                )}
                id={`stepper-step-${step.id}`}
              >
                {/* Left: Indicator & Labels */}
                <div className="flex items-center gap-3 z-10 min-w-0">
                  {/* Status Indicator Circle */}
                  <div className="shrink-0 flex items-center justify-center w-6 h-6 rounded-full">
                    {isDone && (
                      <div className="w-5 h-5 rounded-full bg-[#2DD4BF]/20 text-[#2DD4BF] flex items-center justify-center">
                        <CheckCircle2 size={16} />
                      </div>
                    )}
                    {isRunning && (
                      <div className="w-5 h-5 rounded-full bg-[#2DD4BF]/20 text-[#2DD4BF] flex items-center justify-center">
                        <Loader2 size={14} className="animate-spin" />
                      </div>
                    )}
                    {isFailed && (
                      <div className="w-5 h-5 rounded-full bg-[#F87171]/20 text-[#F87171] flex items-center justify-center">
                        <AlertCircle size={15} />
                      </div>
                    )}
                    {isPending && (
                      <div className="w-2.5 h-2.5 rounded-full bg-[#383838]" />
                    )}
                  </div>

                  {/* Text details */}
                  <div className="flex flex-col min-w-0">
                    <span 
                      className={cn(
                        "text-xs sm:text-sm font-medium tracking-tight truncate",
                        isRunning && "text-[#EDEDED] font-semibold",
                        isDone && "text-[#EDEDED]",
                        isFailed && "text-[#F87171] font-semibold",
                        isPending && "text-[#737373]"
                      )}
                    >
                      {step.label}
                    </span>

                    {/* Subtitle helper */}
                    {(isRunning || isDone) && step.sublabel && (
                      <span className="text-[11px] text-[#737373] truncate">
                        {step.sublabel}
                      </span>
                    )}
                  </div>
                </div>

                {/* Right: State Chip or Step Duration */}
                <div className="z-10 shrink-0 ml-2">
                  {isDone && stepDurations[step.id] && (
                    <span className="text-[10px] font-mono text-[#737373]">
                      {(stepDurations[step.id] / 1000).toFixed(1)}s
                    </span>
                  )}
                  {isRunning && (
                    <Badge variant="teal" className="text-[10px] py-0 px-2 animate-pulse">
                      Running
                    </Badge>
                  )}
                  {isFailed && (
                    <Badge variant="weak" className="text-[10px] py-0 px-2">
                      Failed
                    </Badge>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Error State: Failed Step with Plain Message & "Try again" Button */}
        {failedStep !== null && !zeroConceptsError && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-3.5 rounded-[10px] bg-[#F87171]/10 border border-[#F87171]/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
            id="error-failed-step"
          >
            <div className="flex items-start gap-2.5 text-xs text-[#EDEDED]">
              <AlertCircle size={16} className="text-[#F87171] shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-[#F87171]">
                  Step {failedStep} failed to complete.
                </span>
                <p className="text-[#A3A3A3] text-[11px] mt-0.5">
                  An unexpected error occurred while processing this step. Please check your network and retry.
                </p>
              </div>
            </div>

            <Button
              size="sm"
              onClick={handleRetryClick}
              className="bg-[#F87171] text-[#0A0A0A] hover:bg-[#ef4444] text-xs shrink-0 self-end sm:self-auto font-medium"
              id="btn-retry-failed-step"
            >
              <RotateCcw size={12} className="mr-1.5" />
              <span>Try again</span>
            </Button>
          </motion.div>
        )}

        {/* Error State: Zero Concepts Found ("I could not find clear concepts in this text") */}
        {zeroConceptsError && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 rounded-[10px] bg-[#F87171]/10 border border-[#F87171]/30 flex flex-col gap-3"
            id="error-zero-concepts"
          >
            <div className="flex items-start gap-3">
              <AlertCircle size={18} className="text-[#F87171] shrink-0 mt-0.5" />
              <div className="flex flex-col gap-1 text-xs">
                <span className="font-semibold text-sm text-[#F87171]">
                  I could not find clear concepts in this text
                </span>
                <p className="text-[#EDEDED] text-xs leading-relaxed">
                  EduMentor looks for core definitions, distinct topics, or prerequisite concepts. 
                  Your notes may be too brief, fragmented, or unformatted.
                </p>
                <div className="p-2.5 rounded-[6px] bg-[#111111] border border-[#262626] text-[11px] text-[#A3A3A3] mt-1">
                  💡 <strong className="text-[#EDEDED]">Advice:</strong> Add more detail, include section headers or bulleted definitions, or paste a chapter summary to help identify key concepts.
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-1 border-t border-[#F87171]/20">
              <Button
                variant="secondary"
                size="sm"
                onClick={onEditNotes}
                className="text-xs"
                id="btn-edit-notes-zero-concepts"
              >
                <Edit3 size={12} className="mr-1.5" />
                <span>Edit notes</span>
              </Button>
              <Button
                size="sm"
                onClick={handleRetryClick}
                className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] text-xs font-medium"
                id="btn-retry-zero-concepts"
              >
                <RotateCcw size={12} className="mr-1.5" />
                <span>Try again</span>
              </Button>
            </div>
          </motion.div>
        )}

        {/* Cancelled State View */}
        {isCancelled && !failedStep && !zeroConceptsError && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-3.5 rounded-[10px] bg-[#111111] border border-[#262626] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
            id="view-cancelled-processing"
          >
            <div className="flex items-start gap-2.5 text-xs text-[#EDEDED]">
              <Clock size={16} className="text-[#FBBF24] shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-[#EDEDED]">
                  Processing paused at step {currentStepIndex}.
                </span>
                <p className="text-[#737373] text-[11px] mt-0.5">
                  Your notes and attachments have been preserved.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 self-end sm:self-auto">
              <Button
                variant="secondary"
                size="sm"
                onClick={onEditNotes}
                className="text-xs"
                id="btn-edit-notes-cancelled"
              >
                <Edit3 size={12} className="mr-1" />
                <span>Edit notes</span>
              </Button>
              <Button
                size="sm"
                onClick={handleResumeClick}
                className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] text-xs font-medium"
                id="btn-resume-processing"
              >
                <span>Resume</span>
                <ArrowRight size={12} className="ml-1" />
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
