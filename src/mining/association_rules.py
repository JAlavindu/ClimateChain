import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

class RuleMiner:
    def __init__(self, min_support=0.05, min_confidence=0.3):
        self.min_support = min_support
        self.min_confidence = min_confidence
        
        # We define what NASA base climate metrics look like.
        self.nasa_bases = ['EXTREME_HEAT', 'WARM', 'EXTREME_COLD', 'COLD', 
                           'EXTREME_RAIN', 'WET', 'SEVERE_DROUGHT', 'DRY']

    def has_lagged_trigger(self, items):
        """Returns True if the antecedent contains at least one lagged T- item."""
        return any(item.startswith("T-") for item in items)

    def has_noaa_disaster(self, items):
        """Returns True if the consequent contains at least one current-month NOAA disaster."""
        for item in items:
            # If it doesn't start with T-, isn't a NASA base, isn't a PROFILE, and isn't an anomaly flag...
            if (not item.startswith("T-") and 
                item not in self.nasa_bases and 
                not item.startswith("PROFILE_") and 
                item != "CLIMATE_ANOMALY"):
                return True
        return False

    def mine_rules(self, transactions_list):
        """
        Takes a list of item lists and returns a DataFrame of association rules.
        """
        if not transactions_list:
            raise ValueError("No transactions provided for mining.")

        print("1. One-hot encoding transactions...")
        te = TransactionEncoder()
        te_ary = te.fit(transactions_list).transform(transactions_list)
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

        print(f"2. Finding frequent itemsets (min_support={self.min_support})...")
        frequent_itemsets = fpgrowth(df_encoded, min_support=self.min_support, use_colnames=True, max_len=3)
        
        if frequent_itemsets.empty:
            print("No frequent itemsets found. Try lowering min_support.")
            return pd.DataFrame()
        
        print(f"-> Found {len(frequent_itemsets)} frequent itemsets. Calculating math logic...")
        print(f"3. Generating association rules (min_confidence={self.min_confidence})...")
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=self.min_confidence)
        
        if rules.empty:
            print("No association rules found. Try lowering min_confidence.")
            return rules
            
        print("4. Filtering rules for Early Warning Intelligence...")
        
        # 1. Triggers must contain at least one past anomaly
        rules = rules[rules['antecedents'].apply(self.has_lagged_trigger)]
        
        # 2. Predicted outcomes must contain at least one current NOAA disaster
        rules = rules[rules['consequents'].apply(self.has_noaa_disaster)]
        
        # 3. Clean up the output: Strip non-disaster "noise" from the consequents for cleaner display
        def isolate_disaster(items):
            return frozenset(item for item in items 
                             if not item.startswith("T-") 
                             and item not in self.nasa_bases
                             and not item.startswith("PROFILE_")
                             and item != "CLIMATE_ANOMALY")
            
        rules['consequents'] = rules['consequents'].apply(isolate_disaster)
        
        # Sort by confidence and lift to bubble up the best correlations
        rules = rules.sort_values(by=['confidence', 'lift'], ascending=[False, False])
        
        # Drop duplicate rules that emerge after isolating the disasters
        rules = rules.drop_duplicates(subset=['antecedents', 'consequents'])
        
        return rules