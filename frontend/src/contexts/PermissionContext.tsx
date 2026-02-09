import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { UserPermissionsV2 } from '../types';
import { userRolesApi } from '../api';

interface PermissionContextType {
  userPermissions: UserPermissionsV2 | null;
  loading: boolean;
  refreshPermissions: () => Promise<void>;
  hasPermission: (permissionCode: string) => boolean;
  hasScenarioPermission: (scenarioId: string, permissionCode: string) => boolean;
  userRole: string;
  hasRole: (roles: string[]) => boolean;
  hasScenarioAccess: (scenarioId: string) => boolean;
}

export const PermissionContext = createContext<PermissionContextType | undefined>(undefined);

interface PermissionProviderProps {
  children: ReactNode;
}

export const PermissionProvider: React.FC<PermissionProviderProps> = ({ children }) => {
  const [userPermissions, setUserPermissions] = useState<UserPermissionsV2 | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPermissions();
  }, []);

  const fetchPermissions = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await userRolesApi.getMyPermissions();
      setUserPermissions(response.data);
    } catch (error) {
      console.error('Failed to fetch permissions', error);
      if ((error as any)?.response?.status === 401) {
        localStorage.removeItem('access_token');
      }
    } finally {
      setLoading(false);
    }
  };

  const hasPermission = (permissionCode: string): boolean => {
    if (!userPermissions) return false;
    return userPermissions.global_permissions.includes(permissionCode);
  };

  const hasScenarioPermission = (scenarioId: string, permissionCode: string): boolean => {
    if (!userPermissions) return false;
    if (userPermissions.global_permissions.includes(permissionCode)) return true;
    const scenarioPerms = userPermissions.scenario_permissions[scenarioId];
    return scenarioPerms ? scenarioPerms.includes(permissionCode) : false;
  };

  const hasRole = (roles: string[]): boolean => {
    if (!userPermissions) return false;
    if (roles.includes('SYSTEM_ADMIN') && hasPermission('user_management')) return true;
    if (roles.includes('SCENARIO_ADMIN') && Object.keys(userPermissions.scenario_permissions).length > 0) return true;
    if (roles.includes('AUDITOR') && hasPermission('audit_logs') && !hasPermission('user_management')) return true;
    if (roles.includes('ANNOTATOR') && hasPermission('smart_labeling')) return true;
    return false;
  };

  const hasScenarioAccess = (scenarioId: string): boolean => {
    if (!userPermissions) return false;
    if (hasPermission('app_management')) return true;
    return scenarioId in userPermissions.scenario_permissions;
  };

  const value: PermissionContextType = {
    userPermissions,
    loading,
    refreshPermissions: fetchPermissions,
    hasPermission,
    hasScenarioPermission,
    userRole: localStorage.getItem('user_role') || '',
    hasRole,
    hasScenarioAccess,
  };

  return (
    <PermissionContext.Provider value={value}>
      {children}
    </PermissionContext.Provider>
  );
};
