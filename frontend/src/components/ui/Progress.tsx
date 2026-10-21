import React from 'react';
import { cn } from '../../utils/cn';

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number; // 0 to 100
  max?: number;
  variant?: 'teal' | 'success' | 'caution' | 'weak';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function Progress({
  value = 0,
  max = 100,
  variant = 'teal',
  size = 'md',
  showLabel = false,
  className,
  ...props
}: ProgressProps) {
  const percentage = Math.min(100, Math.max(0, Math.round((value / max) * 100)));

  return (
    <div className={cn('w-full flex flex-col gap-1.5', className)} {...props}>
      {showLabel && (
        <div className="flex items-center justify-between text-xs text-[#A3A3A3]">
          <span>Progress</span>
          <span className="font-medium text-[#EDEDED]">{percentage}%</span>
        </div>
      )}
      <div
        className={cn(
          'w-full bg-[#1F1F1F] rounded-full overflow-hidden border border-[#262626]',
          size === 'sm' && 'h-1.5',
          size === 'md' && 'h-2.5',
          size === 'lg' && 'h-4'
        )}
        role="progressbar"
        aria-valuenow={percentage}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className={cn(
            'h-full rounded-full transition-all duration-200 ease-out',
            variant === 'teal' && 'bg-[#2DD4BF]',
            variant === 'success' && 'bg-[#34D399]',
            variant === 'caution' && 'bg-[#FBBF24]',
            variant === 'weak' && 'bg-[#F87171]'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
