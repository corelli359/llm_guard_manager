export interface MetaTag {
  id: string;
  tag_code: string;
  tag_name: string;
  parent_code?: string;
  level: number;
  is_active: boolean;
}

export interface GlobalKeyword {
  id: string;
  keyword: string;
  tag_code: string;
  risk_level: string;
  is_active: boolean;
}

export interface ScenarioKeyword {
  id: string;
  scenario_id: string;
  keyword: string;
  tag_code?: string;
  rule_mode: number; // 0: Super, 1: Custom
  risk_level?: string;
  is_active: boolean;
  category: number; // 0: White, 1: Black
}

export interface RuleScenarioPolicy {
  id: string;
  scenario_id: string;
  match_type: 'KEYWORD' | 'TAG';
  match_value: string;
  rule_mode: number; // 0: Super, 1: Custom
  extra_condition?: string;
  strategy: string; // BLOCK / PASS / REWRITE
  is_active: boolean;
}

export interface RuleGlobalDefault {
  id: string;
  tag_code: string;
  extra_condition?: string;
  strategy: string; // BLOCK / PASS / REWRITE
  is_active: boolean;
}

export interface ScenarioApp {
  id: string;
  app_id: string;
  app_name: string;
  description?: string;
  is_active: boolean;
  enable_whitelist: boolean;
  enable_blacklist: boolean;
  enable_custom_policy: boolean;
}

export interface PlaygroundRequest {
  app_id: string;
  input_prompt: string;
  use_customize_white: boolean;
  use_customize_words: boolean;
  use_customize_rule: boolean;
  use_vip_black: boolean;
  use_vip_white: boolean;
}

export interface PlaygroundResponse {
  all_decision_dict?: Record<string, any>;
  final_decision?: {
    priority: number;
    score: number;
  };
  [key: string]: any;
}

export interface PlaygroundHistory {
  id: string;
  request_id: string;
  playground_type: string;
  app_id: string;
  input_data: {
    input_prompt: string;
    [key: string]: any;
  };
  config_snapshot: Record<string, any>;
  output_data: any;
  score: number;
  latency?: number;
  upstream_latency?: number;
  created_at: string;
}

// RBAC Types
export interface User {
  id: string;
  user_id: string | null;
  role: 'SYSTEM_ADMIN' | 'SCENARIO_ADMIN' | 'ANNOTATOR' | 'AUDITOR';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserScenarioAssignment {
  id: string;
  user_id: string;
  scenario_id: string;
  role: 'SCENARIO_ADMIN' | 'ANNOTATOR';
  created_at: string;
  created_by?: string;
}

export interface ScenarioAdminPermission {
  id: string;
  user_id: string;
  scenario_id: string;
  scenario_basic_info: boolean;
  scenario_keywords: boolean;
  scenario_policies: boolean;
  playground: boolean;
  performance_test: boolean;
  created_at: string;
  updated_at?: string;
  created_by?: string;
}

export interface UserPermissions {
  user_id: string;
  username: string;
  role: string;
  scenarios: Array<{
    scenario_id: string;
    scenario_name: string;
    role: string;
    permissions?: {
      scenario_basic_info: boolean;
      scenario_keywords: boolean;
      scenario_policies: boolean;
      playground: boolean;
      performance_test: boolean;
    };
  }>;
}

export interface AuditLog {
  id: string;
  user_id: string;
  username: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  scenario_id?: string;
  details?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

// SSO Types
export interface SSOLoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  role: string;
}

export interface SSOUserInfo {
  user_id: string;
  user_name: string;
  email?: string;
  department?: string;
  phone?: string;
  role: string;
  scenarios: Array<{
    scenario_id: string;
    scenario_name: string;
    role: string;
    permissions?: {
      scenario_basic_info: boolean;
      scenario_keywords: boolean;
      scenario_policies: boolean;
      playground: boolean;
      performance_test: boolean;
    };
  }>;
}

export interface SSOUserBrief {
  user_id: string;
  user_name: string;
  email?: string;
  department?: string;
}

// RBAC V2 类型
export interface Role {
  id: string;
  role_code: string;
  role_name: string;
  role_type: 'GLOBAL' | 'SCENARIO';
  description?: string;
  is_system: boolean;
  is_active: boolean;
  created_at: string;
  permission_count: number;
}

export interface PermissionItem {
  id: string;
  permission_code: string;
  permission_name: string;
  permission_type: 'MENU' | 'ACTION';
  scope: 'GLOBAL' | 'SCENARIO';
  parent_code?: string;
  sort_order: number;
}

export interface UserRoleAssignment {
  id: string;
  user_id: string;
  scenario_id?: string;
  role_id: string;
  role_code: string;
  role_name: string;
  role_type: string;
  created_at: string;
}

export interface UserPermissionsV2 {
  user_id: string;
  global_permissions: string[];
  scenario_permissions: Record<string, string[]>;
}
