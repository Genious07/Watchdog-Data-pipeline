#!/usr/bin/env python3
"""
Demo Data Generator for Data Quality Watchdog

This script generates realistic historical data for the Grafana dashboard
to create an impressive showcase with meaningful trends and patterns.
"""

import os
import sys
import pymongo
from datetime import datetime, timedelta
import random
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_to_mongodb():
    """Connect to MongoDB using environment variables."""
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        mongodb_db = os.getenv("MONGODB_DB", "quality_monitor")
        mongodb_collection = os.getenv("MONGODB_COLLECTION", "quality_metrics")
        
        if not mongodb_uri:
            print("❌ MONGODB_URI not found in environment variables")
            return None, None
        
        client = pymongo.MongoClient(mongodb_uri)
        db = client[mongodb_db]
        collection = db[mongodb_collection]
        
        # Test connection
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {mongodb_db}.{mongodb_collection}")
        
        return client, collection
    
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return None, None

def generate_realistic_data_point(timestamp, base_quality=95, trend_factor=0):
    """Generate a realistic data quality validation result."""
    
    # Add some realistic variation
    quality_variation = random.uniform(-10, 5)  # Slight negative bias
    trend_influence = trend_factor * random.uniform(-2, 2)
    
    # Calculate quality score with bounds
    quality_score = max(70, min(100, base_quality + quality_variation + trend_influence))
    
    # Determine success based on quality score
    success = quality_score >= 95
    
    # Generate expectation results
    n_expectations = 8  # Fixed number of expectations
    n_success = int((quality_score / 100) * n_expectations)
    n_failed = n_expectations - n_success
    percent_valid = (n_success / n_expectations) * 100
    
    # Generate content hash (simulate data changes)
    content_hash = f"demo_hash_{timestamp.strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    
    return {
        "timestamp": timestamp,
        "success": success,
        "n_expectations": n_expectations,
        "n_success": n_success,
        "n_failed": n_failed,
        "percent_valid": round(percent_valid, 2),
        "content_hash": content_hash,
        "stored_at": timestamp,
        "demo_data": True  # Flag to identify demo data
    }

def generate_demo_dataset(hours=72, interval_minutes=60):
    """Generate a complete demo dataset with realistic patterns."""
    
    print(f"🎯 Generating {hours} hours of demo data (every {interval_minutes} minutes)")
    
    data_points = []
    current_time = datetime.utcnow()
    
    # Create realistic patterns
    for i in range(int(hours * 60 / interval_minutes)):
        timestamp = current_time - timedelta(minutes=i * interval_minutes)
        
        # Create daily patterns (higher quality during business hours)
        hour = timestamp.hour
        if 9 <= hour <= 17:  # Business hours
            base_quality = 96
        elif 18 <= hour <= 23 or 6 <= hour <= 8:  # Evening/morning
            base_quality = 94
        else:  # Night hours
            base_quality = 92
        
        # Add weekly patterns (slightly lower quality on weekends)
        if timestamp.weekday() >= 5:  # Weekend
            base_quality -= 2
        
        # Add some long-term trends
        trend_factor = -0.1 if i > hours * 0.7 else 0.1  # Slight degradation over time
        
        # Occasionally simulate incidents (5% chance)
        if random.random() < 0.05:
            base_quality = random.uniform(75, 85)  # Incident quality
        
        data_point = generate_realistic_data_point(timestamp, base_quality, trend_factor)
        data_points.append(data_point)
    
    return data_points

def insert_demo_data(collection, data_points, clear_existing=False):
    """Insert demo data into MongoDB collection."""
    
    if clear_existing:
        print("🧹 Clearing existing demo data...")
        result = collection.delete_many({"demo_data": True})
        print(f"   Deleted {result.deleted_count} existing demo records")
    
    print(f"📊 Inserting {len(data_points)} demo data points...")
    
    try:
        result = collection.insert_many(data_points)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} records")
        
        # Show summary statistics
        total_records = collection.count_documents({})
        demo_records = collection.count_documents({"demo_data": True})
        success_rate = collection.count_documents({"success": True, "demo_data": True}) / demo_records * 100
        avg_quality = list(collection.aggregate([
            {"$match": {"demo_data": True}},
            {"$group": {"_id": None, "avg_quality": {"$avg": "$percent_valid"}}}
        ]))[0]["avg_quality"]
        
        print(f"\n📈 Dataset Summary:")
        print(f"   Total records in collection: {total_records}")
        print(f"   Demo records: {demo_records}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Average quality score: {avg_quality:.1f}%")
        
    except Exception as e:
        print(f"❌ Failed to insert data: {e}")

def main():
    """Main function to generate and insert demo data."""
    
    print("🚀 Data Quality Watchdog - Demo Data Generator")
    print("=" * 50)
    
    # Connect to MongoDB
    client, collection = connect_to_mongodb()
    if not collection:
        sys.exit(1)
    
    # Check for existing data
    existing_count = collection.count_documents({})
    demo_count = collection.count_documents({"demo_data": True})
    
    print(f"\n📊 Current Database Status:")
    print(f"   Total records: {existing_count}")
    print(f"   Demo records: {demo_count}")
    
    # Generate demo data
    print(f"\n🎲 Generating demo data...")
    
    # Generate 3 days of hourly data for good showcase
    data_points = generate_demo_dataset(hours=72, interval_minutes=60)
    
    # Insert data
    insert_demo_data(collection, data_points, clear_existing=True)
    
    # Show latest records for verification
    print(f"\n🔍 Latest 5 records:")
    latest_records = list(collection.find({"demo_data": True}).sort("timestamp", -1).limit(5))
    for record in latest_records:
        status = "✅ PASS" if record["success"] else "❌ FAIL"
        print(f"   {record['timestamp'].strftime('%Y-%m-%d %H:%M')} | {status} | {record['percent_valid']:.1f}%")
    
    print(f"\n🎉 Demo data generation complete!")
    print(f"💡 Your Grafana dashboard should now show rich historical data")
    print(f"🔗 Time range recommendation: Last 72 hours")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    main()

