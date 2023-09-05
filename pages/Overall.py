import streamlit as st
import pandas as pd
import altair as alt
from google.oauth2.service_account import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient

# Load Google Analytics credentials using service account key
credentials = Credentials.from_service_account_file('credentials.json')
client = BetaAnalyticsDataClient(credentials=credentials)

# Create Streamlit app
st.title('Google Analytics 4 Report')

# Date picker
st.subheader('Date Range')
start_date = st.date_input('Start Date', pd.to_datetime('2022-01-01'))
end_date = st.date_input('End Date', pd.to_datetime('today'))

# Query for metrics using GA4 API
response = client.run_report(
    entity={
        "property_id": "properties/254216168"
    },
    date_ranges=[
        {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }
    ],
    dimensions=[
        {
            "name": "pagePath"
        }
    ],
    metrics=[
        {
            "name": "screenPageViews"
        }
    ],
    order_bys=[
        {
            "metric": {
                "metric_name": "screenPageViews"
            },
            "desc": True
        }
    ],
    limit=10
)

chart_data = []
for row in response.rows:
    chart_data.append({'Page Path': row.dimension_values[0], 'Screen Page Views': row.metric_values[0].value})

chart_df = pd.DataFrame(chart_data)
chart = alt.Chart(chart_df).mark_bar(color='#c41b1a').encode(
    x='Screen Page Views',
    y=alt.Y('Page Path', sort='-x')
).properties(
    width=600,
    height=300
)

st.altair_chart(chart, use_container_width=True)
