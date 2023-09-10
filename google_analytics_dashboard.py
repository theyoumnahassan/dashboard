import streamlit as st
from google.auth.transport import requests
from google.auth import load_credentials_from_file
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunRealtimeReportRequest
import pandas as pd
import altair as alt
import openai

# Load credentials
credentials = load_credentials_from_file("./credentials.json")[0]

# Initialize the client
client = BetaAnalyticsDataClient(credentials=credentials)

# Streamlit UI
st.title("Asharq Now Realtime Analytics")

# Add logo image
st.sidebar.image("img.png", width=150)  # Adjust the width as needed
#add chatbot
with st.sidebar:
    openai_api_key = st.text_input("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", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot") if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    openai.api_key = openai_api_key
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message
    st.session_state.messages.append(msg)
    st.chat_message("assistant").write(msg.content)


#add openai


# Fetch Data
request = RunRealtimeReportRequest(
    property=f"properties/254216168",
    dimensions=[{"name": "unifiedScreenName"}],
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
        columns=["Screen", "Page Views"],
    )
    
    # Sort DataFrame by Page Views in descending order
    df = df.sort_values(by="Page Views", ascending=False)

    # Calculate total screenPageViews and total active users
    total_page_views = df["Page Views"].sum()
    total_active_users = len(df)

    # Custom styling for total numbers
    total_style = "font-size: 18px; color: #000000; padding: 3px;"
    
    # Add total screenPageViews and total active users to the sidebar with custom styling
    st.sidebar.markdown(f'<p style="{total_style}">Total Screen Page Views:</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<p style="{total_style}">{total_page_views}</p>', unsafe_allow_html=True)

    st.sidebar.markdown(f'<p style="{total_style}">Total Active Users:</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<p style="{total_style}">{total_active_users}</p>', unsafe_allow_html=True)

    # Display Bar Chart using Altair with adjusted axis configuration
    st.write("Real-time Page Views by Screen")
    chart = alt.Chart(df).mark_bar(color='#c41b1a').encode(
        x=alt.X('Page Views:Q', title='Page Views', axis=alt.Axis(grid=False, titlePadding=20, labelPadding=10)),
        y=alt.Y('Screen:O', title='Screen Name', sort='-x', axis=alt.Axis(labelOffset=10)),
        tooltip=['Screen', 'Page Views']
    ).properties(width=1200)  # Increase chart width for better readability

    st.altair_chart(chart, use_container_width=True)
else:
    st.write("No data available")
