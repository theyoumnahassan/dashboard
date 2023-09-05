import streamlit as st
import pandas as pd
import altair as alt
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load Google Analytics credentials
credentials = Credentials.from_authorized_user_file('credentials.json')
analytics = build('analyticsreporting', 'v4', credentials=credentials)

# Define the Google Analytics report request
report_request = {
    'viewId': 'properties/254216168',
    'dateRanges': [{'startDate': '2022-01-01', 'endDate': 'today'}],
    'metrics': [
        {'expression': 'ga:users'},
        {'expression': 'ga:screenviews'},
        {'expression': 'ga:sessions'},
        {'expression': 'ga:engagedSessions'}
    ]
}

response = analytics.reports().batchGet(body={'reportRequests': [report_request]}).execute()

# Extract data from the response
data = response['reports'][0]['data']['rows'][0]['metrics'][0]['values']

# Create Streamlit app
st.title('Google Analytics Report')

# Display metrics cards
st.subheader('Metrics')
metric_names = ['Total Users', 'Screen Page Views', 'Sessions', 'Engaged Sessions']
for i, metric_name in enumerate(metric_names):
    st.metric(label=metric_name, value=data[i])

# Date picker
st.subheader('Date Range')
start_date = st.date_input('Start Date', pd.to_datetime('2022-01-01'))
end_date = st.date_input('End Date', pd.to_datetime('today'))

# Bar graph using Altair
st.subheader('Bar Graph: Page Views by Page Title')
query_response = analytics.reports().batchGet(
    body={
        'reportRequests': [{
            'viewId': 'properties/254216168',
            'dateRanges': [{'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')}],
            'metrics': [{'expression': 'ga:screenviews'}],
            'dimensions': [{'name': 'ga:pageTitle'}],
            'orderBys': [{'fieldName': 'ga:screenviews', 'sortOrder': 'DESCENDING'}],
            'pageSize': 10
        }]
    }
).execute()

chart_data = []
for row in query_response['reports'][0]['data']['rows']:
    chart_data.append({'Page Title': row['dimensions'][0], 'Screen Page Views': int(row['metrics'][0]['values'][0])})

chart_df = pd.DataFrame(chart_data)
chart = alt.Chart(chart_df).mark_bar(color='#c41b1a').encode(
    x='Screen Page Views',
    y=alt.Y('Page Title', sort='-x')
).properties(
    width=600,
    height=300
)

st.altair_chart(chart, use_container_width=True)
