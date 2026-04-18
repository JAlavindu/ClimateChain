import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

class RuleMiner:
    def __init__(self, min_support=0.03, min_confidence=0.4):
        self.min_support = min_support
        self.min_confidence = min_confidence
        
        # We define what NASA base climate metrics look like.
        # Anything starting with a 'T-' is a lag feature. 
        # Anything matching these bases without a prefix is current month's NASA weather.
        self.nasa_bases = ['EXTREME_HEAT', 'WARM', 'EXTREME_COLD', 'COLD', 
                           'EXTREME_RAIN', 'WET', 'SEVERE_DROUGHT', 'DRY']

    def is_noaa_disaster(self, items):
        """Returns True if the itemset contains AT LEAST ONE actual NOAA disaster event (T-0).""" # NASA metrics (e.g., EXTREME_HEAT) occurring in the current month are not a "disaster output" in this context.
        for item in items:
            if not item.startswith("T-") and item not in self.nasa_bases:
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
        frequent_itemsets = fpgrowth(df_encoded, min_support=self.min_support, use_colnames=True)
        
        if frequent_itemsets.empty:
            print("No frequent itemsets found. Try lowering min_support.")
            return pd.DataFrame()

        print(f"3. Generating association rules (min_confidence={self.min_confidence})...")
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=self.min_confidence)
        
        if rules.empty:
            return rules
            
        print("4. Filtering rules for Early Warning Intelligence...")
        # A good Early Warning Rule MUST have a lagged variable as an antecedent
        rules = rules[rules['antecedents'].apply(lambda items: any(item.startswith('T-') for item in items))]
        
        # A good Early Warning Rule MUST predict a NOAA Disaster in the current month as the consequent
        rules = rules[rules['consequents'].apply(self.is_noaa_disaster)]
        
        # Sort by confidence and lift 
        rules = rules.sort_values(by=['confidence', 'lift'], ascending=[False, False])
        
        return rules