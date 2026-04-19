from src.database.mongo_schema import MongoManager
from src.mining.association_rules import RuleMiner
from src.config import MONGO_URI
import pandas as pd

def run_trend_analysis():
    print("1. Connecting to MongoDB Atlas for Date Split Analysis...")
    mongo = MongoManager(uri=MONGO_URI)
    
    # Query datasets by decade bounds
    cursor_2005_2012 = mongo.collection.find({"YEAR": {"$lte": 2012}}, {"_id": 0, "ITEMS": 1})
    cursor_2013_2020 = mongo.collection.find({"YEAR": {"$gte": 2013}}, {"_id": 0, "ITEMS": 1})

    noise_items = {'WARM', 'COLD', 'WET', 'DRY', 'NORMAL_T', 'NORMAL_R',
                   'T-1_WARM', 'T-1_COLD', 'T-1_WET', 'T-1_DRY', 'T-1_NORMAL_T', 'T-1_NORMAL_R',
                   'T-2_WARM', 'T-2_COLD', 'T-2_WET', 'T-2_DRY', 'T-2_NORMAL_T', 'T-2_NORMAL_R',
                   'T-3_WARM', 'T-3_COLD', 'T-3_WET', 'T-3_DRY', 'T-3_NORMAL_T', 'T-3_NORMAL_R'}
    
    def clean_transactions(cursor):
        transactions = []
        for doc in cursor:
            if "ITEMS" in doc and len(doc["ITEMS"]) > 1:
                cleaned = [item for item in doc["ITEMS"] if item not in noise_items]
                if len(cleaned) > 1:
                    transactions.append(cleaned)
        return transactions

    tx_early = clean_transactions(cursor_2005_2012)
    tx_late = clean_transactions(cursor_2013_2020)

    print(f"Loaded {len(tx_early)} transactions from 2005-2012.")
    print(f"Loaded {len(tx_late)} transactions from 2013-2020.")
    
    # Mine the rules identically for both sets
    miner = RuleMiner(min_support=0.03, min_confidence=0.2)
    rules_early = miner.mine_rules(tx_early)
    rules_late = miner.mine_rules(tx_late)
    
    # Formatting helper to convert frozensets into consistent string representations
    def rule_signature(row):
        ants = tuple(sorted(list(row['antecedents'])))
        cons = tuple(sorted(list(row['consequents'])))
        return f"{ants} -> {cons}"
    
    if not rules_early.empty and not rules_late.empty:
        rules_early['signature'] = rules_early.apply(rule_signature, axis=1)
        rules_late['signature'] = rules_late.apply(rule_signature, axis=1)
        
        merged_rules = pd.merge(
            rules_early[['signature', 'antecedents', 'consequents', 'support', 'confidence']],
            rules_late[['signature', 'support', 'confidence']],
            on='signature',
            how='inner',
            suffixes=('_2005_2012', '_2013_2020')
        )
        
        # Calculate Delta to find the Climate Change Signal
        merged_rules['confidence_change'] = merged_rules['confidence_2013_2020'] - merged_rules['confidence_2005_2012']
        merged_rules['support_change'] = merged_rules['support_2013_2020'] - merged_rules['support_2005_2012']
        
        # Sort by the largest increase in confidence across the decade
        merged_rules = merged_rules.sort_values(by='confidence_change', ascending=False)
        
        print("\n========================================================")
        print("📈 CLIMATE CHANGE SIGNAL DETECTED: DECADE OVER DECADE   📈")
        print("========================================================")
        for _, row in merged_rules.head(10).iterrows():
            ants = ", ".join(list(row['antecedents']))
            cons = ", ".join(list(row['consequents']))
            print(f"🚨 Rule: [{ants}]  --->  [{cons}]")
            print(f"   2005-2012 Confidence: {row['confidence_2005_2012'] * 100:.1f}%")
            print(f"   2013-2020 Confidence: {row['confidence_2013_2020'] * 100:.1f}%")
            print(f"   Shift: +{row['confidence_change'] * 100:.1f}%\n")
    else:
        print("Not enough overlapping rules to detect a macro trend. Try lowering thresholds.")

if __name__ == "__main__":
    run_trend_analysis()