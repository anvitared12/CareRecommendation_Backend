from pathlib import Path


target_file = Path(__file__).resolve().parent / "CareRecomendationModelAPI.py"

with target_file.open('a', encoding='utf-8') as f:
    f.write('''
@app.get("/care-recommendation")
async def get_care_recommendation(plant: str):
    plant_key = plant.lower().strip()
    if plant_key in care_dict:
        return {"plant": plant, "recommendation": care_dict[plant_key]}
    else:
        raise HTTPException(status_code=404, detail="Plant not found in the dataset")
''')
