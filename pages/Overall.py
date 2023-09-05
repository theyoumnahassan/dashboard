
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Load credentials
creds = Credentials.from_authorized_user_file("credentials.json")

# Initialize the Google Analytics Reporting API
service = build("analyticsreporting", "v4", credentials=creds)

# Streamlit UI
st.title("Asharq Now Analytics")

# Datepicker for selecting the date range
st.sidebar.write("Select Date Range:")
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=7))
end_date = st.sidebar.date_input("End Date", datetime.now())

# Fetch Data using the Reporting API
response = service.reports().batchGet(
    body={
        "reportRequests": [
            {
                "viewId": "254216168",  # Replace with your view ID
                "dateRanges": [{"startDate": start_date.strftime("%Y-%m-%d"), "endDate": end_date.strftime("%Y-%m-%d")}],
                "metrics": [{"expression": "ga:sessions"}, {"expression": "ga:screenPageViews"}, {"expression": "ga:engagementRate"}, {"expression": "ga:totalUsers"}],
                "dimensions": [{"name": "ga:screenPageViews"}],
                "orderBys": [{"fieldName": "ga:screenPageViews", "sortOrder": "DESCENDING"}],
            }
        ]
    }
).execute()

data = response["reports"][0]["data"]["rows"]
if data:
    df = pd.DataFrame(
        [(row["dimensions"][0], int(row["metrics"][0]["values"][0]), float(row["metrics"][0]["values"][1]), float(row["metrics"][0]["values"][2]), int(row["metrics"][0]["values"][3])) for row in data],
        columns=["Screen", "Sessions", "Page Views", "Engagement Rate", "Total Users"],
    )

    # Display cards with total metrics
    st.sidebar.write("Overall Metrics:")
    st.sidebar.write(f"Total Sessions: {df['Sessions'].sum()}")
    st.sidebar.write(f"Total Screen Page Views: {df['Page Views'].sum()}")
    st.sidebar.write(f"Average Engagement Rate: {df['Engagement Rate'].mean():.2f}%")
    st.sidebar.write(f"Total Users: {df['Total Users'].sum()}")

    # Display Bar Chart using Altair
    st.write("Page Views by Screen")
    chart = alt.Chart(df).mark_bar(color='#c41b1a').encode(
        x=alt.X('Page Views:Q', title='Page Views', axis=alt.Axis(grid=False, titlePadding=20, labelPadding=10)),
        y=alt.Y('Screen:O', title='Screen Name', sort='-x', axis=alt.Axis(labelOffset=10)),
        tooltip=['Screen', 'Page Views']
    ).properties(width=1200)  # Increase chart width for better readability

    st.altair_chart(chart, use_container_width=True)
else:
    st.write("No data available")
