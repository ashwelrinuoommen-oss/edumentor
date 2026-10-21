import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from 'lucide-react';
import { cn } from '../../utils/cn';

export type ToastType = 'success' | 'caution' | 'weak' | 'info';

export interface ToastItem {
  id: string;
  title: string;
  description?: string;
  type?: ToastType;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextType {
  toast: (item: Omit<ToastItem, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(({ title, description, type = 'info', action }: Omit<ToastItem, 'id'>) => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const newToast: ToastItem = { id, title, description, type, action };
    setToasts((prev) => [...prev, newToast]);

    setTimeout(() => {
      removeToast(id);
    }, 5000);
  }, [removeToast]);

  return (
    <ToastContext.Provider value={{ toast, removeToast }}>
      {children}
      {/* Toast container */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cn(
              'pointer-events-auto flex items-center justify-between gap-3 p-3.5 rounded-[12px] border shadow-2xl transition-all duration-200 select-none',
              'bg-[#171717]',
              t.type === 'success' && 'border-[#34D399]/40 text-[#EDEDED]',
              t.type === 'caution' && 'border-[#FBBF24]/40 text-[#EDEDED]',
              t.type === 'weak' && 'border-[#F87171]/40 text-[#EDEDED]',
              t.type === 'info' && 'border-[#262626] text-[#EDEDED]'
            )}
          >
            <div className="flex items-start gap-2.5 min-w-0">
              <div className="mt-0.5 shrink-0">
                {t.type === 'success' && <CheckCircle2 size={16} className="text-[#34D399]" />}
                {t.type === 'caution' && <AlertTriangle size={16} className="text-[#FBBF24]" />}
                {t.type === 'weak' && <AlertCircle size={16} className="text-[#F87171]" />}
                {t.type === 'info' && <Info size={16} className="text-[#2DD4BF]" />}
              </div>

              <div className="flex-1 min-w-0">
                <div className="text-xs font-semibold text-[#EDEDED]">{t.title}</div>
                {t.description && (
                  <div className="text-[11px] text-[#A3A3A3] mt-0.5 leading-relaxed">{t.description}</div>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {t.action && (
                <button
                  type="button"
                  onClick={() => {
                    t.action?.onClick();
                    removeToast(t.id);
                  }}
                  className="px-2.5 py-1 text-xs font-bold rounded-full bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] transition-colors shadow-sm"
                  id="btn-toast-action"
                >
                  {t.action.label}
                </button>
              )}

              <button
                type="button"
                onClick={() => removeToast(t.id)}
                className="text-[#737373] hover:text-[#EDEDED] p-1 rounded-md transition-colors"
              >
                <X size={13} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
