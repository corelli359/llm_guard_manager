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