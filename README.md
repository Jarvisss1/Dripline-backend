# 👕 AI Fashion Advisor – Backend

This repository contains the backend service for the **AI Fashion Advisor**, a mobile application that provides **personalized clothing recommendations**.  
The backend is built with **FastAPI** and leverages a hybrid AI system combining **LLM-based tagging** and a **Siamese Neural Network** for intelligent and context-aware fashion advice.

---

## 🚀 System Overview

The system follows a **Filter → Rank** approach:

- **Filter**: Wardrobe items are filtered by descriptive tags (season, occasion, etc.), auto-generated via a Large Language Model (LLM).  
- **Rank**: Filtered items are ranked based on **visual compatibility** using a trained **Siamese Neural Network**.

👉 **Frontend**: The React Native Expo app is available in a separate repository. [Frontend Repo Link](#)  

---

## ✨ Core Features

- 🔐 **Secure Authentication** – User sign-up/sign-in via Clerk with JWT-based session management.  
- 👗 **Wardrobe Management** – Upload, view, and delete clothing items, stored in **MongoDB Atlas**.  
- 🧾 **AI-Powered Tagging** – Uses **Google Gemini API** to automatically tag items (e.g., *casual, summer, work, swimwear*).  
- 🎨 **Visual Compatibility Ranking** – Trained **Siamese Neural Network** predicts compatibility between outfits.  
- 🧠 **Advanced Recommendation Engine** – Combines LLM tags + Siamese embeddings for context-aware outfit suggestions.  

---

## 🛠️ Tech Stack

- **Framework**: FastAPI  
- **Database**: MongoDB + Motor (async driver)  
- **Authentication**: Clerk + JWT  
- **Machine Learning**:
  - LLM Tagging → Google Gemini Pro API  
  - Visual Model → TensorFlow/Keras (Siamese Network)  
- **Deployment**: Render / Heroku  
- **Environment**: Python 3.9+, `venv`, `python-dotenv`  

---

## 🧠 AI Models

### 1. Siamese Network – Visual Compatibility  
- Learns a **vector embedding space** where compatible clothing items cluster together.  
- **Training Dataset**: Polyvore Outfits (~164K outfits, 365K items).  
- **Training Notebook**: [Link to Notebook](https://github.com/Jarvisss1/Dripline-backend/blob/main/Fashion_Compatibility_ML_Model.ipynb)  
- **Model File**: `models/fashion_compatibility_encoder.h5`  

### 2. Google Gemini – Metadata Tagging  
- Uses **Gemini Pro API** with custom prompts for **fashion-specific tagging**.  
- Generates structured JSON tags: *category, type, season, occasion*.  

---

## ⚡ Getting Started

### ✅ Prerequisites
- Python 3.9+  
- MongoDB Atlas account + connection string  
- Clerk app with Issuer URL  
- Google AI Studio API key  

### 🔧 Setup Instructions

```bash
# 1. Clone the repo
git clone https://github.com/Jarvisss1/Dripline-backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add environment variables
touch .env
```
## ⚙️ Example `.env` file
```env
MONGO_DETAILS="your_mongodb_connection_string"
CLERK_ISSUER_URL="https://your-instance.clerk.accounts.dev"
GEMINI_API_KEY="your_google_gemini_api_key"
```
## 🧠 Add Trained Model

Place `fashion_compatibility_encoder.h5` inside the `models/` directory.

## 🚀 Run Server
```bash
uvicorn app.main:app --reload
```

- Visit: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

## 📡 API Endpoints

| Method | Endpoint                     | Access  | Description                         |
|--------|------------------------------|---------|-------------------------------------|
| GET    | `/`                          | Public  | Health check                        |
| POST   | `/wardrobe/add-item`         | Private | Upload clothing item + auto-tags    |
| GET    | `/wardrobe`                  | Private | Fetch user’s wardrobe               |
| DELETE | `/wardrobe/items/{item_id}`  | Private | Delete wardrobe item                |
| POST   | `/recommendations/filtered`  | Private | Get outfit recommendations          |

## Related Links
- [Frontend Repository](https://github.com/Jarvisss1/Dripline-backend/blob/main/Fashion_Compatibility_ML_Model.ipynb)
- [Training Notebook](https://github.com/Jarvisss1/Dripline-frontend)

