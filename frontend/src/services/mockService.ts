/**
 * EduMentor Mock Service Layer
 * Switched by one flag (USE_MOCK).
 * Persists all mock data in localStorage. Never puts secrets in front-end code.
 */

import { SAMPLE_NOTE_SETS } from '../data/sampleNotes';
import { extractConceptsFromText } from './conceptExtractor';
import { calculateSM2, isConceptDueForReview, getDaysOverdue } from './sm2Scheduler';

export const USE_MOCK = true; // Environment toggle flag

const STORAGE_KEY_AUTH = 'edumentor_auth_session_v1';
const STORAGE_KEY_USERS = 'edumentor_registered_users_v1';
const STORAGE_KEY_SESSIONS = 'edumentor_sessions_v3';

export const SESSION_DURATION_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  dailyReviewGoal?: number;
  preferredReviewTime?: string;
}

export interface AuthSession {
  token: string;
  user: User;
  expiresAt: number; // Unix timestamp in ms
}

interface StoredUser extends User {
  passwordHash: string;
}

export interface Concept {
  id: string;
  title: string;
  summary: string;
  rawContent?: string;
  keyTerms: string[];
  prerequisites: string[];
  prerequisiteIds?: string[];
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  estTimeMinutes: number;
  orderIndex: number;
  status: 'unstudied' | 'in_progress' | 'mastered' | 'review_due';
  sm2: {
    repetition: number;
    interval: number;
    easinessFactor: number;
    nextReviewDate: string | null;
    lastScore: number | null;
    history: Array<{
      timestamp: string;
      quality: number;
      interval: number;
      repetition: number;
      easinessFactor: number;
    }>;
  };
}

export interface FileAttachment {
  name: string;
  size: string; // e.g. "245 KB"
  type: string; // "pdf" | "txt" | "md" | "docx"
}

export interface ChatMessage {
  id: string;
  role: 'mentor' | 'student' | 'system';
  content: string;
  timestamp: string;
  conceptId?: string;
  attachments?: FileAttachment[];
  isInitialNotes?: boolean;
  evaluation?: {
    overallScore: number; // 0 - 100
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
    keywordCoverage: {
      matched: string[];
      missed: string[];
      score: number;
    };
    semanticScore: number;
    aiJudgeNotes: string;
    encouragement: string;
  };
}

export interface StudySession {
  id: string;
  title: string;
  category: string;
  icon?: string;
  notes: string;
  concepts: Concept[];
  messages: ChatMessage[];
  currentConceptIndex: number;
  createdAt: string;
  updatedAt: string;
}

// Default Demo User & Registered Accounts
const DEFAULT_REGISTERED_USERS: StoredUser[] = [
  {
    id: 'usr_demo_42',
    name: 'Alex Rivera',
    email: 'alex@edumentor.app',
    passwordHash: 'password123',
    createdAt: new Date(Date.now() - 30 * 86400000).toISOString(),
    dailyReviewGoal: 10,
    preferredReviewTime: '09:00'
  }
];

/**
 * Initializes Mock Database with realistic sessions & registered users
 */
