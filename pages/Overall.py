import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Google Analytics 4 credentials
KEY_FILE_LOCATION = 'your-service-account-key.json'
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

# Initialize Streamlit
st.title('GA4 Reporting Dashboard')

# Authenticate with the GA4 API
credentials = service_account.Credentials.from_service_account_file(
    KEY_FILE_LOCATION, scopes=SCOPES)
analytics = build('analyticsreporting', 'v4', credentials=credentials)

# Main Metrics
st.header('Main Metrics')

# Date Picker
start_date = st.date_input('Select Start Date', pd.to_datetime('7 days ago'))
end_date = st.date_input('Select End Date', pd.to_datetime('1 day ago'))

# Country Picker
selected_country = st.selectbox('Select Country', ['All', 'United States', 'Canada', 'United Kingdom'])

# Fetch GA4 Data
def fetch_ga4_data(start_date, end_date, country):
    # Build the GA4 Reporting API query
    body = {
        'reportRequests': [
            {
                'viewId': '254216168',  # Replace with your GA4 view ID
                'dateRanges': [{'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')}],
                'metrics': [{'expression': 'ga:users'}],
                'dimensions': [{'name': 'ga:country'}],
                'filtersExpression': f'ga:country=={country}' if country != 'All' else '',
            }
        ]
    }

    # Execute the query
    response = analytics.reports().batchGet(body=body).execute()

    # Process the response and return the data as a DataFrame
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

# Close the GA4 API connection
analytics.close()
