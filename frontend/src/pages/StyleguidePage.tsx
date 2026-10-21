import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Chip } from '../components/ui/Chip';
import { Progress } from '../components/ui/Progress';
import { Tooltip } from '../components/ui/Tooltip';
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogContent, DialogFooter, DialogClose } from '../components/ui/Dialog';
import { Drawer, DrawerHeader, DrawerTitle, DrawerDescription, DrawerBody, DrawerFooter, DrawerClose } from '../components/ui/Drawer';
import { useToast } from '../components/ui/Toast';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { ProcessingStepperCard } from '../components/chat/ProcessingStepperCard';
import { StudyPathCard } from '../components/chat/StudyPathCard';
import { sessionService, StudySession } from '../services/mockService';
import { 
  Sparkles, 
  Send, 
  Clock, 
  Tag, 
  CheckCircle2, 
  AlertTriangle, 
  AlertCircle, 
  Info, 
  ArrowRight, 
  Layers, 
  Search,
  BookOpen
} from 'lucide-react';

export function StyleguidePage() {
  const { toast } = useToast();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [chipSelected, setChipSelected] = useState<Record<string, boolean>>({
    cs: true,
    bio: false,
    neuro: true
  });
  const [demoSession, setDemoSession] = useState<StudySession | null>(() => sessionService.getAll()[0] || null);

  return (
    <div className="p-8 max-w-6xl mx-auto flex flex-col gap-10 bg-[#0A0A0A] text-[#EDEDED] select-none">
      {/* Top Banner */}
      <div className="flex flex-col gap-2 border-b border-[#262626] pb-6">
        <div className="flex items-center gap-2">
          <Badge variant="teal">Phase 0 • Foundations</Badge>
          <span className="text-xs text-[#737373]">•</span>
          <span className="text-xs text-[#A3A3A3]">Design System Specification</span>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-[#EDEDED]">
          Component Styleguide
        </h1>
        <p className="text-xs text-[#737373] max-w-2xl leading-relaxed">
          Theme: black, calm, focused. WCAG AA contrast. All interactive controls feature visible focus rings in teal. Radius: 12px cards, 999px pills/composer.
        </p>
      </div>

      {/* 1. Color Palette Tokens */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          1. Color Palette Tokens
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
          <div className="p-3 rounded-[12px] bg-[#0A0A0A] border border-[#262626]">
            <div className="w-full h-8 rounded-md bg-[#0A0A0A] border border-[#262626] mb-2" />
            <div className="text-xs font-semibold">App Background</div>
            <div className="text-[11px] text-[#737373]">#0A0A0A</div>
          </div>
          <div className="p-3 rounded-[12px] bg-[#111111] border border-[#262626]">
            <div className="w-full h-8 rounded-md bg-[#111111] border border-[#262626] mb-2" />
            <div className="text-xs font-semibold">Surface</div>
            <div className="text-[11px] text-[#737373]">#111111</div>
          </div>
          <div className="p-3 rounded-[12px] bg-[#171717] border border-[#262626]">
            <div className="w-full h-8 rounded-md bg-[#171717] border border-[#262626] mb-2" />
            <div className="text-xs font-semibold">Raised Card</div>
            <div className="text-[11px] text-[#737373]">#171717</div>
          </div>
          <div className="p-3 rounded-[12px] bg-[#171717] border border-[#262626]">
            <div className="w-full h-8 rounded-md bg-[#1F1F1F] border border-[#262626] mb-2" />
            <div className="text-xs font-semibold">Hover Surface</div>
            <div className="text-[11px] text-[#737373]">#1F1F1F</div>
          </div>
          <div className="p-3 rounded-[12px] bg-[#171717] border border-[#262626]">
            <div className="w-full h-8 rounded-md bg-[#262626] mb-2" />
            <div className="text-xs font-semibold">Borders</div>
            <div className="text-[11px] text-[#737373]">#262626</div>
          </div>
          <div className="p-3 rounded-[12px] bg-[#171717] border border-[#262626]">
            <div className="w-full h-8 rounded-md bg-[#2DD4BF] mb-2" />
            <div className="text-xs font-semibold text-[#2DD4BF]">Accent Teal</div>
            <div className="text-[11px] text-[#737373]">#2DD4BF</div>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-1">
          <div className="p-3 rounded-[12px] bg-[#171717] border border-[#262626] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 rounded-full bg-[#34D399]" />
              <span className="text-xs">Success (Desaturated)</span>
            </div>
            <span className="text-xs text-[#737373]">#34D399</span>
          </div>
          <div className="p-3 rounded-[12px] bg-[#171717] border border-[#262626] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 rounded-full bg-[#FBBF24]" />
              <span className="text-xs">Caution (Desaturated)</span>
            </div>
            <span className="text-xs text-[#737373]">#FBBF24</span>
          </div>
          <div className="p-3 rounded-[12px] bg-[#171717] border border-[#262626] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 rounded-full bg-[#F87171]" />
              <span className="text-xs">Weak / Error (Desaturated)</span>
            </div>
            <span className="text-xs text-[#737373]">#F87171</span>
          </div>
        </div>
      </section>

      {/* 2. Buttons */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          2. Button Component (Variants, Sizes & States)
        </h2>
        <Card raised className="p-5 flex flex-col gap-4">
          <div className="flex items-center gap-3 flex-wrap">
            <Button variant="default">Default Teal</Button>
            <Button variant="secondary">Secondary Card</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="danger">Weak / Danger</Button>
            <Button variant="default" disabled>Disabled</Button>
          </div>

          <div className="pt-3 border-t border-[#262626] flex items-center gap-3 flex-wrap">
            <Button size="sm">Small (sm)</Button>
            <Button size="md">Medium (md)</Button>
            <Button size="lg">Large (lg)</Button>
            <Button size="icon" title="Icon Button"><Send size={14} /></Button>
            <Button variant="secondary" size="md">
              <Sparkles size={14} className="text-[#2DD4BF]" />
              <span>With Leading Icon</span>
            </Button>
            <Button variant="default" size="md">
              <span>With Trailing Icon</span>
              <ArrowRight size={14} />
            </Button>
          </div>
        </Card>
      </section>

      {/* 3. Inputs & Textareas */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          3. Input & Textarea Components
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card raised className="p-5 flex flex-col gap-3">
            <h4 className="text-xs font-semibold text-[#EDEDED]">Input States</h4>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs text-[#737373]">Default Input</label>
              <Input placeholder="Type a concept name..." />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs text-[#737373]">Filled Input</label>
              <Input defaultValue="Translation Lookaside Buffer (TLB)" />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs text-[#737373]">Disabled Input</label>
              <Input disabled defaultValue="Locked field" />
            </div>
          </Card>

          <Card raised className="p-5 flex flex-col gap-3">
            <h4 className="text-xs font-semibold text-[#EDEDED]">Textarea States</h4>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs text-[#737373]">Notes Editor Textarea</label>
              <Textarea placeholder="Paste your study notes here..." rows={4} />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs text-[#737373]">Disabled Textarea</label>
              <Textarea disabled defaultValue="Read-only lecture notes preview..." rows={2} />
            </div>
          </Card>
        </div>
      </section>

      {/* 4. Cards */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          4. Card Component (Tonal Steps & Structure)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card raised>
            <CardHeader>
              <CardTitle>Raised Card Variant (#171717)</CardTitle>
              <CardDescription>Separation achieved through borders and subtle tonal elevation.</CardDescription>
            </CardHeader>
            <CardContent>
              This card uses <code>raised={true}</code>, giving it an elevated background for primary modules.
            </CardContent>
            <CardFooter>
              <span>Card Footer meta</span>
              <Button size="sm" variant="outline">Action</Button>
            </CardFooter>
          </Card>

          <Card raised={false}>
            <CardHeader>
              <CardTitle>Surface Card Variant (#111111)</CardTitle>
              <CardDescription>Flatter card for inner containers and side panels.</CardDescription>
            </CardHeader>
            <CardContent>
              This card uses <code>raised={false}</code> for flush, calm surface integration.
            </CardContent>
            <CardFooter>
              <span className="text-[#737373]">WCAG AA Contrast</span>
              <Badge variant="teal">Verified</Badge>
            </CardFooter>
          </Card>
        </div>
      </section>

      {/* 5. Badges & Chips */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          5. Badge & Chip Components (Pill 999px Radius)
        </h2>
        <Card raised className="p-5 flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <span className="text-xs text-[#737373] font-semibold">Status Badges (Pills)</span>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="teal">Teal Accent</Badge>
              <Badge variant="success">Success #34D399</Badge>
              <Badge variant="caution">Caution #FBBF24</Badge>
              <Badge variant="weak">Weak #F87171</Badge>
              <Badge variant="neutral">Neutral #1F1F1F</Badge>
            </div>
          </div>

          <div className="pt-3 border-t border-[#262626] flex flex-col gap-2">
            <span className="text-xs text-[#737373] font-semibold">Interactive Chips (Selectable & Removable)</span>
            <div className="flex items-center gap-2 flex-wrap">
              <Chip
                selected={chipSelected.cs}
                onClick={() => setChipSelected(p => ({ ...p, cs: !p.cs }))}
                icon={<Tag size={11} />}
              >
                Computer Science
              </Chip>
              <Chip
                selected={chipSelected.neuro}
                onClick={() => setChipSelected(p => ({ ...p, neuro: !p.neuro }))}
                icon={<Tag size={11} />}
              >
                Neuroscience
              </Chip>
              <Chip
                selected={chipSelected.bio}
                onClick={() => setChipSelected(p => ({ ...p, bio: !p.bio }))}
                icon={<Tag size={11} />}
              >
                Biology
              </Chip>
              <Chip
                onRemove={() => alert('Removed custom tag')}
              >
                Removable Tag
              </Chip>
              <Chip disabled>
                Disabled Chip
              </Chip>
            </div>
          </div>
        </Card>
      </section>

      {/* 6. Progress Bars */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          6. Progress Component
        </h2>
        <Card raised className="p-5 flex flex-col gap-4">
          <Progress value={20} size="sm" showLabel variant="weak" />
          <Progress value={55} size="md" showLabel variant="caution" />
          <Progress value={85} size="md" showLabel variant="teal" />
          <Progress value={100} size="lg" showLabel variant="success" />
        </Card>
      </section>

      {/* 7. Tooltips */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          7. Tooltip Component
        </h2>
        <Card raised className="p-5 flex items-center justify-around flex-wrap gap-4">
          <Tooltip content="Tooltip displayed on Top" position="top">
            <Button variant="secondary" size="sm">Hover Top</Button>
          </Tooltip>
          <Tooltip content="Tooltip displayed on Bottom" position="bottom">
            <Button variant="secondary" size="sm">Hover Bottom</Button>
          </Tooltip>
          <Tooltip content="Tooltip on Left" position="left">
            <Button variant="secondary" size="sm">Hover Left</Button>
          </Tooltip>
          <Tooltip content="Tooltip on Right" position="right">
            <Button variant="secondary" size="sm">Hover Right</Button>
          </Tooltip>
        </Card>
      </section>

      {/* 8. Dialog & Drawer */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          8. Dialog & Drawer Components
        </h2>
        <Card raised className="p-5 flex items-center gap-4 flex-wrap">
          <Button variant="default" onClick={() => setDialogOpen(true)}>
            Open Dialog Modal
          </Button>
          <Button variant="secondary" onClick={() => setDrawerOpen(true)}>
            Open Slide-over Drawer
          </Button>

          {/* Dialog Modal */}
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogHeader>
              <DialogClose onClose={() => setDialogOpen(false)} />
              <DialogTitle>Modal Dialog Component</DialogTitle>
              <DialogDescription>
                Calm black theme modal with blur backdrop and 12px radius.
              </DialogDescription>
            </DialogHeader>
            <DialogContent>
              <p className="text-xs text-[#A3A3A3] leading-relaxed">
                Modal dialogs are used for focused interactions such as editing concept prerequisites or confirming review session completions.
              </p>
              <Input placeholder="Enter concept name..." />
            </DialogContent>
            <DialogFooter>
              <Button variant="secondary" size="sm" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button variant="default" size="sm" onClick={() => setDialogOpen(false)}>Confirm Action</Button>
            </DialogFooter>
          </Dialog>

          {/* Drawer */}
          <Drawer open={drawerOpen} onOpenChange={setDrawerOpen} position="right">
            <DrawerHeader>
              <DrawerClose onClose={() => setDrawerOpen(false)} />
              <DrawerTitle>Slide-over Drawer</DrawerTitle>
              <DrawerDescription>Smooth side-sheet with backdrop blur.</DrawerDescription>
            </DrawerHeader>
            <DrawerBody>
              <div className="flex flex-col gap-3 text-xs text-[#A3A3A3]">
                <p>Useful for inspecting detailed concept prerequisite graphs, recall metrics, or review history.</p>
                <div className="p-3 rounded-[8px] bg-[#171717] border border-[#262626]">
                  <span className="font-semibold text-[#EDEDED]">Drawer Body Container</span>
                  <p className="mt-1 text-[11px] text-[#737373]">Full scrollable support with WCAG AA compliant text.</p>
                </div>
              </div>
            </DrawerBody>
            <DrawerFooter>
              <Button variant="secondary" size="sm" onClick={() => setDrawerOpen(false)}>Close Drawer</Button>
            </DrawerFooter>
          </Drawer>
        </Card>
      </section>

      {/* 9. Toast Notifications */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          9. Toast Notification System
        </h2>
        <Card raised className="p-5 flex items-center gap-3 flex-wrap">
          <Button
            size="sm"
            variant="outline"
            className="border-[#34D399]/40 text-[#34D399]"
            onClick={() => toast({ title: 'Concept Mastered', description: 'Recall score 92% • Interval rescheduled to 6 days.', type: 'success' })}
          >
            Trigger Success Toast
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="border-[#FBBF24]/40 text-[#FBBF24]"
            onClick={() => toast({ title: 'Caution', description: 'Memory trace is fading. Review scheduled for tomorrow.', type: 'caution' })}
          >
            Trigger Caution Toast
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="border-[#F87171]/40 text-[#F87171]"
            onClick={() => toast({ title: 'Blackout Recall', description: 'Key terms were missed. Concept reset to day 1.', type: 'weak' })}
          >
            Trigger Weak Toast
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => toast({ title: 'System Notice', description: 'Study thread synchronized to local storage.', type: 'info' })}
          >
            Trigger Info Toast
          </Button>
        </Card>
      </section>

      {/* 10. Skeleton Loaders */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          10. Skeleton Component (Shimmer Loaders)
        </h2>
        <Card raised className="p-5 flex flex-col gap-3">
          <div className="flex items-center gap-3">
            <Skeleton variant="circular" className="w-10 h-10 shrink-0" />
            <div className="flex flex-col gap-2 flex-1">
              <Skeleton className="w-1/3 h-4" />
              <Skeleton className="w-2/3 h-3" />
            </div>
          </div>
          <Skeleton className="w-full h-16 mt-2" />
        </Card>
      </section>

      {/* 11. EmptyState Component */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
          11. EmptyState Component (Calm, Supportive Voice)
        </h2>
        <EmptyState
          icon={<BookOpen size={20} />}
          title="No study threads in this category yet"
          description="Upload lecture slides, paste notes, or pick one of our sample decks to start your active recall journey."
          action={
            <Button size="sm" variant="default" onClick={() => window.location.href = '/home'}>
              <span>Create First Thread</span>
              <ArrowRight size={13} />
            </Button>
          }
        />
      </section>

      {/* 12. Phase 4: Processing View Stepper Component */}
      <section className="flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <Badge variant="teal">Phase 4 Specification</Badge>
          <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
            12. Live Processing Stepper (4 Steps, Timer, Shimmer, Cancel, Retry)
          </h2>
        </div>
        <p className="text-xs text-[#737373]">
          Live stepper with 4 sequential states: Reading your notes, Finding key concepts, Mapping what depends on what, Building your study path. Total mock duration is ~4 to 6 seconds with subtle shimmer on the running step.
        </p>
        <Card raised className="p-6 flex flex-col gap-4">
          <ProcessingStepperCard
            notesTitle="Styleguide Demonstration Deck"
            onComplete={() => toast({ title: 'Study Path Ready', description: 'All 4 processing steps completed in 5.2s.', type: 'success' })}
            onCancel={() => toast({ title: 'Processing Paused', description: 'Cancelled by user.', type: 'caution' })}
            onEditNotes={() => toast({ title: 'Return to Editor', description: 'Notes preserved.', type: 'info' })}
          />
        </Card>
      </section>

      {/* 13. Phase 5: Study Path Display Component */}
      <section className="flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <Badge variant="teal">Phase 5 Specification</Badge>
          <h2 className="text-sm font-semibold text-[#A3A3A3] uppercase tracking-wider">
            13. Your Study Path Display (List View & Graph View)
          </h2>
        </div>
        <p className="text-xs text-[#737373]">
          Complete study path presentation with segmented toggle (List view with vertical connector line, Graph view with React Flow DAG), Concept Drawer with cycle detection, and actions bar.
        </p>
        {demoSession ? (
          <StudyPathCard
            session={demoSession}
            onUpdateSession={(updated) => setDemoSession(updated)}
            onRegeneratePath={() => toast({ title: 'Regenerating Study Path', description: 'Re-evaluating prerequisite graph...', type: 'info' })}
          />
        ) : (
          <div className="p-4 rounded-[12px] bg-[#171717] border border-[#262626] text-xs text-[#737373]">
            No demo session loaded.
          </div>
        )}
      </section>
    </div>
  );
}


