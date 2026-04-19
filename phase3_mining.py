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

    noise_items = {'WARM', 'COLD', 'WET', 'DRY', 'NORMAL_T', 'NORMAL_R',
                   'T-1_WARM', 'T-1_COLD', 'T-1_WET', 'T-1_DRY', 'T-1_NORMAL_T', 'T-1_NORMAL_R',
                   'T-2_WARM', 'T-2_COLD', 'T-2_WET', 'T-2_DRY', 'T-2_NORMAL_T', 'T-2_NORMAL_R',
                   'T-3_WARM', 'T-3_COLD', 'T-3_WET', 'T-3_DRY', 'T-3_NORMAL_T', 'T-3_NORMAL_R'}
    
    # Extract just the lists of items
    transactions = []
    for doc in cursor:
        if "ITEMS" in doc and len(doc["ITEMS"]) > 1:
            # Strip noise items to prevent FP-Growth memory explosion
            cleaned = [item for item in doc["ITEMS"] if item not in noise_items]
            if len(cleaned) > 1:
                transactions.append(cleaned)

    print(f"Loaded {len(transactions)} multi-event transactions from NoSQL DB.")
    
    miner = RuleMiner(min_support=0.05, min_confidence=0.3)
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