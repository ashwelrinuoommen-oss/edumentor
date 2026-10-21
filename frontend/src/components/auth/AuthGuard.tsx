import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAppStore } from '../../store/useAppStore';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const user = useAppStore(state => state.user);
  const location = useLocation();

  if (!user) {
    // Redirect unauthenticated visitors to /login, remembering their target
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
