/**
 * EduMentor Unified API Service Layer
 * Switched between Mock and Real mode by one environment flag (USE_MOCK).
 * Provides identical function names, loading, error, and retry handling.
 */

import { EduMentorApiService } from './types';
import { MockEduMentorService, setSimulatedMockError } from './mock';
import { RealEduMentorService } from './real';

// Single source of truth for environment flag
// Defaults to true (mock mode) unless explicitly configured as false
export const USE_MOCK_ENV: boolean = import.meta.env.VITE_USE_MOCK !== 'false';

// Runtime mode state (can be overridden via Settings toggle)
let currentUseMock: boolean = (() => {
  const stored = localStorage.getItem('edumentor_use_mock_v1');
  return stored !== null ? stored === 'true' : USE_MOCK_ENV;
})();

const mockServiceInstance = new MockEduMentorService();
const realServiceInstance = new RealEduMentorService();

/**
 * Get current active mode
 */
export function isMockMode(): boolean {
  return currentUseMock;
}

/**
 * Dynamically switch between Mock and Real modes at runtime
 */
export function setMockMode(enabled: boolean): void {
  currentUseMock = enabled;
  localStorage.setItem('edumentor_use_mock_v1', String(enabled));
}

/**
 * Unified API Service instance delegating dynamically to Mock or Real mode
 */
export const apiService: EduMentorApiService = {
  // Auth
  signup: (req) => (currentUseMock ? mockServiceInstance.signup(req) : realServiceInstance.signup(req)),
  login: (req) => (currentUseMock ? mockServiceInstance.login(req) : realServiceInstance.login(req)),
  logout: () => (currentUseMock ? mockServiceInstance.logout() : realServiceInstance.logout()),

  // Modules
  createModule: (req) => (currentUseMock ? mockServiceInstance.createModule(req) : realServiceInstance.createModule(req)),
  getModuleStatus: (id) => (currentUseMock ? mockServiceInstance.getModuleStatus(id) : realServiceInstance.getModuleStatus(id)),
  getModuleConcepts: (id) => (currentUseMock ? mockServiceInstance.getModuleConcepts(id) : realServiceInstance.getModuleConcepts(id)),
  getModulePath: (id) => (currentUseMock ? mockServiceInstance.getModulePath(id) : realServiceInstance.getModulePath(id)),

  // Concepts
  updateConcept: (id, req) => (currentUseMock ? mockServiceInstance.updateConcept(id, req) : realServiceInstance.updateConcept(id, req)),

  // Recall
  evaluateRecall: (req) => (currentUseMock ? mockServiceInstance.evaluateRecall(req) : realServiceInstance.evaluateRecall(req)),

  // Review Queue
  getDueReviews: (date) => (currentUseMock ? mockServiceInstance.getDueReviews(date) : realServiceInstance.getDueReviews(date)),

  // Progress Dashboard
  getProgress: (date) => (currentUseMock ? mockServiceInstance.getProgress(date) : realServiceInstance.getProgress(date))
};

// Re-export types & utilities
export * from './types';
export { ApiError, withRetry } from './client';
export { useApiCall } from './useApiCall';
export { setSimulatedMockError };
