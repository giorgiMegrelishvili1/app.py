import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# ──────────────────────────────────────────
# PAGE SETTINGS
# ──────────────────────────────────────────
st.set_page_config(
    page_title="Baby Food Price Monitoring",
    page_icon="👶",
    layout="wide"
)

st.title("👶 Baby Food Price Monitoring Dashboard")
st.write("📊 Category Manager Analytics — Aversi")

# ──────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    # Clean PRICE column — remove ₾, quotes, spaces
    df['PRICE'] = df['PRICE'].astype(str)
    df['PRICE'] = df['PRICE'].str.replace('₾', '', regex=False)
    df['PRICE'] = df['PRICE'].str.replace('"', '', regex=False)
    df['PRICE'] = df['PRICE'].str.strip()
    df['PRICE'] = pd.to_numeric(df['PRICE'], errors='coerce')
    df = df.dropna(subset=['PRICE'])
    df = df[df['PRICE'] > 0]
    return df

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx", "xls"])

if uploaded_file:
    df = load_data(uploaded_file)

    # ──────────────────────────────────────
    # SIDEBAR FILTERS
    # ──────────────────────────────────────
    st.sidebar.title("🔎 Filters")

    brands = sorted(df['BRAND'].dropna().unique().tolist())
    selected_brands = st.sidebar.multiselect(
        "Select Brands",
        options=brands,
        default=brands
    )

    price_min = float(df['PRICE'].min())
    price_max = float(df['PRICE'].max())
    price_range = st.sidebar.slider(
        "Price Range (₾)",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max)
    )

    # Apply filters
    filtered_df = df[
        (df['BRAND'].isin(selected_brands)) &
        (df['PRICE'] >= price_range[0]) &
        (df['PRICE'] <= price_range[1])
    ]

    # ──────────────────────────────────────
    # KPI METRICS
    # ──────────────────────────────────────
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Products", len(filtered_df))
    with col2:
        st.metric("Total Brands", filtered_df['BRAND'].nunique())
    with col3:
        st.metric("Avg Price (₾)", f"{filtered_df['PRICE'].mean():.2f}")
    with col4:
        st.metric("Min Price (₾)", f"{filtered_df['PRICE'].min():.2f}")
    with col5:
        st.metric("Max Price (₾)", f"{filtered_df['PRICE'].max():.2f}")

    st.divider()

    # ──────────────────────────────────────
    # CHARTS ROW 1
    # ──────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏷️ Products per Brand")
        brand_counts = filtered_df['BRAND'].value_counts().reset_index()
        brand_counts.columns = ['BRAND', 'COUNT']
        fig1 = px.bar(
            brand_counts,
            x='COUNT', y='BRAND',
            orientation='h',
            color='COUNT',
            color_continuous_scale='Blues',
            title="Number of Products by Brand"
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("💰 Average Price per Brand")
        avg_price = filtered_df.groupby('BRAND')['PRICE'].mean().reset_index()
        avg_price.columns = ['BRAND', 'AVG_PRICE']
        avg_price = avg_price.sort_values('AVG_PRICE', ascending=False)
        fig2 = px.bar(
            avg_price,
            x='AVG_PRICE', y='BRAND',
            orientation='h',
            color='AVG_PRICE',
            color_continuous_scale='Oranges',
            title="Average Price by Brand (₾)"
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

    # ──────────────────────────────────────
    # CHARTS ROW 2
    # ──────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥧 Market Share by Brand")
        brand_share = filtered_df['BRAND'].value_counts().reset_index()
        brand_share.columns = ['BRAND', 'COUNT']
        fig3 = px.pie(
            brand_share,
            names='BRAND',
            values='COUNT',
            title="Market Share (by number of products)"
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.subheader("📦 Price Distribution")
        fig4 = px.box(
            filtered_df,
            x='BRAND',
            y='PRICE',
            color='BRAND',
            title="Price Distribution by Brand (₾)"
        )
        fig4.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)

    # ──────────────────────────────────────
    # PRICE SEGMENTS
    # ──────────────────────────────────────
    st.subheader("💎 Price Segments")

    def price_segment(price):
        if price < 3:
            return "Budget (< 3₾)"
        elif price < 7:
            return "Mid Range (3-7₾)"
        elif price < 15:
            return "Premium (7-15₾)"
        else:
            return "Luxury (> 15₾)"

    filtered_df = filtered_df.copy()
    filtered_df['SEGMENT'] = filtered_df['PRICE'].apply(price_segment)

    col1, col2 = st.columns(2)

    with col1:
        segment_counts = filtered_df['SEGMENT'].value_counts().reset_index()
        segment_counts.columns = ['SEGMENT', 'COUNT']
        fig5 = px.pie(
            segment_counts,
            names='SEGMENT',
            values='COUNT',
            color='SEGMENT',
            color_discrete_map={
                'Budget (< 3₾)': '#2ecc71',
                'Mid Range (3-7₾)': '#3498db',
                'Premium (7-15₾)': '#9b59b6',
                'Luxury (> 15₾)': '#e74c3c'
            },
            title="Products by Price Segment"
        )
        fig5.update_layout(height=350)
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        segment_brand = filtered_df.groupby(['BRAND', 'SEGMENT']).size().reset_index(name='COUNT')
        fig6 = px.bar(
            segment_brand,
            x='BRAND',
            y='COUNT',
            color='SEGMENT',
            title="Price Segments by Brand",
            barmode='stack'
        )
        fig6.update_layout(height=350, xaxis_tickangle=-45)
        st.plotly_chart(fig6, use_container_width=True)

    # ──────────────────────────────────────
    # TOP & BOTTOM PRODUCTS
    # ──────────────────────────────────────
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔝 Top 10 Most Expensive Products")
        top10 = filtered_df.nlargest(10, 'PRICE')[['BRAND', 'PRICE']].reset_index(drop=True)
        top10.index += 1
        st.dataframe(top10, use_container_width=True)

    with col2:
        st.subheader("💚 Top 10 Cheapest Products")
        bottom10 = filtered_df.nsmallest(10, 'PRICE')[['BRAND', 'PRICE']].reset_index(drop=True)
        bottom10.index += 1
        st.dataframe(bottom10, use_container_width=True)

    # ──────────────────────────────────────
    # BRAND COMPARISON TABLE
    # ──────────────────────────────────────
    st.divider()
    st.subheader("📋 Brand Comparison Table")

    brand_summary = filtered_df.groupby('BRAND').agg(
        Products=('PRICE', 'count'),
        Avg_Price=('PRICE', 'mean'),
        Min_Price=('PRICE', 'min'),
        Max_Price=('PRICE', 'max'),
        Total_Value=('PRICE', 'sum')
    ).round(2).reset_index()

    brand_summary.columns = ['Brand', 'Products', 'Avg Price (₾)', 'Min Price (₾)', 'Max Price (₾)', 'Total Value (₾)']
    brand_summary = brand_summary.sort_values('Products', ascending=False)
    st.dataframe(brand_summary, use_container_width=True)

    # ──────────────────────────────────────
    # FULL DATA TABLE
    # ──────────────────────────────────────
    st.divider()
    st.subheader("🗂️ Full Product List")
    st.dataframe(filtered_df[['BRAND', 'PRICE', 'SEGMENT']].reset_index(drop=True), use_container_width=True)

    # ──────────────────────────────────────
    # DOWNLOAD
    # ──────────────────────────────────────
    st.divider()
    st.subheader("⬇️ Download Data")
    col1, col2 = st.columns(2)

    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name="baby_food_analysis.csv",
            mime="text/csv"
        )
    with col2:
        csv2 = brand_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Brand Summary (CSV)",
            data=csv2,
            file_name="brand_summary.csv",
            mime="text/csv"
        )

    # ──────────────────────────────────────
    # CHATBOT
    # ──────────────────────────────────────
    st.divider()
    st.subheader("🤖 Chat with Your Data!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Ask about your data... (e.g. how many brands?)"):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        prompt_lower = prompt.lower()
        response = ""

        if "brand" in prompt_lower and ("how many" in prompt_lower or "count" in prompt_lower):
            response = f"🏷️ There are **{filtered_df['BRAND'].nunique()} brands** in the current selection."
        elif "product" in prompt_lower and ("how many" in prompt_lower or "count" in prompt_lower):
            response = f"📦 There are **{len(filtered_df)} products** in the current selection."
        elif "average" in prompt_lower or "mean" in prompt_lower:
            response = f"💰 The average price is **{filtered_df['PRICE'].mean():.2f}₾**"
        elif "expensive" in prompt_lower or "maximum" in prompt_lower or "max" in prompt_lower:
            max_row = filtered_df.loc[filtered_df['PRICE'].idxmax()]
            response = f"🔝 Most expensive product: **{max_row['BRAND']}** at **{max_row['PRICE']:.2f}₾**"
        elif "cheap" in prompt_lower or "minimum" in prompt_lower or "min" in prompt_lower:
            min_row = filtered_df.loc[filtered_df['PRICE'].idxmin()]
            response = f"💚 Cheapest product: **{min_row['BRAND']}** at **{min_row['PRICE']:.2f}₾**"
        elif "total" in prompt_lower or "sum" in prompt_lower:
            response = f"💎 Total value of all products: **{filtered_df['PRICE'].sum():.2f}₾**"
        elif "budget" in prompt_lower:
            count = len(filtered_df[filtered_df['SEGMENT'] == 'Budget (< 3₾)'])
            response = f"🟢 Budget products (< 3₾): **{count} products**"
        elif "premium" in prompt_lower:
            count = len(filtered_df[filtered_df['SEGMENT'] == 'Premium (7-15₾)'])
            response = f"🟣 Premium products (7-15₾): **{count} products**"
        elif "luxury" in prompt_lower:
            count = len(filtered_df[filtered_df['SEGMENT'] == 'Luxury (> 15₾)'])
            response = f"🔴 Luxury products (> 15₾): **{count} products**"
        else:
            response = """🤖 I can answer questions like:
- How many brands?
- How many products?
- What is the average price?
- What is the most expensive?
- What is the cheapest?
- What is the total value?
- How many budget products?
- How many premium products?
- How many luxury products?"""

        with st.chat_message("assistant"):
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.info("👆 Please upload your Excel file to get started!")
    st.markdown("""
    ### 📋 This Dashboard Shows:
    - **KPI Metrics** — total products, brands, average price
    - **Products per Brand** — bar chart
    - **Average Price per Brand** — comparison
    - **Market Share** — pie chart
    - **Price Distribution** — box plot
    - **Price Segments** — Budget / Mid / Premium / Luxury
    - **Top 10 Most Expensive** products
    - **Top 10 Cheapest** products
    - **Brand Comparison Table**
    - **Chatbot** — ask questions about your data!
    - **Download** — export your analysis
    """)
