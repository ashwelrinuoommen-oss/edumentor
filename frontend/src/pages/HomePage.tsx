import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '../store/useAppStore';
import { sessionService, FileAttachment, StudySession } from '../services/mockService';
import { apiService } from '../services/api';
import { SAMPLE_NOTE_SETS } from '../data/sampleNotes';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Dialog } from '../components/ui/Dialog';
import { InitialNotesContent } from '../components/chat/InitialNotesContent';
import { ProcessingStepperCard } from '../components/chat/ProcessingStepperCard';
import { StudyPathCard } from '../components/chat/StudyPathCard';
import { ActiveRecallFlow } from '../components/chat/ActiveRecallFlow';
import { 
  Paperclip, 
  ArrowUp, 
  FileText, 
  X, 
  Clock, 
  RotateCcw, 
  BookOpen, 
  AlertCircle, 
  UploadCloud, 
  Tag, 
  Edit3, 
  Sparkles, 
  CheckCircle2, 
  ArrowRight,
  Info,
  FileQuestion,
  FileCode
} from 'lucide-react';
import { cn } from '../utils/cn';

const MAX_FILES = 3;
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB
const SOFT_WORD_LIMIT = 50000;
const SHORT_INPUT_WORD_THRESHOLD = 150;

interface AttachedFileItem {
  id: string;
  name: string;
  size: string;
  sizeBytes: number;
  type: string;
  rawText?: string;
  isUnreadable?: boolean;
}

