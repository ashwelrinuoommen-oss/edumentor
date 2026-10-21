/**
 * HTTP REST Client with Authentication, Error Normalization, and Automatic Retry
 */

export class ApiError extends Error {
  status: number;
  data?: any;
  isRetryable: boolean;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    // 5xx errors or network failures (status 0) are transient and retryable
    this.isRetryable = status >= 500 || status === 0;
  }
}

export interface RequestOptions extends RequestInit {
  retries?: number;
  retryDelayMs?: number;
}

const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function getAuthToken(): string | null {
  try {
    const raw = localStorage.getItem('edumentor_auth_session_v1');
    if (raw) {
      const parsed = JSON.parse(raw);
      return parsed.token || null;
    }
  } catch {
    return null;
  }
  return null;
}

/**
 * Executes a function with automatic retry and exponential backoff
 */
export async function withRetry<T>(
  operation: () => Promise<T>,
  retries = 2,
  baseDelayMs = 500
): Promise<T> {
  let attempt = 0;
  while (true) {
    try {
      return await operation();
    } catch (err: any) {
      attempt++;
      const isRetryable = err instanceof ApiError ? err.isRetryable : true;
      if (attempt > retries || !isRetryable) {
        throw err;
      }
      const delay = baseDelayMs * Math.pow(2, attempt - 1);
      console.warn(`[ApiClient] Request failed. Retrying (attempt ${attempt}/${retries}) in ${delay}ms...`);
      await new Promise(r => setTimeout(r, delay));
    }
  }
}

/**
 * Universal fetch wrapper for JSON and Multipart endpoints
 */
export async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { retries = 2, retryDelayMs = 400, ...fetchOptions } = options;
  const baseUrl = DEFAULT_BASE_URL.replace(/\/$/, '');
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${baseUrl}${cleanEndpoint}`;

  const token = getAuthToken();
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(options.headers as Record<string, string>)
  };

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Do not set Content-Type for FormData; browser sets it automatically with boundary
  if (!(fetchOptions.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  return withRetry(async () => {
    let res: Response;
    try {
      res = await fetch(url, {
        ...fetchOptions,
        headers
      });
    } catch (netErr: any) {
      throw new ApiError(0, netErr.message || 'Network connection failed. Please check your internet connection.');
    }

    let responseData: any = null;
    const contentType = res.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      try {
        responseData = await res.json();
      } catch {
        responseData = null;
      }
    } else {
      responseData = await res.text();
    }

    if (!res.ok) {
      const errorMsg = (responseData && typeof responseData === 'object' && (responseData.detail || responseData.message || responseData.error)) ||
        `Request failed with status ${res.status}`;
      throw new ApiError(res.status, errorMsg, responseData);
    }

    return responseData as T;
  }, retries, retryDelayMs);
}
