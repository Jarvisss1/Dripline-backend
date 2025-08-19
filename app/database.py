from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .config import settings
from bson import ObjectId

# Create a new client and connect to the server using the modern async API
client = MongoClient(settings.MONGO_DETAILS, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ Could not connect to MongoDB: {e}")


db = client.fashion_advisor
wardrobe_collection = db.get_collection("wardrobes")

# Helper to convert MongoDB document to Python dict
def item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "user_id": item["user_id"],
        "image_url": item["image_url"],
        "category": item["category"],
        "tags": item["tags"],
        "embedding": item["embedding"],
    }
