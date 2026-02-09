import React, { ReactNode } from 'react';
import { usePermission } from '../hooks/usePermission';

interface PermissionGuardProps {
  roles?: string[];
  scenarioId?: string;
  permission?: string;
  fallback?: ReactNode;
  children: ReactNode;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  roles,
  scenarioId,
  permission,
  fallback = null,
  children,
}) => {
  const { hasRole, hasScenarioPermission } = usePermission();

  // Role check
  if (roles && !hasRole(roles)) {
    return <>{fallback}</>;
  }

  // Scenario permission check
  if (scenarioId && permission && !hasScenarioPermission(scenarioId, permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
