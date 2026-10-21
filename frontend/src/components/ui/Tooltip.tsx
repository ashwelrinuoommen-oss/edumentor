import React, { useState } from 'react';
import { cn } from '../../utils/cn';

export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactElement;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export function Tooltip({
  content,
  children,
  position = 'top',
  className
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div
          role="tooltip"
          className={cn(
            'absolute z-50 px-2.5 py-1 text-xs font-medium text-[#EDEDED] bg-[#1F1F1F] border border-[#262626] rounded-md shadow-md whitespace-nowrap pointer-events-none select-none transition-opacity duration-150',
            position === 'top' && 'bottom-full left-1/2 -translate-x-1/2 mb-1.5',
            position === 'bottom' && 'top-full left-1/2 -translate-x-1/2 mt-1.5',
            position === 'left' && 'right-full top-1/2 -translate-y-1/2 mr-1.5',
            position === 'right' && 'left-full top-1/2 -translate-y-1/2 ml-1.5',
            className
          )}
        >
          {content}
        </div>
      )}
    </div>
  );
}
