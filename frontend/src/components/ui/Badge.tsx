import React from 'react';
import { cn } from '../../utils/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'teal' | 'success' | 'caution' | 'weak' | 'neutral';
}

export function Badge({ 
  className, 
  variant = 'neutral', 
  children, 
  ...props 
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-medium rounded-full border select-none transition-colors duration-150',
        variant === 'teal' && 'bg-[#2DD4BF]/10 text-[#2DD4BF] border-[#2DD4BF]/30',
        variant === 'success' && 'bg-[#34D399]/10 text-[#34D399] border-[#34D399]/30',
        variant === 'caution' && 'bg-[#FBBF24]/10 text-[#FBBF24] border-[#FBBF24]/30',
        variant === 'weak' && 'bg-[#F87171]/10 text-[#F87171] border-[#F87171]/30',
        variant === 'neutral' && 'bg-[#1F1F1F] text-[#A3A3A3] border-[#262626]',
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
