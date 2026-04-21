from pathlib import Path

from fastapi import FastAPI
from keras.models import load_model

from PIL import Image
import numpy as np

from fastapi import File, UploadFile, HTTPException
from sklearn import preprocessing
import pandas as pd

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
CARE_DATASET_PATH = PROJECT_ROOT  / "PlantCareDataset.xlsx"
PLANT_MODEL_PATH = PROJECT_ROOT / "Models" / "plant_efficientnet_model.keras"
DISEASE_MODEL_PATH = PROJECT_ROOT / "Models" / "plantdisease_efficientnet_model.keras"

try:
    care_df = pd.read_excel(CARE_DATASET_PATH)
    care_dict = {}
    for _, row in care_df.iterrows():
        plant_name = str(row['Plant Name']).lower().strip()
        care_dict[plant_name] = {
            "Growth": row.get("Growth", ""),
            "Soil": row.get("Soil", ""),
            "Sunlight": row.get("Sunlight", ""),
            "Watering": row.get("Watering", ""),
            "Fertilization Type": row.get("Fertilization Type", "")
        }
except Exception as e:
    print(f"Error loading Care recommendation dataset: {e}")
    care_dict = {}

plant_identification_model = load_model(str(PLANT_MODEL_PATH))
disease_identification_model = load_model(str(DISEASE_MODEL_PATH))

def processing_image(image, size=(244,244)):
    image = image.resize(size)
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image


plant_labels = []
disease_labels = []

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    image = Image.open(file.file).convert("RGB")
    img = processing_image(image)

    # PLANT DETECTION
    plant_pred = plant_identification_model.predict(img)
    plant_idx = int(np.argmax(plant_pred))
    plant_name = plant_labels[plant_idx]

    # DISEASE DETECTION
    disease_pred = disease_identification_model.predict(img)
    disease_idx = int(np.argmax(disease_pred))
    disease_name = disease_labels[disease_idx]

    return {
        "plant":plant_name,
        "plant_confidence": float(np.max(plant_pred)),
        "disease":disease_name,
        "disease_confidence":float(np.max(disease_pred))
    }


@app.get("/care-recommendation")
async def get_care_recommendation(plant: str):
    plant_key = plant.lower().strip()
    if plant_key in care_dict:
        return {"plant": plant, "recommendation": care_dict[plant_key]}
    else:
        raise HTTPException(status_code=404, detail="Plant not found in the dataset")
