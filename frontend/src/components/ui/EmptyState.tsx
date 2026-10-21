import React from 'react';
import { LucideIcon } from 'lucide-react';
import { Button } from './Button';
import { cn } from '../../utils/cn';

export interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  actionIcon?: LucideIcon;
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  actionIcon: ActionIcon,
  className
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'p-8 rounded-[16px] bg-[#141414] border border-[#262626] text-center flex flex-col items-center justify-center gap-3.5',
        className
      )}
      role="status"
    >
      {Icon && (
        <div className="w-12 h-12 rounded-full bg-[#1A1A1A] border border-[#262626] flex items-center justify-center text-[#2DD4BF] shrink-0 mb-1">
          <Icon size={22} />
        </div>
      )}

      <div className="flex flex-col gap-1 max-w-sm">
        <h3 className="text-sm font-semibold text-[#EDEDED] tracking-tight">
          {title}
        </h3>
        <p className="text-xs text-[#A3A3A3] leading-relaxed">
          {description}
        </p>
      </div>

      {actionLabel && onAction && (
        <Button
          size="sm"
          onClick={onAction}
          className="mt-1 bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] font-semibold text-xs px-4"
        >
          <span>{actionLabel}</span>
          {ActionIcon && <ActionIcon size={13} className="ml-1.5" />}
        </Button>
      )}
    </div>
  );
}
