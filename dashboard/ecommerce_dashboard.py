import streamlit as st 
import duckdb
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go 

st.set_page_config(page_title="E-commerce Price Tracker", page_icon="🛒", layout="wide")

#connect to duckdb
@st.cache_resource
def get_connection():
    return duckdb.connect("../ecommerce_analytics/dev.duckdb", read_only=True)

@st.cache_data(ttl=600)
def load_data(query):
    conn = get_connection()
    return conn.execute(query).df()

st.title("🛒 E-commerce Price Tracker")
st.markdown("---")

#load data
price_history = load_data("SELECT * FROM product_price_history ORDER BY price_date DESC")
products = load_data("SELECT DISTINCT product_name, category FROM stg_products")

#key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_products = len(products)
    st.metric("Total Products", total_products)

with col2:
    price_drops = len(price_history[price_history['price_trend'] == 'PRICE_DROP'])
    st.metric("Price Drops Today", price_drops)

with col3:
    avg_discount = price_history[price_history['price_trend'] == 'PRICE_DROP']['price_change'].mean()
    st.metric("Avg Price Drop", f"${abs(avg_discount):.2f}")

with col4:
    categories = len(products['category'].unique())  # Change from nunique() to len(unique())
    st.metric("Categories", categories)


st.markdown("---")

#price trends chart
st.subheader("📈 Price Trends Over Time")

selected_products = st.multiselect(
    "Select products to compare",
    options=products['product_name'].unique(),
    default=products['product_name'].unique()[:3]
)

if selected_products:
    filtered_data = price_history[price_history['product_name'].isin(selected_products)].copy()
    
    # Convert date to datetime
    filtered_data['price_date'] = pd.to_datetime(filtered_data['price_date'])
    
    fig = go.Figure()
    
    for product in selected_products:
        product_data = filtered_data[filtered_data['product_name'] == product].sort_values('price_date')
        
        fig.add_trace(go.Scatter(
            x=product_data['price_date'],
            y=product_data['avg_price'],
            name=product,
            mode='lines+markers'
        ))


# Best deals section
st.markdown("---")
st.subheader("🔥 Biggest Price Drops")

price_drops_df = price_history[price_history['price_trend'] == 'PRICE_DROP'].sort_values('price_change').head(10)

if len(price_drops_df) > 0:
    # Convert date to datetime for display
    price_drops_df = price_drops_df.copy()
    price_drops_df['price_date'] = pd.to_datetime(price_drops_df['price_date'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_df = price_drops_df[['product_name', 'price_date', 'avg_price', 'price_change']].copy()
        display_df['avg_price'] = display_df['avg_price'].round(2)
        display_df['price_change'] = display_df['price_change'].round(2)
        
        st.dataframe(
            display_df.rename(columns={
                'product_name': 'Product',
                'price_date': 'Date',
                'avg_price': 'Current Price',
                'price_change': 'Price Drop'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
       fig = px.bar(
            price_drops_df,
            x='product_name',
            y='price_change',
            title='Top 10 Price Drops',
            labels={'product_name': 'Product', 'price_change': 'Price Change ($)'}  # labels plural
        )
else:
    st.info("No price drops detected yet!")


#category analysis
st.markdown("---")
st.subheader("📊 Price Analysis by Category")

category_stats = load_data(""" 
    SELECT
        category,
        AVG(avg_price) as avg_price,
        MIN(min_price) as lowest_price,
        MAX(max_price) as highest_price,
        COUNT(DISTINCT product_id) as product_count
    FROM product_price_history
    GROUP BY category
""")

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        category_stats,
        x='category',
        y='avg_price',
        title='Average Price by Category',
        labels={'category': 'Category', 'avg_price': 'Average Price ($)'}  # labels plural
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.dataframe(
        category_stats.rename(columns={
            'category': 'Category',
            'avg_price': 'Avg Price',
            'lowest_price': 'Lowest',
            'highest_price': 'Highest',
            'product_count': 'Products'
        }),
        use_container_width=True,
        hide_index=True
    )
