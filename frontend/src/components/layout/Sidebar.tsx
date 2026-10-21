import React, { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate, useParams } from 'react-router-dom';
import { 
  Plus, 
  Home,
  Clock, 
  BarChart2, 
  Settings, 
  LogOut, 
  Trash2, 
  Edit3, 
  MessageSquare,
  Check,
  X,
  PanelLeftClose,
  PanelLeft,
  ChevronRight,
  MoreVertical,
  Search
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { sessionService, StudySession } from '../../services/mockService';
import { Dialog } from '../ui/Dialog';
import { Button } from '../ui/Button';
import { useToast } from '../ui/Toast';
import { cn } from '../../utils/cn';

// Helper to compute circular mastery ring
function MasteryRing({ percentage }: { percentage: number }) {
  const radius = 7;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative w-4 h-4 shrink-0 flex items-center justify-center" title={`${percentage}% Mastered`}>
      <svg className="w-4 h-4 transform -rotate-90" viewBox="0 0 18 18">
        <circle
          cx="9"
          cy="9"
          r={radius}
          stroke="#262626"
          strokeWidth="2"
          fill="none"
        />
        <circle
          cx="9"
          cy="9"
          r={radius}
          stroke={percentage === 100 ? '#34D399' : '#2DD4BF'}
          strokeWidth="2"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}

export function Sidebar() {
  const navigate = useNavigate();
  const { id: currentSessionId } = useParams<{ id?: string }>();
  const { 
    user, 
    sessions, 
    deleteSession, 
    restoreSession,
    renameSession, 
    logout,
    sidebarCollapsed,
    toggleSidebar,
    mobileSidebarOpen,
    setMobileSidebarOpen,
    simulatedDaysOffset,
    getSimulatedDate
  } = useAppStore();

  const { toast } = useToast();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sessionToDelete, setSessionToDelete] = useState<StudySession | null>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);

  const simulatedDate = getSimulatedDate();
  const dueReviewItems = sessionService.getDueReviewConcepts(simulatedDate);
  const dueCount = dueReviewItems.length;

  // Close user menu on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleStartRename = (e: React.MouseEvent, session: StudySession) => {
    e.stopPropagation();
    setEditingId(session.id);
    setEditingTitle(session.title);
  };

  const handleSaveRename = (e: React.FormEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    if (editingTitle.trim()) {
      renameSession(id, editingTitle.trim());
    }
    setEditingId(null);
  };

  // Confirm delete and trigger Undo toast
  const handleDeleteConfirmed = () => {
    if (!sessionToDelete) return;
    const deleted = sessionToDelete;
    setSessionToDelete(null);
    deleteSession(deleted.id);

    if (currentSessionId === deleted.id) {
      navigate('/home');
    }

    toast({
      title: 'Session deleted',
      description: `"${deleted.title}" was removed.`,
      type: 'info',
      action: {
        label: 'Undo',
        onClick: () => {
          restoreSession(deleted);
        }
      }
    });
  };

  // Filter sessions by search query
  const filteredSessions = searchQuery.trim()
    ? sessions.filter(s => s.title.toLowerCase().includes(searchQuery.toLowerCase().trim()))
    : sessions;

  // Group sessions by: Today (< 24h), Last 7 days (< 7d), Older (> 7d)
  const now = Date.now();
  const ONE_DAY_MS = 24 * 60 * 60 * 1000;
  const SEVEN_DAYS_MS = 7 * ONE_DAY_MS;

  const groupedSessions = filteredSessions.reduce<{
    today: StudySession[];
    last7Days: StudySession[];
    older: StudySession[];
  }>(
    (acc, session) => {
      const createdTime = new Date(session.createdAt || session.updatedAt).getTime();
      const diff = now - createdTime;

      if (diff < ONE_DAY_MS) {
        acc.today.push(session);
      } else if (diff < SEVEN_DAYS_MS) {
        acc.last7Days.push(session);
      } else {
        acc.older.push(session);
      }
      return acc;
    },
    { today: [], last7Days: [], older: [] }
  );

  const renderSessionItem = (session: StudySession) => {
    const isActive = currentSessionId === session.id;
    const isEditing = editingId === session.id;
    const total = session.concepts.length;
    const mastered = session.concepts.filter(c => c.status === 'mastered').length;
    const masteryPct = total > 0 ? Math.round((mastered / total) * 100) : 0;

    if (isEditing) {
      return (
        <form
          key={session.id}
          onSubmit={(e) => handleSaveRename(e, session.id)}
          className="flex items-center gap-1.5 px-2 py-1.5 bg-[#171717] border border-[#2DD4BF] rounded-[8px]"
          onClick={(e) => e.stopPropagation()}
        >
          <input
            type="text"
            value={editingTitle}
            onChange={(e) => setEditingTitle(e.target.value)}
            className="w-full text-xs bg-transparent text-[#EDEDED] outline-none"
            autoFocus
            onBlur={(e) => handleSaveRename(e, session.id)}
          />
          <button type="submit" className="text-[#34D399] p-0.5 hover:bg-[#262626] rounded">
            <Check size={12} />
          </button>
          <button 
            type="button" 
            onClick={() => setEditingId(null)}
            className="text-[#737373] p-0.5 hover:bg-[#262626] rounded"
          >
            <X size={12} />
          </button>
        </form>
      );
    }

    return (
      <div
        key={session.id}
        onClick={() => {
          navigate(`/session/${session.id}`);
          setMobileSidebarOpen(false);
        }}
        className={cn(
          'group flex items-center justify-between px-2.5 py-2 rounded-[8px] cursor-pointer text-xs transition-colors duration-150',
          'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none',
          isActive
            ? 'bg-[#171717] text-[#EDEDED] border border-[#262626]'
            : 'text-[#A3A3A3] hover:bg-[#171717] hover:text-[#EDEDED]'
        )}
        tabIndex={0}
      >
        <div className="flex items-center gap-2 min-w-0 pr-1">
          <MasteryRing percentage={masteryPct} />
          <span className="truncate text-xs" title={session.title}>
            {session.title}
          </span>
        </div>

        {/* Hover Menu with Rename and Delete */}
        <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity shrink-0">
          <button
            type="button"
            title="Rename session"
            onClick={(e) => handleStartRename(e, session)}
            className="p-1 text-[#737373] hover:text-[#2DD4BF] rounded transition-colors"
          >
            <Edit3 size={12} />
          </button>
          <button
            type="button"
            title="Delete session"
            onClick={(e) => {
              e.stopPropagation();
              setSessionToDelete(session);
            }}
            className="p-1 text-[#737373] hover:text-[#F87171] rounded transition-colors"
            id={`btn-delete-session-${session.id}`}
          >
            <Trash2 size={12} />
          </button>
        </div>
      </div>
    );
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-[#111111] border-r border-[#262626] select-none">
      {/* Top Header: Wordmark & Collapse Toggle */}
      <div className="p-4 border-b border-[#262626] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-[6px] bg-[#2DD4BF]/15 border border-[#2DD4BF]/40 flex items-center justify-center shrink-0">
            <div className="w-2.5 h-2.5 bg-[#2DD4BF] rotate-45 rounded-[1px]" />
          </div>
          {!sidebarCollapsed && (
            <div>
              <h1 className="text-base font-semibold text-[#EDEDED] tracking-tight">EduMentor</h1>
              <p className="text-[10px] text-[#737373] tracking-wide">Study. Recall. Master.</p>
            </div>
          )}
        </div>

        {/* Desktop Collapse Toggle */}
        <button
          type="button"
          onClick={toggleSidebar}
          className="hidden md:flex p-1.5 rounded-md text-[#737373] hover:text-[#EDEDED] hover:bg-[#1F1F1F] transition-colors focus-visible:ring-2 focus-visible:ring-[#2DD4BF]"
          title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {sidebarCollapsed ? <PanelLeft size={15} /> : <PanelLeftClose size={15} />}
        </button>

        {/* Mobile Close Button */}
        <button
          type="button"
          onClick={() => setMobileSidebarOpen(false)}
          className="md:hidden p-1.5 rounded-md text-[#737373] hover:text-[#EDEDED] transition-colors"
          title="Close drawer"
        >
          <X size={16} />
        </button>
      </div>

      {/* New Session Button (Teal Outline) */}
      <div className="p-3">
        <NavLink
          to="/home"
          onClick={() => setMobileSidebarOpen(false)}
          className={({ isActive }) => cn(
            'flex items-center justify-center gap-2 w-full py-2 px-3 text-xs font-semibold rounded-[10px] transition-colors duration-150',
            'border border-[#2DD4BF] text-[#2DD4BF] hover:bg-[#2DD4BF]/10',
            'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none',
            isActive && 'bg-[#2DD4BF]/15'
          )}
          id="btn-sidebar-new-session"
          title="New session"
        >
          <Plus size={15} />
          {!sidebarCollapsed && <span>New session</span>}
        </NavLink>
      </div>

      {/* Navigation Items: Home, Review (with badge), Progress */}
      <nav aria-label="Main Navigation" className="px-3 py-1 flex flex-col gap-1 border-b border-[#262626]/70 pb-3">
        <NavLink
          to="/home"
          onClick={() => setMobileSidebarOpen(false)}
          className={({ isActive }) => cn(
            'flex items-center gap-2.5 px-3 py-2 text-xs font-medium rounded-[8px] transition-colors duration-150',
            'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none',
            isActive ? 'bg-[#171717] text-[#EDEDED] border border-[#262626]' : 'text-[#A3A3A3] hover:text-[#EDEDED] hover:bg-[#171717]'
          )}
          title="Home"
        >
          <Home size={15} className="text-[#2DD4BF] shrink-0" />
          {!sidebarCollapsed && <span>Home</span>}
        </NavLink>

        <NavLink
          to="/review"
          onClick={() => setMobileSidebarOpen(false)}
          className={({ isActive }) => cn(
            'flex items-center justify-between px-3 py-2 text-xs font-medium rounded-[8px] transition-colors duration-150',
            'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none',
            isActive ? 'bg-[#171717] text-[#EDEDED] border border-[#262626]' : 'text-[#A3A3A3] hover:text-[#EDEDED] hover:bg-[#171717]'
          )}
          title={`Review (${dueCount} due today)`}
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <Clock size={15} className={dueCount > 0 ? "text-[#FBBF24] shrink-0" : "text-[#737373] shrink-0"} />
            {!sidebarCollapsed && <span>Review</span>}
          </div>
          {!sidebarCollapsed && (
            dueCount > 0 ? (
              <span className="px-1.5 py-0.2 text-[10px] font-bold rounded-full bg-[#FBBF24]/20 text-[#FBBF24] border border-[#FBBF24]/30">
                {dueCount}
              </span>
            ) : (
              <span className="text-[11px] text-[#737373]">0</span>
            )
          )}
        </NavLink>

        <NavLink
          to="/progress"
          onClick={() => setMobileSidebarOpen(false)}
          className={({ isActive }) => cn(
            'flex items-center gap-2.5 px-3 py-2 text-xs font-medium rounded-[8px] transition-colors duration-150',
            'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none',
            isActive ? 'bg-[#171717] text-[#EDEDED] border border-[#262626]' : 'text-[#A3A3A3] hover:text-[#EDEDED] hover:bg-[#171717]'
          )}
          title="Progress"
        >
          <BarChart2 size={15} className="text-[#34D399] shrink-0" />
          {!sidebarCollapsed && <span>Progress</span>}
        </NavLink>
      </nav>

      {/* Session Search Box */}
      {!sidebarCollapsed && (
        <div className="px-3 pt-2 pb-1">
          <div className="relative flex items-center">
            <Search size={13} className="absolute left-2.5 text-[#737373] pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search sessions..."
              className="w-full pl-8 pr-7 py-1.5 text-xs bg-[#171717] text-[#EDEDED] placeholder-[#737373] border border-[#262626] rounded-[8px] outline-none focus:border-[#2DD4BF] transition-colors"
              id="input-search-sessions-sidebar"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-2 text-[#737373] hover:text-[#EDEDED] p-0.5 rounded"
                title="Clear search"
              >
                <X size={12} />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Scrollable Sessions List (Grouped by Today, Last 7 days, Older) */}
      {!sidebarCollapsed && (
        <div className="flex-1 overflow-y-auto px-3 py-2 flex flex-col gap-3">
          {/* Today Group */}
          {groupedSessions.today.length > 0 && (
            <div className="flex flex-col gap-1">
              <span className="px-2 text-[10px] font-bold tracking-wider text-[#737373] uppercase">
                Today
              </span>
              {groupedSessions.today.map(renderSessionItem)}
            </div>
          )}

          {/* Last 7 Days Group */}
          {groupedSessions.last7Days.length > 0 && (
            <div className="flex flex-col gap-1">
              <span className="px-2 text-[10px] font-bold tracking-wider text-[#737373] uppercase">
                Last 7 days
              </span>
              {groupedSessions.last7Days.map(renderSessionItem)}
            </div>
          )}

          {/* Older Group */}
          {groupedSessions.older.length > 0 && (
            <div className="flex flex-col gap-1">
              <span className="px-2 text-[10px] font-bold tracking-wider text-[#737373] uppercase">
                Older
              </span>
              {groupedSessions.older.map(renderSessionItem)}
            </div>
          )}

          {filteredSessions.length === 0 && (
            <div className="p-4 text-center text-xs text-[#737373] flex flex-col items-center gap-2">
              <MessageSquare size={18} className="text-[#383838]" />
              <p>
                {searchQuery.trim() ? `No sessions matching "${searchQuery}"` : 'No study sessions yet.'}
              </p>
              {searchQuery.trim() ? (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="text-[11px] text-[#2DD4BF] hover:underline"
                >
                  Clear search
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    navigate('/home');
                    setMobileSidebarOpen(false);
                  }}
                  className="text-[11px] text-[#2DD4BF] hover:underline"
                >
                  Create your first session
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Collapsed spacer */}
      {sidebarCollapsed && <div className="flex-1" />}

      {/* Bottom User Area with Avatar & Dropdown Menu */}
      <div className="p-3 border-t border-[#262626] bg-[#0A0A0A] relative" ref={userMenuRef}>
        <div
          onClick={() => setUserMenuOpen(!userMenuOpen)}
          className={cn(
            'flex items-center justify-between p-1.5 rounded-[8px] cursor-pointer hover:bg-[#171717] transition-colors',
            'focus-visible:ring-2 focus-visible:ring-[#2DD4BF] focus-visible:outline-none'
          )}
          tabIndex={0}
          title={user?.name || 'Account'}
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-full bg-[#171717] border border-[#262626] flex items-center justify-center text-xs font-semibold text-[#2DD4BF] shrink-0">
              {user?.name ? user.name[0] : 'U'}
            </div>
            {!sidebarCollapsed && (
              <div className="truncate text-left">
                <div className="text-xs font-medium text-[#EDEDED] truncate">{user?.name || 'Alex Rivera'}</div>
                <div className="text-[10px] text-[#737373] truncate">{user?.email || 'alex@edumentor.app'}</div>
              </div>
            )}
          </div>
          {!sidebarCollapsed && <MoreVertical size={14} className="text-[#737373]" />}
        </div>

        {/* Dropdown Menu (Settings & Logout) */}
        {userMenuOpen && (
          <div className="absolute bottom-full left-3 right-3 mb-2 bg-[#171717] border border-[#262626] rounded-[10px] shadow-xl overflow-hidden z-50 flex flex-col p-1 animate-fade-in">
            <button
              type="button"
              onClick={() => {
                setUserMenuOpen(false);
                navigate('/settings');
                setMobileSidebarOpen(false);
              }}
              className="flex items-center gap-2.5 px-3 py-2 text-xs text-[#A3A3A3] hover:text-[#EDEDED] hover:bg-[#262626] rounded-md transition-colors text-left"
            >
              <Settings size={14} className="text-[#737373]" />
              <span>Settings</span>
            </button>
            <div className="my-1 border-t border-[#262626]" />
            <button
              type="button"
              onClick={handleLogout}
              className="flex items-center gap-2.5 px-3 py-2 text-xs text-[#F87171] hover:bg-[#F87171]/10 rounded-md transition-colors text-left"
            >
              <LogOut size={14} />
              <span>Log out</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside 
        aria-label="Sidebar navigation"
        className={cn(
          'hidden md:block h-full transition-all duration-200 ease-out z-20',
          sidebarCollapsed ? 'w-[64px] min-w-[64px]' : 'w-[280px] min-w-[280px]'
        )}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Overlay */}
      {mobileSidebarOpen && (
        <div 
          className="fixed inset-0 z-50 flex md:hidden bg-black/75 backdrop-blur-sm"
          onClick={() => setMobileSidebarOpen(false)}
        >
          <div 
            className="w-[280px] h-full bg-[#111111] border-r border-[#262626] shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {sidebarContent}
          </div>
        </div>
      )}

      {/* Phase 9: Delete Session Confirmation Dialog */}
      <Dialog
        isOpen={Boolean(sessionToDelete)}
        onClose={() => setSessionToDelete(null)}
        title="Delete Study Session"
      >
        <div className="flex flex-col gap-4 text-xs">
          <p className="text-[#EDEDED] leading-relaxed">
            Are you sure you want to delete <strong className="text-[#EDEDED]">"{sessionToDelete?.title}"</strong>?
          </p>
          <p className="text-[#A3A3A3] leading-relaxed">
            This will permanently remove this session, its {sessionToDelete?.concepts.length || 0} concepts, and their spaced repetition schedules from your review queue.
          </p>
          <div className="flex items-center justify-end gap-2.5 pt-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setSessionToDelete(null)}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleDeleteConfirmed}
              className="bg-[#F87171] text-white hover:bg-[#ef4444] font-semibold text-xs px-4"
              id="btn-confirm-delete-session"
            >
              Delete session
            </Button>
          </div>
        </div>
      </Dialog>
    </>
  );
}
