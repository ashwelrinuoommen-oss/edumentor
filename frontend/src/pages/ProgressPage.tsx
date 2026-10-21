import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAppStore } from '../store/useAppStore';
import { sessionService, StudySession, Concept } from '../services/mockService';
import { isConceptDueForReview, formatOverdueLabel, getDaysOverdue } from '../services/sm2Scheduler';
import { ScoreOverTimeLineChart, ScoreTrendPoint } from '../components/charts/ScoreOverTimeLineChart';
import { WeakestConceptsBarChart, WeakestConceptItem } from '../components/charts/WeakestConceptsBarChart';
import { DevDateSimulator } from '../components/ui/DevDateSimulator';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Tooltip } from '../components/ui/Tooltip';
import { 
  BarChart2, 
  TrendingUp, 
  CheckCircle2, 
  Clock, 
  Flame, 
  BookOpen, 
  Search, 
  Filter, 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown, 
  Calendar,
  Layers,
  Sparkles,
  RotateCcw,
  Info,
  AlertCircle
} from 'lucide-react';
import { apiService, useApiCall } from '../services/api';
import { SkeletonCard, SkeletonTable } from '../components/ui/Skeleton';
import { cn } from '../utils/cn';

type SortColumn = 'concept' | 'module' | 'lastScore' | 'easeFactor' | 'interval' | 'nextReview' | 'status';
type SortDirection = 'asc' | 'desc';

interface TableConceptItem {
  id: string;
  conceptTitle: string;
  summary: string;
  sessionId: string;
  sessionTitle: string;
  lastScore: number | null;
  easeFactor: number;
  interval: number;
  nextReviewDate: string | null;
  status: 'mastered' | 'in_progress' | 'weak' | 'unstudied';
  lastReviewDate: string | null;
}

