import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

class RuleMiner:
    def __init__(self, min_support=0.05, min_confidence=0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence

    def mine_rules(self, transactions_list):
        """
        Takes a list of item lists and returns a DataFrame of association rules.
        Example input: [['HIGH_WIND', 'MODERATE_DAMAGE'], ['EXTREME_WIND', 'TORNADO', 'SEVERE_DAMAGE']]
        """
        if not transactions_list:
            raise ValueError("No transactions provided for mining.")

        print("1. One-hot encoding transactions...")
        # Machine learning algorithms require transactions to be a boolean matrix (One-Hot Encoded)
        te = TransactionEncoder()
        te_ary = te.fit(transactions_list).transform(transactions_list)
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

        print(f"2. Finding frequent itemsets (min_support={self.min_support})...")
        # Use FP-Growth instead of Apriori for better performance
        frequent_itemsets = fpgrowth(df_encoded, min_support=self.min_support, use_colnames=True)
        
        if frequent_itemsets.empty:
            print("No frequent itemsets found. Try lowering min_support.")
            return pd.DataFrame()

        print(f"3. Generating association rules (min_confidence={self.min_confidence})...")
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=self.min_confidence)
        
        # Sort by confidence and lift (Lift > 1 means the events are positively correlated)
        rules = rules.sort_values(by=['confidence', 'lift'], ascending=[False, False])
        
        return rules