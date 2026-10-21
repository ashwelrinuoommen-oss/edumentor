import React from 'react';
import { Dialog } from './Dialog';
import { useAppStore } from '../../store/useAppStore';
import { Keyboard, Command } from 'lucide-react';

interface ShortcutGroup {
  category: string;
  items: { keys: string[]; description: string }[];
}

const SHORTCUT_GROUPS: ShortcutGroup[] = [
  {
    category: 'Actions & Creation',
    items: [
      { keys: ['N'], description: 'Create a new study session' },
      { keys: ['/'], description: 'Focus notes composer or recall input' },
      { keys: ['Esc'], description: 'Close modals, drawers, or dialogs' },
      { keys: ['?'], description: 'Toggle this keyboard shortcuts cheat sheet' }
    ]
  },
  {
    category: 'Navigation Chords',
    items: [
      { keys: ['G', 'R'], description: 'Go to Spaced Review queue' },
      { keys: ['G', 'P'], description: 'Go to Progress & Mastery Matrix' },
      { keys: ['G', 'S'], description: 'Go to Application Settings' },
      { keys: ['G', 'H'], description: 'Go to Home / New Session' }
    ]
  }
];

export function KeyboardShortcutsModal() {
  const { shortcutsModalOpen, setShortcutsModalOpen } = useAppStore();

  return (
    <Dialog
      isOpen={shortcutsModalOpen}
      onClose={() => setShortcutsModalOpen(false)}
      title="Keyboard Shortcuts"
    >
      <div className="flex flex-col gap-5 text-xs text-[#EDEDED] select-none">
        <p className="text-[#A3A3A3] text-xs">
          Navigate and study quickly in EduMentor using your keyboard.
        </p>

        {SHORTCUT_GROUPS.map((group) => (
          <div key={group.category} className="flex flex-col gap-2">
            <h4 className="text-[11px] font-semibold text-[#737373] uppercase tracking-wider">
              {group.category}
            </h4>

            <div className="flex flex-col gap-1.5">
              {group.items.map((item) => (
                <div
                  key={item.description}
                  className="flex items-center justify-between p-2 rounded-[8px] bg-[#141414] border border-[#262626]"
                >
                  <span className="text-xs text-[#EDEDED]">{item.description}</span>
                  <div className="flex items-center gap-1">
                    {item.keys.map((k, idx) => (
                      <React.Fragment key={k}>
                        {idx > 0 && <span className="text-[10px] text-[#737373]">then</span>}
                        <kbd className="min-w-[22px] px-1.5 py-0.5 text-[11px] font-mono font-bold text-[#2DD4BF] bg-[#1E1E1E] border border-[#262626] rounded-[6px] shadow-sm text-center">
                          {k}
                        </kbd>
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="pt-2 text-center text-[11px] text-[#737373]">
          Tip: Press <kbd className="px-1 py-0.2 bg-[#1E1E1E] rounded text-[#A3A3A3]">Esc</kbd> anytime to dismiss.
        </div>
      </div>
    </Dialog>
  );
}
