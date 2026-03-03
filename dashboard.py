import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set professional layout
st.set_page_config(page_title="E-Commerce Decision Support", layout="wide")

# Custom CSS for a high-end look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #1f77b4; }
    .stButton>button { border-radius: 20px; background-color: #1f77b4; color: white; height: 3em; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('cleaned_master_data.csv')

df = load_data()

st.title("📦 Sales Forecasting & Profit Optimisation System")
st.markdown("---")

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("🔍 Product Search")
    item_name = st.text_input("What are you selling?", "Fridge", help="Type a specific product like 'Air Fryer' or 'Monitor'.")
    category = st.selectbox("Category", df['main_category'].unique())
    
    st.divider()
    
    st.header("📈 Strategy Inputs")
    quantity = st.number_input("Inventory Quantity", min_value=1, value=100)
    
    # --- DUAL PRICE INPUT (Typed and Slider) ---
    st.write("Selling Price (£)")
    # We use a session state to sync the two inputs
    if 'price' not in st.session_state:
        st.session_state.price = 150.0

    # Number input (Typing)
    price_typed = st.number_input("Type Price (£)", min_value=1.0, value=st.session_state.price, step=1.0)
    # Slider (Moving with cursor)
    price_slider = st.slider("Slide to Adjust", 1.0, 2000.0, price_typed)
    
    # Syncing the values
    st.session_state.price = price_slider
    
    user_rating = st.slider("Target Rating (Quality)", 1.0, 5.0, 4.2)
    
    st.divider()
    run_sim = st.button("🚀 Analyze Market Potential")

# --- MAIN DASHBOARD ---
if run_sim:
    # 1. Search Logic
    similar_items = df[df['name'].str.contains(item_name, case=False, na=False)]
    
    if similar_items.empty:
        st.warning(f"No specific matches for '{item_name}'. Using average '{category}' data.")
        similar_items = df[df['main_category'] == category]

    # 2. Simulation Logic (Velocity & Revenue)
    avg_mkt_price = similar_items['actual_price_gbp'].mean()
    avg_mkt_reviews = similar_items['no_of_ratings'].mean()
    
    # Velocity math [cite: 23]
    # Lower price relative to market = Faster sales
    # Higher rating relative to market = Faster sales
    price_ratio = st.session_state.price / avg_mkt_price
    velocity_base = (avg_mkt_reviews * 0.08) # Base monthly units
    adjusted_velocity = velocity_base * (1 / (price_ratio**1.5)) * (user_rating / 4.0)
    
    if adjusted_velocity < 0.5: adjusted_velocity = 0.5
    
    days_to_sell = int((quantity / adjusted_velocity) * 30)
    total_revenue = quantity * st.session_state.price
    predicted_reviews = int(avg_mkt_reviews * (user_rating / 4.2))

    # 3. UI Display Metrics 
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Predicted Reviews", f"{predicted_reviews:,}")
    with m2:
        st.metric("Total Revenue", f"£{total_revenue:,.2f}")
    with m3:
        st.metric("Estimated Days to Sell", f"{days_to_sell} Days")

    st.markdown("---")

    # 4. Interactive Plotly Graph [cite: 12, 15]
    # Show how price affects Days to Sell
    price_range = np.linspace(st.session_state.price * 0.5, st.session_state.price * 1.5, 30)
    days_range = [int((quantity / (velocity_base * (1 / ((p / avg_mkt_price)**1.5)) * (user_rating / 4.0))) * 30) for p in price_range]
    
    fig_df = pd.DataFrame({"Price (£)": price_range, "Days to Sell": days_range})
    fig = px.area(fig_df, x="Price (£)", y="Days to Sell", title="Price Sensitivity vs. Inventory Turnover",
                  color_discrete_sequence=['#1f77b4'])
    fig.add_scatter(x=[st.session_state.price], y=[days_to_sell], mode='markers+text', 
                    name="Current Price", text=["Current Selection"], textposition="top center",
                    marker=dict(size=12, color='red'))
    
    st.plotly_chart(fig, use_container_width=True)

    # 5. Strategic Advice [cite: 24]
    with st.expander("📝 Strategic Advice for Sellers"):
        if days_to_sell < 30:
            st.success(f"**High Demand!** You are priced to sell out in under a month. Consider increasing price to maximize profit.")
        elif days_to_sell > 365:
            st.error(f"**Inventory Risk:** It will take over a year to sell {quantity} units at £{st.session_state.price}. Lower your price or quantity.")
        else:
            st.info(f"**Balanced:** Your turnover rate is healthy. This represents a solid investment opportunity.")