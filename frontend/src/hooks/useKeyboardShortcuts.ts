import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';

/**
 * Global Keyboard Shortcuts Hook
 * - 'n' or 'N': New session (navigates to /home)
 * - '/': Focus composer textarea
 * - 'g' then 'r': Go to Review (/review)
 * - 'g' then 'p': Go to Progress (/progress)
 * - 'g' then 's': Go to Settings (/settings)
 * - '?' or 'Shift+/': Toggle Keyboard Shortcuts dialog
 */
export function useKeyboardShortcuts() {
  const navigate = useNavigate();
  const { 
    shortcutsModalOpen, 
    setShortcutsModalOpen,
    setMobileSidebarOpen,
    setStudyPathOpen
  } = useAppStore();

  const chordPendingRef = useRef<string | null>(null);
  const chordTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Ignore if user is currently typing inside an input, textarea, or contentEditable element
      const target = e.target as HTMLElement | null;
      const isInput = target && (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      );

      // Handle Escape globally to close modals / mobile drawers
      if (e.key === 'Escape') {
        if (shortcutsModalOpen) {
          setShortcutsModalOpen(false);
          return;
        }
        setMobileSidebarOpen(false);
        return;
      }

      if (isInput) return;

      // Handle '?' to open shortcuts modal
      if (e.key === '?' || (e.shiftKey && e.key === '/')) {
        e.preventDefault();
        setShortcutsModalOpen(!shortcutsModalOpen);
        return;
      }

      // Handle '/' to focus composer
      if (e.key === '/') {
        e.preventDefault();
        const composer = (document.getElementById('composer-textarea') || 
                          document.getElementById('recall-composer-textarea')) as HTMLTextAreaElement | null;
        if (composer) {
          composer.focus();
        } else {
          navigate('/home');
          setTimeout(() => {
            const comp = document.getElementById('composer-textarea') as HTMLTextAreaElement | null;
            if (comp) comp.focus();
          }, 150);
        }
        return;
      }

      // Handle 'n' or 'N' for new session
      if (e.key === 'n' || e.key === 'N') {
        e.preventDefault();
        navigate('/home');
        setTimeout(() => {
          const comp = document.getElementById('composer-textarea') as HTMLTextAreaElement | null;
          if (comp) comp.focus();
        }, 150);
        return;
      }

      // Handle Chords starting with 'g' or 'G'
      if (e.key === 'g' || e.key === 'G') {
        chordPendingRef.current = 'g';
        if (chordTimeoutRef.current) clearTimeout(chordTimeoutRef.current);
        chordTimeoutRef.current = window.setTimeout(() => {
          chordPendingRef.current = null;
        }, 1000);
        return;
      }

      if (chordPendingRef.current === 'g') {
        const nextKey = e.key.toLowerCase();
        chordPendingRef.current = null;
        if (chordTimeoutRef.current) clearTimeout(chordTimeoutRef.current);

        if (nextKey === 'r') {
          e.preventDefault();
          navigate('/review');
          return;
        }
        if (nextKey === 'p') {
          e.preventDefault();
          navigate('/progress');
          return;
        }
        if (nextKey === 's') {
          e.preventDefault();
          navigate('/settings');
          return;
        }
        if (nextKey === 'h') {
          e.preventDefault();
          navigate('/home');
          return;
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (chordTimeoutRef.current) clearTimeout(chordTimeoutRef.current);
    };
  }, [navigate, shortcutsModalOpen, setShortcutsModalOpen, setMobileSidebarOpen]);
}
