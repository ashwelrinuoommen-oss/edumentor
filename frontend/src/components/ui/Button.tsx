import React from 'react';
import { cn } from '../../utils/cn';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg' | 'icon';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'md', children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={cn(
          // Base styles: calm, focused, generous line height, universal teal focus ring
          'inline-flex items-center justify-center font-medium transition-all duration-150 ease-out select-none',
          'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0A0A0A] focus-visible:outline-none',
          'disabled:opacity-45 disabled:cursor-not-allowed',
          // Variants
          variant === 'default' && 'bg-[#2DD4BF] text-[#0A0A0A] font-semibold hover:bg-[#14B8A6] active:scale-[0.98]',
          variant === 'secondary' && 'bg-[#171717] text-[#EDEDED] border border-[#262626] hover:bg-[#1F1F1F] hover:border-[#333333]',
          variant === 'outline' && 'bg-transparent text-[#EDEDED] border border-[#262626] hover:bg-[#111111] hover:border-[#383838]',
          variant === 'ghost' && 'bg-transparent text-[#A3A3A3] hover:text-[#EDEDED] hover:bg-[#171717]',
          variant === 'danger' && 'bg-[#F87171]/15 text-[#F87171] border border-[#F87171]/30 hover:bg-[#F87171]/25',
          // Sizes
          size === 'sm' && 'h-8 px-3 text-xs rounded-md gap-1.5',
          size === 'md' && 'h-10 px-4 text-sm rounded-[10px] gap-2',
          size === 'lg' && 'h-12 px-6 text-base rounded-[12px] gap-2.5',
          size === 'icon' && 'h-9 w-9 p-0 rounded-md',
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
