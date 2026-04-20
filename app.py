import streamlit as st
from sheets_client import init_sheets
import log_session
import dashboard
import notes_page

st.set_page_config(
    page_title="🏓 乒乓训练追踪",
    page_icon="🏓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_sheets()

st.title("🏓 乒乓球训练追踪")
page = st.radio(
    "",
    ["📝 记录训练", "📊 训练看板", "📚 技术笔记"],
    horizontal=True,
    label_visibility="collapsed",
)
st.divider()

if page == "📝 记录训练":
    log_session.render()
elif page == "📊 训练看板":
    dashboard.render()
else:
    notes_page.render()