export function initMockDatabase(): { 
  user: User | null; 
  sessions: StudySession[]; 
  sessionExpired: boolean 
} {
  // Ensure default registered users exist
  try {
    const rawUsers = localStorage.getItem(STORAGE_KEY_USERS);
    if (!rawUsers) {
      localStorage.setItem(STORAGE_KEY_USERS, JSON.stringify(DEFAULT_REGISTERED_USERS));
    }
  } catch (e) {
    console.error('Error initializing registered users:', e);
  }

  // Check current session
  let user: User | null = null;
  let sessionExpired = false;

  try {
    const rawSession = localStorage.getItem(STORAGE_KEY_AUTH);
    if (rawSession) {
      const authSession: AuthSession = JSON.parse(rawSession);
      const now = Date.now();
      if (authSession.expiresAt && now > authSession.expiresAt) {
        // Session expired (older than 7 days)
        sessionExpired = true;
        localStorage.removeItem(STORAGE_KEY_AUTH);
        user = null;
      } else {
        user = authSession.user;
      }
    } else {
      // Auto-seed active session for immediate seamless testing
      const newSession: AuthSession = {
        token: `tok_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
        user: DEFAULT_REGISTERED_USERS[0],
        expiresAt: Date.now() + SESSION_DURATION_MS
      };
      localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(newSession));
      user = newSession.user;
    }
  } catch {
    user = null;
  }

  // Load Sessions
  let sessions: StudySession[] = [];
  try {
    const rawSessions = localStorage.getItem(STORAGE_KEY_SESSIONS);
    if (rawSessions) {
      sessions = JSON.parse(rawSessions);
    } else {
      sessions = SAMPLE_NOTE_SETS.map((sample, sIdx) => {
        const concepts = extractConceptsFromText(sample.content, sample.title) as Concept[];
        
        // Enrich the first session (Operating Systems) with realistic SM-2 spaced repetition state
        if (sIdx === 0 && concepts.length >= 6) {
          const nowMs = Date.now();
          // Concept 0: "Process" -> Due today, score 2.2, weak
          concepts[0].sm2 = {
            repetition: 1,
            interval: 1,
            easinessFactor: 2.3,
            nextReviewDate: new Date(nowMs - 2 * 3600 * 1000).toISOString(),
            lastReviewDate: new Date(nowMs - 26 * 3600 * 1000).toISOString(),
            lastScore: 2.2,
            history: [{ timestamp: new Date(nowMs - 26 * 3600 * 1000).toISOString(), quality: 2, interval: 1, repetition: 1, easinessFactor: 2.3 }]
          };
          concepts[0].status = 'weak';

          // Concept 1: "Virtual Memory" -> 1 day overdue, score 1.8, weak
          concepts[1].sm2 = {
            repetition: 0,
            interval: 1,
            easinessFactor: 2.1,
            nextReviewDate: new Date(nowMs - 28 * 3600 * 1000).toISOString(),
            lastReviewDate: new Date(nowMs - 52 * 3600 * 1000).toISOString(),
            lastScore: 1.8,
            history: [{ timestamp: new Date(nowMs - 52 * 3600 * 1000).toISOString(), quality: 1, interval: 1, repetition: 0, easinessFactor: 2.1 }]
          };
          concepts[1].status = 'weak';

          // Concept 2: "Page Fault" -> Due today, score 2.7, in_progress
          concepts[2].sm2 = {
            repetition: 1,
            interval: 1,
            easinessFactor: 2.4,
            nextReviewDate: new Date(nowMs - 1 * 3600 * 1000).toISOString(),
            lastReviewDate: new Date(nowMs - 25 * 3600 * 1000).toISOString(),
            lastScore: 2.7,
            history: [{ timestamp: new Date(nowMs - 25 * 3600 * 1000).toISOString(), quality: 3, interval: 1, repetition: 1, easinessFactor: 2.4 }]
          };
          concepts[2].status = 'in_progress';

          // Concept 3: "Paging" -> Due in 1 day (+1d)
          concepts[3].sm2 = {
            repetition: 2,
            interval: 1,
            easinessFactor: 2.5,
            nextReviewDate: new Date(nowMs + 24 * 3600 * 1000).toISOString(),
            lastReviewDate: new Date(nowMs).toISOString(),
            lastScore: 3.8,
            history: [{ timestamp: new Date().toISOString(), quality: 4, interval: 1, repetition: 2, easinessFactor: 2.5 }]
          };
          concepts[3].status = 'in_progress';

          // Concept 4: Due in 3 days (+3d)
          concepts[4].sm2 = {
            repetition: 2,
            interval: 3,
            easinessFactor: 2.5,
            nextReviewDate: new Date(nowMs + 3 * 24 * 3600 * 1000).toISOString(),
            lastReviewDate: new Date(nowMs).toISOString(),
            lastScore: 4.2,
            history: [{ timestamp: new Date().toISOString(), quality: 4, interval: 3, repetition: 2, easinessFactor: 2.5 }]
          };
          concepts[4].status = 'in_progress';

          // Concept 5: Due in 7 days (+7d)
          concepts[5].sm2 = {
            repetition: 2,
            interval: 7,
            easinessFactor: 2.6,
            nextReviewDate: new Date(nowMs + 7 * 24 * 3600 * 1000).toISOString(),
            lastReviewDate: new Date(nowMs).toISOString(),
            lastScore: 4.8,
            history: [{ timestamp: new Date().toISOString(), quality: 5, interval: 7, repetition: 2, easinessFactor: 2.6 }]
          };
          concepts[5].status = 'in_progress';
        }

        const initialMessages: ChatMessage[] = [
          {
            id: `msg-seed-${Date.now()}-1`,
            role: 'mentor',
            content: `Welcome to your active recall session on **${sample.title}**.\n\nWe will work through ${concepts.length} ordered concepts. In active recall, you recall principles in your own words rather than re-reading notes. Let's begin with concept 1: **${concepts[0]?.title || 'Fundamentals'}**.\n\nIn your own words, how would you define this and why does it matter?`,
            timestamp: new Date().toISOString(),
            conceptId: concepts[0]?.id
          }
        ];

        return {
          id: sample.id,
          title: sample.title,
          category: sample.category,
          icon: sample.icon,
          notes: sample.content,
          concepts: concepts,
          messages: sIdx === 0 ? initialMessages : [],
          currentConceptIndex: 0,
          createdAt: new Date(Date.now() - (sIdx + 1) * 86400000).toISOString(),
          updatedAt: new Date().toISOString()
        };
      });

      localStorage.setItem(STORAGE_KEY_SESSIONS, JSON.stringify(sessions));
    }
  } catch (err) {
    console.error('Error loading mock sessions:', err);
  }

  return { user, sessions, sessionExpired };
}

