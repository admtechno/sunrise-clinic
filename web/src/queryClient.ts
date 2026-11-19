// The one QueryClient of the app: it holds the cache and the default rules.
import { QueryClient } from "@tanstack/react-query";
import { ApiError } from "./api";

// Do not retry a request that failed because of what we sent (4xx): sending it
// again cannot help. Retry a missing answer or a server problem twice.
export function smartRetry(failureCount: number, error: Error): boolean {
  if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
    return false;
  }
  return failureCount < 2;
}

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // an answer stays fresh for 30 seconds
      retry: smartRetry,
    },
  },
});
