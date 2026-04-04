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

st.set_page_config(layout = "wide")
st.header("SMART LOGISTICS MANAGEMENT AND ANALYTICS")

# 1.OPERATIONAL KPIs
st.subheader('OPERTIONAL KPIS')
df_kpis = fetch_data("""SELECT
(SELECT count(shipment_id) from shipments) as total_shipments,  
(SELECT COUNT(CASE WHEN delivery_status = 'Delivered' THEN 1 END) * 100 / COUNT(*) from shipments)
AS delivered_percentage,
(SELECT COUNT(CASE WHEN delivery_status = 'Cancelled' THEN 1 END) * 100 / COUNT(*) from shipments) 
AS cancelled_percentage, 
(SELECT sum(fuel_cost + labor_cost + misc_cost) from costs) as total_operational_cost,
(SELECT sum(avg_time_hours) / count(avg_time_hours) from routes) as avg_time from routes""")

total_shipments, delivered_percentage, cancelled_percentage, total_operational_cost, avg_time = df_kpis.iloc[0]

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.metric(label = "TOTAL SHIPMENTS HANDLED", value = (int(total_shipments)), border=True)
with kpi2:    
    st.metric(label = "DELIVERED SHIPMENTS PERCENTAGE", value = f'{delivered_percentage} %', border=True)
with kpi3:    
    st.metric(label = "CANCELLED SHIPMENTS PERCENTAGE", value = f'{cancelled_percentage} %',border=True)
with kpi4:
    st.metric(label = "TOTAL OPERATIONAL COST", value = f'{total_operational_cost} $',border=True)
with kpi5:
    st.metric(label = "AVERAGE DALIVERY TIME", value = f'{avg_time} Hours', border=True)


# 2.VISUALIZATION.
st.subheader("VISUALS")
chart_column1, chart_column2, chart_column3 = st.columns(3)
with chart_column1:
    warehouse_df = fetch_data("select distinct city, capacity from warehouses order by capacity desc limit 30")
    st.subheader("HIGH TRAFFIC WAREHOUSE CITIES")
    fig, ax = plt.subplots()
    ax.bar(warehouse_df["city"], warehouse_df["capacity"])
    plt.xticks(rotation=90)
    plt.xlabel("CITY NAME OF WAREHOUSE")
    plt.ylabel("CAPACITY OF WAREHOUSE")
    st.pyplot(fig)

with chart_column2:
    routes_df = fetch_data("select route_id, avg_time_hours from routes order by avg_time_hours desc limit 10;")
    st.subheader("MOST DELAYED ROUTES")
    fig, ax = plt.subplots()
    ax.bar(routes_df["route_id"], routes_df["avg_time_hours"])
    plt.xticks(rotation=90)
    plt.xlabel("ROUTE ID")
    plt.ylabel("DELIVERY TIME TAKEN IN HOURS")
    st.pyplot(fig)    

with chart_column3:
    df = fetch_data("select distance_km, avg_time_hours from routes")
    st.subheader("DELIVERY TIME VS DISTANCE COMPARISION")
    fig, ax = plt.subplots()
    ax.scatter(df["distance_km"], df["avg_time_hours"], alpha = 0.5)
    ax.set_xlabel("Distanace (KM)")
    ax.set_ylabel("avg_time (Hours)")
    plt.xticks(rotation=90)
    st.pyplot(fig)


# 3.ANALYSIS TABLE
shipment_id_df = fetch_data("select distinct shipment_id from shipments")["shipment_id"].tolist()
delivery_status_df = fetch_data("select distinct delivery_status from shipments;")["delivery_status"].tolist()
destination_df = fetch_data("select distinct destination from shipments;")["destination"].tolist()
courier_df = fetch_data("select distinct courier_id from shipments;")["courier_id"].tolist()
Dates_df = fetch_data("select distinct order_date from shipments")["order_date"].tolist()
Sorted_dates = sorted(Dates_df)

st.subheader("OVERALL SHIPMENT ANALYSIS")
filter_col1, filter_col2, filter_col3, filter_col4, filter_col5, filter_col6 = st.columns(6)
with filter_col1:
    search = st.text_input("Search ShipmentID")
