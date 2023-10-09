import streamlit as st
from google.auth.transport import requests
from google.auth import load_credentials_from_file
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunRealtimeReportRequest
import pandas as pd
import altair as alt
import openai
from linkpreview import link_preview

# Load credentials
credentials = load_credentials_from_file("./credentials.json")[0]

# Initialize the client
client = BetaAnalyticsDataClient(credentials=credentials)

# Streamlit UI
st.title("Asharq Now Realtime Analytics")

# Add logo image
st.sidebar.image("img.png", width=150)  # Adjust the width as needed

# Fetch Data
request = RunRealtimeReportRequest(
    property=f"properties/254216168",
    dimensions=[{"name": "pagePath"}],  # Use pagePath instead of unifiedScreenName
    metrics=[{"name": "screenPageViews"}],
)
response = client.run_realtime_report(request)

data = response.rows
if data:
    df = pd.DataFrame(
        [
            (row.dimension_values[0].value, int(row.metric_values[0].value))
            for row in data
        ],
        columns=["Page Path", "Page Views"],
    )

    # Sort DataFrame by Page Views in descending order
    df = df.sort_values(by="Page Views", ascending=False)

    # Calculate total screenPageViews and total active users
    total_page_views = df["Page Views"].sum()
    total_active_users = len(df)

    # Custom styling for total numbers
    total_style = "font-size: 18px; color: #000000; padding: 3px;"

    # Add total screenPageViews and total active users to the sidebar with custom styling
    st.sidebar.markdown(f'<p style="{total_style}">Total Page Views:</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<p style="{total_style}">{total_page_views}</p>', unsafe_allow_html=True)

    st.sidebar.markdown(f'<p style="{total_style}">Total Active Users:</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<p style="{total_style}">{total_active_users}</p>', unsafe_allow_html=True)

    # Display Link Previews along with Page Views
    st.write("Real-time Page Views by Page Path with Link Previews")

    # Create an empty list to store link preview data
    link_previews = []

    for page_path in df["Page Path"]:
        # Fetch link preview data for each page path
        preview = link_preview(page_path)
        
        # Check if a preview is available for the page path
        if preview:
            # Extract relevant information from the link preview
            title = preview.get("title", "No title available")
            description = preview.get("description", "No description available")
            image = preview.get("image", None)

            # Add the link preview data to the list
            link_previews.append({"Page Path": page_path, "Title": title, "Description": description, "Image": image})
        else:
            # If no preview is available, use placeholders
            link_previews.append({"Page Path": page_path, "Title": "No title available", "Description": "No description available", "Image": None})

    # Create a DataFrame from the link preview data
    link_preview_df = pd.DataFrame(link_previews)

    # Display the link previews as a table
    st.table(link_preview_df)

else:
    st.write("No data available")
