import numpy as tf_np
import tensorflow as tf
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
import base64
import io
import requests
import json
from bson import ObjectId
from typing import List

# Import from our other modules
from .config import settings
from .database import wardrobe_collection, item_helper
from .auth import get_current_user_id
from .schemas import RecommendationRequest, RecommendationResponse, ClothingItemSchema

# --- 1. Application Setup ---
app = FastAPI(
    title="AI Fashion Advisor API",
    description="Provides fashion recommendations using a hybrid Filter-then-Rank system.",
)

origins = ["http://localhost:8081", "exp://..."] # Add your Expo Go URL
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- 2. Model and Helper Functions ---
ENCODER_MODEL = None
IMG_SHAPE = (128, 128, 3)

@app.on_event("startup")
def load_model():
    global ENCODER_MODEL
    try:
        ENCODER_MODEL = tf.keras.models.load_model('models/fashion_compatibility_encoder.h5', compile=False)
        print("✅ Siamese encoder model loaded successfully.")
    except IOError:
        print("❌ CRITICAL ERROR: 'models/fashion_compatibility_encoder.h5' not found.")

def preprocess_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((IMG_SHAPE[0], IMG_SHAPE[1]))
        img = tf_np.array(img) / 255.0
        return tf_np.expand_dims(img, axis=0)
    except (IOError, UnidentifiedImageError):
        return None

def get_embedding_from_bytes(image_bytes):
    if not ENCODER_MODEL: return None
    processed_img = preprocess_image(image_bytes)
    if processed_img is None: return None
    return ENCODER_MODEL.predict(processed_img, verbose=0).tolist()

def get_compatibility_score(embedding1, embedding2):
    return tf_np.linalg.norm(tf_np.array(embedding1) - tf_np.array(embedding2))

# --- 3. API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Fashion Advisor API"}

@app.post("/wardrobe/add-item", response_model=ClothingItemSchema)
async def add_item_to_wardrobe(user_id: str = Depends(get_current_user_id), file: UploadFile = File(...)):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")

    image_bytes = await file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # --- Step 1: LLM Tagging ---
    prompt_parts = [
        {
            "text": """You are a fashion expert metadata tagger. Analyze the clothing item in the image and return a single, valid JSON object. The object must have the following keys:
- "category": A string, one of ["top", "bottom", "shoes", "outerwear", "accessory"].
- "type": A specific string describing the item (e.g., "t-shirt", "blouse", "jeans", "sneakers").
- "season": An array of strings, choose from ["spring", "summer", "autumn", "winter"].
- "occasion": An array of strings, choose from ["casual", "work", "formal", "party", "sporty"].
Do not include any text or markdown formatting before or after the JSON object."""
        },
        {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64_image
            }
        }
    ]
    payload = {"contents": [{"parts": prompt_parts}], "generationConfig": {"response_mime_type": "application/json"}}
    response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}", json=payload)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Error from Gemini API: {response.text}")
    
    tags = json.loads(response.json()['candidates'][0]['content']['parts'][0]['text'])

    # --- Step 2: Calculate Embedding ---
    embedding = get_embedding_from_bytes(image_bytes)
    if not embedding:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    # --- Step 3: Save to DB ---
    new_item_data = {
        "user_id": user_id,
        "image_url": f"https://storage.example.com/{user_id}/{file.filename}", # Placeholder URL
        "category": tags.get("category", "unknown"),
        "tags": tags,
        "embedding": embedding[0]
    }
    
    result = await wardrobe_collection.insert_one(new_item_data)
    created_item = await wardrobe_collection.find_one({"_id": result.inserted_id})
    return item_helper(created_item)

@app.get("/wardrobe", response_model=List[ClothingItemSchema])
async def get_wardrobe(user_id: str = Depends(get_current_user_id)):
    items = []
    async for item in wardrobe_collection.find({"user_id": user_id}):
        items.append(item_helper(item))
    return items

@app.delete("/wardrobe/items/{item_id}", status_code=204)
async def delete_wardrobe_item(item_id: str, user_id: str = Depends(get_current_user_id)):
    delete_result = await wardrobe_collection.delete_one({"_id": ObjectId(item_id), "user_id": user_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found in your wardrobe.")
    return

@app.post("/recommendations/filtered", response_model=List[RecommendationResponse])
async def get_filtered_recommendations(request: RecommendationRequest, user_id: str = Depends(get_current_user_id)):
    query = {"user_id": user_id}
    for key, value in request.filters.items():
        query[f"tags.{key}"] = value
        
    cursor = wardrobe_collection.find(query)
    candidates = await cursor.to_list(length=100)
    
    candidates = [item for item in candidates if str(item['_id']) != request.input_item_id]

    if not candidates:
        return []

    input_item_doc = await wardrobe_collection.find_one({"_id": ObjectId(request.input_item_id), "user_id": user_id})
    if not input_item_doc:
        raise HTTPException(status_code=404, detail="Input item not found.")
    
    input_embedding = input_item_doc["embedding"]

    recommendations = []
    for candidate in candidates:
        score = get_compatibility_score(input_embedding, candidate["embedding"])
        recommendations.append({"item": item_helper(candidate), "compatibility_score": float(score)})

    recommendations.sort(key=lambda x: x['compatibility_score'])
    return recommendations[:10]