with filter_col2:
    deliverystatus = st.selectbox("Delivery Status", ["ALL"] + delivery_status_df)
with filter_col3:
    destination = st.selectbox("Destination", ["ALL"] + destination_df)
with filter_col4:
    courierids = st.selectbox("CourierID",["ALL"] + courier_df)
with filter_col5:
    start_date = st.selectbox("Select Start Date", ["ALL"] + Sorted_dates)
with filter_col6:
    end_date = st.selectbox("Select End Date", ["ALL"] + Sorted_dates)

query = "select * from shipments where 1=1"
params = []

if search:
    query += " and shipment_id like %s"
    params.append(f"%{search}%")

if deliverystatus != "ALL":
    query += " and delivery_status = %s"
    params.append(deliverystatus)

if destination != "ALL":
    query += " and destination = %s"
    params.append(destination)

if courierids != "ALL":
    query += " and courier_id = %s"
    params.append(courierids)

if start_date != "ALL" and end_date != "ALL":
    query += " and order_date between %s and %s"  
    params.extend([start_date, end_date])        

Filtered_df = fetch_data(query, params)  
st.dataframe(Filtered_df, use_container_width = True)   

# 4.ANALYTICAL VIEWS
st.subheader("ANALATICAL VIEWS")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["AVG DELIVERY TIME PER ROUTE", "TOP 10 DELAYED ROUTES", "NUMBER OF SHIPMENTS BY COURIER", 
    "TOTAL COST PER SHIPMENT - HIGHEST TO LOWEST", "SHIPMENTS CANCELLED RATE BY ORIGIN", "SHIPMENTS CANCELLED RATE BY COURIER"]
    )
with tab1:
    df = fetch_data("select route_id, avg_time_hours from routes")
    st.subheader("AVG DELIVERY TIME PER ROUTE")
    st.dataframe(df, use_container_width = True)

with tab2:
    df = fetch_data("select route_id, avg_time_hours from routes order by avg_time_hours desc limit 10")
    st.subheader("TOP 10 DELAYED ROUTES")
    st.dataframe(df, use_container_width = True)

with tab3:
    df = fetch_data("""select
    cs.name, 
    count(s.shipment_id) AS total_shipments
    from 
    courier_staff cs
    left join 
    shipments s on cs.courier_id = s.courier_id
    group by 
    cs.courier_id;""")
    st.subheader("NUMBER OF SHIPMENTS HANDLED BY COURIER")
    st.dataframe(df, use_container_width = True)

with tab4:
    df = fetch_data("""select 
    shipment_id, fuel_cost, labor_cost, misc_cost, sum(fuel_cost + labor_cost + misc_cost) 
    as total_cost_per_shipment from costs group by shipment_id 
    order by total_cost_per_shipment DESC""")
    st.subheader("TOTAL COST PER SHIPMENT, HIGHEST TO LOWEST")
    st.dataframe(df, use_container_width = True)

with tab5:
    df = fetch_data("""select origin, count(shipment_id) as total_shipments, 
    sum(case when delivery_status = "cancelled" then 1 else 0 end) as cancelled_shipments, 
    (sum(case when delivery_status = "cancelled" then 1 else 0 end) / count(shipment_id) *100) as `cancellation(%)`
    from shipments group by origin order by `cancellation(%)` desc;""")
    st.subheader("SHIPMENTS CANCELLED RATE BY ORIGIN")
    st.dataframe(df, use_container_width = True)

with tab6:
    df = fetch_data("""SELECT
    cs.name, 
    COUNT(s.shipment_id) AS total_shipments, 
    sum(case when delivery_status = "cancelled" then 1 else 0 end) as cancelled_shipments,
    (sum(case when delivery_status = "cancelled" then 1 else 0 end) / count(shipment_id) * 100) as `cancellation(%)`
    FROM 
    courier_staff cs
    LEFT JOIN 
    shipments s ON cs.courier_id = s.courier_id
    GROUP BY 
    cs.courier_id order by `cancellation(%)` desc""")
    st.dataframe(df, use_container_width = True)