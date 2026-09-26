# Philadelphia Eviction Early Warning System

**Authors:** Angel Rutherford, Ixchel Ramirez, Tess Vu

**Affiliation:** University of Pennsylvania | MUSA 5080: Public Policy Analytics

**Date:** December 8, 2025

## Executive Summary

Eviction is both a cause and consequence of poverty that destabilizes entire neighborhoods. Currently, city responses to eviction are reactive, with resources like legal aid and rental assistance deployed *after* filing volumes become a crisis. This project develops a Real-Time Operational Tool for the Philadelphia Office of Homeless Services and the Fair Housing Commission. By shifting from reactive to predictive analysis, we enable the city to allocate limited staff to specific census tracts predicted to experience elevated eviction filings in the coming month.

Our Negative Binomial regression model leverages temporal momentum, spatial spillover effects, policy intervention effects, property tax delinquency stress, and American Community Survey socioeconomic indicators to forecast monthly eviction filing counts at the census tract level.

The model demonstrates strong performance with meaningful improvement, and sets the foundation for building up to a practical and usable tool down the line. Using a robust temporal validation strategy (training through 2023, testing on 2024-2025), the model generalizes well to future periods without overfitting. Also stark racial disparities in eviction burden was identified, with Black-majority tracts accounting for disproportionate shares of filings. These findings emphasize the need for equity-centered implementation safeguards to prevent perpetuating existing disparities through algorithmic resource allocation.

## Predictive Question

**"Where should renter's assistance programs be targeted in Philadelphia?"**

**Target Variable:** Monthly Count of Eviction Filings per Census Tract.

## Data Sources & Integration

[Eviction Lab Main Data](https://evictionlab.org/eviction-tracking/get-the-data/)

[Eviction Lab Claims Data](https://evictionlab.org/eviction-tracking/philadelphia-pa/)

[Real Estate Tax Balances](https://opendataphilly.org/datasets/real-estate-tax-balances/)

[Neighborhood Boundaries](https://opendataphilly.org/datasets/philadelphia-neighborhoods/)

[Tract Boundaries](https://opendataphilly.org/datasets/census-tracts/)

ACS 2023 Data via `tidycensus` API

# Methodology

### Volatility & Overdispersion

Eviction data is **zero-inflated** (37% of tracts have 0 filings) and **overdispersed** (Variance > Mean). Standard OLS or Poisson models fail to capture the unpredictable, volatile nature of eviction spikes.

### Negative Binomial Regression

We trained a series of **Negative Binomial Models**, progressively adding complexity:

* **Model 1 (Baseline):** Time + Seasonality.
* **Model 2 (+ Actionable):** Adds Tax Delinquency + Spatial Lag.
* **Model 3 (+ Structural):** Adds ACS Demographics.
* **Model 4 (+ Interaction):** Tests Racial Disparities in Policy Impact.

### Capping & Flagging

To handle extreme "mass displacement events" (e.g., 694 filings in a single tract), we developed a robust capping strategy where the target variable capped at the 99th percentile (20 filings) to stabilize coefficients, created an `is_extreme_spike` flag to explicitly model crisis propensity, and evaluated on raw, uncapped data to prove real-world usefulness.

## Key Findings & Performance

Our final model (**Model 3 + ACS**) achieved the best balance of accuracy and stability.

### Predictive Accuracy

* **Test MAE:** **1.48** (The model is accurate to within < 2 filings per tract).

* **Stability:** The model performed *better* on the 2024-2025 Test Set than the Training Set, proving it is not overfit and can generalize well to unseen, real-world data.

### Equity Analysis

* **Disparate Impact:** Black-majority tracts face a structurally higher baseline risk that standard economic variables cannot fully explain.

* **Model Fairness:** The model's error rate (MAE) is slightly higher in Black tracts, indicating higher unmeasured volatility in these neighborhoods that are historically and currently most vulnerable.

## Operational Recommendations

This model's future would be best used as a monthly **Triage Dashboard**:

1.  **Input:** Load previous month's filing data on 1st of month.
2.  **Output:** Generate list of the **Top 50 "Critical Risk" Tracts**.
3.  **Potential Action:**
    * **Deploy Canvassers:** Aid 50 tracts *before* any major court dates in the system.
    * **Direct Mail:** Send "Know Your Rights" flyers to all rental units within zip codes.
    * **Legal Aid Pop-Ups:** Establish temporary clinics in these specific zones.

## Repository Structure

```
analysis/      Quarto modeling notebooks (EDA and final model)
slides/        Quarto presentation
python/        Fairness audit, PDF brief generator, mail campaign, FastAPI service
frontend/      Vue 3 + Vite dashboard (MapLibre, Pinia)
outputs/       Model predictions, equity audit, generated briefs (not tracked)
data/          Source datasets (not tracked)
```

## Running Full System Locally

Run from the repository root. Requires Python 3.12+ and Node 20+.

```bash
pip install -r python/requirements.txt

# 1. Audit model predictions for disparate impact.
python -m python.fairness.audit --predictions outputs/model_predictions.csv --output outputs/equity_audit.json

# 2. Generate a monthly PDF brief.
python -m python.pdf.generator --predictions outputs/model_predictions.csv --equity-audit outputs/equity_audit.json --output outputs/brief_2026_01.pdf

# 3. Serve API.
uvicorn python.app.main:app --reload --port 8000
```

In a second terminal, start the dashboard:

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies `/api` and `/health` to the FastAPI service on port 8000.

## Live Dashboard (GitHub Pages)

The dashboard is also published as a static site, which runs without a backend by reading pre-exported JSON instead of calling the API. PDF brief generation and the mail campaign are hidden in this mode since both require the Python service.

**Deploy Setup (Once):** in the repository settings under **Pages**, set **Source** to **GitHub Actions**. The workflow in [.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml) builds and publishes on every push to `main`.

**Refreshing Published Data:** Static payloads are in `frontend/public/api/` and are committed to the repository, because `outputs/` is gitignored and unavailable to CI. Regenerate them whenever the model outputs change:

```bash
python -m python.export_static
git add frontend/public/api
```

This writes one JSON file per month and per Top-N option, mirroring the `/api/months`, `/api/tracts`, and `/api/equity` responses.

**Build Locally:**

```bash
cd frontend
npm run build:pages # builds with VITE_STATIC=true and the /eviction-warning/ base path
npm run preview -- --mode pages
```

The base path is set in [frontend/.env.pages](frontend/.env.pages) and must match the repository name. If the repository is renamed, or if this is moved to a `<user>.github.io` user site (where the base path is `/`), update `VITE_BASE_PATH` there.

The Quarto report and slides are intentionally excluded from the published site, only the dashboard is deployed.

**Ethical Safeguard:** This tool must be used strictly for providing resources, never for automated decision-making or punitive enforcement.
