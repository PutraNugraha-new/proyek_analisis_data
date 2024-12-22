import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(
    page_title="E-commerce Delivery Analysis",
    page_icon="🚚",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('all_df.csv')
    # Convert date columns
    date_columns = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col])
    return df

# Load the data
df = load_data()

# Title
st.title('🚚 E-commerce Delivery Analysis Dashboard')

# Sidebar
st.sidebar.header('Filters')

# State filter
selected_states = st.sidebar.multiselect(
    'Select States',
    options=df['customer_state'].unique(),
    default=df['customer_state'].unique()[:5]
)

# Date range filter
date_range = st.sidebar.date_input(
    'Select Date Range',
    value=(df['order_purchase_timestamp'].min().date(),
           df['order_purchase_timestamp'].max().date()),
    min_value=df['order_purchase_timestamp'].min().date(),
    max_value=df['order_purchase_timestamp'].max().date()
)

# Filter data
filtered_df = df[
    (df['customer_state'].isin(selected_states)) &
    (df['order_purchase_timestamp'].dt.date >= date_range[0]) &
    (df['order_purchase_timestamp'].dt.date <= date_range[1])
]

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = len(filtered_df['order_id'].unique())
    st.metric("Total Orders", f"{total_orders:,}")

with col2:
    on_time_percentage = (filtered_df['delivery_status'] == 'On Time').mean() * 100
    st.metric("On-Time Delivery", f"{on_time_percentage:.1f}%")

with col3:
    avg_delay = filtered_df[filtered_df['delivery_delay'] > 0]['delivery_delay'].mean()
    st.metric("Average Delay (Days)", f"{avg_delay:.1f}")

with col4:
    total_states = len(filtered_df['customer_state'].unique())
    st.metric("States Covered", total_states)

# Analysis 1: Delivery Performance by State
st.header("1. Delivery Performance Analysis by State")
col1, col2 = st.columns(2)

with col1:
    # Average delay by state
    fig_state_delay = px.bar(
        filtered_df.groupby('customer_state')['delivery_delay'].mean().reset_index(),
        x='customer_state',
        y='delivery_delay',
        title='Average Delivery Delay by State',
        labels={'delivery_delay': 'Average Delay (Days)', 'customer_state': 'State'}
    )
    st.plotly_chart(fig_state_delay, use_container_width=True)

with col2:
    # Delivery status distribution
    status_dist = filtered_df['delivery_status'].value_counts()
    fig_status = px.pie(
        values=status_dist.values,
        names=status_dist.index,
        title='Delivery Status Distribution',
        color_discrete_map={'On Time': 'green', 'Delayed': 'red'}
    )
    st.plotly_chart(fig_status, use_container_width=True)

# Analysis 2: Product Analysis
st.header("2. Product Impact Analysis")
col1, col2 = st.columns(2)

with col1:
    # Top 10 delayed categories
    top_delayed = (filtered_df.groupby('product_category_name')
                  ['delivery_delay'].mean()
                  .sort_values(ascending=False)
                  .head(10))
    fig_category = px.bar(
        top_delayed,
        title='Top 10 Product Categories with Highest Delay',
        labels={'value': 'Average Delay (Days)', 'product_category_name': 'Product Category'}
    )
    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    # Correlation heatmap
    corr_features = ['delivery_delay', 'product_weight_g', 'product_length_cm', 
                     'product_height_cm', 'product_width_cm', 'volume']
    corr_matrix = filtered_df[corr_features].corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        title='Correlation between Product Characteristics and Delay'
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# Weight category analysis
st.subheader("Delivery Performance by Weight Category")
weight_performance = filtered_df.groupby('weight_category').agg({
    'delivery_delay': 'mean',
    'order_id': 'count'
}).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig_weight_delay = px.bar(
        weight_performance,
        x='weight_category',
        y='delivery_delay',
        title='Average Delay by Weight Category',
        labels={'delivery_delay': 'Average Delay (Days)', 'weight_category': 'Weight Category'}
    )
    st.plotly_chart(fig_weight_delay, use_container_width=True)

with col2:
    fig_weight_dist = px.pie(
        weight_performance,
        values='order_id',
        names='weight_category',
        title='Distribution of Orders by Weight Category'
    )
    st.plotly_chart(fig_weight_dist, use_container_width=True)

# Additional insights
st.header("Additional Insights")
col1, col2 = st.columns(2)

with col1:
    # Monthly trend
    monthly_trend = (filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.to_period('M'))
                    ['delivery_delay'].mean()
                    .reset_index())
    monthly_trend['order_purchase_timestamp'] = monthly_trend['order_purchase_timestamp'].astype(str)
    
    fig_trend = px.line(
        monthly_trend,
        x='order_purchase_timestamp',
        y='delivery_delay',
        title='Average Delivery Delay Trend',
        labels={'delivery_delay': 'Average Delay (Days)', 'order_purchase_timestamp': 'Month'}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    # Weekday performance
    weekday_perf = (filtered_df.groupby('order_weekday')
                   ['delivery_delay'].mean()
                   .reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
                   .reset_index())
    
    fig_weekday = px.bar(
        weekday_perf,
        x='order_weekday',
        y='delivery_delay',
        title='Average Delay by Day of Week',
        labels={'delivery_delay': 'Average Delay (Days)', 'order_weekday': 'Day of Week'}
    )
    st.plotly_chart(fig_weekday, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Dashboard created for E-commerce Delivery Analysis")