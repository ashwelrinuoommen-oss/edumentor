import { create } from 'zustand';
import { 
  User, 
  StudySession, 
  Concept, 
  initMockDatabase, 
  authService, 
  sessionService 
} from '../services/mockService';

interface AppState {
  user: User | null;
  sessions: StudySession[];
  activeSessionId: string | null;
  isLoading: boolean;
  useMock: boolean;
  sessionExpired: boolean;

  // App Shell layout states
  sidebarCollapsed: boolean;
  mobileSidebarOpen: boolean;
  studyPathOpen: boolean;
  scrollToConceptId: string | null;

  // Phase 7: Dev Toggle Date Simulation
  simulatedDaysOffset: number;
  advanceSimulatedDays: (days: number) => void;
  resetSimulatedDays: () => void;
  getSimulatedDate: () => Date;

  toggleSidebar: () => void;
  setMobileSidebarOpen: (open: boolean) => void;
  toggleStudyPath: () => void;
  setStudyPathOpen: (open: boolean) => void;
  setScrollToConceptId: (id: string | null) => void;

  // Shortcuts modal
  shortcutsModalOpen: boolean;
  setShortcutsModalOpen: (open: boolean) => void;

  // Auth actions
  login: (email: string, password?: string, rememberMe?: boolean) => Promise<void>;
  signup: (name: string, email: string, password?: string) => Promise<void>;
  logout: () => Promise<void>;
  clearSessionExpired: () => void;
  simulateExpiry: () => void;
  updateProfile: (name: string, email: string, dailyReviewGoal?: number, preferredReviewTime?: string) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  deleteAccount: () => Promise<void>;
  exportUserData: () => void;

  // Session actions
  loadInitialData: () => void;
  createSession: (title: string, notes: string, category?: string, attachments?: any[]) => StudySession;
  renameSession: (id: string, newTitle: string) => void;
  updateSession: (session: StudySession) => void;
  deleteSession: (id: string) => void;
  restoreSession: (session: StudySession) => void;
  selectSession: (id: string) => void;
  submitAnswer: (sessionId: string, answer: string) => Promise<any>;
  toggleMockMode: () => void;
}

import { apiService, isMockMode, setMockMode } from '../services/api';

