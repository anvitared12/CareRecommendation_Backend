import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATASET_PATH = PROJECT_ROOT / "PlantCareDataset.xlsx"
OUTPUT_PATH = BASE_DIR / "dump.json"

df = pd.read_excel(DATASET_PATH)
with OUTPUT_PATH.open('w', encoding='utf-8') as f:
    f.write(json.dumps(df.head(2).to_dict(orient='records'), indent=4))
