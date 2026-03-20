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
def fetch_data(query, params = None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params = params)
    conn.close()
    return df

st.sidebar.title("DATA ANALYSIS DASHBOARD")
option = st.sidebar.radio(
    "Navigate", ("Home", "Shipments Analysis", "Operational KPIS", "Visuals", "Analytical Views")
    )

if option == "Home":
    st.title("WELCOME")
    st.subheader("Smart Logistics Management and Analytics Dashboard", divider = True)
    st.subheader("Navigate through options for different Analysis")

elif option == "Shipments Analysis":
    st.title("SHIPMENTS ANALYSIS")
    
    # SHIPMENT ID SEARCH.
    st.sidebar.header("Search")
    search = st.sidebar.text_input("search Shipment ID")
    query = "select * from shipments where shipment_id like %s"
    params = [f"{search}"]
    
    shipment_id_df = fetch_data(query, params)
    st.subheader("Shipment ID")
    st.dataframe(shipment_id_df)
    
    # FILTER BY DESCRIPTION.
    st.badge("FILTERED") 
    delivery_status_df = fetch_data("select distinct delivery_status from shipments;")["delivery_status"].tolist()
    destination_df = fetch_data("select distinct destination from shipments;")["destination"].tolist()
    courier_df = fetch_data("select distinct courier_id from shipments;")["courier_id"].tolist()

    st.sidebar.header ("Filter by Description")
    deliverystatus = st.sidebar.selectbox("Delivery Status", ["ALL"] + delivery_status_df)
    destination = st.sidebar.selectbox("Destination", ["ALL"] + destination_df)
    courierids = st.sidebar.selectbox("CourierID",["ALL"] + courier_df)

    query = "select * from shipments where 1=1"
    params = []

    if deliverystatus != "ALL":
        query += " and delivery_status = %s"
        params.append(deliverystatus)

    if destination != "ALL":
        query += " and destination = %s"
        params.append(destination)

    if courierids != "ALL":
        query += " and courier_id = %s"
        params.append(courierids)    

    Filtered_df = fetch_data(query, params)  
    st.subheader("Filtered by Description")
    st.dataframe(Filtered_df)   
    
    # FILTER BY DATE RANGE.
    st.sidebar.header("Filter by Date Range")
    Dates_df = fetch_data("select distinct order_date from shipments")["order_date"].tolist()
    Sorted_dates = sorted(Dates_df)

    start_date = st.sidebar.selectbox("Select Start Date", ["ALL"] + Sorted_dates)
    end_date = st.sidebar.selectbox("Select End Date", ["ALL"] + Sorted_dates)

    query = "select * from shipments where 1=1"
    params = []

    if start_date != "ALL" and end_date != "ALL":
       query += " and order_date between %s and %s"  
       params.extend([start_date, end_date])

    filtered_df = fetch_data(query, params)
    st.subheader("Filtered by Date Range")
    st.dataframe(filtered_df)

elif option == "Operational KPIS":
    # OPERATIONAL KPIs
    st.badge('OPERTIONAL KPIS')
    df_kpis = fetch_data("""SELECT
    (SELECT count(shipment_id) from shipments) as total_shipments,  
    (SELECT COUNT(CASE WHEN delivery_status = 'Delivered' THEN 1 END) * 100 / COUNT(*) from shipments) 
    AS delivered_percentage,
    (SELECT COUNT(CASE WHEN delivery_status = 'Cancelled' THEN 1 END) * 100 / COUNT(*) from shipments) 
    AS cancelled_percentage, 
    (SELECT sum(fuel_cost + labor_cost + misc_cost) from costs) as total_operational_cost,
    (SELECT sum(avg_time_hours) / count(avg_time_hours) from routes) as avg_time from routes""")
    
    total_shipments, delivered_percentage, cancelled_percentage, total_operational_cost, avg_time = df_kpis.iloc[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label = "Total Shipments Handled", value = (round(total_shipments, 0)))
        st.metric(label = "Delivered Shipments Percentage", value = f'{delivered_percentage} %')
        st.metric(label = "Cancelled Shipments Percentage", value = f'{cancelled_percentage} %')
    with col2:
        st.metric(label = "Total Operational Cost", value = f'{total_operational_cost} $')
    with col3:
        st.metric(label = "Average Dalivery Time", value = f'{avg_time} Hours')

