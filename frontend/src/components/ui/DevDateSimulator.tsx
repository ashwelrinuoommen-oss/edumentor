import React from 'react';
import { Calendar, FastForward, RotateCcw, Clock } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { sessionService } from '../../services/mockService';
import { cn } from '../../utils/cn';

export function DevDateSimulator({ className }: { className?: string }) {
  const { simulatedDaysOffset, advanceSimulatedDays, resetSimulatedDays, getSimulatedDate } = useAppStore();
  const simulatedDate = getSimulatedDate();
  const dueItems = sessionService.getDueReviewConcepts(simulatedDate);
  const dueCount = dueItems.length;

  const formattedDate = simulatedDate.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });

  return (
    <div
      className={cn(
        'inline-flex flex-wrap items-center gap-2 p-1.5 px-3 rounded-[12px] bg-[#171717] border border-[#262626] text-xs shadow-md',
        className
      )}
      id="dev-date-simulator"
    >
      <div className="flex items-center gap-1.5 text-[#A3A3A3]">
        <Calendar size={13} className="text-[#2DD4BF]" />
        <span className="text-[11px] font-mono text-[#737373]">Dev Toggle:</span>
        <strong className="text-[#EDEDED] font-semibold font-mono">{formattedDate}</strong>
        {simulatedDaysOffset > 0 && (
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-[#2DD4BF]/20 text-[#2DD4BF] font-mono font-bold">
            +{simulatedDaysOffset}d
          </span>
        )}
      </div>

      <div className="h-3 w-px bg-[#262626] mx-0.5" />

      {/* Quick Advance Buttons */}
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={() => advanceSimulatedDays(1)}
          className="px-2 py-0.5 rounded bg-[#111111] hover:bg-[#262626] text-[#EDEDED] border border-[#262626] hover:border-[#2DD4BF]/50 text-[11px] font-mono transition-colors"
          title="Fast-forward 1 day to trigger tomorrow's SM-2 reviews"
          id="btn-dev-plus-1-day"
        >
          +1 Day
        </button>

        <button
          type="button"
          onClick={() => advanceSimulatedDays(3)}
          className="px-2 py-0.5 rounded bg-[#111111] hover:bg-[#262626] text-[#EDEDED] border border-[#262626] hover:border-[#2DD4BF]/50 text-[11px] font-mono transition-colors"
          title="Fast-forward 3 days"
          id="btn-dev-plus-3-days"
        >
          +3 Days
        </button>

        <button
          type="button"
          onClick={() => advanceSimulatedDays(7)}
          className="px-2 py-0.5 rounded bg-[#111111] hover:bg-[#262626] text-[#EDEDED] border border-[#262626] hover:border-[#2DD4BF]/50 text-[11px] font-mono transition-colors"
          title="Fast-forward 7 days to trigger weekly reviews"
          id="btn-dev-plus-7-days"
        >
          +7 Days
        </button>

        {simulatedDaysOffset > 0 && (
          <button
            type="button"
            onClick={resetSimulatedDays}
            className="p-1 rounded bg-[#111111] hover:bg-[#F87171]/20 text-[#737373] hover:text-[#F87171] border border-[#262626] transition-colors"
            title="Reset to today"
            id="btn-dev-reset-date"
          >
            <RotateCcw size={11} />
          </button>
        )}
      </div>

      <div className="h-3 w-px bg-[#262626] mx-0.5" />

      {/* Live Due Count Indicator */}
      <span
        className={cn(
          'text-[10px] font-semibold px-2 py-0.5 rounded-full border',
          dueCount > 0
            ? 'bg-[#FBBF24]/15 text-[#FBBF24] border-[#FBBF24]/30'
            : 'bg-[#34D399]/15 text-[#34D399] border-[#34D399]/30'
        )}
      >
        {dueCount} due
      </span>
    </div>
  );
}