/* ==========================================================================
   Auth Services
   ========================================================================== */
export const authService = {
  getRegisteredUsers(): StoredUser[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY_USERS);
      return raw ? JSON.parse(raw) : DEFAULT_REGISTERED_USERS;
    } catch {
      return DEFAULT_REGISTERED_USERS;
    }
  },

  getCurrentSession(): { user: User | null; isExpired: boolean; token: string | null } {
    try {
      const raw = localStorage.getItem(STORAGE_KEY_AUTH);
      if (!raw) return { user: null, isExpired: false, token: null };

      const session: AuthSession = JSON.parse(raw);
      if (session.expiresAt && Date.now() > session.expiresAt) {
        localStorage.removeItem(STORAGE_KEY_AUTH);
        return { user: null, isExpired: true, token: null };
      }
      return { user: session.user, isExpired: false, token: session.token };
    } catch {
      return { user: null, isExpired: false, token: null };
    }
  },

  async login(email: string, password?: string, rememberMe = true): Promise<User> {
    await new Promise(r => setTimeout(r, 300)); // Simulate network latency

    const users = this.getRegisteredUsers();
    const cleanEmail = email.trim().toLowerCase();

    // Check credentials
    const found = users.find(u => u.email.toLowerCase() === cleanEmail);

    // If demo email or matching user
    if (!found) {
      // For demo convenience: if user enters demo password or standard credentials, allow
      if (cleanEmail === 'alex@edumentor.app' && (!password || password === 'password123' || password === 'demo')) {
        const demoUser = DEFAULT_REGISTERED_USERS[0];
        this.saveAuthSession(demoUser, rememberMe);
        return demoUser;
      }
      throw new Error('Email or password is incorrect');
    }

    if (password && password !== found.passwordHash && password !== 'password123' && password !== 'demo') {
      throw new Error('Email or password is incorrect');
    }

    this.saveAuthSession(found, rememberMe);
    return found;
  },

  async signup(name: string, email: string, password?: string): Promise<User> {
    await new Promise(r => setTimeout(r, 350));

    const users = this.getRegisteredUsers();
    const cleanEmail = email.trim().toLowerCase();

    // Duplicate check
    const existing = users.find(u => u.email.toLowerCase() === cleanEmail);
    if (existing) {
      throw new Error('An account with this email already exists.');
    }

    const newUser: StoredUser = {
      id: `usr_${Date.now()}`,
      name: name.trim() || 'Learner',
      email: cleanEmail,
      passwordHash: password || 'password123',
      createdAt: new Date().toISOString()
    };

    users.push(newUser);
    localStorage.setItem(STORAGE_KEY_USERS, JSON.stringify(users));

    this.saveAuthSession(newUser, true);
    return newUser;
  },

  async logout(): Promise<void> {
    localStorage.removeItem(STORAGE_KEY_AUTH);
  },

  async resetPassword(email: string): Promise<boolean> {
    await new Promise(r => setTimeout(r, 300));
    // Always returns true regardless of whether email exists to prevent user enumeration
    return true;
  },

  saveAuthSession(user: User, rememberMe = true) {
    const duration = rememberMe ? SESSION_DURATION_MS : 24 * 60 * 60 * 1000;
    const session: AuthSession = {
      token: `tok_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        createdAt: user.createdAt,
        dailyReviewGoal: user.dailyReviewGoal || 10,
        preferredReviewTime: user.preferredReviewTime || '09:00'
      },
      expiresAt: Date.now() + duration
    };
    localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(session));
  },

  async updateProfile(userId: string, updates: Partial<User>): Promise<User> {
    await new Promise(r => setTimeout(r, 200));
    const users = this.getRegisteredUsers();
    const idx = users.findIndex(u => u.id === userId);
    
    let updatedUser: User;
    if (idx !== -1) {
      users[idx] = { ...users[idx], ...updates };
      localStorage.setItem(STORAGE_KEY_USERS, JSON.stringify(users));
      updatedUser = users[idx];
    } else {
      updatedUser = {
        id: userId,
        name: updates.name || 'Learner',
        email: updates.email || 'alex@edumentor.app',
        createdAt: new Date().toISOString(),
        ...updates
      };
    }

    this.saveAuthSession(updatedUser, true);
    return updatedUser;
  },

  async changePassword(userId: string, currentPassword: string, newPassword: string): Promise<void> {
    await new Promise(r => setTimeout(r, 250));
    const users = this.getRegisteredUsers();
    const user = users.find(u => u.id === userId);

    if (user) {
      // Validate current password (or demo fallbacks)
      if (user.passwordHash && user.passwordHash !== currentPassword && currentPassword !== 'password123' && currentPassword !== 'demo') {
        throw new Error('Current password does not match.');
      }
      user.passwordHash = newPassword;
      localStorage.setItem(STORAGE_KEY_USERS, JSON.stringify(users));
    }
  },

  async deleteAccount(userId: string): Promise<void> {
    await new Promise(r => setTimeout(r, 300));
    const users = this.getRegisteredUsers().filter(u => u.id !== userId);
    localStorage.setItem(STORAGE_KEY_USERS, JSON.stringify(users));
    localStorage.removeItem(STORAGE_KEY_AUTH);
    localStorage.removeItem(STORAGE_KEY_SESSIONS);
  },

  /**
   * Test helper to simulate 7-day session expiration
   */
  simulateSessionExpiry() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY_AUTH);
      if (raw) {
        const session: AuthSession = JSON.parse(raw);
        session.expiresAt = Date.now() - 1000; // Expired 1 second ago
        localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(session));
      }
    } catch (e) {
      console.error(e);
    }
  }
};

/* ==========================================================================
   Sessions & Study Data Services
   ========================================================================== */
export const sessionService = {
  getAll(): StudySession[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY_SESSIONS);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  },

  getById(id: string): StudySession | null {
    const sessions = this.getAll();
    return sessions.find(s => s.id === id) || null;
  },

  save(session: StudySession): StudySession[] {
    const sessions = this.getAll();
    const index = sessions.findIndex(s => s.id === session.id);
    if (index >= 0) {
      sessions[index] = { ...session, updatedAt: new Date().toISOString() };
    } else {
      sessions.unshift({ ...session, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() });
    }
    localStorage.setItem(STORAGE_KEY_SESSIONS, JSON.stringify(sessions));
    return sessions;
  },

  create(title: string, notes: string, category = 'General', attachments?: FileAttachment[]): StudySession {
    const concepts = extractConceptsFromText(notes, title) as Concept[];
    const initialMessages: ChatMessage[] = [
      {
        id: `msg-${Date.now()}-user-notes`,
        role: 'student',
        content: notes,
        timestamp: new Date().toISOString(),
        attachments: attachments || [],
        isInitialNotes: true
      },
      {
        id: `msg-${Date.now()}-mentor-welcome`,
        role: 'mentor',
        content: `Welcome to **${title}**. We have organized ${concepts.length} concepts into a prerequisite study path.\n\nLet's begin with concept 1: **${concepts[0]?.title || 'Introduction'}**.\n\nExplain this concept in your own words. What is its main purpose and how does it function?`,
        timestamp: new Date().toISOString(),
        conceptId: concepts[0]?.id
      }
    ];

    const newSession: StudySession = {
      id: `session-${Date.now()}`,
      title: title.trim() || 'Untitled Study Session',
      category,
      notes,
      concepts,
      messages: initialMessages,
      currentConceptIndex: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    this.save(newSession);
    return newSession;
  },

  rename(id: string, newTitle: string): StudySession | null {
    const sessions = this.getAll();
    const session = sessions.find(s => s.id === id);
    if (!session) return null;
    session.title = newTitle.trim() || 'Untitled Study Session';
    session.updatedAt = new Date().toISOString();
    this.save(session);
    return session;
  },

  delete(id: string): StudySession[] {
    const remaining = this.getAll().filter(s => s.id !== id);
    localStorage.setItem(STORAGE_KEY_SESSIONS, JSON.stringify(remaining));
    return remaining;
  },

  /* ==========================================================================
     Socratic Mentor & Hybrid Evaluation Engine
     ========================================================================== */
  async submitRecallAnswer(
    sessionId: string,
    studentAnswer: string
  ): Promise<{ session: StudySession; evaluation: any }> {
    await new Promise(r => setTimeout(r, 350));

    const session = this.getById(sessionId);
    if (!session) throw new Error('Session not found');

    const currentConcept = session.concepts[session.currentConceptIndex] || session.concepts[0];
    const keyTerms = currentConcept?.keyTerms || [];

    // 1. Keyword coverage evaluation
    const answerLower = studentAnswer.toLowerCase();
    const matchedTerms: string[] = [];
    const missedTerms: string[] = [];

    keyTerms.forEach(term => {
      const termLower = term.toLowerCase();
      if (answerLower.includes(termLower)) {
        matchedTerms.push(term);
      } else {
        const parts = termLower.split(/\s+/);
        if (parts.some(p => p.length > 4 && answerLower.includes(p))) {
          matchedTerms.push(term);
        } else {
          missedTerms.push(term);
        }
      }
    });

    const keywordRatio = keyTerms.length > 0 ? (matchedTerms.length / keyTerms.length) : 0.8;
    const keywordScore = Math.round(keywordRatio * 100);

    // 2. Semantic Similarity heuristic
    const wordCount = studentAnswer.trim().split(/\s+/).length;
    let semanticScore = 50;
    if (wordCount >= 25) semanticScore += 25;
    else if (wordCount >= 12) semanticScore += 15;
    if (studentAnswer.includes('because') || studentAnswer.includes('which') || studentAnswer.includes('allows') || studentAnswer.includes('works by')) {
      semanticScore += 15;
    }
    semanticScore = Math.min(95, Math.max(30, semanticScore));

    // 3. Hybrid Score & AI Judge evaluation
    const overallScore = Math.round(keywordScore * 0.45 + semanticScore * 0.55);
    let grade: 'A' | 'B' | 'C' | 'D' | 'F' = 'B';
    let qualityScore = 3;

    if (overallScore >= 88) {
      grade = 'A';
      qualityScore = 5;
    } else if (overallScore >= 75) {
      grade = 'B';
      qualityScore = 4;
    } else if (overallScore >= 60) {
      grade = 'C';
      qualityScore = 3;
    } else if (overallScore >= 45) {
      grade = 'D';
      qualityScore = 2;
    } else {
      grade = 'F';
      qualityScore = 1;
    }

    let aiJudgeNotes = '';
    let encouragement = '';

    if (overallScore >= 80) {
      aiJudgeNotes = `Strong conceptual explanation. You accurately articulated the mechanism and captured key terminology like ${matchedTerms.slice(0, 2).join(' and ')}.`;
      encouragement = 'Solid grasp. The foundations for subsequent topics are clearly established.';
    } else if (overallScore >= 60) {
      aiJudgeNotes = `Good baseline understanding. You described the high-level intent, but missed mentioning ${missedTerms.slice(0, 2).join(', ')}.`;
      encouragement = 'You have the core intuition down. Connecting these specific mechanisms will solidify your retention.';
    } else {
      aiJudgeNotes = `Supportive critique: You started explaining the topic, but essential details regarding ${missedTerms.slice(0, 2).join(' and ')} were omitted.`;
      encouragement = 'Recalling challenging concepts from scratch is how durable learning happens. We will revisit this shortly in spaced review.';
    }

    const evaluation = {
      overallScore,
      grade,
      keywordCoverage: {
        matched: matchedTerms,
        missed: missedTerms,
        score: keywordScore
      },
      semanticScore,
      aiJudgeNotes,
      encouragement
    };

    // Update Concept SM-2 & status
    const updatedSM2 = calculateSM2(currentConcept.sm2, qualityScore);
    const newStatus = overallScore >= 75 ? 'mastered' : 'review_due';

    currentConcept.sm2 = updatedSM2;
    currentConcept.status = newStatus;

    const studentMsg: ChatMessage = {
      id: `msg-${Date.now()}-student`,
      role: 'student',
      content: studentAnswer,
      timestamp: new Date().toISOString(),
      conceptId: currentConcept.id
    };

    const nextIndex = session.currentConceptIndex + 1;
    const isCompleted = nextIndex >= session.concepts.length;

    let mentorNextReply = '';
    if (!isCompleted) {
      const nextConcept = session.concepts[nextIndex];
      mentorNextReply = `Here is your evaluation for **${currentConcept.title}** (Score: ${overallScore}% • Grade: ${grade}).\n\n${aiJudgeNotes}\n\n*${encouragement}*\n\n---\n\nNext in our prerequisite path is Concept ${nextIndex + 1}: **${nextConcept.title}**.\n\nPrerequisites completed: ${nextConcept.prerequisites.join(', ') || 'None'}.\n\nWhen you are ready, explain **${nextConcept.title}** in your own words.`;
    } else {
      mentorNextReply = `Outstanding work! You have completed all ${session.concepts.length} ordered concepts in **${session.title}**.\n\nYour recall scores have been scheduled into the SM-2 spaced repetition queue. Weak concepts will reappear at calculated intervals to guarantee durable mastery.`;
    }

    const mentorMsg: ChatMessage = {
      id: `msg-${Date.now()}-mentor`,
      role: 'mentor',
      content: mentorNextReply,
      timestamp: new Date().toISOString(),
      conceptId: currentConcept.id,
      evaluation
    };

    session.messages.push(studentMsg, mentorMsg);
    if (!isCompleted) {
      session.currentConceptIndex = nextIndex;
    }

    this.save(session);
    return { session, evaluation };
  },

  /* ==========================================================================
     Spaced Repetition & Progress Analytics
     ========================================================================== */
  getDueReviewConcepts(simulatedDate: Date = new Date()): Array<{ session: StudySession; concept: Concept }> {
    const sessions = this.getAll();
    const dueList: Array<{ session: StudySession; concept: Concept }> = [];

    sessions.forEach(session => {
      (session.concepts || []).forEach(concept => {
        if (concept.status === 'review_due' || isConceptDueForReview(concept, simulatedDate)) {
          dueList.push({ session, concept });
        }
      });
    });

    // Phase 7: Order queue weakest first (lowest lastScore first, then most overdue first)
    dueList.sort((a, b) => {
      const scoreA = a.concept.sm2?.lastScore ?? 0;
      const scoreB = b.concept.sm2?.lastScore ?? 0;
      if (scoreA !== scoreB) {
        return scoreA - scoreB;
      }
      const overdueA = getDaysOverdue(a.concept, simulatedDate);
      const overdueB = getDaysOverdue(b.concept, simulatedDate);
      return overdueB - overdueA;
    });

    return dueList;
  },

  getAnalyticsSummary(simulatedDate: Date = new Date()) {
    const sessions = this.getAll();
    let totalConcepts = 0;
    let masteredCount = 0;
    let reviewDueCount = 0;
    let unstudiedCount = 0;

    sessions.forEach(s => {
      (s.concepts || []).forEach(c => {
        totalConcepts++;
        const isDue = c.status === 'review_due' || isConceptDueForReview(c, simulatedDate);
        if (c.status === 'mastered') masteredCount++;
        else if (isDue) reviewDueCount++;
        else unstudiedCount++;
      });
    });

    const masteryPercent = totalConcepts > 0 ? Math.round((masteredCount / totalConcepts) * 100) : 0;

    return {
      totalSessions: sessions.length,
      totalConcepts,
      masteredCount,
      reviewDueCount,
      unstudiedCount,
      masteryPercent
    };
  },

  exportAllUserData(user: User | null, simulatedDate: Date = new Date()) {
    const sessions = this.getAll();
    const dueQueue = this.getDueReviewConcepts(simulatedDate);
    const analytics = this.getAnalyticsSummary(simulatedDate);

    return {
      appName: 'EduMentor',
      version: '1.0.0',
      exportedAt: new Date().toISOString(),
      user: user || {
        id: 'usr_guest',
        name: 'Learner',
        email: 'alex@edumentor.app',
        createdAt: new Date().toISOString()
      },
      analyticsSummary: analytics,
      totalSessions: sessions.length,
      dueQueueCount: dueQueue.length,
      sessions: sessions
    };
  }
};
