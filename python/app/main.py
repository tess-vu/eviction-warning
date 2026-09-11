from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .config import FRONTEND_BUILD_DIR
from .data import data_loaded, last_updated, available_months
from .schemas import HealthResponse, MonthsResponse
from .routers import tracts, equity, brief, campaign

app = FastAPI(title="Eviction Early Warning System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracts.router, prefix="/api")
app.include_router(equity.router, prefix="/api")
app.include_router(brief.router, prefix="/api")
app.include_router(campaign.router, prefix="/api")

@app.get("/health", response_model=HealthResponse)
def health():
    loaded = data_loaded()
    return HealthResponse(
        status="ok" if loaded else "degraded",
        data_loaded=loaded,
        last_updated=last_updated() if loaded else "",
    )

@app.get("/api/months", response_model=MonthsResponse)
def get_months():
    return MonthsResponse(available_months=available_months())

if FRONTEND_BUILD_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD_DIR), html=True), name="frontend")
