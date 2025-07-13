import streamlit as st
from inventory import Product, Supplier, recommend_best_suppliers
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configure Streamlit page
st.set_page_config(
    page_title="AI Inventory Management",
    layout="wide"
)

# Initialize session state
if 'products' not in st.session_state:
    st.session_state.products = {}

if 'suppliers' not in st.session_state:
    st.session_state.suppliers = {}

# Helper functions
def add_product(product_id, name, shelf_life, category):
    if product_id in st.session_state.products:
        st.error(f"Product with ID {product_id} already exists!")
        return False
    st.session_state.products[product_id] = Product(product_id, name, shelf_life, category)
    st.success(f"Product {name} added successfully!")
    return True

def record_sale(product_id, quantity):
    if product_id not in st.session_state.products:
        st.error(f"Product {product_id} not found!")
        return False
    st.session_state.products[product_id].add_sale(quantity)
    st.success(f"Sale recorded for {quantity} units of {st.session_state.products[product_id].name}")
    return True

def get_forecast(product_id, days, location=None):
    if product_id not in st.session_state.products:
        st.error(f"Product {product_id} not found!")
        return None
    
    product = st.session_state.products[product_id]
    forecast = product.get_forecast(days, location)
    recommended_order = product.get_recommended_order(days)
    
    return {
        'forecast': forecast,
        'recommended_order': recommended_order,
        'current_inventory': product.inventory,
        'shelf_life': product.shelf_life_days
    }

def get_sales_history(product_id):
    if product_id not in st.session_state.products:
        return []
    return st.session_state.products[product_id].sales_history

def add_supplier(supplier_id, name):
    if supplier_id in st.session_state.suppliers:
        st.error(f"Supplier with ID {supplier_id} already exists!")
        return False
    st.session_state.suppliers[supplier_id] = Supplier(supplier_id, name)
    st.success(f"Supplier {name} added successfully!")
    return True

def record_supplier_performance(supplier_id, delivery_days, cost, quality_rating):
    if supplier_id not in st.session_state.suppliers:
        st.error(f"Supplier {supplier_id} not found!")
        return False
    st.session_state.suppliers[supplier_id].record_delivery(delivery_days, cost, quality_rating)
    st.success(f"Recorded performance for supplier {st.session_state.suppliers[supplier_id].name}")
    return True

def generate_purchase_orders():
    st.warning("Auto-Replenishment System feature has been removed as per user request.")

def mark_order_received(index):
    st.warning("Auto-Replenishment System feature has been removed as per user request.")

