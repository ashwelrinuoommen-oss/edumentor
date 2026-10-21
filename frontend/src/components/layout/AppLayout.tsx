import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { StudyPathTracker } from './StudyPathTracker';
import { OfflineBanner } from '../ui/OfflineBanner';
import { KeyboardShortcutsModal } from '../ui/KeyboardShortcutsModal';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';

export function AppLayout() {
  const location = useLocation();
  // Activate global keyboard shortcuts
  useKeyboardShortcuts();

  return (
    <div className="flex w-screen h-screen bg-[#0A0A0A] text-[#EDEDED] overflow-hidden flex-col">
      {/* Accessibility: Skip to Content link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-[#2DD4BF] focus:text-[#0A0A0A] focus:rounded-md focus:font-semibold focus:shadow-xl focus:outline-none focus:ring-2 focus:ring-white"
      >
        Skip to main content
      </a>

      {/* Global Offline Banner */}
      <OfflineBanner />

      <div className="flex-1 flex w-full h-full overflow-hidden">
        {/* Zone 1: Left Sidebar (Collapsible, Drawer on mobile) */}
        <Sidebar />

        {/* Center Main Work Area with Zone 2 (Top bar) and Content */}
        <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#0A0A0A] min-w-0">
          <Header />

          <div className="flex-1 flex overflow-hidden relative">
            <main
              id="main-content"
              role="main"
              tabIndex={-1}
              className="flex-1 overflow-y-auto relative bg-[#0A0A0A] min-w-0 outline-none"
            >
              <AnimatePresence mode="wait">
                <motion.div
                  key={location.pathname}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  transition={{ duration: 0.18, ease: 'easeOut' }}
                  className="h-full w-full"
                >
                  <Outlet />
                </motion.div>
              </AnimatePresence>
            </main>

            {/* Zone 3: Right Panel (Study path tracker, bottom sheet on mobile, aside on desktop) */}
            <StudyPathTracker />
          </div>
        </div>
      </div>

      {/* Global Keyboard Shortcuts Cheat Sheet Modal */}
      <KeyboardShortcutsModal />
    </div>
  );
}
