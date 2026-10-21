import React from 'react';
import { cn } from '../../utils/cn';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

/**
 * Base shimmer skeleton with modern dark mode styling
 */
export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-[8px] bg-[#1E1E1E]/80 border border-[#262626]/40',
        className
      )}
      {...props}
    />
  );
}

/**
 * Skeleton list item for sessions and queue lists
 */
export function SkeletonListItem({ className }: { className?: string }) {
  return (
    <div className={cn('p-3 rounded-[10px] bg-[#141414] border border-[#262626] flex items-center gap-3 animate-pulse', className)}>
      <Skeleton className="w-8 h-8 rounded-full shrink-0" />
      <div className="flex-1 flex flex-col gap-1.5 min-w-0">
        <Skeleton className="h-3.5 w-3/4" />
        <Skeleton className="h-2.5 w-1/2" />
      </div>
      <Skeleton className="w-12 h-5 rounded-full shrink-0" />
    </div>
  );
}

/**
 * Skeleton card for stat cards and concept drawers
 */
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('p-5 rounded-[14px] bg-[#171717] border border-[#262626] flex flex-col gap-3 animate-pulse shadow-sm', className)}>
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-1/3" />
        <Skeleton className="w-6 h-6 rounded-full" />
      </div>
      <Skeleton className="h-7 w-1/2 my-1" />
      <Skeleton className="h-2.5 w-4/5" />
    </div>
  );
}

/**
 * Skeleton table rows for Progress matrix
 */
export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="w-full flex flex-col gap-2">
      <div className="h-9 w-full bg-[#171717] rounded-[8px] border border-[#262626]/80 flex items-center px-4 gap-4">
        <Skeleton className="h-3 w-1/4" />
        <Skeleton className="h-3 w-1/5" />
        <Skeleton className="h-3 w-16 ml-auto" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="h-12 w-full bg-[#141414] rounded-[8px] border border-[#262626] flex items-center px-4 gap-4 animate-pulse"
        >
          <Skeleton className="h-3.5 w-1/3" />
          <Skeleton className="h-3 w-1/4" />
          <Skeleton className="h-5 w-14 rounded-full ml-auto" />
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
      ))}
    </div>
  );
}
