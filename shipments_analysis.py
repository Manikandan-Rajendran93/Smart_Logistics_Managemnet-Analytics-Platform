import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

def get_connection():
    return mysql.connector.connect(
        host = "localhost", 
        user = "root", 
        password = "9095", 
        database= "smart_logistics"
    )
@st.cache_data
def fetch_data(query, params = None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params = params)
    conn.close()
    return df

st.sidebar.title("Data Analysis Dashboard")
option = st.sidebar.radio("Navigate", ("Home", "shipments"))

if option=="Home":
    st.title("Welcome")
    st.subheader("Look for options in the navigation bar")

elif option=="shipments":
    st.title("Shipments Analysis")
    
    # shipment ID search bar.
    search = st.sidebar.text_input("search Shipment ID")
    query = "select * from shipments where shipment_id like %s"
    params = [f"{search}"]
    
    filtered_df = fetch_data(query, params)
    st.subheader("Shipment ID")
    st.dataframe(filtered_df)
    
    # Delivery status filter bar.   
    delivery_status_df = fetch_data("select distinct delivery_status from shipments;")
    deliverystatus = st.sidebar.selectbox("Delivery Status", delivery_status_df["delivery_status"])
    query = "select * from shipments where delivery_status = %s"
    params =[deliverystatus]

    filtered_df = fetch_data(query, params)
    st.subheader("Delivery Statu wise")
    st.dataframe(filtered_df)     
    
    # Destination filter bar.
    destination_df = fetch_data("select distinct destination from shipments;")
    destination = st.sidebar.selectbox("Destination", destination_df["destination"])
    query = "select * from shipments where destination = %s"
    params = [destination]

    filtered_df = fetch_data(query, params)
    st.subheader("Destination wise")
    st.dataframe(filtered_df)
    
    # Courier ID filter bar.
    courier_df = fetch_data("select distinct courier_id from shipments;")
    courierids = st.sidebar.selectbox("CourierID", courier_df["courier_id"])
    query = "select * from shipments where courier_id = %s"
    params = [courierids]

    filtered_df = fetch_data(query, params)
    st.subheader("Courier ID wise")
    st.dataframe(filtered_df)
    
    # Date Range filter bar.
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")

    query = """select * from shipments group by shipment_id, origin, destination, weight, 
    courier_id, delivery_status, delivery_date having order_date between %s and %s"""
    paramses = [start_date, end_date]
    filtered_df = fetch_data(query, paramses)
    st.subheader("Order Date Range")
    st.dataframe(filtered_df)

    
    warehouse_df = fetch_data("select distinct city, capacity from warehouses limit 30")
    if not warehouse_df.empty:
        st.subheader("High traffic warehouse cities")
        fig, ax = plt.subplots()
        ax.bar(warehouse_df["city"], warehouse_df["capacity"])
        plt.xticks(rotation=90)
        st.pyplot(fig)
    
    # B) OPERATIONAL KPIs
    # 1)TOTAL SHIPMENTS.
    # select count(shipment_id) from shipments;

    # 2)DELIVERED SHIPMENTS PERCENTAGE.
    # """SELECT 
    # (COUNT(CASE WHEN delivery_status = 'Delivered' THEN 1 END) * 100.0 / COUNT(*)) AS delivered_percentage
    # FROM shipments;"""

    # 3)CANCELLED SHIPMENTS PERCENTAGE.
    # """SELECT 
    # (COUNT(CASE WHEN delivery_status = 'Cancelled' THEN 1 END) * 100.0 / COUNT(*)) AS cancelled_percentage
    # FROM shipments;"""
    
    # 4)TOTAL OPERATIONAL COST
    # """SELECT 
    # SUM(labor_cost) AS sum1, 
    # SUM(fuel_cost) AS sum2, 
    # SUM(misc_cost) AS sum3,
    # (SUM(labor_cost) + SUM(fuel_cost) + SUM(misc_cost)) AS grand_total
    # FROM costs;"""
    
    # 5)AVG DELIVERY TIME
    # select sum(avg_time_hours) / count(avg_time_hours) from routes;
    
    # C) ANALYTICAL VIEWS
    # 1) DELIVERY PERFORMANCE INSIGHTS
    # AVG DELIVERY TIME PER ROUTE
    # select route_id, avg_time_hours from routes;

    # MOST DELAYED ROUTES
    # select route_id, avg_time_hours from routes order by avg_time_hours desc limit 10;
    
    # DELIVERY TIME VS DISTANCE COMPARISION
    # WRITE CODE TO VISUALIZE THE QUERY : select distance_km, avg_time_hours from routes;
    
    # 2) COURIER PERFORMANCE
    # NUM OF SHIPMENTS HANDLED BY COURIER
    # select courier_id, count(*) as total_shipments from shipments group by courier_id
    
    # ON-TIEM DELIVERY % - Cannot find data source.

    # AVERANGE RATING COMPARISION - Unable to understand.

    # 3) COST ANALYSIS
    # TOTAL COST PER SHIPMENT.
    # """select shipment_id,
    # sum(fuel_cost) as sum1, 
    # sum(labor_cost) as sum2,
    # sum(misc_cost) as sum3,
    # (sum(fuel_cost) + sum(labor_cost) + sum(misc_cost)) as total_cost_per_shipment from costs group by shipment_Id"""
    
    # COST PER ROUTE - no common column between routes and costs table.
    
    # FUEL VS LABOR PERCENTAGE CONTRIBUTION - unable to understand
    
    # HIGH-COST SHIPMENTS
    # """select shipment_id,
    # sum(fuel_cost) as sum1, 
    # sum(labor_cost) as sum2,
    # sum(misc_cost) as sum3,
    # (sum(fuel_cost) + sum(labor_cost) + sum(misc_cost)) as total_cost_per_shipment 
    # from costs group by shipment_Id order by total_cost_per_shipment desc limit 10""""

    # 4) CANCELLATION ANALYSIS
    # CANCELLATION RATE BY ORIGIN
    # select origin, count(*) as cancelled_count from shipments where delivery_status = "Cancelled" group by origin

    # CANCELLATION RATE BY COURIER
    # select courier_id, count(*) as cancelled_count from shipments where delivery_status = "Cancelled" group by courier_id;

    # TIME-TO-CANCELLATION ANALYSIS - unable to uderstand

    # 5) WAREHOUSE INSIGHTS
    # WAREHOUSE CAPACITY COMPARISION
    # wirte code to visualize city in x axis and capacity in y axis: select city, capacity from warehouses;
        
    # HIGH-TRAFFIC WAREHOUSE CITIES
    # select city, capacity from warehouses order by capacity desc limit 10;