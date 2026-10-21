/**
 * SuperMemo-2 (SM-2) Spaced Repetition Scheduling Engine
 * Fully adheres to Phase 7 specifications:
 * - Quality q is the final score rounded to 0..5
 * - If q < 3: repetitions reset to 0, interval becomes 1 day
 * - Otherwise: repetition 1 gives interval 1, repetition 2 gives 6, later give round(prev * ef)
 * - ef = ef + (0.1 - (5-q) * (0.08 + (5-q) * 0.02)), never below 1.3, starting at 2.5
 * - Mastered means interval of 21 days or more
 * - Supports simulated base dates for time-travel testing
 */

export interface SM2Data {
  repetition: number;
  interval: number;
  easinessFactor: number;
  nextReviewDate: string | null;
  lastReviewDate?: string | null;
  lastScore?: number | null;
  history?: Array<{
    timestamp: string;
    quality: number;
    interval: number;
    repetition: number;
    easinessFactor: number;
  }>;
}

export const SM2_CONFIG = {
  DEFAULT_EASINESS_FACTOR: 2.5,
  MIN_EASINESS_FACTOR: 1.3,
  INITIAL_INTERVAL_1: 1, // 1 day
  INITIAL_INTERVAL_2: 6, // 6 days
  MASTERED_INTERVAL_THRESHOLD: 21 // 21 days or more = mastered
};

/**
 * Calculates updated SM-2 parameters after a recall attempt.
 * @param currentSM2 Existing SM-2 state
 * @param quality Score 0-5 (will be rounded to 0..5)
 * @param baseDate Date of the attempt (defaults to now, or simulated date)
 */
export function calculateSM2(
  currentSM2: Partial<SM2Data> = {},
  quality: number,
  baseDate: Date = new Date()
): SM2Data {
  const currentRep = currentSM2.repetition || 0;
  const currentInterval = currentSM2.interval || 0;
  const currentEF = currentSM2.easinessFactor || SM2_CONFIG.DEFAULT_EASINESS_FACTOR;

  // Quality q is the final score rounded to 0..5
  const q = Math.max(0, Math.min(5, Math.round(quality)));

  let nextRepetition = 0;
  let nextInterval = 0;

  if (q < 3) {
    // If q is below 3, repetitions reset to 0 and interval becomes 1 day
    nextRepetition = 0;
    nextInterval = 1;
  } else {
    // Otherwise repetition 1 gives interval 1, repetition 2 gives 6,
    // and later repetitions give round(previous interval times ease factor).
    if (currentRep === 0) {
      nextInterval = SM2_CONFIG.INITIAL_INTERVAL_1;
      nextRepetition = 1;
    } else if (currentRep === 1) {
      nextInterval = SM2_CONFIG.INITIAL_INTERVAL_2;
      nextRepetition = 2;
    } else {
      nextInterval = Math.round(currentInterval * currentEF);
      nextRepetition = currentRep + 1;
    }
  }

  // Ease factor update: ef = ef + (0.1 - (5-q) * (0.08 + (5-q) * 0.02)), never below 1.3, starting at 2.5.
  let nextEF = currentEF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));
  if (nextEF < SM2_CONFIG.MIN_EASINESS_FACTOR) {
    nextEF = SM2_CONFIG.MIN_EASINESS_FACTOR;
  }

  const base = new Date(baseDate);
  const nextReview = new Date(base.getTime() + nextInterval * 24 * 60 * 60 * 1000);

  const historyItem = {
    timestamp: base.toISOString(),
    quality: q,
    interval: nextInterval,
    repetition: nextRepetition,
    easinessFactor: Number(nextEF.toFixed(2))
  };

  return {
    repetition: nextRepetition,
    interval: nextInterval,
    easinessFactor: Number(nextEF.toFixed(2)),
    nextReviewDate: nextReview.toISOString(),
    lastReviewDate: base.toISOString(),
    lastScore: Number(quality.toFixed ? quality.toFixed(1) : quality),
    history: [...(currentSM2.history || []), historyItem]
  };
}

/**
 * Determines concept learning status based on SM-2 interval and recall score
 */
export function getConceptStatus(
  interval: number,
  score: number | null
): 'unstudied' | 'in_progress' | 'mastered' | 'weak' {
  if (interval >= SM2_CONFIG.MASTERED_INTERVAL_THRESHOLD) {
    return 'mastered';
  }
  if (score !== null && score < 3) {
    return 'weak';
  }
  if (interval > 0) {
    return 'in_progress';
  }
  return 'unstudied';
}

