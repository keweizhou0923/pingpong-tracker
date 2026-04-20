import streamlit as st
from sheets_client import init_sheets
import log_session
import dashboard

st.set_page_config(
    page_title="🏓 乒乓训练追踪",
    page_icon="🏓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Initialize sheets on first run
init_sheets()

# Navigation
st.title("🏓 乒乓球训练追踪")
page = st.radio(
    "",
    ["📝 记录训练", "📊 训练看板"],
    horizontal=True,
    label_visibility="collapsed",
)
st.divider()

if page == "📝 记录训练":
    log_session.render()
else:
    dashboard.render()
