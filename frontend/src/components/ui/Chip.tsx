import React from 'react';
import { X } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface ChipProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean;
  onRemove?: () => void;
  icon?: React.ReactNode;
}

export function Chip({
  className,
  selected = false,
  onRemove,
  icon,
  children,
  disabled,
  ...props
}: ChipProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      className={cn(
        'inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-full transition-all duration-150 select-none border',
        'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0A0A0A] focus-visible:outline-none',
        'disabled:opacity-40 disabled:cursor-not-allowed',
        selected
          ? 'bg-[#2DD4BF]/15 text-[#2DD4BF] border-[#2DD4BF]/50'
          : 'bg-[#171717] text-[#A3A3A3] border-[#262626] hover:bg-[#1F1F1F] hover:text-[#EDEDED] hover:border-[#333333]',
        className
      )}
      {...props}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{children}</span>
      {onRemove && (
        <span
          role="button"
          tabIndex={0}
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="p-0.5 -mr-1 hover:bg-[#262626] rounded-full text-[#737373] hover:text-[#EDEDED] transition-colors"
          title="Remove"
        >
          <X size={12} />
        </span>
      )}
    </button>
  );
}
