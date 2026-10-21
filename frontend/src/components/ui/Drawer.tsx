import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface DrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
  position?: 'right' | 'bottom';
}

export function Drawer({
  open,
  onOpenChange,
  children,
  position = 'right'
}: DrawerProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) onOpenChange(false);
    };
    if (open) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [open, onOpenChange]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex bg-black/75 backdrop-blur-sm transition-opacity duration-200"
      onClick={() => onOpenChange(false)}
    >
      <div
        className={cn(
          'bg-[#111111] border-[#262626] shadow-2xl flex flex-col transition-transform duration-200 ease-out',
          position === 'right' && 'ml-auto h-full w-full max-w-md border-l',
          position === 'bottom' && 'mt-auto w-full max-h-[80vh] border-t rounded-t-[16px]'
        )}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
      >
        {children}
      </div>
    </div>
  );
}

export function DrawerHeader({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('p-5 border-b border-[#262626] flex flex-col gap-1.5 relative', className)} {...props}>
      {children}
    </div>
  );
}

export function DrawerTitle({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn('text-base font-semibold text-[#EDEDED] tracking-tight', className)} {...props}>
      {children}
    </h3>
  );
}

export function DrawerDescription({ className, children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn('text-xs text-[#A3A3A3] leading-relaxed', className)} {...props}>
      {children}
    </p>
  );
}

export function DrawerBody({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('flex-1 overflow-y-auto p-5 text-sm text-[#EDEDED] flex flex-col gap-4', className)} {...props}>
      {children}
    </div>
  );
}

export function DrawerFooter({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('p-4 border-t border-[#262626] bg-[#0A0A0A] flex items-center justify-end gap-2.5', className)} {...props}>
      {children}
    </div>
  );
}

export function DrawerClose({ onClose }: { onClose: () => void }) {
  return (
    <button
      type="button"
      onClick={onClose}
      className="absolute top-4 right-4 p-1.5 rounded-md text-[#737373] hover:text-[#EDEDED] hover:bg-[#1F1F1F] transition-colors focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none"
      title="Close"
    >
      <X size={15} />
    </button>
  );
}
