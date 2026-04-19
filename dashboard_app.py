import streamlit as st
import pandas as pd
from pyvis.network import Network
import tempfile
import os

from src.database.mongo_schema import MongoManager
from src.mining.association_rules import RuleMiner
from src.config import MONGO_URI

# Configure page settings
st.set_page_config(page_title="ClimateChain Early Warning System", layout="wide")

@st.cache_data
def fetch_transactions_from_db():
    """Downloads data from Mongo ONCE per session. Never reruns when sliders move."""
    mongo = MongoManager(uri=MONGO_URI)
    cursor = mongo.collection.find({}, {"_id": 0, "ITEMS": 1})
    transactions = [doc["ITEMS"] for doc in cursor if "ITEMS" in doc and len(doc["ITEMS"]) > 1]
    return transactions

@st.cache_data
def run_mining(_transactions, min_supp, min_conf):
    """Mines the rules. The underscore in _transactions tells Streamlit not to hash the massive dataset."""
    miner = RuleMiner(min_support=min_supp, min_confidence=min_conf)
    return miner.mine_rules(_transactions)

@st.cache_data
def load_and_mine_data(min_supp, min_conf):
    """Loads data from Mongo and mines rules. Cached so it doesn't query constantly."""
    mongo = MongoManager(uri=MONGO_URI)
    cursor = mongo.collection.find({}, {"_id": 0, "ITEMS": 1})
    transactions = [doc["ITEMS"] for doc in cursor if "ITEMS" in doc and len(doc["ITEMS"]) > 1]
    
    miner = RuleMiner(min_support=min_supp, min_confidence=min_conf)
    return miner.mine_rules(transactions)

# ----- UI Layout -----
st.title("🌪️ ClimateChain: Disaster Early Warning System")
st.markdown("Mining cascading climate patterns using Multi-Level Association Rules over a NoSQL architecture.")

# --- Sidebar Controls ---
st.sidebar.header("Mining Parameters")
min_support = st.sidebar.slider("Minimum Support Threshold", 0.01, 0.10, 0.05, 0.01)
min_confidence = st.sidebar.slider("Minimum Confidence Threshold", 0.1, 1.0, 0.3, 0.1)

st.sidebar.markdown("""
---
**Support:** How often the pattern appears.  
**Confidence:** Likelihood the consequent follows the antecedent.
""")

# --- Process Data ---
with st.spinner("Connecting to database..."):
    # This runs exactly once!
    transactions = fetch_transactions_from_db()
    
with st.spinner("Querying NoSQL database and mining rules..."):
    rules_df = load_and_mine_data(min_support, min_confidence)

if rules_df.empty:
    st.warning("No strong rules found with the current thresholds. Try lowering them.")
else:
    # --- Top Rules Table ---
    st.subheader("Top Actionable Cascading Risks")
    
    # Format for display
    display_df = rules_df.head(20).copy()
    display_df['Antecedents (Triggers)'] = display_df['antecedents'].apply(lambda x: ", ".join(list(x)))
    display_df['Consequents (Disaster)'] = display_df['consequents'].apply(lambda x: ", ".join(list(x)))
    display_df['Confidence'] = (display_df['confidence'] * 100).apply(lambda x: f"{x:.1f}%")
    display_df['Lift'] = display_df['lift'].apply(lambda x: f"{x:.2f}x")
    
    st.dataframe(display_df[['Antecedents (Triggers)', 'Consequents (Disaster)', 'Confidence', 'Lift', 'support']])

    # --- Interactive Network Graph ---
    st.subheader("Cascading Threat Network")
    st.markdown("This graph visually models how preceding conditions cascade into ultimate disasters.")
    
    # Build PyVis Network
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    
    for _, row in rules_df.head(15).iterrows():
        ants = list(row['antecedents'])
        cons = list(row['consequents'])
        
        # Add Consequent (The ultimate disaster)
        for c in cons:
            net.add_node(c, label=c, color="#ff4b4b", size=30)  # Red for disaster
            
        # Add Antecedents (Triggers) and point them to Consequents
        for a in ants:
            net.add_node(a, label=a, color="#feca57", size=20)  # Yellow for triggers
            for c in cons:
                # Hover title shows confidence percentage
                title = f"Confidence: {row['confidence']*100:.1f}%"
                net.add_edge(a, c, title=title, value=row['confidence'])

    # Save and render the graph in Streamlit
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)
        with open(tmp_file.name, 'r', encoding='utf-8') as f:
            html_string = f.read()
            
    st.components.v1.html(html_string, height=650)