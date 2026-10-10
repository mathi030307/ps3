export type MatchStatus = 'Supported' | 'Partial Match' | 'Not Found' | 'Contradicted' | 'Uncertain';

export type ClaimCategory = 
  | 'Offer / Pricing'
  | 'Feature / Benefit'
  | 'Call to Action'
  | 'Social Proof / Trust'
  | 'Audience / Scope';

export type PriorityLevel = 'HIGH' | 'MEDIUM' | 'LOW';

export interface AdInput {
  headline: string;
  description: string;
  cta?: string;
}

export interface ClaimContribution {
  claim_id: string;
  claim_text: string;
  source_part: string;
  category: ClaimCategory;
  status: MatchStatus;
  base_value: number;
  weight: number;
  weighted_points: number;
  max_possible_points: number;
  contribution_percent: number;
}

export interface CtaComparison {
  ad_cta?: string | null;
  page_primary_cta?: string | null;
  all_page_ctas: string[];
  match_status: MatchStatus;
  similarity_score: number;
  friction_detected: boolean;
  friction_notes: string;
}

export interface ScoreBreakdown {
  headline_hero_alignment: number;
  cta_alignment: number;
  claim_coverage_rate: number;
  offer_consistency: number;
  contradiction_penalty: number;
  is_capped_at_40: boolean;
  formula_text: string;
  presentation_aid_label: string;
  claim_contributions: ClaimContribution[];
}

export interface ClaimAudit {
  claim_id: string;
  source_part: 'headline' | 'description' | 'cta';
  category: ClaimCategory;
  claim_text: string;
  status: MatchStatus;
  similarity_score: number;
  evidence_quote?: string;
  is_quote_verified: boolean;
  quote_source_element?: string;
  status_reason: string;
  suggested_action: string;
}

export interface Recommendation {
  id: string;
  priority: PriorityLevel;
  category: string;
  issue: string;
  impact: string;
  recommended_fix: string;
  suggested_ad_copy?: string;
  suggested_page_copy?: string;
}

export interface PageExtractionSummary {
  url?: string;
  title?: string;
  headings_h1: string[];
  headings_h2_h3: string[];
  hero_text?: string;
  detected_ctas: string[];
  footer_disclosures: string[];
  word_count: number;
  reading_time_minutes: number;
  text_length: number;
}

export interface AuditResponse {
  success: boolean;
  is_synthetic_demo: boolean;
  demo_badge?: string | null;
  error_message?: string | null;
  error_type?: string | null;
  timestamp: string;
  source_description: string;
  overall_score?: number | null;
  grade?: string | null;
  presentation_aid_note?: string | null;
  summary_verdict?: string | null;
  score_breakdown?: ScoreBreakdown | null;
  cta_analysis?: CtaComparison | null;
  total_claims: number;
  supported_count: number;
  partial_count: number;
  not_found_count: number;
  contradicted_count: number;
  uncertain_count: number;
  claims: ClaimAudit[];
  recommendations: Recommendation[];
  page_summary?: PageExtractionSummary | null;
}

export interface SyntheticScenario {
  id: string;
  name: string;
  label: string;
  category: string;
  mismatch_description: string;
  ad: AdInput;
  html_file_path?: string | null;
  simulated_error?: string | null;
  html_content?: string;
}
