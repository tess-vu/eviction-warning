export interface TractRecord {
  rank: number
  geoid: string
  neighborhood: string
  predicted: number
  action_tier: string
  racial_majority: string
  tax_stress: string
  risk_quintile: number
  spatial_lag_tier: string
}

export interface KPISummary {
  critical_tracts: number
  predicted_filings_top_n: number
  model_mae: number
  equity_passed: boolean
  equity_label: string
  top_n: number
}

export interface TractsResponse {
  month: string
  top_n: number
  kpi: KPISummary
  tracts: TractRecord[]
}

export interface EquityGroup {
  group: string
  mae: number
  bias: number
  mean_observed: number
  mean_predicted: number
  equity_flag: string
}

export interface EquityResponse {
  month: string
  passed: boolean
  equity_gap_mae: number
  narrative: string
  groups: EquityGroup[]
}

export interface CampaignAccepted {
  job_id: string
  status: string
}