elif option == "Visuals":
    # VISUALIZATION.
    # CITY VS WAREHOUSE CAPACITY
    st.badge("VISUALS CHARTS")
    warehouse_df = fetch_data("select distinct city, capacity from warehouses limit 30")
    st.subheader("High traffic warehouse cities")
    fig, ax = plt.subplots()
    ax.bar(warehouse_df["city"], warehouse_df["capacity"])
    plt.xticks(rotation=90)
    st.pyplot(fig)

    # DELIVERY TIME VS DISTANCE COMPARISION
    df = fetch_data("select distance_km, avg_time_hours from routes")
    st.subheader("Delivery time vs Distance Comparision")
    fig, ax = plt.subplots()
    ax.scatter(df["distance_km"], df["avg_time_hours"], alpha = 0.5)
    ax.set_xlabel("Distanace (KM)")
    ax.set_ylabel("avg_time (Hours)")
    plt.xticks(rotation=90)
    st.pyplot(fig)

elif option == "Analytical Views":
    # C) ANALYTICAL VIEWS
    # 1) DELIVERY PERFORMANCE INSIGHTS
    # AVG DELIVERY TIME PER ROUTE
    st.badge("ANALATICAL VIEWS")
    df = fetch_data("select route_id, avg_time_hours from routes")
    st.subheader("Avg delivery time per route")
    st.dataframe(df)

    # MOST DELAYED ROUTES
    df = fetch_data("select route_id, avg_time_hours from routes order by avg_time_hours desc limit 10")
    st.subheader("Top 10 delayed routes")
    st.table(df)
        
    # 2) COURIER PERFORMANCE
    # NUM OF SHIPMENTS HANDLED BY COURIER
    df = fetch_data("select courier_id, count(shipment_id) as total_shipments from shipments group by courier_id")
    st.subheader("Number of Shipments Handled by Courier")
    st.dataframe(df)
    
    # 3) COST ANALYSIS
    # TOTAL COST PER SHIPMENT
    df = fetch_data("""select 
    shipment_id, fuel_cost, labor_cost, misc_cost, sum(fuel_cost + labor_cost + misc_cost) 
    as total_cost_per_shipment from costs group by shipment_id 
    order by total_cost_per_shipment DESC""")
    st.subheader("Total Cost per Shipment from Highest to Lowest")
    st.dataframe(df)
    
    # 4) Cancellation Analysis
    # CANCELLATION RATE BY ORIGIN
    df = fetch_data("""select origin, count(shipment_id) as total_shipments, 
    sum(case when delivery_status = "cancelled" then 1 else 0 end) as cancelled_shipments, 
    (sum(case when delivery_status = "cancelled" then 1 else 0 end) / count(shipment_id) *100) as `cancellation(%)`
    from shipments group by origin order by `cancellation(%)` desc;""")
    st.subheader("Shipments Cancelled Rate by Origin")
    st.dataframe(df)

    # CANCELLATION RATE BY COURIER
    df = fetch_data("""select courier_id, count(shipment_id) as total_shipments,
    sum(case when delivery_status = "cancelled" then 1 else 0 end) as cancelled_shipments,
    (sum(case when delivery_status = "cancelled" then 1 else 0 end) / count(shipment_id) * 100) as `cancellation(%)`
    from shipments group by courier_id order by `cancellation(%)` desc""")
    st.subheader("Shipments Cancelled Rate by Courier")
    st.dataframe(df)

    # TIME-TO-CANCELLATION ANALYSIS - not sure about how to manipulate data.
    
    # COST PER ROUTE - no common column between routes and costs table.
    
    # FUEL VS LABOR PERCENTAGE CONTRIBUTION - unable to understand the question.
    
    # ON-TIEM DELIVERY % - unable to find data source.

    # AVERANGE RATING COMPARISION - Unable to understand the problem statement.
