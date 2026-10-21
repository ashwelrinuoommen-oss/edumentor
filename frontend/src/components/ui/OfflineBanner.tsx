import React, { useState, useEffect } from 'react';
import { WifiOff, AlertTriangle, X } from 'lucide-react';
import { cn } from '../../utils/cn';

export function OfflineBanner() {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
      setDismissed(false);
    };
    const handleOffline = () => {
      setIsOffline(true);
      setDismissed(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOffline || dismissed) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="w-full bg-[#FBBF24]/15 border-b border-[#FBBF24]/30 px-4 py-2 flex items-center justify-between text-xs text-[#FBBF24] select-none z-50 animate-fade-in"
    >
      <div className="flex items-center gap-2 mx-auto sm:mx-0">
        <WifiOff size={14} className="shrink-0" />
        <span className="font-medium">
          You are currently offline. Your study notes and reviews are saved locally and will sync when reconnected.
        </span>
      </div>

      <button
        type="button"
        onClick={() => setDismissed(true)}
        className="p-1 rounded hover:bg-[#FBBF24]/20 text-[#FBBF24] transition-colors shrink-0 ml-2"
        aria-label="Dismiss offline banner"
      >
        <X size={13} />
      </button>
    </div>
  );
}

/**
 * Dismissible Error Banner for critical alerts
 */
export function ErrorBanner({
  message,
  onDismiss
}: {
  message: string | null;
  onDismiss: () => void;
}) {
  if (!message) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="w-full bg-[#F87171]/15 border-b border-[#F87171]/30 px-4 py-2.5 flex items-center justify-between text-xs text-[#F87171] select-none z-50 animate-fade-in"
    >
      <div className="flex items-center gap-2">
        <AlertTriangle size={14} className="shrink-0" />
        <span className="font-medium">{message}</span>
      </div>

      <button
        type="button"
        onClick={onDismiss}
        className="p-1 rounded hover:bg-[#F87171]/20 text-[#F87171] transition-colors shrink-0 ml-2"
        aria-label="Dismiss error banner"
      >
        <X size={13} />
      </button>
    </div>
  );
}
