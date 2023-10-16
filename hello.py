import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Create a Streamlit app title
st.title("GA4 Bar Graph")

# Authenticate with Google Analytics using a service account key
st.sidebar.header("Google Analytics Authentication")

# You'll need to upload your service account key JSON file
service_account_key = st.sidebar.file_uploader("Upload Service Account Key JSON", type=["json"])

# Create a function to authenticate with Google Analytics
def authenticate_ga4():
    if service_account_key is not None:
        try:
            credentials = service_account.Credentials.from_service_account_info(
                service_account_key, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
            )
            analytics = build("analyticsdata", "v1alpha", credentials=credentials)
            return analytics
        except Exception as e:
            st.sidebar.error("Authentication failed. Please check your credentials.")
            st.stop()
    else:
        st.sidebar.info("Please upload a Service Account Key JSON file.")
        st.stop()

analytics = authenticate_ga4()

# Fetch GA4 data
st.sidebar.header("Fetch GA4 Data")
property_id = st.sidebar.text_input("Enter GA4 Property ID (e.g., 'ga:123456789'):")

if st.sidebar.button("Fetch Data"):
    if not property_id:
        st.sidebar.warning("Please enter a GA4 Property ID.")
    else:
        try:
            # Query Google Analytics for page views
            response = analytics.runReport(
                entity={"propertyId": property_id},
                dimensions=[{"name": "pagePath"}],
                metrics=[{"name": "engagement"}],
                dateRanges=[{"startDate": "7daysAgo", "endDate": "today"}],
            ).execute()

            # Extract data
            rows = response["rows"]
            data = [(row["dimensionValues"][0]["value"], int(row["metricValues"][0]["value"])) for row in rows]
            df = pd.DataFrame(data, columns=["Page Title", "Views"])

            # Create a bar chart
            st.bar_chart(df.set_index("Page Title"))

        except Exception as e:
            st.sidebar.error("Error fetching data. Please check the Property ID or try again later.")

# Display instructions
st.sidebar.subheader("Instructions")
st.sidebar.markdown("1. Upload your Google Analytics Service Account Key JSON file.")
st.sidebar.markdown("2. Enter your GA4 Property ID.")
st.sidebar.markdown("3. Click 'Fetch Data' to fetch and display the page views data.")

# Add more Streamlit content if needed
