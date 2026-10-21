/**
 * TypeScript Contracts and DTOs for EduMentor Backend API
 * Both Mock Service and Real REST endpoints implement this exact interface.
 */

import { User } from '../mockService';

// ============================================================================
// 1. Auth DTOs
// ============================================================================
export interface SignupRequest {
  name: string;
  email: string;
  password?: string;
}

export interface LoginRequest {
  email: string;
  password?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// ============================================================================
// 2. Modules & Processing DTOs
// ============================================================================
export interface CreateModuleRequest {
  files?: File[];
  pasted_text?: string;
  module_name?: string;
}

export interface CreateModuleResponse {
  module_id: string;
  status: string; // e.g. "queued" | "processing" | "ready"
}

export type StepState = 'pending' | 'running' | 'done' | 'failed';

export interface ModuleStatusStep {
  name: string;
  state: StepState;
}

export interface ModuleStatusResponse {
  steps: ModuleStatusStep[];
  error?: string;
}

// ============================================================================
// 3. Concepts & Path DTOs
// ============================================================================
export interface ConceptDto {
  id: string;
  name: string;
  definition: string;
  depends_on: string[]; // List of concept IDs this concept depends on
}

export interface ModuleConceptsResponse {
  concepts: ConceptDto[];
}

export interface ModulePathResponse {
  order: string[]; // Concept IDs in topological / learning order
  cycles_removed: Array<[string, string]>; // List of [fromId, toId] pruned to ensure DAG
}

export interface UpdateConceptRequest {
  name?: string;
  definition?: string;
  depends_on?: string[];
}

// ============================================================================
// 4. Recall Evaluation DTOs
// ============================================================================
export interface EvaluateRecallRequest {
  concept_id: string;
  answer: string;
  hinted: boolean;
}

export interface EvaluateRecallResponse {
  final_score: number; // 0.0 - 5.0
  similarity: number; // 0 - 100 percentage (Meaning match)
  keyword: number; // 0 - 100 percentage (Key terms covered)
  llm_score: number; // 0 - 100 percentage (Tutor judgement)
  correct_parts: string[];
  missing_parts: string[];
  wrong_parts: string[];
  copied: boolean;
  next_review_date: string; // ISO string
  interval_days: number;
}

// ============================================================================
// 5. Spaced Repetition Review Queue DTOs
// ============================================================================
export interface ReviewDueItemDto {
  concept_id: string;
  name: string;
  module: string;
  last_score: number | null;
  days_overdue: number;
}

export interface ReviewDueResponse {
  items: ReviewDueItemDto[];
}

// ============================================================================
// 6. Progress & Matrix Dashboard DTOs
// ============================================================================
export interface ProgressStatsDto {
  conceptsMastered: number;
  totalConcepts: number;
  averageScore: number;
  studyStreakDays: number;
  dueTodayCount: number;
}

export interface ProgressScorePointDto {
  date: string;
  averageScore: number;
  conceptCount: number;
}

export interface ProgressWeakestConceptDto {
  id: string;
  title: string;
  moduleName: string;
  lastScore: number;
  color: string;
}

export interface ProgressTableItemDto {
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

export interface ProgressResponse {
  stats: ProgressStatsDto;
  charts: {
    scoreOverTime: ProgressScorePointDto[];
    weakestConcepts: ProgressWeakestConceptDto[];
  };
  table: ProgressTableItemDto[];
}

// ============================================================================
// 7. Full Service Contract Interface
// ============================================================================
export interface EduMentorApiService {
  // Auth
  signup(req: SignupRequest): Promise<AuthResponse>;
  login(req: LoginRequest): Promise<AuthResponse>;
  logout(): Promise<void>;

  // Modules & Processing
  createModule(req: CreateModuleRequest): Promise<CreateModuleResponse>;
  getModuleStatus(id: string): Promise<ModuleStatusResponse>;
  getModuleConcepts(id: string): Promise<ModuleConceptsResponse>;
  getModulePath(id: string): Promise<ModulePathResponse>;

  // Concepts
  updateConcept(id: string, req: UpdateConceptRequest): Promise<ConceptDto>;

  // Recall
  evaluateRecall(req: EvaluateRecallRequest): Promise<EvaluateRecallResponse>;

  // Review Queue
  getDueReviews(simulatedDate?: Date): Promise<ReviewDueResponse>;

  // Progress Dashboard
  getProgress(simulatedDate?: Date): Promise<ProgressResponse>;
}