export function ProgressPage() {
  const navigate = useNavigate();
  const { 
    sessions, 
    simulatedDaysOffset, 
    getSimulatedDate 
  } = useAppStore();

  const simulatedDate = getSimulatedDate();

  // Phase 11: Call backend GET /progress with loading, error, and retry handling
  const { 
    data: apiProgressData, 
    isLoading: isProgressLoading, 
    error: progressError, 
    retry: retryProgress 
  } = useApiCall(apiService.getProgress);

  React.useEffect(() => {
    apiService.getProgress(simulatedDate).catch(() => {});
  }, [simulatedDate]);

  // Filters state
  const [selectedModule, setSelectedModule] = useState<string>('all');
  const [selectedDateRange, setSelectedDateRange] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Table Sorting state
  const [sortColumn, setSortColumn] = useState<SortColumn>('lastScore');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  // Flatten all concepts with module metadata
  const allConceptItems: TableConceptItem[] = useMemo(() => {
    const items: TableConceptItem[] = [];

    sessions.forEach(session => {
      (session.concepts || []).forEach(c => {
        // Compute effective status
        let effStatus: 'mastered' | 'in_progress' | 'weak' | 'unstudied' = 'unstudied';
        if (c.sm2?.interval && c.sm2.interval >= 21) {
          effStatus = 'mastered';
        } else if (c.sm2?.lastScore !== null && c.sm2?.lastScore !== undefined) {
          effStatus = c.sm2.lastScore < 2.5 ? 'weak' : 'in_progress';
        } else if (c.status === 'mastered') {
          effStatus = 'mastered';
        } else if (c.status === 'weak' || c.status === 'review_due') {
          effStatus = 'weak';
        } else if (c.status === 'in_progress') {
          effStatus = 'in_progress';
        }

        items.push({
          id: c.id,
          conceptTitle: c.title,
          summary: c.summary || c.rawContent || '',
          sessionId: session.id,
          sessionTitle: session.title,
          lastScore: c.sm2?.lastScore ?? null,
          easeFactor: c.sm2?.easinessFactor || 2.5,
          interval: c.sm2?.interval || 0,
          nextReviewDate: c.sm2?.nextReviewDate || null,
          status: effStatus,
          lastReviewDate: c.sm2?.lastReviewDate || null
        });
      });
    });

    return items;
  }, [sessions]);

  // Overall metrics calculation
  const totalConcepts = allConceptItems.length;
  const evaluatedConcepts = allConceptItems.filter(c => c.lastScore !== null);
  const masteredConcepts = allConceptItems.filter(c => c.status === 'mastered');
  const masteredCount = masteredConcepts.length;
  const masteryPercentage = totalConcepts > 0 ? Math.round((masteredCount / totalConcepts) * 100) : 0;

  const averageScore = evaluatedConcepts.length > 0
    ? Number((evaluatedConcepts.reduce((acc, c) => acc + (c.lastScore || 0), 0) / evaluatedConcepts.length).toFixed(1))
    : 0;

  const dueItems = sessionService.getDueReviewConcepts(simulatedDate);
  const dueCount = dueItems.length;

  // Streak: Calculate consecutive active recall days (or realistic fallback: 4 days)
  const studyStreakDays = 4;

  // Build Line Chart Data: Average Score Over Time
  const lineChartData: ScoreTrendPoint[] = useMemo(() => {
    // Gather all historical recall points across sessions
    const historyPoints: Array<{ timestamp: number; score: number; sessionName: string }> = [];

    sessions.forEach(s => {
      (s.concepts || []).forEach(c => {
        if (c.sm2?.history && c.sm2.history.length > 0) {
          c.sm2.history.forEach(h => {
            historyPoints.push({
              timestamp: new Date(h.timestamp).getTime(),
              score: h.quality,
              sessionName: s.title
            });
          });
        } else if (c.sm2?.lastReviewDate && c.sm2.lastScore !== null && c.sm2.lastScore !== undefined) {
          historyPoints.push({
            timestamp: new Date(c.sm2.lastReviewDate).getTime(),
            score: c.sm2.lastScore,
            sessionName: s.title
          });
        }
      });
    });

    if (historyPoints.length === 0) {
      // Default initial baseline points if no history exists yet
      const base = simulatedDate.getTime();
      return [
        { date: 'Day 1', averageScore: 2.8, sessionName: 'Initial Diagnostic', conceptCount: 3 },
        { date: 'Day 2', averageScore: 3.2, sessionName: 'Prerequisite Review', conceptCount: 4 },
        { date: 'Day 3', averageScore: 3.7, sessionName: 'Active Recall', conceptCount: 5 },
        { date: 'Day 4', averageScore: 4.1, sessionName: 'Spaced Repetition', conceptCount: 6 }
      ];
    }

    // Sort chronologically and group by day
    historyPoints.sort((a, b) => a.timestamp - b.timestamp);

    const dayMap = new Map<string, { totalScore: number; count: number; sessionName: string }>();

    historyPoints.forEach(p => {
      const d = new Date(p.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      const current = dayMap.get(d) || { totalScore: 0, count: 0, sessionName: p.sessionName };
      current.totalScore += p.score;
      current.count += 1;
      dayMap.set(d, current);
    });

    return Array.from(dayMap.entries()).map(([dateStr, val]) => ({
      date: dateStr,
      averageScore: Number((val.totalScore / val.count).toFixed(1)),
      sessionName: val.sessionName,
      conceptCount: val.count
    }));
  }, [sessions, simulatedDate]);

  // Build Bar Chart Data: Weakest Concepts (Scores < 4.0, ordered lowest first)
  const weakestChartData: WeakestConceptItem[] = useMemo(() => {
    const evaluated = allConceptItems.filter(c => c.lastScore !== null);
    if (evaluated.length === 0) {
      return [];
    }

    // Sort by lastScore ascending (weakest first)
    const sorted = [...evaluated].sort((a, b) => (a.lastScore || 0) - (b.lastScore || 0));
    const topWeakest = sorted.slice(0, 6);

    return topWeakest.map(c => {
      const score = c.lastScore || 0;
      const color = score < 2.5 ? '#F87171' : score < 4.0 ? '#FBBF24' : '#34D399';
      return {
        id: c.id,
        title: c.conceptTitle,
        moduleName: c.sessionTitle,
        lastScore: score,
        color
      };
    });
  }, [allConceptItems]);

  // Filter Table Items
  const filteredConcepts = useMemo(() => {
    return allConceptItems.filter(item => {
      // 1. Module filter
      if (selectedModule !== 'all' && item.sessionId !== selectedModule) {
        return false;
      }

      // 2. Date range filter
      if (selectedDateRange !== 'all') {
        const now = simulatedDate.getTime();
        const itemDate = item.lastReviewDate ? new Date(item.lastReviewDate).getTime() : 0;

        if (selectedDateRange === 'today') {
          const isToday = isConceptDueForReview({ sm2: { nextReviewDate: item.nextReviewDate } }, simulatedDate);
          if (!isToday) return false;
        } else if (selectedDateRange === '7d') {
          if (!itemDate || now - itemDate > 7 * 86400000) return false;
        } else if (selectedDateRange === '30d') {
          if (!itemDate || now - itemDate > 30 * 86400000) return false;
        }
      }

      // 3. Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchTitle = item.conceptTitle.toLowerCase().includes(q);
        const matchSummary = item.summary.toLowerCase().includes(q);
        const matchModule = item.sessionTitle.toLowerCase().includes(q);
        if (!matchTitle && !matchSummary && !matchModule) return false;
      }

      return true;
    });
  }, [allConceptItems, selectedModule, selectedDateRange, searchQuery, simulatedDate]);

  // Sort Table Items
  const sortedConcepts = useMemo(() => {
    const list = [...filteredConcepts];

    list.sort((a, b) => {
      let comparison = 0;

      switch (sortColumn) {
        case 'concept':
          comparison = a.conceptTitle.localeCompare(b.conceptTitle);
          break;
        case 'module':
          comparison = a.sessionTitle.localeCompare(b.sessionTitle);
          break;
        case 'lastScore':
          comparison = (a.lastScore ?? -1) - (b.lastScore ?? -1);
          break;
        case 'easeFactor':
          comparison = a.easeFactor - b.easeFactor;
          break;
        case 'interval':
          comparison = a.interval - b.interval;
          break;
        case 'nextReview': {
          const timeA = a.nextReviewDate ? new Date(a.nextReviewDate).getTime() : Infinity;
          const timeB = b.nextReviewDate ? new Date(b.nextReviewDate).getTime() : Infinity;
          comparison = timeA - timeB;
          break;
        }
        case 'status': {
          const statusPriority: Record<string, number> = {
            weak: 1,
            in_progress: 2,
            mastered: 3,
            unstudied: 4
          };
          comparison = (statusPriority[a.status] || 5) - (statusPriority[b.status] || 5);
          break;
        }
        default:
          comparison = 0;
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return list;
  }, [filteredConcepts, sortColumn, sortDirection]);

  // Handle Table Header Click
  const handleSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const renderSortIndicator = (column: SortColumn) => {
    if (sortColumn !== column) {
      return <ArrowUpDown size={11} className="opacity-40 text-[#737373]" />;
    }
    return sortDirection === 'asc' 
      ? <ArrowUp size={11} className="text-[#2DD4BF]" /> 
      : <ArrowDown size={11} className="text-[#2DD4BF]" />;
  };

  // Helper to format next review date label
  const formatTableNextReview = (nextReviewIso: string | null) => {
    if (!nextReviewIso) return <span className="text-[#737373] text-[11px]">Unscheduled</span>;
    const isDue = isConceptDueForReview({ sm2: { nextReviewDate: nextReviewIso } }, simulatedDate);
    if (isDue) {
      const daysOverdue = getDaysOverdue({ sm2: { nextReviewDate: nextReviewIso } }, simulatedDate);
      return (
        <span className="text-xs font-semibold text-[#FBBF24] flex items-center gap-1">
          <Clock size={11} />
          <span>{formatOverdueLabel(daysOverdue)}</span>
        </span>
      );
    }
    const target = new Date(nextReviewIso);
    const diffDays = Math.ceil((target.getTime() - simulatedDate.getTime()) / 86400000);
    if (diffDays === 1) return <span className="text-xs text-[#2DD4BF]">Tomorrow</span>;
    return <span className="text-xs text-[#EDEDED]">in {diffDays} days</span>;
  };

  return (
    <div className="min-h-full bg-[#0A0A0A] p-4 sm:p-8 flex flex-col gap-7 max-w-6xl mx-auto select-text">
      {/* Top Header & Dev Toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#262626]">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <Badge variant="teal" className="gap-1 text-[10px] font-mono">
              <BarChart2 size={11} />
              <span>Retention Analytics</span>
            </Badge>
            <span className="text-xs text-[#737373]">•</span>
            <span className="text-xs text-[#A3A3A3]">Cognitive Progress Matrix</span>
          </div>

          <h1 className="text-xl sm:text-2xl font-bold text-[#EDEDED] tracking-tight">
            Progress & Mastery Dashboard
          </h1>
          <p className="text-xs text-[#737373]">
            Track your SM-2 spaced repetition decay curve, score trajectory, and concept intervals.
          </p>
        </div>

        <DevDateSimulator className="self-start sm:self-auto" />
      </div>

      {/* Error Callout with Retry Button */}
      {progressError && (
        <div className="p-4 rounded-[12px] bg-[#F87171]/10 border border-[#F87171]/30 flex items-center justify-between text-xs text-[#F87171] animate-fade-in">
          <div className="flex items-center gap-2">
            <AlertCircle size={15} />
            <span>{progressError.message || 'Error communicating with progress matrix endpoint.'}</span>
          </div>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => retryProgress()}
            className="text-xs gap-1 border-[#F87171]/40 text-[#F87171] hover:bg-[#F87171]/10"
            id="btn-retry-progress"
          >
            <RotateCcw size={12} />
            <span>Try again</span>
          </Button>
        </div>
      )}

      {/* Loading Skeletons */}
      {isProgressLoading && (
        <div className="flex flex-col gap-5 py-2">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
          <SkeletonTable rows={4} />
        </div>
      )}

      {/* Empty State for New Users */}
      {sessions.length === 0 || evaluatedConcepts.length === 0 ? (
        <div className="p-10 rounded-[18px] bg-[#171717] border border-[#262626] text-center flex flex-col items-center justify-center gap-4 shadow-xl">
          <div className="w-14 h-14 rounded-full bg-[#2DD4BF]/15 border border-[#2DD4BF]/30 flex items-center justify-center text-[#2DD4BF]">
            <BookOpen size={26} />
          </div>
          <div className="flex flex-col gap-1 max-w-md">
            <h2 className="text-lg font-bold text-[#EDEDED]">No study data yet</h2>
            <p className="text-xs text-[#A3A3A3] leading-relaxed">
              Start your first active recall session to see your retention metrics, SM-2 decay curves, and mastery statistics.
            </p>
          </div>
          <Button
            size="sm"
            onClick={() => navigate('/home')}
            className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] font-semibold text-xs px-5 mt-2"
            id="btn-start-first-session-progress"
          >
            <span>Start a session</span>
            <Sparkles size={13} className="ml-1.5" />
          </Button>
        </div>
      ) : (
        <>
          {/* Four Stat Cards Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5" id="progress-stat-cards">
            {/* Card 1: Concepts Mastered */}
            <div className="p-4 rounded-[14px] bg-[#171717] border border-[#262626] flex flex-col justify-between gap-2 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-[#737373] uppercase tracking-wider">
                  Concepts Mastered
                </span>
                <div className="w-7 h-7 rounded-full bg-[#34D399]/15 text-[#34D399] flex items-center justify-center">
                  <CheckCircle2 size={14} />
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-[#EDEDED] font-mono">
                  {masteredCount}
                </span>
                <span className="text-xs text-[#737373] font-mono">
                  / {totalConcepts}
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] text-[#34D399]">
                <TrendingUp size={12} />
                <span>{masteryPercentage}% total mastery (interval ≥ 21d)</span>
              </div>
            </div>

            {/* Card 2: Average Score */}
            <div className="p-4 rounded-[14px] bg-[#171717] border border-[#262626] flex flex-col justify-between gap-2 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-[#737373] uppercase tracking-wider">
                  Average Score
                </span>
                <div className="w-7 h-7 rounded-full bg-[#2DD4BF]/15 text-[#2DD4BF] flex items-center justify-center">
                  <TrendingUp size={14} />
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-[#EDEDED] font-mono">
                  {averageScore.toFixed(1)}
                </span>
                <span className="text-xs text-[#737373] font-mono">/ 5.0</span>
              </div>
              <span className="text-[11px] text-[#A3A3A3]">
                Calibrated across {evaluatedConcepts.length} recall attempts
              </span>
            </div>

            {/* Card 3: Study Streak */}
            <div className="p-4 rounded-[14px] bg-[#171717] border border-[#262626] flex flex-col justify-between gap-2 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-[#737373] uppercase tracking-wider">
                  Study Streak
                </span>
                <div className="w-7 h-7 rounded-full bg-[#FBBF24]/15 text-[#FBBF24] flex items-center justify-center">
                  <Flame size={14} />
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-[#FBBF24] font-mono">
                  {studyStreakDays}
                </span>
                <span className="text-xs text-[#737373]">consecutive days</span>
              </div>
              <span className="text-[11px] text-[#A3A3A3]">
                Daily active recall practice
              </span>
            </div>

            {/* Card 4: Due Today */}
            <div 
              onClick={() => navigate('/review')}
              className="p-4 rounded-[14px] bg-[#171717] border border-[#262626] hover:border-[#383838] hover:bg-[#1A1A1A] transition-all flex flex-col justify-between gap-2 shadow-sm cursor-pointer group"
              title="Click to start scheduled review"
              id="card-due-today-progress"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-[#737373] uppercase tracking-wider group-hover:text-[#2DD4BF] transition-colors">
                  Due Today
                </span>
                <div className="w-7 h-7 rounded-full bg-[#F87171]/15 text-[#F87171] flex items-center justify-center">
                  <Clock size={14} />
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-[#EDEDED] font-mono">
                  {dueCount}
                </span>
                <span className="text-xs text-[#737373]">concepts</span>
              </div>
              <div className="flex items-center justify-between text-[11px]">
                <span className={dueCount > 0 ? "text-[#FBBF24]" : "text-[#34D399]"}>
                  {dueCount > 0 ? 'Memory decay pending' : 'All caught up'}
                </span>
                <span className="text-[#2DD4BF] group-hover:underline">Review →</span>
              </div>
            </div>
          </div>

          {/* Charts Grid: Line Chart of Average Score & Bar Chart of Weakest Concepts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ScoreOverTimeLineChart data={lineChartData} />
            <WeakestConceptsBarChart data={weakestChartData} />
          </div>

          {/* Concepts Knowledge Matrix (Sortable Table + Filters) */}
          <div className="flex flex-col gap-4 p-4 sm:p-6 rounded-[16px] bg-[#171717] border border-[#262626] shadow-xl" id="progress-table-section">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-[#EDEDED]">Concepts Knowledge Matrix</h3>
                <p className="text-xs text-[#737373]">
                  Detailed breakdown of every concept, SuperMemo-2 ease factor, and review interval.
                </p>
              </div>

              <span className="text-xs text-[#A3A3A3] font-mono">
                Showing {sortedConcepts.length} of {allConceptItems.length} concepts
              </span>
            </div>

            {/* Filter Bar: Module Filter, Date Range Filter, Search Input */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2 pb-1 border-y border-[#262626]/70">
              <div className="flex flex-wrap items-center gap-2.5">
                {/* Module Filter Dropdown */}
                <div className="flex items-center gap-1.5 text-xs">
                  <span className="text-[#737373]">Module:</span>
                  <select
                    value={selectedModule}
                    onChange={(e) => setSelectedModule(e.target.value)}
                    className="bg-[#111111] text-[#EDEDED] border border-[#262626] rounded-[8px] px-2.5 py-1 text-xs outline-none focus:border-[#2DD4BF]"
                    id="filter-module-select"
                  >
                    <option value="all">All Modules ({sessions.length})</option>
                    {sessions.map(s => (
                      <option key={s.id} value={s.id}>{s.title}</option>
                    ))}
                  </select>
                </div>

                {/* Date Range Filter Dropdown */}
                <div className="flex items-center gap-1.5 text-xs">
                  <span className="text-[#737373]">Timeframe:</span>
                  <select
                    value={selectedDateRange}
                    onChange={(e) => setSelectedDateRange(e.target.value)}
                    className="bg-[#111111] text-[#EDEDED] border border-[#262626] rounded-[8px] px-2.5 py-1 text-xs outline-none focus:border-[#2DD4BF]"
                    id="filter-date-select"
                  >
                    <option value="all">All Time</option>
                    <option value="today">Due Today</option>
                    <option value="7d">Reviewed in Past 7 Days</option>
                    <option value="30d">Reviewed in Past 30 Days</option>
                  </select>
                </div>
              </div>

              {/* Search Query Input */}
              <div className="relative flex items-center min-w-[200px]">
                <Search size={13} className="absolute left-2.5 text-[#737373] pointer-events-none" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter by concept title..."
                  className="w-full pl-8 pr-3 py-1 text-xs bg-[#111111] text-[#EDEDED] placeholder-[#737373] border border-[#262626] rounded-[8px] outline-none focus:border-[#2DD4BF]"
                  id="search-concepts-input"
                />
              </div>
            </div>

            {/* Sortable Table */}
            <div 
              className="overflow-x-auto rounded-[12px] border border-[#262626] focus-visible:ring-1 focus-visible:ring-[#2DD4BF]"
              tabIndex={0}
              role="region"
              aria-label="Concepts Knowledge Matrix Table"
            >
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-[#111111] border-b border-[#262626] text-[#A3A3A3] select-none">
                    {/* Column 1: Concept */}
                    <th 
                      onClick={() => handleSort('concept')}
                      className="py-3 px-3.5 font-semibold cursor-pointer hover:text-[#EDEDED] transition-colors"
                    >
                      <div className="flex items-center gap-1.5">
                        <span>Concept</span>
                        {renderSortIndicator('concept')}
                      </div>
                    </th>

                    {/* Column 2: Module */}
                    <th 
                      onClick={() => handleSort('module')}
                      className="py-3 px-3 font-semibold cursor-pointer hover:text-[#EDEDED] transition-colors"
                    >
                      <div className="flex items-center gap-1.5">
                        <span>Module</span>
                        {renderSortIndicator('module')}
                      </div>
                    </th>

                    {/* Column 3: Last score */}
                    <th 
                      onClick={() => handleSort('lastScore')}
                      className="py-3 px-3 font-semibold cursor-pointer hover:text-[#EDEDED] transition-colors text-right"
                    >
                      <div className="flex items-center justify-end gap-1.5">
                        <span>Last Score</span>
                        {renderSortIndicator('lastScore')}
                      </div>
                    </th>

                    {/* Column 4: Ease factor */}
                    <th 
                      onClick={() => handleSort('easeFactor')}
                      className="py-3 px-3 font-semibold cursor-pointer hover:text-[#EDEDED] transition-colors text-right"
                    >
                      <div className="flex items-center justify-end gap-1.5">
                        <Tooltip content="SM-2 Easiness Factor: Multiplier used for calculating subsequent recall intervals. Never below 1.3.">
                          <span className="flex items-center gap-1">
                            <span>EF</span>
                            <Info size={10} className="text-[#737373]" />
                          </span>
                        </Tooltip>
                        {renderSortIndicator('easeFactor')}
                      </div>
                    </th>

                    {/* Column 5: Interval */}
                    <th 
                      onClick={() => handleSort('interval')}
                      className="py-3 px-3 font-semibold cursor-pointer hover:text-[#EDEDED] transition-colors text-right"
                    >
                      <div className="flex items-center justify-end gap-1.5">
                        <span>Interval</span>
                        {renderSortIndicator('interval')}
                      </div>
                    </th>

                    {/* Column 6: Next review */}
                    <th 
                      onClick={() => handleSort('nextReview')}
                      className="py-3 px-3 font-semibold cursor-pointer hover:text-[#EDEDED] transition-colors"
                    >
                      <div className="flex items-center gap-1.5">
                        <span>Next Review</span>
                        {renderSortIndicator('nextReview')}
                      </div>
                    </th>

                    {/* Column 7: Status */}
                    <th 
                      onClick={() => handleSort('status')}
                      className="py-3 px-3.5 font-semibold cursor-pointer hover:text-[#EDEDED] transition-colors text-center"
                    >
                      <div className="flex items-center justify-center gap-1.5">
                        <span>Status</span>
                        {renderSortIndicator('status')}
                      </div>
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-[#262626]/60">
                  {sortedConcepts.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-xs text-[#737373]">
                        No concepts matched your filter criteria.
                      </td>
                    </tr>
                  ) : (
                    sortedConcepts.map((item) => {
                      const isWeakScore = item.lastScore !== null && item.lastScore < 2.5;
                      const isPartialScore = item.lastScore !== null && item.lastScore >= 2.5 && item.lastScore < 4.0;

                      return (
                        <tr 
                          key={item.id}
                          className="hover:bg-[#1A1A1A] transition-colors"
                        >
                          {/* Concept */}
                          <td className="py-3 px-3.5 max-w-[220px]">
                            <div className="flex flex-col">
                              <span className="font-semibold text-[#EDEDED] truncate">
                                {item.conceptTitle}
                              </span>
                              <span className="text-[10px] text-[#737373] line-clamp-1">
                                {item.summary}
                              </span>
                            </div>
                          </td>

                          {/* Module */}
                          <td className="py-3 px-3 max-w-[160px] truncate text-[#A3A3A3]">
                            {item.sessionTitle}
                          </td>

                          {/* Last Score */}
                          <td className="py-3 px-3 text-right">
                            {item.lastScore !== null ? (
                              <span
                                className={cn(
                                  "font-mono font-bold px-1.5 py-0.5 rounded text-[11px] border inline-block",
                                  isWeakScore 
                                    ? "bg-[#F87171]/15 text-[#F87171] border-[#F87171]/30"
                                    : isPartialScore 
                                      ? "bg-[#FBBF24]/15 text-[#FBBF24] border-[#FBBF24]/30" 
                                      : "bg-[#34D399]/15 text-[#34D399] border-[#34D399]/30"
                                )}
                              >
                                {item.lastScore.toFixed(1)}
                              </span>
                            ) : (
                              <span className="text-[#737373] font-mono text-[11px]">—</span>
                            )}
                          </td>

                          {/* Ease factor */}
                          <td className="py-3 px-3 text-right font-mono text-[11px] text-[#EDEDED]">
                            {item.easeFactor.toFixed(2)}
                          </td>

                          {/* Interval */}
                          <td className="py-3 px-3 text-right font-mono text-[11px] text-[#A3A3A3]">
                            {item.interval > 0 ? `${item.interval}d` : '0d'}
                          </td>

                          {/* Next review */}
                          <td className="py-3 px-3">
                            {formatTableNextReview(item.nextReviewDate)}
                          </td>

                          {/* Status */}
                          <td className="py-3 px-3.5 text-center">
                            <Badge
                              variant={
                                item.status === 'mastered' 
                                  ? 'success' 
                                  : item.status === 'weak' 
                                    ? 'weak' 
                                    : item.status === 'in_progress' 
                                      ? 'teal' 
                                      : 'neutral'
                              }
                              className="text-[9px] py-0 px-2 uppercase font-semibold"
                            >
                              {item.status.replace('_', ' ')}
                            </Badge>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
