from src.database.mongo_schema import MongoManager
from src.mining.association_rules import RuleMiner
from src.config import MONGO_URI
import os

def run_phase_3():
    print("1. Connecting to MongoDB Atlas...")
    # Using the secure URI loaded from .env via config.py
    mongo = MongoManager(uri=MONGO_URI)
    
    # Query the collection for all transactions
    cursor = mongo.collection.find({}, {"_id": 0, "ITEMS": 1})
    
    # Extract just the lists of items
    transactions = [doc["ITEMS"] for doc in cursor if "ITEMS" in doc and len(doc["ITEMS"]) > 1]
    
    print(f"Loaded {len(transactions)} multi-event transactions from NoSQL DB.")
    
    miner = RuleMiner(min_support=0.01, min_confidence=0.2)
    rules_df = miner.mine_rules(transactions)
    
    if rules_df.empty:
        print("No strong rules found with current thresholds.")
        return

    print("\n========================================================")
    print("🥇 TOP CASCADING CLIMATE DISASTER PATTERNS DISCOVERED 🥇")
    print("========================================================")
    
    for index, row in rules_df.head(10).iterrows():
        antecedents = ", ".join(list(row['antecedents']))
        consequents = ", ".join(list(row['consequents']))
        confidence = row['confidence'] * 100
        lift = row['lift']
        
        print(f"🚨 Rule: [{antecedents}]  --->  [{consequents}]")
        print(f"   Confidence: {confidence:.1f}% | Lift: {lift:.2f}x greater than chance\n")

if __name__ == "__main__":
    run_phase_3()