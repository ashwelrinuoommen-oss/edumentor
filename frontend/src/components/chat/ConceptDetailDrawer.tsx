import React, { useState, useEffect } from 'react';
import { 
  X, 
  Trash2, 
  Plus, 
  AlertTriangle, 
  Check, 
  Sparkles, 
  BookOpen, 
  Layers, 
  ArrowRight, 
  Clock, 
  TrendingUp,
  Tag,
  AlertCircle,
  Edit3
} from 'lucide-react';
import { Concept } from '../../services/mockService';
import { apiService } from '../../services/api';
import { Drawer, DrawerHeader, DrawerTitle, DrawerDescription, DrawerBody, DrawerFooter, DrawerClose } from '../ui/Drawer';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { 
  wouldCreateCycle, 
  reorderConceptsWithPrerequisites, 
  getPrerequisitesForConcept, 
  getDependentsForConcept 
} from '../../utils/graphValidation';
import { cn } from '../../utils/cn';

export interface ConceptDetailDrawerProps {
  isOpen: boolean;
  concept: Concept | null;
  allConcepts: Concept[];
  onClose: () => void;
  onUpdateConcepts: (updatedConcepts: Concept[]) => void;
}

export function ConceptDetailDrawer({
  isOpen,
  concept,
  allConcepts,
  onClose,
  onUpdateConcepts
}: ConceptDetailDrawerProps) {
  if (!concept) return null;

  // Form states for editing
  const [editedTitle, setEditedTitle] = useState(concept.title);
  const [editedSummary, setEditedSummary] = useState(concept.summary || concept.rawContent || '');
  const [currentPrereqIds, setCurrentPrereqIds] = useState<string[]>(concept.prerequisiteIds || []);
  const [selectedCandidatePrereq, setSelectedCandidatePrereq] = useState<string>('');
  const [loopError, setLoopError] = useState<string | null>(null);
  const [isConfirmingDelete, setIsConfirmingDelete] = useState<boolean>(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState<boolean>(false);

  // Sync state whenever selected concept changes
  useEffect(() => {
    if (concept) {
      setEditedTitle(concept.title);
      setEditedSummary(concept.summary || concept.rawContent || '');
      setCurrentPrereqIds(concept.prerequisiteIds || []);
      setLoopError(null);
      setIsConfirmingDelete(false);
      setHasUnsavedChanges(false);
      setSelectedCandidatePrereq('');
    }
  }, [concept]);

  // Compute prerequisites and dependents from `allConcepts`
  const activePrereqs = allConcepts.filter(c => currentPrereqIds.includes(c.id));
  const activeDependents = allConcepts.filter(c => (c.prerequisiteIds || []).includes(concept.id));

  // Eligible concepts that can potentially be added as prerequisites (excluding self and current prereqs)
  const availablePrereqCandidates = allConcepts.filter(
    c => c.id !== concept.id && !currentPrereqIds.includes(c.id)
  );

  // Add Prerequisite with CYCLE DETECTION
  const handleAddPrerequisite = () => {
    if (!selectedCandidatePrereq) return;

    // Check if adding this creates a cycle
    const isCycle = wouldCreateCycle(allConcepts, concept.id, selectedCandidatePrereq);
    if (isCycle) {
      const candidateObj = allConcepts.find(c => c.id === selectedCandidatePrereq);
      setLoopError(
        `This would create a loop! "${candidateObj?.title || 'Selected concept'}" already depends on "${concept.title}". Circular dependencies are not allowed in a study path.`
      );
      return;
    }

    setLoopError(null);
    const updatedPrereqIds = [...currentPrereqIds, selectedCandidatePrereq];
    setCurrentPrereqIds(updatedPrereqIds);
    setSelectedCandidatePrereq('');

    // Immediately apply and re-order the whole path!
    applyConceptChanges(editedTitle, editedSummary, updatedPrereqIds);
  };

  // Remove Prerequisite
  const handleRemovePrerequisite = (prereqId: string) => {
    setLoopError(null);
    const updatedPrereqIds = currentPrereqIds.filter(id => id !== prereqId);
    setCurrentPrereqIds(updatedPrereqIds);

    // Immediately apply and re-order the whole path!
    applyConceptChanges(editedTitle, editedSummary, updatedPrereqIds);
  };

  // Immediate save & re-order helper
  const applyConceptChanges = (newTitle: string, newDef: string, newPrereqs: string[]) => {
    const updatedList = allConcepts.map(c => {
      if (c.id === concept.id) {
        return {
          ...c,
          title: newTitle.trim() || c.title,
          summary: newDef.trim() || c.summary,
          prerequisiteIds: newPrereqs,
          // Update string title references as well
          prerequisites: allConcepts.filter(item => newPrereqs.includes(item.id)).map(p => p.title)
        };
      }
      return c;
    });

    const reordered = reorderConceptsWithPrerequisites(updatedList);
    onUpdateConcepts(reordered);
    setHasUnsavedChanges(false);

    // Phase 11: Call PATCH /concepts/{id}
    apiService.updateConcept(concept.id, {
      name: newTitle.trim() || concept.title,
      definition: newDef.trim() || concept.summary,
      depends_on: newPrereqs
    }).catch(console.error);
  };

  // Save manual edits (rename, edit definition)
  const handleManualSave = (e: React.FormEvent) => {
    e.preventDefault();
    applyConceptChanges(editedTitle, editedSummary, currentPrereqIds);
    setHasUnsavedChanges(false);
  };

  // Remove Concept
  const handleRemoveConcept = () => {
    // 1. Remove concept from list
    // 2. Remove from any other concept's prerequisiteIds
    const remaining = allConcepts
      .filter(c => c.id !== concept.id)
      .map(c => ({
        ...c,
        prerequisiteIds: (c.prerequisiteIds || []).filter(pId => pId !== concept.id),
        prerequisites: (c.prerequisites || []).filter(pTitle => pTitle.toLowerCase() !== concept.title.toLowerCase())
      }));

    const reordered = reorderConceptsWithPrerequisites(remaining);
    onUpdateConcepts(reordered);
    onClose();
  };

  // SM-2 Spaced Repetition values
  const easeFactor = concept.sm2?.easinessFactor ? concept.sm2.easinessFactor.toFixed(2) : '2.50';
  const repetitionCount = concept.sm2?.repetition || 0;
  const nextReview = concept.sm2?.nextReviewDate 
    ? new Date(concept.sm2.nextReviewDate).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    : 'After first recall';

  return (
    <Drawer open={isOpen} onOpenChange={onClose} position="right">
      <DrawerHeader className="relative">
        <DrawerClose onClose={onClose} />
        <div className="flex items-center gap-2 mb-1">
          <span className="w-5 h-5 rounded-full bg-[#171717] border border-[#262626] text-[10px] font-bold text-[#2DD4BF] flex items-center justify-center">
            #{concept.orderIndex}
          </span>
          <Badge variant="teal" className="text-[10px] uppercase font-semibold">
            Concept Details
          </Badge>
          <Badge
            variant={
              concept.status === 'mastered' 
                ? 'success' 
                : concept.status === 'weak' 
                  ? 'weak' 
                  : 'neutral'
            }
            className="text-[10px] capitalize"
          >
            {concept.status || 'Unstudied'}
          </Badge>
        </div>

        <DrawerTitle className="text-lg leading-snug pr-8">
          {editedTitle}
        </DrawerTitle>
        <DrawerDescription className="text-xs">
          Order position #{concept.orderIndex} • Estimated study time: {concept.estTimeMinutes || 3} mins
        </DrawerDescription>
      </DrawerHeader>

      <DrawerBody className="gap-5">
        {/* Cycle Error Banner (Mandatory Prompt Requirement) */}
        {loopError && (
          <div className="p-3.5 rounded-[10px] bg-[#F87171]/15 border border-[#F87171]/40 flex items-start gap-2.5 text-xs text-[#EDEDED] animate-shake">
            <AlertTriangle size={18} className="text-[#F87171] shrink-0 mt-0.5" />
            <div className="flex flex-col gap-1">
              <span className="font-semibold text-[#F87171]">This would create a loop</span>
              <p className="text-[11px] text-[#A3A3A3] leading-relaxed">
                {loopError}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setLoopError(null)}
              className="text-[#A3A3A3] hover:text-[#EDEDED] ml-auto p-1"
            >
              <X size={13} />
            </button>
          </div>
        )}

        {/* 1. Full Definition from Notes */}
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs font-semibold text-[#EDEDED]">
            <span className="flex items-center gap-1.5 text-[#2DD4BF]">
              <BookOpen size={13} />
              Full Definition from Notes
            </span>
            <span className="text-[10px] text-[#737373] italic">Extracted content</span>
          </div>
          <div className="p-3 rounded-[10px] bg-[#171717] border border-[#262626] text-xs text-[#EDEDED] leading-relaxed whitespace-pre-wrap max-h-40 overflow-y-auto">
            {editedSummary || 'No explicit definition extracted from notes.'}
          </div>
        </div>

        {/* 2. Prerequisites & Dependents */}
        <div className="flex flex-col gap-3 p-3.5 rounded-[12px] bg-[#171717] border border-[#262626]">
          {/* Prerequisites (Needs to be studied first) */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between text-xs font-semibold text-[#EDEDED]">
              <span>Prerequisites (Needs to be studied before this):</span>
              <span className="text-[10px] text-[#737373]">{activePrereqs.length} total</span>
            </div>

            {activePrereqs.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {activePrereqs.map(p => (
                  <span
                    key={p.id}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#111111] border border-[#262626] text-xs text-[#EDEDED]"
                  >
                    <span className="text-[#2DD4BF] font-mono text-[10px]">#{p.orderIndex}</span>
                    <span className="truncate max-w-[130px]">{p.title}</span>
                    <button
                      type="button"
                      onClick={() => handleRemovePrerequisite(p.id)}
                      className="text-[#737373] hover:text-[#F87171] ml-0.5 rounded p-0.5"
                      title="Remove prerequisite"
                    >
                      <X size={11} />
                    </button>
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-[11px] text-[#737373] italic">
                None (Foundation concept — can be studied immediately)
              </p>
            )}

            {/* Add Prerequisite selector */}
            {availablePrereqCandidates.length > 0 && (
              <div className="flex items-center gap-2 mt-1 pt-2 border-t border-[#262626]/60">
                <select
                  value={selectedCandidatePrereq}
                  onChange={(e) => {
                    setSelectedCandidatePrereq(e.target.value);
                    setLoopError(null);
                  }}
                  className="bg-[#111111] text-[#EDEDED] text-xs border border-[#262626] rounded-md px-2.5 py-1.5 flex-1 outline-none focus:border-[#2DD4BF]"
                >
                  <option value="">+ Add a prerequisite...</option>
                  {availablePrereqCandidates.map(c => (
                    <option key={c.id} value={c.id}>
                      #{c.orderIndex} {c.title}
                    </option>
                  ))}
                </select>
                <Button
                  size="sm"
                  variant="secondary"
                  disabled={!selectedCandidatePrereq}
                  onClick={handleAddPrerequisite}
                  className="text-xs h-8 px-2.5"
                >
                  <Plus size={13} className="mr-1" />
                  <span>Add</span>
                </Button>
              </div>
            )}
          </div>

          <div className="my-1 border-t border-[#262626]" />

          {/* Dependents (Concepts that depend on this) */}
          <div className="flex flex-col gap-1.5">
            <span className="text-xs font-semibold text-[#EDEDED]">
              Dependents (Concepts that require this):
            </span>
            {activeDependents.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {activeDependents.map(d => (
                  <span
                    key={d.id}
                    className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#111111] border border-[#262626] text-[11px] text-[#A3A3A3]"
                  >
                    <span className="text-[#2DD4BF] font-mono text-[9px]">#{d.orderIndex}</span>
                    <span className="truncate max-w-[140px]">{d.title}</span>
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-[11px] text-[#737373] italic">
                None (Terminal node in study path)
              </p>
            )}
          </div>
        </div>

        {/* 3. Spaced Repetition (SM-2) Stats */}
        <div className="grid grid-cols-2 gap-2.5">
          <div className="p-3 rounded-[10px] bg-[#171717] border border-[#262626] flex flex-col gap-1">
            <span className="text-[10px] text-[#737373] uppercase tracking-wider font-semibold">
              Ease Factor (SM-2)
            </span>
            <div className="flex items-center gap-1.5 text-sm font-semibold text-[#2DD4BF]">
              <TrendingUp size={14} />
              <span>{easeFactor}</span>
            </div>
            <span className="text-[10px] text-[#737373]">
              {repetitionCount} completed recall{repetitionCount === 1 ? '' : 's'}
            </span>
          </div>

          <div className="p-3 rounded-[10px] bg-[#171717] border border-[#262626] flex flex-col gap-1">
            <span className="text-[10px] text-[#737373] uppercase tracking-wider font-semibold">
              Next Review
            </span>
            <div className="flex items-center gap-1.5 text-sm font-semibold text-[#EDEDED]">
              <Clock size={14} className="text-[#A3A3A3]" />
              <span>{nextReview}</span>
            </div>
            <span className="text-[10px] text-[#737373]">
              SM-2 interval queue
            </span>
          </div>
        </div>

        {/* 4. Edit Section (Rename, Edit Definition, Delete) */}
        <div className="flex flex-col gap-3 p-3.5 rounded-[12px] bg-[#171717] border border-[#262626]">
          <div className="flex items-center justify-between text-xs font-semibold text-[#EDEDED]">
            <span className="flex items-center gap-1.5">
              <Edit3 size={13} className="text-[#2DD4BF]" />
              Edit Concept Details
            </span>
            {hasUnsavedChanges && (
              <Badge variant="caution" className="text-[9px] py-0">Unsaved edits</Badge>
            )}
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] text-[#A3A3A3] font-medium">Concept Name:</label>
            <input
              type="text"
              value={editedTitle}
              onChange={(e) => {
                setEditedTitle(e.target.value);
                setHasUnsavedChanges(true);
              }}
              className="bg-[#111111] text-[#EDEDED] text-xs border border-[#262626] rounded-md px-3 py-2 outline-none focus:border-[#2DD4BF]"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] text-[#A3A3A3] font-medium">Definition / Summary:</label>
            <textarea
              rows={3}
              value={editedSummary}
              onChange={(e) => {
                setEditedSummary(e.target.value);
                setHasUnsavedChanges(true);
              }}
              className="bg-[#111111] text-[#EDEDED] text-xs border border-[#262626] rounded-md p-2.5 outline-none resize-none leading-relaxed focus:border-[#2DD4BF]"
            />
          </div>

          <div className="flex items-center justify-between pt-1">
            {/* Delete button with confirmation */}
            {!isConfirmingDelete ? (
              <button
                type="button"
                onClick={() => setIsConfirmingDelete(true)}
                className="text-xs text-[#F87171] hover:text-[#ef4444] flex items-center gap-1.5 p-1 transition-colors"
                title="Remove concept from study path"
              >
                <Trash2 size={13} />
                <span>Remove concept</span>
              </button>
            ) : (
              <div className="flex items-center gap-1.5">
                <span className="text-[11px] text-[#F87171]">Confirm?</span>
                <Button
                  size="sm"
                  onClick={handleRemoveConcept}
                  className="bg-[#F87171] hover:bg-[#ef4444] text-[#0A0A0A] h-7 text-[11px] px-2"
                >
                  Yes, Remove
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setIsConfirmingDelete(false)}
                  className="h-7 text-[11px] px-2"
                >
                  Cancel
                </Button>
              </div>
            )}

            {/* Save Edits button */}
            {hasUnsavedChanges && (
              <Button
                size="sm"
                onClick={handleManualSave}
                className="bg-[#2DD4BF] hover:bg-[#14B8A6] text-[#0A0A0A] text-xs font-medium"
              >
                <Check size={13} className="mr-1" />
                <span>Save Edits</span>
              </Button>
            )}
          </div>
        </div>
      </DrawerBody>

      <DrawerFooter className="justify-between">
        <span className="text-[11px] text-[#737373]">
          Edits immediately re-order the learning path.
        </span>
        <Button size="sm" variant="secondary" onClick={onClose}>
          Done
        </Button>
      </DrawerFooter>
    </Drawer>
  );
}
