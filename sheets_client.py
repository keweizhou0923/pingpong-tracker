import os
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from config import SHEET_SESSIONS, SHEET_TECHNIQUE_LOG, SESSIONS_COLUMNS, TECHNIQUE_COLUMNS

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def get_client():
    json_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    if os.path.exists(json_path):
        creds = Credentials.from_service_account_file(json_path, scopes=SCOPES)
    else:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet():
    client = get_client()
    spreadsheet_id = st.secrets["spreadsheet_id"]
    return client.open_by_key(spreadsheet_id)


def _get_or_create_sheet(spreadsheet, name: str, headers: list[str]):
    try:
        ws = spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=1000, cols=len(headers))
        ws.append_row(headers)
    return ws


def init_sheets():
    ss = get_spreadsheet()
    _get_or_create_sheet(ss, SHEET_SESSIONS, SESSIONS_COLUMNS)
    _get_or_create_sheet(ss, SHEET_TECHNIQUE_LOG, TECHNIQUE_COLUMNS)


def append_session(row: dict):
    ss = get_spreadsheet()
    ws = ss.worksheet(SHEET_SESSIONS)
    ws.append_row([row[c] for c in SESSIONS_COLUMNS])


def append_technique_logs(rows: list[dict]):
    ss = get_spreadsheet()
    ws = ss.worksheet(SHEET_TECHNIQUE_LOG)
    for row in rows:
        ws.append_row([row[c] for c in TECHNIQUE_COLUMNS])


@st.cache_data(ttl=60)
def load_sessions() -> pd.DataFrame:
    ss = get_spreadsheet()
    ws = ss.worksheet(SHEET_SESSIONS)
    data = ws.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=SESSIONS_COLUMNS)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce")
    return df


@st.cache_data(ttl=60)
def load_technique_log() -> pd.DataFrame:
    ss = get_spreadsheet()
    ws = ss.worksheet(SHEET_TECHNIQUE_LOG)
    data = ws.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=TECHNIQUE_COLUMNS)
    if not df.empty:
        df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce")
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    return df