/**
 * Checks if a concept is due for review based on its nextReviewDate and the simulated date.
 */
export function isConceptDueForReview(
  concept: { sm2?: { nextReviewDate?: string | null }; status?: string },
  simulatedDate: Date = new Date()
): boolean {
  if (!concept.sm2 || !concept.sm2.nextReviewDate) return false;
  const targetDate = new Date(concept.sm2.nextReviewDate);
  return targetDate <= new Date(simulatedDate);
}

/**
 * Calculates how many days overdue a concept is relative to the simulated date.
 * Returns 0 if due today, or a positive integer if overdue.
 */
export function getDaysOverdue(
  concept: { sm2?: { nextReviewDate?: string | null } },
  simulatedDate: Date = new Date()
): number {
  if (!concept.sm2 || !concept.sm2.nextReviewDate) return 0;
  const targetDate = new Date(concept.sm2.nextReviewDate);
  const sim = new Date(simulatedDate);

  // Normalize to calendar day difference (midnight to midnight)
  const targetMidnight = new Date(targetDate.getFullYear(), targetDate.getMonth(), targetDate.getDate()).getTime();
  const simMidnight = new Date(sim.getFullYear(), sim.getMonth(), sim.getDate()).getTime();

  const diffMs = simMidnight - targetMidnight;
  const days = Math.floor(diffMs / (24 * 60 * 60 * 1000));
  return Math.max(0, days);
}

/**
 * Formats overdue badge text: e.g. "Due today", "1 day overdue", "3 days overdue"
 */
export function formatOverdueLabel(daysOverdue: number): string {
  if (daysOverdue <= 0) return 'Due today';
  if (daysOverdue === 1) return '1 day overdue';
  return `${daysOverdue} days overdue`;
}

/**
 * Finds the earliest upcoming review date among all concepts that is strictly in the future.
 */
export function getNextUpcomingReviewDate(
  sessions: Array<{ concepts?: Array<{ sm2?: { nextReviewDate?: string | null } }> }>,
  simulatedDate: Date = new Date()
): string | null {
  const sim = new Date(simulatedDate).getTime();
  let earliestFutureTime: number | null = null;

  sessions.forEach(session => {
    (session.concepts || []).forEach(concept => {
      if (concept.sm2?.nextReviewDate) {
        const time = new Date(concept.sm2.nextReviewDate).getTime();
        if (time > sim) {
          if (earliestFutureTime === null || time < earliestFutureTime) {
            earliestFutureTime = time;
          }
        }
      }
    });
  });

  if (!earliestFutureTime) return null;
  return new Date(earliestFutureTime).toISOString();
}

export interface DayTimelineItem {
  dayOffset: number;
  date: Date;
  dateFormatted: string;
  dayOfWeek: string;
  count: number;
  conceptTitles: string[];
}

/**
 * Generates upcoming-reviews timeline data for the next 14 days.
 */
export function getUpcoming14DaysTimeline(
  sessions: Array<{ concepts?: Array<{ title: string; sm2?: { nextReviewDate?: string | null } }> }>,
  simulatedDate: Date = new Date()
): DayTimelineItem[] {
  const timeline: DayTimelineItem[] = [];
  const base = new Date(simulatedDate);

  for (let offset = 1; offset <= 14; offset++) {
    const dayDate = new Date(base.getFullYear(), base.getMonth(), base.getDate() + offset);
    const dayStart = dayDate.getTime();
    const dayEnd = dayStart + 24 * 60 * 60 * 1000;

    const matchedTitles: string[] = [];

    sessions.forEach(session => {
      (session.concepts || []).forEach(concept => {
        if (concept.sm2?.nextReviewDate) {
          const revTime = new Date(concept.sm2.nextReviewDate).getTime();
          if (revTime >= dayStart && revTime < dayEnd) {
            matchedTitles.push(concept.title);
          }
        }
      });
    });

    timeline.push({
      dayOffset: offset,
      date: dayDate,
      dateFormatted: dayDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      dayOfWeek: dayDate.toLocaleDateString(undefined, { weekday: 'short' }),
      count: matchedTitles.length,
      conceptTitles: matchedTitles
    });
  }

  return timeline;
}
