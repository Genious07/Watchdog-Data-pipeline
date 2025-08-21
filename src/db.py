import os
from datetime import datetime
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "quality_monitor")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "quality_metrics")

client = None
collection = None

if MONGODB_URI:
    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB]
        collection = db[MONGODB_COLLECTION]
    except Exception as e:
        print(f"MongoDB init failed: {e}")
        client = None
        collection = None


def store_results(summary, full_results):
    if not collection:
        print("MongoDB not configured; skipping store_results.")
        return
    doc = {
        **summary,
        "full_results": full_results,
        "stored_at": datetime.utcnow(),
    }
    collection.insert_one(doc)


def get_last_hash():
    if not collection:
        return None
    last_doc = collection.find_one(sort=[("timestamp", -1)])
    return (
        last_doc["content_hash"]
        if last_doc and "content_hash" in last_doc
        else None
    )
