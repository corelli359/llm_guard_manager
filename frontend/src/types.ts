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
