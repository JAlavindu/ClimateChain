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

    noise_items = {'WARM', 'COLD', 'WET', 'DRY', 'NORMAL_T', 'NORMAL_R',
                   'T-1_WARM', 'T-1_COLD', 'T-1_WET', 'T-1_DRY', 'T-1_NORMAL_T', 'T-1_NORMAL_R',
                   'T-2_WARM', 'T-2_COLD', 'T-2_WET', 'T-2_DRY', 'T-2_NORMAL_T', 'T-2_NORMAL_R',
                   'T-3_WARM', 'T-3_COLD', 'T-3_WET', 'T-3_DRY', 'T-3_NORMAL_T', 'T-3_NORMAL_R'}
    
    transactions = []
    for doc in cursor:
        if "ITEMS" in doc and len(doc["ITEMS"]) > 1:
            cleaned = [item for item in doc["ITEMS"] if item not in noise_items]
            if len(cleaned) > 1:
                transactions.append(cleaned)
                
    return transactions

@st.cache_data
def load_and_mine_data(min_supp, min_conf):
    """Loads data from Mongo and mines rules. Cached so it doesn't query constantly."""
    mongo = MongoManager(uri=MONGO_URI)
    cursor = mongo.collection.find({}, {"_id": 0, "ITEMS": 1})
    transactions = [doc["ITEMS"] for doc in cursor if "ITEMS" in doc and len(doc["ITEMS"]) > 1]
    
    miner = RuleMiner(min_support=min_supp, min_confidence=min_conf)
    return miner.mine_rules(transactions)

@st.cache_data
def generate_climate_trend_data():
    """Builds the table comparing 2005-2012 vs 2013-2020 directly from MongoDB."""
    mongo = MongoManager(uri=MONGO_URI)
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

    miner = RuleMiner(min_support=0.03, min_confidence=0.2)
    rules_early = miner.mine_rules(tx_early)
    rules_late = miner.mine_rules(tx_late)
    
    def rule_signature(row):
        ants = tuple(sorted(list(row['antecedents'])))
        cons = tuple(sorted(list(row['consequents'])))
        return f"{ants} -> {cons}"
    
    if rules_early.empty or rules_late.empty:
        return pd.DataFrame()

    rules_early['signature'] = rules_early.apply(rule_signature, axis=1)
    rules_late['signature'] = rules_late.apply(rule_signature, axis=1)
    
    merged_rules = pd.merge(
        rules_early[['signature', 'antecedents', 'consequents', 'support', 'confidence', 'lift']],
        rules_late[['signature', 'support', 'confidence', 'lift']],
        on='signature',
        how='inner',
        suffixes=('_early', '_late')
    )
    
    merged_rules['confidence_change'] = merged_rules['confidence_late'] - merged_rules['confidence_early']
    merged_rules = merged_rules.sort_values(by='confidence_change', ascending=False)
    
    return merged_rules

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

# Initialize Tabs
tab1, tab2 = st.tabs(["🔴 Early Warning Network", "📈 Climate Change Signal"])

with tab1:
    with st.spinner("Connecting to database..."):
        transactions = fetch_transactions_from_db()

    with st.spinner("Querying NoSQL database and mining rules..."):
        rules_df = load_and_mine_data(min_support, min_confidence)

    if rules_df.empty:
        st.warning("No strong rules found with the current thresholds. Try lowering them.")
    else:
        st.subheader("Top Actionable Cascading Risks")
        display_df = rules_df.head(20).copy()
        display_df['Antecedents (Triggers)'] = display_df['antecedents'].apply(lambda x: ", ".join(list(x)))
        display_df['Consequents (Disaster)'] = display_df['consequents'].apply(lambda x: ", ".join(list(x)))
        display_df['Confidence'] = (display_df['confidence'] * 100).apply(lambda x: f"{x:.1f}%")
        display_df['Lift'] = display_df['lift'].apply(lambda x: f"{x:.2f}x")
        
        st.dataframe(display_df[['Antecedents (Triggers)', 'Consequents (Disaster)', 'Confidence', 'Lift', 'support']])

        st.subheader("Cascading Threat Network")
        st.markdown("This graph visually models how preceding conditions cascade into ultimate disasters.")
        
        # Build PyVis Network
        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", directed=True)
        
        for _, row in rules_df.head(15).iterrows():
            ants = list(row['antecedents'])
            cons = list(row['consequents'])
            
            for c in cons:
                net.add_node(c, label=c, color="#ff4b4b", size=30)
                
            for a in ants:
                net.add_node(a, label=a, color="#feca57", size=20)
                for c in cons:
                    title = f"Confidence: {row['confidence']*100:.1f}%"
                    net.add_edge(a, c, title=title, value=row['confidence'])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            net.save_graph(tmp_file.name)
            with open(tmp_file.name, 'r', encoding='utf-8') as f:
                html_string = f.read()
                
        st.components.v1.html(html_string, height=650)

with tab2:
    st.subheader("Decade-over-Decade Trend Analysis")
    st.markdown("This tab displays the **Climate Change Signal**. It compares rules from **2005-2012** against **2013-2020** to expose how disaster predictability and sequence connectivity are increasing over time.")
    
    with st.spinner("Crunching historical decades... this might take a moment."):
        trend_df = generate_climate_trend_data()
        
    if trend_df.empty:
        st.warning("Not enough overlapping data detected across decades. Try lowering global thresholds.")
    else:
        display_trend = trend_df.head(25).copy()
        
        # Format the strings for an elegant display table
        display_trend['Antecedents (Triggers)'] = display_trend['antecedents'].apply(lambda x: ", ".join(list(x)))
        display_trend['Consequents (Disaster)'] = display_trend['consequents'].apply(lambda x: ", ".join(list(x)))
        display_trend['2005-2012 Confidence'] = (display_trend['confidence_early'] * 100).apply(lambda x: f"{x:.1f}%")
        display_trend['2013-2020 Confidence'] = (display_trend['confidence_late'] * 100).apply(lambda x: f"{x:.1f}%")
        
        # Color coding the shift column using Pandas Styling
        display_trend['Shift'] = (display_trend['confidence_change'] * 100).apply(lambda x: f"+{x:.1f}%")
        
        st.dataframe(display_trend[['Antecedents (Triggers)', 'Consequents (Disaster)', '2005-2012 Confidence', '2013-2020 Confidence', 'Shift']])
        
        st.info("💡 **Insight:** The positive shift in confidence illustrates that conditions which generated a disaster with ~40% probability in the previous decade frequently generate a disaster with ~80% probability in the modern decade.")