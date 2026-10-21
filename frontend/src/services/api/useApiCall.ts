import { useState, useCallback, useRef } from 'react';

export interface UseApiCallOptions<TResult> {
  onSuccess?: (data: TResult) => void;
  onError?: (error: Error) => void;
}

export interface UseApiCallReturn<TArgs extends any[], TResult> {
  execute: (...args: TArgs) => Promise<TResult>;
  data: TResult | null;
  isLoading: boolean;
  error: Error | null;
  retry: () => Promise<TResult>;
  reset: () => void;
}

/**
 * Universal Hook providing loading, error, and retry state for any API call
 */
export function useApiCall<TArgs extends any[], TResult>(
  apiFn: (...args: TArgs) => Promise<TResult>,
  options: UseApiCallOptions<TResult> = {}
): UseApiCallReturn<TArgs, TResult> {
  const [data, setData] = useState<TResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  // Preserve latest arguments for retry
  const lastArgsRef = useRef<TArgs | null>(null);

  const execute = useCallback(
    async (...args: TArgs): Promise<TResult> => {
      lastArgsRef.current = args;
      setIsLoading(true);
      setError(null);

      try {
        const result = await apiFn(...args);
        setData(result);
        setIsLoading(false);
        options.onSuccess?.(result);
        return result;
      } catch (err: any) {
        const normalizedError = err instanceof Error ? err : new Error(String(err));
        setError(normalizedError);
        setIsLoading(false);
        options.onError?.(normalizedError);
        throw normalizedError;
      }
    },
    [apiFn, options]
  );

  const retry = useCallback(async (): Promise<TResult> => {
    if (!lastArgsRef.current) {
      throw new Error('No previous API call to retry.');
    }
    return execute(...lastArgsRef.current);
  }, [execute]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
    lastArgsRef.current = null;
  }, []);

  return {
    execute,
    data,
    isLoading,
    error,
    retry,
    reset
  };
}
