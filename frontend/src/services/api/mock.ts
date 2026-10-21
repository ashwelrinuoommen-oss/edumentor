/**
 * Mock API Service Implementation
 * Simulates network latency (300 to 1200 ms) and provides test error injection.
 * Fully backed by persistent localStorage and the SM-2 spaced repetition scheduler.
 */

import { 
  EduMentorApiService,
  SignupRequest,
  LoginRequest,
  AuthResponse,
  CreateModuleRequest,
  CreateModuleResponse,
  ModuleStatusResponse,
  ModuleConceptsResponse,
  ModulePathResponse,
  UpdateConceptRequest,
  ConceptDto,
  EvaluateRecallRequest,
  EvaluateRecallResponse,
  ReviewDueResponse,
  ProgressResponse
} from './types';
import { ApiError } from './client';
import { 
  authService, 
  sessionService, 
  StudySession, 
  Concept, 
  User 
} from '../mockService';
import { extractConceptsFromText } from '../conceptExtractor';
import { evaluateStudentAnswer, checkIfCopiedAnswer } from '../evaluationEngine';
import { isConceptDueForReview, getDaysOverdue } from '../sm2Scheduler';

// Configurable mock error simulation for testing retry behavior
let simulatedErrorTrigger: string | null = null;

export function setSimulatedMockError(errorMsg: string | null) {
  simulatedErrorTrigger = errorMsg;
}

/**
 * Simulates network latency between 300ms and 1200ms
 */
async function simulateLatency(min = 300, max = 1200): Promise<void> {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  await new Promise(r => setTimeout(r, delay));

  if (simulatedErrorTrigger) {
    const msg = simulatedErrorTrigger;
    simulatedErrorTrigger = null; // Auto-clear after firing once to test retry!
    throw new ApiError(500, `[Simulated Mock Error] ${msg}`);
  }
}

export class MockEduMentorService implements EduMentorApiService {
  // ==========================================================================
  // Auth Endpoints
  // ==========================================================================
  async signup(req: SignupRequest): Promise<AuthResponse> {
    await simulateLatency(350, 700);
    const user = await authService.signup(req.name, req.email, req.password);
    return {
      user,
      token: `mock_jwt_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
    };
  }

  async login(req: LoginRequest): Promise<AuthResponse> {
    await simulateLatency(300, 600);
    const user = await authService.login(req.email, req.password);
    return {
      user,
      token: `mock_jwt_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
    };
  }

  async logout(): Promise<void> {
    await simulateLatency(200, 400);
    await authService.logout();
  }

  // ==========================================================================
  // Modules Endpoints
  // ==========================================================================
  async createModule(req: CreateModuleRequest): Promise<CreateModuleResponse> {
    await simulateLatency(500, 1000);

    let combinedNotes = req.pasted_text || '';
    if (req.files && req.files.length > 0) {
      combinedNotes += `\n[Uploaded ${req.files.length} attached file(s): ${req.files.map(f => f.name).join(', ')}]`;
    }

    const title = req.module_name?.trim() || 'New Study Module';
    const newSession = sessionService.create(title, combinedNotes, 'General');

    return {
      module_id: newSession.id,
      status: 'ready'
    };
  }

  async getModuleStatus(id: string): Promise<ModuleStatusResponse> {
    await simulateLatency(300, 600);
    const session = sessionService.getById(id);
    if (!session) {
      return {
        steps: [
          { name: 'Reading your notes', state: 'failed' },
          { name: 'Finding key concepts', state: 'pending' },
          { name: 'Mapping what depends on what', state: 'pending' },
          { name: 'Building your study path', state: 'pending' }
        ],
        error: `Module ${id} not found.`
      };
    }

    return {
      steps: [
        { name: 'Reading your notes', state: 'done' },
        { name: 'Finding key concepts', state: 'done' },
        { name: 'Mapping what depends on what', state: 'done' },
        { name: 'Building your study path', state: 'done' }
      ]
    };
  }

  async getModuleConcepts(id: string): Promise<ModuleConceptsResponse> {
    await simulateLatency(350, 750);
    const session = sessionService.getById(id);
    if (!session) {
      throw new ApiError(404, `Module ${id} not found.`);
    }

    const concepts: ConceptDto[] = (session.concepts || []).map(c => ({
      id: c.id,
      name: c.title,
      definition: c.summary,
      depends_on: c.prerequisites || []
    }));

    return { concepts };
  }

  async getModulePath(id: string): Promise<ModulePathResponse> {
    await simulateLatency(300, 650);
    const session = sessionService.getById(id);
    if (!session) {
      throw new ApiError(404, `Module ${id} not found.`);
    }

    // Topological order by orderIndex
    const sortedConcepts = [...(session.concepts || [])].sort((a, b) => a.orderIndex - b.orderIndex);
    return {
      order: sortedConcepts.map(c => c.id),
      cycles_removed: [] // Valid DAG without cycles
    };
  }

  // ==========================================================================
  // Concept Endpoints
  // ==========================================================================
  async updateConcept(id: string, req: UpdateConceptRequest): Promise<ConceptDto> {
    await simulateLatency(350, 700);

    const sessions = sessionService.getAll();
    let foundConcept: Concept | null = null;
    let foundSession: StudySession | null = null;

    for (const session of sessions) {
      const c = (session.concepts || []).find(item => item.id === id);
      if (c) {
        foundConcept = c;
        foundSession = session;
        break;
      }
    }

    if (!foundConcept || !foundSession) {
      throw new ApiError(404, `Concept ${id} not found.`);
    }

    if (req.name !== undefined) foundConcept.title = req.name;
    if (req.definition !== undefined) foundConcept.summary = req.definition;
    if (req.depends_on !== undefined) foundConcept.prerequisites = req.depends_on;

    sessionService.save(foundSession);

    return {
      id: foundConcept.id,
      name: foundConcept.title,
      definition: foundConcept.summary,
      depends_on: foundConcept.prerequisites
    };
  }

