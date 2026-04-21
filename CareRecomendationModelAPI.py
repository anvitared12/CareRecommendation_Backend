from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Plant Care Recommendation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Paths ─────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent
DATASET_PATH  = BASE_DIR / "PlantCareDataset.xlsx"

# ─── Load Data ─────────────────────────────────────
def load_care_data():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_excel(DATASET_PATH).fillna("")
    df.columns = [str(c).strip() for c in df.columns]
    records = df.to_dict(orient="records")
    indexed = {
        str(r.get("Plant Name", "")).lower().strip(): r
        for r in records
        if str(r.get("Plant Name", "")).strip()
    }
    return records, indexed

records, care_dict = load_care_data()

# ─── Routes ────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "running",
        "total_plants": len(records),
        "columns": list(records[0].keys()) if records else [],
    }

@app.get("/care-recommendation")
def get_care_recommendation(
    plant: str = Query(..., min_length=1, description="Plant name to search")
):
    key = plant.lower().strip()

    # Exact match
    if key in care_dict:
        return {"status": "found", "count": 1, "data": [care_dict[key]]}

    # Partial match
    matches = [
        r for r in records
        if key in str(r.get("Plant Name", "")).lower()
    ]
    if matches:
        return {"status": "partial_match", "count": len(matches), "data": matches}

    raise HTTPException(status_code=404, detail=f"No data found for '{plant}'")

@app.get("/plants")
def list_plants():
    return {
        "total": len(records),
        "plants": [r.get("Plant Name", "") for r in records if r.get("Plant Name")],
    }