export function HomePage() {
  const navigate = useNavigate();
  const { 
    user, 
    sessions, 
    createSession, 
    updateSession, 
    selectSession,
    simulatedDaysOffset,
    getSimulatedDate
  } = useAppStore();

  // Input & composer state
  const [inputText, setInputText] = useState('');
  const [moduleName, setModuleName] = useState('');
  const [isModuleNameCustom, setIsModuleNameCustom] = useState(false);
  const [isEditingModuleChip, setIsEditingModuleChip] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<AttachedFileItem[]>([]);
  
  // Validation & alerts state
  const [fileErrors, setFileErrors] = useState<string[]>([]);
  const [pdfReadingError, setPdfReadingError] = useState<string | null>(null);
  const [shortInputModalOpen, setShortInputModalOpen] = useState(false);
  
  // Drag & drop state
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const dragCounterRef = useRef(0);

  // Send & Chat transition state
  const [hasSent, setHasSent] = useState(false);
  const [createdSession, setCreatedSession] = useState<StudySession | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isProcessingComplete, setIsProcessingComplete] = useState(false);
  const [simulateErrorStep, setSimulateErrorStep] = useState<number | null>(null);
  const [simulateZeroConcepts, setSimulateZeroConcepts] = useState<boolean>(false);
  const [isRecallActive, setIsRecallActive] = useState<boolean>(false);

  // References
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const moduleInputRef = useRef<HTMLInputElement>(null);
  const threadEndRef = useRef<HTMLDivElement>(null);

  const firstName = user?.name ? user.name.split(' ')[0] : 'there';

  // Live Metrics for cards based on simulated date
  const simulatedDate = getSimulatedDate();
  const dueItems = sessionService.getDueReviewConcepts(simulatedDate);
  const dueCount = dueItems.length;
  const analytics = sessionService.getAnalyticsSummary(simulatedDate);
  const weakCount = analytics.reviewDueCount;
  const lastSession = sessions.length > 0 ? sessions[0] : null;

  // Auto-grow textarea up to ~8 lines (~192px)
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 192);
    textarea.style.height = `${Math.max(54, newHeight)}px`;
  }, [inputText]);

  // Auto-fill module name if user hasn't explicitly customized it
  useEffect(() => {
    if (isModuleNameCustom) return;

    if (attachedFiles.length > 0) {
      const firstFile = attachedFiles[0];
      const clean = firstFile.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
      setModuleName(clean.slice(0, 48));
    } else if (inputText.trim()) {
      const firstLine = inputText.trim().split('\n')[0].replace(/^[#*\s-]+/, '').trim();
      if (firstLine) {
        setModuleName(firstLine.slice(0, 48));
      }
    } else {
      setModuleName('');
    }
  }, [inputText, attachedFiles, isModuleNameCustom]);

  // Drag and drop event handlers on the window
  useEffect(() => {
    const handleDragEnter = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounterRef.current += 1;
      if (e.dataTransfer?.types && Array.from(e.dataTransfer.types).includes('Files')) {
        setIsDraggingOver(true);
      }
    };

    const handleDragLeave = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounterRef.current -= 1;
      if (dragCounterRef.current <= 0) {
        setIsDraggingOver(false);
        dragCounterRef.current = 0;
      }
    };

    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
    };

    const handleDrop = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounterRef.current = 0;
      setIsDraggingOver(false);

      if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
        processFiles(Array.from(e.dataTransfer.files));
      }
    };

    window.addEventListener('dragenter', handleDragEnter);
    window.addEventListener('dragleave', handleDragLeave);
    window.addEventListener('dragover', handleDragOver);
    window.addEventListener('drop', handleDrop);

    return () => {
      window.removeEventListener('dragenter', handleDragEnter);
      window.removeEventListener('dragleave', handleDragLeave);
      window.removeEventListener('dragover', handleDragOver);
      window.removeEventListener('drop', handleDrop);
    };
  }, [attachedFiles]);

  // File size formatter helper
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  // Process and validate uploaded files
  const processFiles = (files: File[]) => {
    const newErrors: string[] = [];
    setPdfReadingError(null);

    // Check count limit
    if (attachedFiles.length + files.length > MAX_FILES) {
      newErrors.push(`You can attach up to ${MAX_FILES} files per session. Only the first valid files will be added.`);
    }

    const availableSlots = MAX_FILES - attachedFiles.length;
    const filesToConsider = files.slice(0, Math.max(0, availableSlots));
    const acceptedExtensions = ['.pdf', '.txt', '.md', '.markdown', '.docx'];

    const newAttachments: AttachedFileItem[] = [];

    filesToConsider.forEach((file) => {
      const ext = `.${file.name.split('.').pop()?.toLowerCase()}`;
      const isAccepted = acceptedExtensions.includes(ext);

      // Check format
      if (!isAccepted) {
        newErrors.push(`"${file.name}" has an unsupported format. EduMentor accepts PDF, TXT, MD, and DOCX.`);
        return;
      }

      // Check file size (10 MB limit)
      if (file.size > MAX_FILE_SIZE_BYTES) {
        newErrors.push(`"${file.name}" exceeds the 10 MB limit (${formatFileSize(file.size)}).`);
        return;
      }

      // Check for unreadable / zero-byte / scanned test files
      const isUnreadablePdf = 
        file.size === 0 || 
        file.name.toLowerCase().includes('scanned') || 
        file.name.toLowerCase().includes('unreadable') ||
        file.name.toLowerCase().includes('corrupted');

      if (isUnreadablePdf && ext === '.pdf') {
        setPdfReadingError("I could not read text from this file. Try a text-based PDF or paste the content.");
      }

      // Read text content if TXT or MD
      const item: AttachedFileItem = {
        id: `file-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        name: file.name,
        size: formatFileSize(file.size),
        sizeBytes: file.size,
        type: ext.replace('.', '').toUpperCase(),
        isUnreadable: isUnreadablePdf
      };

      if (ext === '.txt' || ext === '.md' || ext === '.markdown') {
        const reader = new FileReader();
        reader.onload = (event) => {
          const text = event.target?.result;
          if (typeof text === 'string') {
            item.rawText = text;
            // If main textarea is empty, offer to auto-populate or concatenate
            if (!inputText.trim()) {
              setInputText(text);
            }
          }
        };
        reader.readAsText(file);
      }

      newAttachments.push(item);
    });

    if (newErrors.length > 0) {
      setFileErrors(prev => [...prev, ...newErrors]);
    }

    if (newAttachments.length > 0) {
      setAttachedFiles(prev => [...prev, ...newAttachments]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(Array.from(e.target.files));
      e.target.value = '';
    }
  };

  const handleRemoveFile = (fileId: string) => {
    setAttachedFiles(prev => prev.filter(f => f.id !== fileId));
    setFileErrors([]);
    setPdfReadingError(null);
  };

  // Word count & soft limit
  const words = inputText.trim() ? inputText.trim().split(/\s+/).filter(Boolean) : [];
  const wordCount = words.length;
  const isOverSoftLimit = wordCount > SOFT_WORD_LIMIT;
  const isNearSoftLimit = wordCount >= 40000;

  // Validation before sending
  const handleAttemptSend = () => {
    // Disabled check
    if (!inputText.trim() && attachedFiles.length === 0) return;

    // Check if any attached PDF was deemed unreadable
    const hasUnreadable = attachedFiles.some(f => f.isUnreadable);
    if (hasUnreadable && !inputText.trim()) {
      setPdfReadingError("I could not read text from this file. Try a text-based PDF or paste the content.");
      return;
    }

    // Check short input (<150 words) warning
    // If text is under 150 words and no attached file has full text
    if (wordCount > 0 && wordCount < SHORT_INPUT_WORD_THRESHOLD && attachedFiles.length === 0) {
      setShortInputModalOpen(true);
      return;
    }

    // Proceed to send
    executeSend();
  };

  // Keydown handler: Enter sends, Shift+Enter adds newline
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAttemptSend();
    }
  };

  // Execute send & transition into chat thread with live stepper
  const executeSend = (customSimError: number | null = null, customSimZero = false) => {
    setShortInputModalOpen(false);
    setHasSent(true);
    setIsProcessing(true);
    setIsProcessingComplete(false);
    setIsRecallActive(false);
    setCreatedSession(null);
    setSimulateErrorStep(customSimError);
    setSimulateZeroConcepts(customSimZero);

    // Auto-scroll into view smoothly
    setTimeout(() => {
      threadEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 150);
  };

  const handleProcessingComplete = () => {
    const finalTitle = moduleName.trim() || 'Untitled Study Session';
    const notesPayload = inputText.trim() || attachedFiles.map(f => `[Attached Document: ${f.name}]`).join('\n\n');
    
    const formattedAttachments: FileAttachment[] = attachedFiles.map(f => ({
      name: f.name,
      size: f.size,
      type: f.type
    }));

    const session = createSession(finalTitle, notesPayload, 'General', formattedAttachments);
    setCreatedSession(session);
    selectSession(session.id);
    setIsProcessing(false);
    setIsProcessingComplete(true);

    // Phase 11: Call POST /modules, GET /modules/{id}/status, GET /modules/{id}/concepts, GET /modules/{id}/path
    apiService.createModule({
      module_name: finalTitle,
      pasted_text: notesPayload
    }).then(async (modRes) => {
      await apiService.getModuleStatus(modRes.module_id);
      await apiService.getModuleConcepts(modRes.module_id);
      await apiService.getModulePath(modRes.module_id);
    }).catch(console.error);

    setTimeout(() => {
      threadEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 200);
  };

  const handleCancelProcessing = () => {
    setIsProcessing(false);
  };

  const handleEditNotes = () => {
    setHasSent(false);
    setIsProcessing(false);
    setIsProcessingComplete(false);
    setIsRecallActive(false);
    setSimulateErrorStep(null);
    setSimulateZeroConcepts(false);
  };

  // Demo note loaders for rapid testing
  const handleLoadSample = (sample: typeof SAMPLE_NOTE_SETS[0]) => {
    setInputText(sample.content);
    setModuleName(sample.title);
    setIsModuleNameCustom(true);
    setFileErrors([]);
    setPdfReadingError(null);
  };

  const handleSimulateUnreadablePdf = () => {
    setAttachedFiles(prev => [
      ...prev,
      {
        id: `unreadable-${Date.now()}`,
        name: 'scanned_lecture_slides.pdf',
        size: '4.2 MB',
        sizeBytes: 4.2 * 1024 * 1024,
        type: 'PDF',
        isUnreadable: true
      }
    ]);
    setPdfReadingError("I could not read text from this file. Try a text-based PDF or paste the content.");
  };

  const handleSimulateShortNotes = () => {
    setInputText("Mitochondria is the powerhouse of the cell. It produces ATP through chemical reactions.");
    setModuleName("Mitochondria Basics");
    setIsModuleNameCustom(true);
  };

  const handleSimulateStepError = () => {
    handleLoadSample(SAMPLE_NOTE_SETS[0]);
    setTimeout(() => {
      executeSend(3, false);
    }, 80);
  };

  const handleSimulateZeroConcepts = () => {
    setInputText("Rough fragmented snippet with no definitions.");
    setModuleName("Fragmented Fragment");
    setIsModuleNameCustom(true);
    setTimeout(() => {
      executeSend(null, true);
    }, 80);
  };

  return (
    <div className="relative min-h-full flex flex-col justify-between bg-[#0A0A0A] text-[#EDEDED] select-text">
      {/* Full-width Drag and Drop Overlay */}
      <AnimatePresence>
        {isDraggingOver && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-[#0A0A0A]/90 backdrop-blur-md border-2 border-dashed border-[#2DD4BF] flex flex-col items-center justify-center p-6 text-center pointer-events-none"
          >
            <div className="w-16 h-16 rounded-full bg-[#2DD4BF]/10 flex items-center justify-center mb-4 text-[#2DD4BF] animate-bounce">
              <UploadCloud size={32} />
            </div>
            <h3 className="text-xl font-semibold text-[#EDEDED]">Drop your notes to upload</h3>
            <p className="text-sm text-[#A3A3A3] mt-2 max-w-sm">
              EduMentor accepts PDF, TXT, MD, and DOCX files up to 10 MB each.
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Center Column (max-w-[760px] mx-auto) */}
      <div className="w-full max-w-[760px] mx-auto px-4 flex-1 flex flex-col justify-center">
        
        {/* If session hasn't started yet: Center layout with empty state */}
        {!hasSent ? (
          <div className="flex flex-col items-center my-auto py-10 w-full">
            {/* Phase 7: Home Screen Due Review Banner (Visible loop closing) */}
            {dueCount > 0 && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full mb-6 p-4 rounded-[16px] bg-[#171717] border border-[#FBBF24]/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg"
                id="home-due-review-banner"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#FBBF24]/15 border border-[#FBBF24]/30 flex items-center justify-center text-[#FBBF24] shrink-0">
                    <Clock size={18} />
                  </div>
                  <div className="flex flex-col">
                    <h3 className="text-sm font-semibold text-[#EDEDED] flex items-center gap-2">
                      <span>{dueCount} concept{dueCount === 1 ? '' : 's'} {dueCount === 1 ? 'is' : 'are'} ready to review</span>
                      <Badge variant="caution" className="text-[10px] py-0">SM-2 Spaced Recall</Badge>
                    </h3>
                    <p className="text-xs text-[#A3A3A3] mt-0.5">
                      Memory traces are starting to decay. A quick recall session reinforces them into durable mastery.
                    </p>
                  </div>
                </div>

                <Button
                  size="sm"
                  onClick={() => navigate('/review')}
                  className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] font-semibold text-xs px-4 shrink-0 self-start sm:self-auto"
                  id="btn-start-due-review-home"
                >
                  <span>Start review</span>
                  <ArrowRight size={13} className="ml-1.5" />
                </Button>
              </motion.div>
            )}

            {/* Empty State Greeting */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
              className="text-center mb-7 w-full"
            >
              <h1 className="text-2xl sm:text-3xl font-semibold text-[#EDEDED] tracking-tight">
                What are we studying today, {firstName}?
              </h1>
              <p className="text-sm text-[#A3A3A3] mt-2 leading-relaxed">
                Paste your notes or attach a file. I will turn them into a study path.
              </p>
            </motion.div>

            {/* The Composer: Large Rounded Pill Container */}
            <div className="w-full flex flex-col gap-2 sticky bottom-2 sm:static z-20">
              <motion.div
                layout
                className={cn(
                  'w-full bg-[#171717] rounded-[24px] border border-[#262626] p-4 flex flex-col gap-2.5 transition-all shadow-xl',
                  'focus-within:border-[#2DD4BF] focus-within:ring-1 focus-within:ring-[#2DD4BF]'
                )}
                id="composer-container"
              >
                {/* Module Name Chip & Attached Files Row */}
                {(moduleName || attachedFiles.length > 0) && (
                  <div className="flex flex-wrap items-center gap-2 pt-1 pb-1 border-b border-[#262626]/60">
                    {/* Editable Module Name Chip */}
                    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#111111] border border-[#262626] text-xs text-[#2DD4BF]">
                      <Tag size={12} className="text-[#2DD4BF] shrink-0" />
                      <span className="text-[#737373] text-[11px] font-medium">Module:</span>
                      
                      {isEditingModuleChip ? (
                        <input
                          ref={moduleInputRef}
                          type="text"
                          value={moduleName}
                          onChange={(e) => {
                            setModuleName(e.target.value);
                            setIsModuleNameCustom(true);
                          }}
                          onBlur={() => setIsEditingModuleChip(false)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault();
                              setIsEditingModuleChip(false);
                            }
                          }}
                          autoFocus
                          className="bg-transparent text-[#EDEDED] text-xs font-medium outline-none border-b border-[#2DD4BF] px-1 py-0 w-32 sm:w-48"
                        />
                      ) : (
                        <button
                          type="button"
                          onClick={() => {
                            setIsEditingModuleChip(true);
                            setIsModuleNameCustom(true);
                          }}
                          className="font-medium text-[#EDEDED] hover:text-[#2DD4BF] transition-colors truncate max-w-[180px] sm:max-w-[280px] text-left"
                          title="Click to rename module"
                        >
                          {moduleName || 'Untitled Module'}
                        </button>
                      )}

                      <button
                        type="button"
                        onClick={() => {
                          setIsEditingModuleChip(!isEditingModuleChip);
                          setIsModuleNameCustom(true);
                        }}
                        className="text-[#737373] hover:text-[#EDEDED] ml-0.5 p-0.5 rounded"
                        title="Edit module name"
                      >
                        <Edit3 size={11} />
                      </button>
                    </div>

                    {/* Attached File Chips */}
                    {attachedFiles.map((file) => (
                      <div
                        key={file.id}
                        className={cn(
                          'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border transition-colors',
                          file.isUnreadable
                            ? 'bg-[#F87171]/10 text-[#F87171] border-[#F87171]/30'
                            : 'bg-[#111111] text-[#EDEDED] border-[#262626]'
                        )}
                      >
                        <FileText size={12} className={file.isUnreadable ? 'text-[#F87171]' : 'text-[#2DD4BF]'} />
                        <span className="font-medium truncate max-w-[140px]" title={file.name}>
                          {file.name}
                        </span>
                        <span className="text-[10px] text-[#737373]">{file.size}</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveFile(file.id)}
                          className="text-[#737373] hover:text-[#EDEDED] ml-0.5 p-0.5 rounded-full hover:bg-[#262626] transition-colors"
                          title="Remove file"
                        >
                          <X size={11} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Auto-growing Textarea */}
                <textarea
                  ref={textareaRef}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Paste your notes, or attach a PDF or text file..."
                  className="w-full bg-transparent text-[#EDEDED] text-sm placeholder-[#737373] outline-none resize-none leading-relaxed px-1 py-1 min-h-[54px]"
                  id="composer-textarea"
                />

                {/* Composer Bottom Action Row */}
                <div className="flex items-center justify-between pt-1 gap-2">
                  {/* Left: Attach Button & Quick Tools */}
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="p-2 rounded-full text-[#A3A3A3] hover:text-[#EDEDED] hover:bg-[#262626] transition-colors focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none"
                      title="Attach notes (PDF, TXT, MD, DOCX)"
                      id="btn-attach-notes"
                    >
                      <Paperclip size={18} />
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      accept=".pdf,.txt,.md,.markdown,.docx"
                      onChange={handleFileInputChange}
                      className="hidden"
                      id="hidden-file-input"
                    />

                    {/* Subtle Quick Loaders for testing */}
                    <div className="hidden sm:flex flex-wrap items-center gap-1.5 text-[11px] text-[#737373]">
                      <span>Quick demo:</span>
                      <button
                        type="button"
                        onClick={() => handleLoadSample(SAMPLE_NOTE_SETS[0])}
                        className="px-2 py-0.5 rounded bg-[#111111] hover:bg-[#1F1F1F] text-[#A3A3A3] hover:text-[#EDEDED] border border-[#262626] transition-colors"
                      >
                        OS Notes
                      </button>
                      <button
                        type="button"
                        onClick={handleSimulateShortNotes}
                        className="px-2 py-0.5 rounded bg-[#111111] hover:bg-[#1F1F1F] text-[#A3A3A3] hover:text-[#EDEDED] border border-[#262626] transition-colors"
                        title="Load short notes under 150 words to test validation warning"
                      >
                        Short Notes
                      </button>
                      <button
                        type="button"
                        onClick={handleSimulateUnreadablePdf}
                        className="px-2 py-0.5 rounded bg-[#111111] hover:bg-[#1F1F1F] text-[#A3A3A3] hover:text-[#EDEDED] border border-[#262626] transition-colors"
                        title="Simulate unreadable/scanned PDF"
                      >
                        Scanned PDF
                      </button>
                      <button
                        type="button"
                        onClick={handleSimulateStepError}
                        className="px-2 py-0.5 rounded bg-[#111111] hover:bg-[#F87171]/20 text-[#A3A3A3] hover:text-[#F87171] border border-[#262626] transition-colors"
                        title="Phase 4: Simulate step failure (Red error state with Try again button)"
                        id="btn-demo-step-error"
                      >
                        Simulate Error Step
                      </button>
                      <button
                        type="button"
                        onClick={handleSimulateZeroConcepts}
                        className="px-2 py-0.5 rounded bg-[#111111] hover:bg-[#F87171]/20 text-[#A3A3A3] hover:text-[#F87171] border border-[#262626] transition-colors"
                        title="Phase 4: Simulate zero concepts found ('I could not find clear concepts in this text' with advice)"
                        id="btn-demo-zero-concepts"
                      >
                        Simulate 0 Concepts
                      </button>
                    </div>
                  </div>

                  {/* Right: Word Counter & Send Button */}
                  <div className="flex items-center gap-3">
                    {/* Subtle Word Counter near limit */}
                    {wordCount > 300 && (
                      <div className="text-right">
                        <span
                          className={cn(
                            'text-[11px] font-mono transition-colors',
                            isOverSoftLimit 
                              ? 'text-[#FBBF24] font-medium' 
                              : isNearSoftLimit 
                                ? 'text-[#FBBF24]/80' 
                                : 'text-[#737373]'
                          )}
                        >
                          {wordCount.toLocaleString()} {isOverSoftLimit ? '/ 50,000 words (soft limit)' : 'words'}
                        </span>
                      </div>
                    )}

                    {/* Round Teal Send Button */}
                    <button
                      type="button"
                      onClick={handleAttemptSend}
                      disabled={!inputText.trim() && attachedFiles.length === 0}
                      className={cn(
                        'w-9 h-9 rounded-full flex items-center justify-center transition-all',
                        'bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6]',
                        'disabled:opacity-30 disabled:hover:bg-[#2DD4BF] disabled:cursor-not-allowed',
                        'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:ring-offset-2 focus-visible:ring-offset-[#171717] focus-visible:outline-none'
                      )}
                      id="btn-send-notes"
                      title="Turn notes into study path (Enter)"
                    >
                      <ArrowUp size={18} strokeWidth={2.4} />
                    </button>
                  </div>
                </div>
              </motion.div>

              {/* Inline Validation Warnings / Error Messages */}
              {fileErrors.length > 0 && (
                <div className="flex flex-col gap-1.5 px-2">
                  {fileErrors.map((err, i) => (
                    <div
                      key={i}
                      className="p-2.5 rounded-[8px] bg-[#F87171]/10 border border-[#F87171]/30 text-xs text-[#F87171] flex items-center justify-between gap-2"
                    >
                      <div className="flex items-center gap-2">
                        <AlertCircle size={14} className="shrink-0" />
                        <span>{err}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setFileErrors(prev => prev.filter((_, idx) => idx !== i))}
                        className="text-[#F87171] hover:text-[#EDEDED]"
                      >
                        <X size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Edge Case Validation: Empty / Unreadable PDF Message */}
              {pdfReadingError && (
                <div className="p-3 rounded-[8px] bg-[#F87171]/10 border border-[#F87171]/30 text-xs text-[#F87171] flex items-center justify-between gap-2 px-3">
                  <div className="flex items-center gap-2">
                    <FileQuestion size={16} className="shrink-0" />
                    <span>{pdfReadingError}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setPdfReadingError(null)}
                    className="text-[#F87171] hover:text-[#EDEDED]"
                  >
                    <X size={13} />
                  </button>
                </div>
              )}

              {/* Soft word limit banner if exceeded */}
              {isOverSoftLimit && (
                <div className="p-2.5 rounded-[8px] bg-[#FBBF24]/10 border border-[#FBBF24]/30 text-xs text-[#FBBF24] flex items-center gap-2 px-3">
                  <Info size={14} className="shrink-0" />
                  <span>
                    Your notes exceed the 50,000 word soft limit ({wordCount.toLocaleString()} words). Extraction may take slightly longer.
                  </span>
                </div>
              )}

              {/* Helper line under composer */}
              <p className="text-xs text-[#737373] text-center mt-2">
                EduMentor works best with typed notes. Scanned or handwritten pages may not be readable.
              </p>
            </div>

            {/* Three Small Cards Below Composer */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 mt-8 w-full">
              {/* Card 1: Due for review today */}
              <div
                onClick={() => navigate('/review')}
                className={cn(
                  'p-4 rounded-[12px] bg-[#171717] border border-[#262626] hover:border-[#383838] hover:bg-[#1F1F1F] transition-all cursor-pointer group flex flex-col justify-between gap-3',
                  'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none'
                )}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && navigate('/review')}
                id="card-due-for-review"
              >
                <div className="flex items-center justify-between">
                  <div className="w-7 h-7 rounded-[8px] bg-[#2DD4BF]/10 text-[#2DD4BF] flex items-center justify-center">
                    <RotateCcw size={15} />
                  </div>
                  <Badge variant={dueCount > 0 ? 'caution' : 'teal'}>
                    {dueCount} due
                  </Badge>
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-[#EDEDED] group-hover:text-[#2DD4BF] transition-colors">
                    Due for review today
                  </h4>
                  <p className="text-[11px] text-[#737373] mt-0.5">
                    {dueCount > 0 
                      ? `${dueCount} concepts in SM-2 spaced repetition queue`
                      : 'All caught up on spaced recall reviews'}
                  </p>
                </div>
              </div>

              {/* Card 2: Continue where you left off */}
              <div
                onClick={() => {
                  if (lastSession) navigate(`/session/${lastSession.id}`);
                }}
                className={cn(
                  'p-4 rounded-[12px] bg-[#171717] border border-[#262626] hover:border-[#383838] hover:bg-[#1F1F1F] transition-all cursor-pointer group flex flex-col justify-between gap-3',
                  !lastSession && 'opacity-60 cursor-default',
                  'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none'
                )}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && lastSession && navigate(`/session/${lastSession.id}`)}
                id="card-continue-session"
              >
                <div className="flex items-center justify-between">
                  <div className="w-7 h-7 rounded-[8px] bg-[#34D399]/10 text-[#34D399] flex items-center justify-center">
                    <BookOpen size={15} />
                  </div>
                  {lastSession && (
                    <Badge variant="success">
                      Concept {lastSession.currentConceptIndex + 1}/{lastSession.concepts.length}
                    </Badge>
                  )}
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-[#EDEDED] group-hover:text-[#2DD4BF] transition-colors truncate">
                    Continue where you left off
                  </h4>
                  <p className="text-[11px] text-[#737373] mt-0.5 truncate">
                    {lastSession ? lastSession.title : 'Start your first study session above'}
                  </p>
                </div>
              </div>

              {/* Card 3: Weak concepts */}
              <div
                onClick={() => navigate('/progress')}
                className={cn(
                  'p-4 rounded-[12px] bg-[#171717] border border-[#262626] hover:border-[#383838] hover:bg-[#1F1F1F] transition-all cursor-pointer group flex flex-col justify-between gap-3',
                  'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none'
                )}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && navigate('/progress')}
                id="card-weak-concepts"
              >
                <div className="flex items-center justify-between">
                  <div className="w-7 h-7 rounded-[8px] bg-[#F87171]/10 text-[#F87171] flex items-center justify-center">
                    <AlertCircle size={15} />
                  </div>
                  <Badge variant={weakCount > 0 ? 'weak' : 'neutral'}>
                    {weakCount} weak
                  </Badge>
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-[#EDEDED] group-hover:text-[#2DD4BF] transition-colors">
                    Weak concepts
                  </h4>
                  <p className="text-[11px] text-[#737373] mt-0.5">
                    {weakCount > 0 
                      ? `${weakCount} items need reinforcement` 
                      : 'Zero weak concepts flagged'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Transition into Chat Thread State */
          <div className="w-full flex-1 flex flex-col justify-between py-6 gap-6">
            <div className="flex flex-col gap-6 w-full">
              {/* Thread Header Info */}
              <div className="flex items-center justify-between border-b border-[#262626] pb-3">
                <div className="flex items-center gap-2">
                  <Badge variant="teal">Active Study Session</Badge>
                  <h2 className="text-sm font-semibold text-[#EDEDED] truncate">
                    {createdSession?.title || moduleName}
                  </h2>
                </div>
                {createdSession && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/session/${createdSession.id}`)}
                    className="text-xs"
                  >
                    <span>Full Workspace</span>
                    <ArrowRight size={13} />
                  </Button>
                )}
              </div>

              {/* User's Message Bubble (Right-aligned) */}
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="flex flex-col items-end gap-1.5 self-end max-w-2xl w-full"
              >
                <div className="flex items-center gap-2 text-[11px] text-[#737373] px-1">
                  <span>You</span>
                  <span>•</span>
                  <span>Just now</span>
                </div>

                <div className="p-4 rounded-[14px] bg-[#171717] border border-[#262626] text-sm text-[#EDEDED] shadow-md w-full">
                  {/* Attached file chips in user bubble */}
                  {attachedFiles.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-3 pb-2.5 border-b border-[#262626]">
                      {attachedFiles.map((file) => (
                        <div
                          key={file.id}
                          className="inline-flex items-center gap-2 px-2.5 py-1 rounded-[8px] bg-[#111111] border border-[#262626] text-xs text-[#EDEDED]"
                        >
                          <span className="text-[#2DD4BF] font-mono text-[10px] uppercase font-bold">
                            {file.type}
                          </span>
                          <span className="font-medium truncate max-w-[160px]">{file.name}</span>
                          <span className="text-[10px] text-[#737373]">{file.size}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Truncated Notes Content with Show more toggle */}
                  <InitialNotesContent 
                    content={inputText || attachedFiles.map(f => `[Uploaded notes: ${f.name}]`).join('\n')} 
                    isInitial={true} 
                  />
                </div>
              </motion.div>

              {/* Phase 4: Processing Stepper Card (Left-aligned Mentor Message) */}
              {hasSent && (
                <ProcessingStepperCard
                  notesTitle={moduleName.trim() || 'Untitled Study Session'}
                  simulateErrorStep={simulateErrorStep}
                  simulateZeroConcepts={simulateZeroConcepts}
                  onComplete={handleProcessingComplete}
                  onCancel={handleCancelProcessing}
                  onEditNotes={handleEditNotes}
                />
              )}

              {/* Phase 5: Mentor posts "Your study path" Card */}
              {isProcessingComplete && createdSession && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35, delay: 0.15 }}
                  className="w-full flex justify-start"
                >
                  <StudyPathCard
                    session={createdSession}
                    onUpdateSession={(updatedSession) => {
                      setCreatedSession(updatedSession);
                      updateSession(updatedSession);
                    }}
                    onRegeneratePath={() => {
                      executeSend();
                    }}
                    onStartRecall={() => {
                      setIsRecallActive(true);
                      setTimeout(() => {
                        threadEndRef.current?.scrollIntoView({ behavior: 'smooth' });
                      }, 100);
                    }}
                  />
                </motion.div>
              )}

              {/* Phase 6: Active Recall Flow (Core Experience) */}
              {isRecallActive && createdSession && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35 }}
                  className="w-full flex justify-start"
                >
                  <ActiveRecallFlow
                    session={createdSession}
                    onUpdateSession={(updatedSession) => {
                      setCreatedSession(updatedSession);
                      updateSession(updatedSession);
                    }}
                    onFinish={() => {
                      navigate('/progress');
                    }}
                  />
                </motion.div>
              )}

              <div ref={threadEndRef} />
            </div>

            {/* Bottom-pinned Composer in Thread Mode (Hidden during active recall which has its own recall composer) */}
            {!isRecallActive && (
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="sticky bottom-4 w-full bg-[#171717] rounded-[24px] border border-[#262626] p-3 flex items-center justify-between shadow-2xl"
              >
                <input
                  type="text"
                  placeholder={
                    isProcessing
                      ? "EduMentor is reading notes and building study path..."
                      : "Study path generated. Click 'Start Active Recall' to begin..."
                  }
                  disabled
                  className="bg-transparent text-xs text-[#737373] px-3 w-full outline-none"
                />
                <Button
                  size="sm"
                  disabled={!isProcessingComplete || !createdSession}
                  onClick={() => setIsRecallActive(true)}
                  className="shrink-0 bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] disabled:opacity-40 disabled:cursor-not-allowed font-semibold text-xs"
                >
                  Start Active Recall
                </Button>
              </motion.div>
            )}
          </div>
        )}
      </div>

      {/* Edge Case Validation Modal: Very short input warning (<150 words) */}
      <Dialog
        isOpen={shortInputModalOpen}
        onClose={() => setShortInputModalOpen(false)}
        title="Short Notes Notice"
      >
        <div className="flex flex-col gap-4">
          <div className="flex items-start gap-3 p-3 rounded-[8px] bg-[#FBBF24]/10 border border-[#FBBF24]/30">
            <AlertCircle size={20} className="text-[#FBBF24] shrink-0 mt-0.5" />
            <div className="flex flex-col gap-1 text-xs text-[#EDEDED] leading-relaxed">
              <span className="font-semibold text-[#FBBF24]">Under 150 words detected ({wordCount} words)</span>
              <span>
                EduMentor works best with detailed lecture notes or chapter summaries. With very short text, fewer concepts and prerequisites will be found.
              </span>
            </div>
          </div>

          <p className="text-xs text-[#A3A3A3] leading-relaxed">
            Would you like to continue anyway, or return to add more notes?
          </p>

          <div className="flex items-center justify-end gap-3 pt-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShortInputModalOpen(false)}
            >
              Add more notes
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={executeSend}
              className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6]"
            >
              Continue anyway
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
}