export const useAppStore = create<AppState>((set, get) => ({
  user: null,
  sessions: [],
  activeSessionId: null,
  isLoading: false,
  useMock: isMockMode(),
  sessionExpired: false,

  sidebarCollapsed: false,
  mobileSidebarOpen: false,
  studyPathOpen: true, // Default open on desktop
  scrollToConceptId: null,

  // Phase 7: Dev Toggle Date Simulation State
  simulatedDaysOffset: 0,
  advanceSimulatedDays: (days: number) => {
    set(state => ({ simulatedDaysOffset: state.simulatedDaysOffset + days }));
  },
  resetSimulatedDays: () => {
    set({ simulatedDaysOffset: 0 });
  },
  getSimulatedDate: () => {
    const offset = get().simulatedDaysOffset;
    return new Date(Date.now() + offset * 86400000);
  },

  toggleSidebar: () => {
    set(state => ({ sidebarCollapsed: !state.sidebarCollapsed }));
  },

  setMobileSidebarOpen: (open) => {
    set({ mobileSidebarOpen: open });
  },

  toggleStudyPath: () => {
    set(state => ({ studyPathOpen: !state.studyPathOpen }));
  },

  setStudyPathOpen: (open) => {
    set({ studyPathOpen: open });
  },

  setScrollToConceptId: (id) => {
    set({ scrollToConceptId: id });
  },

  loadInitialData: () => {
    const { user, sessions, sessionExpired } = initMockDatabase();
    set({
      user,
      sessions,
      activeSessionId: sessions[0]?.id || null,
      sessionExpired,
      useMock: isMockMode()
    });
  },

  clearSessionExpired: () => {
    set({ sessionExpired: false });
  },

  login: async (email, password, rememberMe = true) => {
    set({ isLoading: true });
    try {
      const res = await apiService.login({ email, password });
      authService.saveAuthSession(res.user, rememberMe);
      set({ user: res.user, isLoading: false, sessionExpired: false });
    } catch (e) {
      set({ isLoading: false });
      throw e;
    }
  },

  signup: async (name, email, password) => {
    set({ isLoading: true });
    try {
      const res = await apiService.signup({ name, email, password });
      authService.saveAuthSession(res.user, true);
      set({ user: res.user, isLoading: false, sessionExpired: false });
    } catch (e) {
      set({ isLoading: false });
      throw e;
    }
  },

  shortcutsModalOpen: false,
  setShortcutsModalOpen: (open) => {
    set({ shortcutsModalOpen: open });
  },

  logout: async () => {
    await authService.logout();
    set({ user: null, sessionExpired: false, mobileSidebarOpen: false });
  },

  simulateExpiry: () => {
    authService.simulateSessionExpiry();
    set({ user: null, sessionExpired: true });
  },

  updateProfile: async (name, email, dailyReviewGoal, preferredReviewTime) => {
    const currentUser = get().user;
    if (!currentUser) return;
    const updated = await authService.updateProfile(currentUser.id, {
      name,
      email,
      dailyReviewGoal: dailyReviewGoal ?? currentUser.dailyReviewGoal ?? 10,
      preferredReviewTime: preferredReviewTime ?? currentUser.preferredReviewTime ?? '09:00'
    });
    set({ user: updated });
  },

  changePassword: async (currentPassword, newPassword) => {
    const currentUser = get().user;
    if (!currentUser) throw new Error('Not logged in');
    await authService.changePassword(currentUser.id, currentPassword, newPassword);
  },

  deleteAccount: async () => {
    const currentUser = get().user;
    if (currentUser) {
      await authService.deleteAccount(currentUser.id);
    }
    localStorage.clear();
    set({
      user: null,
      sessions: [],
      activeSessionId: null,
      sessionExpired: false,
      mobileSidebarOpen: false
    });
  },

  exportUserData: () => {
    const currentUser = get().user;
    const simDate = get().getSimulatedDate();
    const data = sessionService.exportAllUserData(currentUser, simDate);
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `edumentor-data-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  createSession: (title, notes, category = 'General', attachments = []) => {
    const newSession = sessionService.create(title, notes, category, attachments);
    const sessions = sessionService.getAll();
    set({
      sessions,
      activeSessionId: newSession.id
    });
    return newSession;
  },

  renameSession: (id, newTitle) => {
    sessionService.rename(id, newTitle);
    const sessions = sessionService.getAll();
    set({ sessions });
  },

  updateSession: (session) => {
    sessionService.save(session);
    const sessions = sessionService.getAll();
    set({ sessions });
  },

  deleteSession: (id) => {
    const sessions = sessionService.delete(id);
    const currentActive = get().activeSessionId;
    set({
      sessions,
      activeSessionId: currentActive === id ? (sessions[0]?.id || null) : currentActive
    });
  },

  restoreSession: (session) => {
    sessionService.save(session);
    const sessions = sessionService.getAll();
    set({
      sessions,
      activeSessionId: session.id
    });
  },

  selectSession: (id) => {
    set({ activeSessionId: id, mobileSidebarOpen: false });
  },

  submitAnswer: async (sessionId, answer) => {
    set({ isLoading: true });
    try {
      const { session, evaluation } = await sessionService.submitRecallAnswer(sessionId, answer);
      const allSessions = sessionService.getAll();
      set({
        sessions: allSessions,
        isLoading: false
      });
      return evaluation;
    } catch (e) {
      set({ isLoading: false });
      throw e;
    }
  },

  toggleMockMode: () => {
    const next = !get().useMock;
    setMockMode(next);
    set({ useMock: next });
  }
}));
