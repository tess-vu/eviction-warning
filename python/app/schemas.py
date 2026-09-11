from pydantic import BaseModel

class TractRecord(BaseModel):
    rank: int
    geoid: str
    neighborhood: str
    predicted: float
    action_tier: str
    racial_majority: str
    tax_stress: str
    risk_quintile: int
    spatial_lag_tier: str

class KPISummary(BaseModel):
    critical_tracts: int
    predicted_filings_top_n: float
    model_mae: float
    equity_passed: bool
    equity_label: str
    top_n: int

class TractsResponse(BaseModel):
    month: str
    top_n: int
    kpi: KPISummary
    tracts: list[TractRecord]

class EquityGroup(BaseModel):
    group: str
    mae: float
    bias: float
    mean_observed: float
    mean_predicted: float
    equity_flag: str

class EquityResponse(BaseModel):
    month: str
    passed: bool
    equity_gap_mae: float
    narrative: str
    groups: list[EquityGroup]

class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    last_updated: str

class MonthsResponse(BaseModel):
    available_months: list[str]

class CampaignRequest(BaseModel):
    month: str
    top_n: int = 50

class CampaignAccepted(BaseModel):
    job_id: str
    status: str
