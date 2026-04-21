from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Plant Care Recommendation API",
    description="Search plant care details from the Excel dataset.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATASET_PATH = PROJECT_ROOT / "Textual_Datasets" / "PlantCareDataset.xlsx"
PLANT_COLUMN = "Plant Name"


def clean_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_key(value: str) -> str:
    return clean_value(value).lower()


def row_to_record(row: pd.Series) -> dict:
    record = {}
    for column, value in row.items():
        record[column] = clean_value(value)
    return record


def load_care_data():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_excel(DATASET_PATH).fillna("")
    df.columns = [clean_value(column) for column in df.columns]

    if PLANT_COLUMN not in df.columns:
        raise ValueError(f"Missing required column: {PLANT_COLUMN}")

    records = [row_to_record(row) for _, row in df.iterrows()]
    indexed_records = {
        normalize_key(record[PLANT_COLUMN]): record
        for record in records
        if normalize_key(record[PLANT_COLUMN])
    }
    return records, indexed_records


records, care_dict = load_care_data()


@app.get("/")
def root():
    return {
        "message": "Plant Care Recommendation API is running",
        "total_plants": len(records),
        "available_columns": list(records[0].keys()) if records else [],
    }


@app.get("/care-recommendation")
def get_care_recommendation(
    plant: str = Query(..., min_length=1, description="Plant name to search"),
):
    plant_key = normalize_key(plant)

    if plant_key in care_dict:
        return {"status": "found", "count": 1, "data": [care_dict[plant_key]]}

    matches = [
        record
        for record in records
        if plant_key in normalize_key(record.get(PLANT_COLUMN, ""))
    ]
    if matches:
        return {"status": "partial_match", "count": len(matches), "data": matches}

    raise HTTPException(
        status_code=404,
        detail=f"No plant data found for '{plant}'.",
    )


@app.get("/plants")
def list_plants():
    return {
        "total": len(records),
        "plants": [record[PLANT_COLUMN] for record in records if record.get(PLANT_COLUMN)],
    }
