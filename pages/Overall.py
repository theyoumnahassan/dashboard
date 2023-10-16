import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account
import plotly.express as px

# Google Analytics 4 credentials
KEY_FILE_LOCATION = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

# Initialize Streamlit
st.title('GA4 Reporting Dashboard')

# Main Metrics
st.header('Main Metrics')

# Date Picker
end_date = st.date_input('Select End Date', pd.to_datetime('today'))
start_date = end_date - timedelta(days=7)

# Country Picker
selected_country = st.selectbox('Select Country', ['All', 'United States', 'Canada', 'United Kingdom'])

# Display the selected date range
st.write(f'Start Date: {start_date}, End Date: {end_date}')

# Authenticate with the GA4 API
credentials = service_account.Credentials.from_service_account_file(
    KEY_FILE_LOCATION, scopes=SCOPES)
analytics = build('analyticsreporting', 'v4', credentials=credentials)

# Fetch GA4 Data
def fetch_ga4_data(start_date, end_date, country):
    body = {
        'reportRequests': [
            {
                'viewId': '254216168',
                'dateRanges': [{'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')}],
                'metrics': [{'expression': 'ga:users'}],
                'dimensions': [{'name': 'ga:country'}],
                'filtersExpression': f'ga:country=={country}' if country != 'All' else '',
            }
        ]
    }

    response = analytics.reports().batchGet(body=body).execute()
    data = []

    for report in response.get('reports', []):
        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            metrics = row.get('metrics', [])
            data.append([dimensions[0] if dimensions else 'N/A', metrics[0]['values'][0] if metrics else 0])

    df = pd.DataFrame(data, columns=['Country', 'Users'])
    return df

data = fetch_ga4_data(start_date, end_date, selected_country)

# Display the data as a table
st.dataframe(data)

# Control Bar Graph
st.header('Control Bar Graph')
# Create and display a control bar graph based on the selected metrics and date range
fig = px.bar(data, x='Country', y='Users', title='Control Bar Graph')
st.plotly_chart(fig)

# Map showing total users and their countries
st.header('Map showing Total Users and their Countries')
# Create and display a map based on the selected metrics and date range
fig_map = px.choropleth(data, locations='Country', locationmode='country names', color='Users', hover_name='Country', title='Map showing Total Users and their Countries')
st.plotly_chart(fig_map)

# Bar graph with pages with highest views (Placeholder)
st.header('Bar Graph with Pages with Highest Views')
# Add code to create and display a bar graph of pages with the highest views
# Replace this comment with your bar graph code

# Close the GA4 API connection
analytics.close()