# Streamlit app
def main():
    # Main title and description
    st.title("AI-Powered Inventory Management System")
    st.markdown(
        """
        Manage your inventory efficiently with AI-powered forecasting.
        Track sales, predict future demand, and reduce waste.
        """
    )
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Add Product", "Record Sale", "Forecast", "Suppliers", "Supplier Analytics"])
    
    # Main content
    if page == "Dashboard":
        st.header("Dashboard")
        
        if not st.session_state.products:
            st.warning("No products added yet!")
            return
            
        # Show product summary
        st.subheader("Product Summary")
        summary_data = []
        for product in st.session_state.products.values():
            summary_data.append({
                'Product': product.name,
                'Category': product.category,
                'Current Inventory': product.inventory,
                'Shelf Life (days)': product.shelf_life_days,
                'Recent Sales': sum(s[1] for s in product.sales_history[-7:])
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df)
        
        # Show sales history chart
        if any(product.sales_history for product in st.session_state.products.values()):
            st.subheader("Sales History")
            all_sales = []
            for product in st.session_state.products.values():
                for date, quantity in product.sales_history:
                    all_sales.append({
                        'Date': date,
                        'Quantity': quantity,
                        'Product': product.name
                    })
            
            sales_df = pd.DataFrame(all_sales)
            
            # Create a more detailed chart
            fig = go.Figure()
            
            # Add traces for each product
            for product in st.session_state.products.values():
                product_sales = sales_df[sales_df['Product'] == product.name]
                if not product_sales.empty:
                    fig.add_trace(go.Scatter(
                        x=product_sales['Date'],
                        y=product_sales['Quantity'],
                        name=product.name,
                        mode='lines+markers',
                        line=dict(width=2),
                        marker=dict(size=8)
                    ))
            
            # Update layout
            fig.update_layout(
                title='Sales History by Product',
                xaxis_title='Date',
                yaxis_title='Quantity Sold',
                legend_title='Products',
                hovermode='x unified',
                margin=dict(l=50, r=50, t=50, b=50),
                height=500
            )
            
            # Add range slider
            fig.update_layout(
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                 label="1m",
                                 step="month",
                                 stepmode="backward"),
                            dict(count=6,
                                 label="6m",
                                 step="month",
                                 stepmode="backward"),
                            dict(count=1,
                                 label="YTD",
                                 step="year",
                                 stepmode="todate"),
                            dict(count=1,
                                 label="1y",
                                 step="year",
                                 stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(
                        visible=True
                    ),
                    type="date"
                )
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
    elif page == "Add Product":
        st.header("Add New Product")
        
        with st.form("add_product_form"):
            product_id = st.text_input("Product ID", "P1")
            name = st.text_input("Product Name", "Apple")
            shelf_life = st.number_input("Shelf Life (days)", min_value=1, value=7)
            category = st.selectbox("Category", ["dry product", "dairy", "produce"])
            
            if st.form_submit_button("Add Product"):
                add_product(product_id, name, shelf_life, category)
                
    elif page == "Record Sale":
        st.header("Record Sale")
        
        if not st.session_state.products:
            st.warning("No products added yet!")
            return
            
        with st.form("record_sale_form"):
            product_id = st.selectbox("Select Product", list(st.session_state.products.keys()))
            quantity = st.number_input("Quantity Sold", min_value=1, value=1)
            
            if st.form_submit_button("Record Sale"):
                record_sale(product_id, quantity)
                
    elif page == "Forecast":
        st.header("Generate Forecast")
        
        if not st.session_state.products:
            st.warning("No products added yet!")
            return
            
        with st.form("forecast_form"):
            product_id = st.selectbox("Select Product", list(st.session_state.products.keys()))
            days = st.number_input("Days to Forecast", min_value=1, value=7)
            location = st.text_input("Location (for weather-based forecast)", "")
            
            if st.form_submit_button("Generate Forecast"):
                result = get_forecast(product_id, days, location if location else None)
                if result:
                    st.subheader("Forecast Results")
                    st.write(f"Predicted sales for next {days} days: {result['forecast']} units")
                    st.write(f"Current inventory: {result['current_inventory']} units")
                    st.write(f"Recommended order quantity: {result['recommended_order']} units")
                    st.write(f"Product shelf life: {result['shelf_life']} days")
                    
                    # Show detailed sales history for this product
                    sales_history = get_sales_history(product_id)
                    if sales_history:
                        sales_df = pd.DataFrame(sales_history, columns=['Date', 'Quantity'])
                        
                        # Create a detailed chart
                        fig = go.Figure()
                        
                        # Add line and markers
                        fig.add_trace(go.Scatter(
                            x=sales_df['Date'],
                            y=sales_df['Quantity'],
                            mode='lines+markers',
                            line=dict(width=2),
                            marker=dict(size=8)
                        ))
                        
                        # Add trend line
                        if len(sales_df) > 2:
                            trend = px.scatter(sales_df, x='Date', y='Quantity', trendline='ols').data[1]
                            fig.add_trace(
                                go.Scatter(
                                    x=trend['x'],
                                    y=trend['y'],
                                    name='Trend Line',
                                    line=dict(color='red', dash='dash')
                                )
                            )
                        
                        # Update layout
                        fig.update_layout(
                            title=f'Sales History for {st.session_state.products[product_id].name}',
                            xaxis_title='Date',
                            yaxis_title='Quantity Sold',
                            hovermode='x unified',
                            margin=dict(l=50, r=50, t=50, b=50),
                            height=400
                        )
                        
                        # Add range slider
                        fig.update_layout(
                            xaxis=dict(
                                rangeslider=dict(
                                    visible=True
                                ),
                                type="date"
                            )
                        )
                        
                        # Display the chart
                        st.plotly_chart(fig, use_container_width=True)
                        
    elif page == "Suppliers":
        st.header("Manage Suppliers")
        
        with st.form("add_supplier_form"):
            supplier_id = st.text_input("Supplier ID", "S1")
            name = st.text_input("Supplier Name", "Supplier A")
            
            if st.form_submit_button("Add Supplier"):
                add_supplier(supplier_id, name)
        
        st.subheader("Record Supplier Performance")
        if not st.session_state.suppliers:
            st.warning("No suppliers added yet!")
        else:
            with st.form("record_performance_form"):
                supplier_id = st.selectbox("Select Supplier", list(st.session_state.suppliers.keys()))
                delivery_days = st.number_input("Delivery Time (days)", min_value=1, value=3)
                cost = st.number_input("Cost", min_value=0.0, value=100.0, format="%.2f")
                quality_rating = st.slider("Quality Rating", min_value=1, max_value=5, value=4)
                
                if st.form_submit_button("Record Performance"):
                    record_supplier_performance(supplier_id, delivery_days, cost, quality_rating)
                    
    elif page == "Supplier Analytics":
        st.header("Supplier Performance Analytics")
        
        if not st.session_state.suppliers:
            st.warning("No suppliers added yet!")
            return
        
        suppliers = list(st.session_state.suppliers.values())
        recommended = recommend_best_suppliers(suppliers)
        
        data = []
        for supplier in suppliers:
            data.append({
                'Supplier': supplier.name,
                'Avg Delivery Time (days)': supplier.average_delivery_time(),
                'Avg Cost': supplier.average_cost(),
                'Avg Quality Rating': supplier.average_quality()
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df)
        
        st.subheader("Recommended Suppliers")
        for supplier in recommended:
            st.write(f"{supplier.name} - Score: {(supplier.average_quality() or 0) * 0.5 - (supplier.average_delivery_time() or 0) * 0.3 - (supplier.average_cost() or 0) * 0.2:.2f}")

if __name__ == "__main__":
    main()
