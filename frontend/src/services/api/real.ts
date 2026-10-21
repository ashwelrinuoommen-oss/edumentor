/**
 * Real API Service Implementation
 * Interacts with the Python backend REST API endpoints using standard HTTP requests.
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
import { request } from './client';

export class RealEduMentorService implements EduMentorApiService {
  // ==========================================================================
  // Auth Endpoints
  // ==========================================================================
  async signup(req: SignupRequest): Promise<AuthResponse> {
    return request<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(req)
    });
  }

  async login(req: LoginRequest): Promise<AuthResponse> {
    return request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(req)
    });
  }

  async logout(): Promise<void> {
    try {
      await request<void>('/auth/logout', { method: 'POST' });
    } catch {
      // Clean local session regardless of server error
    } finally {
      localStorage.removeItem('edumentor_auth_session_v1');
    }
  }

  // ==========================================================================
  // Modules Endpoints (Multipart POST /modules)
  // ==========================================================================
  async createModule(req: CreateModuleRequest): Promise<CreateModuleResponse> {
    const formData = new FormData();
    if (req.pasted_text) {
      formData.append('pasted_text', req.pasted_text);
    }
    if (req.module_name) {
      formData.append('module_name', req.module_name);
    }
    if (req.files && req.files.length > 0) {
      req.files.forEach((file) => {
        formData.append('files', file, file.name);
      });
    }

    return request<CreateModuleResponse>('/modules', {
      method: 'POST',
      body: formData
    });
  }

  async getModuleStatus(id: string): Promise<ModuleStatusResponse> {
    return request<ModuleStatusResponse>(`/modules/${encodeURIComponent(id)}/status`, {
      method: 'GET'
    });
  }

  async getModuleConcepts(id: string): Promise<ModuleConceptsResponse> {
    return request<ModuleConceptsResponse>(`/modules/${encodeURIComponent(id)}/concepts`, {
      method: 'GET'
    });
  }

  async getModulePath(id: string): Promise<ModulePathResponse> {
    return request<ModulePathResponse>(`/modules/${encodeURIComponent(id)}/path`, {
      method: 'GET'
    });
  }

  // ==========================================================================
  // Concepts Endpoint (PATCH /concepts/{id})
  // ==========================================================================
  async updateConcept(id: string, req: UpdateConceptRequest): Promise<ConceptDto> {
    return request<ConceptDto>(`/concepts/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(req)
    });
  }

  // ==========================================================================
  // Recall Evaluation Endpoint (POST /recall/evaluate)
  // ==========================================================================
  async evaluateRecall(req: EvaluateRecallRequest): Promise<EvaluateRecallResponse> {
    return request<EvaluateRecallResponse>('/recall/evaluate', {
      method: 'POST',
      body: JSON.stringify(req)
    });
  }

  // ==========================================================================
  // Review Queue Endpoint (GET /review/due)
  // ==========================================================================
  async getDueReviews(simulatedDate?: Date): Promise<ReviewDueResponse> {
    const query = simulatedDate ? `?simulated_date=${encodeURIComponent(simulatedDate.toISOString())}` : '';
    return request<ReviewDueResponse>(`/review/due${query}`, {
      method: 'GET'
    });
  }

  // ==========================================================================
  // Progress Dashboard Endpoint (GET /progress)
  // ==========================================================================
  async getProgress(simulatedDate?: Date): Promise<ProgressResponse> {
    const query = simulatedDate ? `?simulated_date=${encodeURIComponent(simulatedDate.toISOString())}` : '';
    return request<ProgressResponse>(`/progress${query}`, {
      method: 'GET'
    });
  }
}