  // ==========================================================================
  // Recall Evaluation Endpoint
  // ==========================================================================
  async evaluateRecall(req: EvaluateRecallRequest): Promise<EvaluateRecallResponse> {
    await simulateLatency(450, 950);

    const sessions = sessionService.getAll();
    let targetConcept: Concept | null = null;
    let parentSession: StudySession | null = null;

    for (const s of sessions) {
      const c = (s.concepts || []).find(item => item.id === req.concept_id);
      if (c) {
        targetConcept = c;
        parentSession = s;
        break;
      }
    }

    if (!targetConcept || !parentSession) {
      throw new ApiError(404, `Concept ${req.concept_id} not found.`);
    }

    const evaluation = evaluateStudentAnswer(
      targetConcept,
      req.answer,
      req.hinted,
      req.answer.trim().toLowerCase() === 'i do not remember' || req.answer.trim() === '',
      new Date()
    );

    // Persist updated SM-2 concept in storage
    const idx = parentSession.concepts.findIndex(c => c.id === targetConcept!.id);
    if (idx !== -1) {
      parentSession.concepts[idx] = evaluation.updatedConcept;
      sessionService.save(parentSession);
    }

    return {
      final_score: evaluation.finalScore,
      similarity: evaluation.similarityScore,
      keyword: evaluation.keywordScore,
      llm_score: evaluation.llmScore,
      correct_parts: evaluation.correctParts,
      missing_parts: evaluation.missingParts,
      wrong_parts: evaluation.wrongParts,
      copied: evaluation.isCopiedFromNotes,
      next_review_date: evaluation.nextReviewDate,
      interval_days: evaluation.intervalDays
    };
  }

  // ==========================================================================
  // Review Queue Endpoint
  // ==========================================================================
  async getDueReviews(simulatedDate: Date = new Date()): Promise<ReviewDueResponse> {
    await simulateLatency(300, 600);
    const dueList = sessionService.getDueReviewConcepts(simulatedDate);

    const items = dueList.map(item => ({
      concept_id: item.concept.id,
      name: item.concept.title,
      module: item.sessionTitle,
      last_score: item.concept.sm2?.lastScore ?? null,
      days_overdue: getDaysOverdue(item.concept, simulatedDate)
    }));

    return { items };
  }

  // ==========================================================================
  // Progress Dashboard Endpoint
  // ==========================================================================
  async getProgress(simulatedDate: Date = new Date()): Promise<ProgressResponse> {
    await simulateLatency(400, 900);
    const sessions = sessionService.getAll();

    const tableItems = [];
    const scorePoints: Array<{ date: string; averageScore: number; conceptCount: number }> = [];
    const weakestItems = [];

    let totalConcepts = 0;
    let masteredCount = 0;
    let scoreSum = 0;
    let evaluatedCount = 0;

    for (const session of sessions) {
      for (const c of session.concepts || []) {
        totalConcepts++;
        const lastScore = c.sm2?.lastScore ?? null;
        const interval = c.sm2?.interval || 0;

        let status: 'mastered' | 'in_progress' | 'weak' | 'unstudied' = 'unstudied';
        if (interval >= 21) {
          status = 'mastered';
          masteredCount++;
        } else if (lastScore !== null) {
          status = lastScore < 2.5 ? 'weak' : 'in_progress';
        }

        if (lastScore !== null) {
          scoreSum += lastScore;
          evaluatedCount++;
          weakestItems.push({
            id: c.id,
            title: c.title,
            moduleName: session.title,
            lastScore,
            color: lastScore < 2.5 ? '#F87171' : lastScore < 4.0 ? '#FBBF24' : '#34D399'
          });
        }

        tableItems.push({
          id: c.id,
          conceptTitle: c.title,
          summary: c.summary,
          sessionId: session.id,
          sessionTitle: session.title,
          lastScore,
          easeFactor: c.sm2?.easinessFactor || 2.5,
          interval,
          nextReviewDate: c.sm2?.nextReviewDate || null,
          status,
          lastReviewDate: c.sm2?.lastReviewDate || null
        });
      }
    }

    const dueList = sessionService.getDueReviewConcepts(simulatedDate);
    const averageScore = evaluatedCount > 0 ? Number((scoreSum / evaluatedCount).toFixed(1)) : 0;

    // Sort weakest
    weakestItems.sort((a, b) => a.lastScore - b.lastScore);

    // Mock trend points for score trajectory
    const daysAgo = (n: number) => {
      const d = new Date(simulatedDate.getTime() - n * 86400000);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    };

    const trend = [
      { date: daysAgo(6), averageScore: 2.4, conceptCount: 2 },
      { date: daysAgo(5), averageScore: 2.8, conceptCount: 3 },
      { date: daysAgo(3), averageScore: 3.2, conceptCount: 4 },
      { date: daysAgo(1), averageScore: 3.9, conceptCount: 5 },
      { date: daysAgo(0), averageScore: averageScore || 4.1, conceptCount: evaluatedCount || 6 }
    ];

    return {
      stats: {
        conceptsMastered: masteredCount,
        totalConcepts,
        averageScore,
        studyStreakDays: evaluatedCount > 0 ? 5 : 0,
        dueTodayCount: dueList.length
      },
      charts: {
        scoreOverTime: trend,
        weakestConcepts: weakestItems.slice(0, 6)
      },
      table: tableItems
    };
  }
}
