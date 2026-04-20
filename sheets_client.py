import os
import base64
import json
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from config import (
    SHEET_SESSIONS, SHEET_TECHNIQUE_LOG, SHEET_NOTES,
    SESSIONS_COLUMNS, TECHNIQUE_COLUMNS, NOTES_COLUMNS
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def get_client():
    json_path = r'C:\Users\yucai\Documents\credentials.json'
    if os.path.exists(json_path):
        creds = Credentials.from_service_account_file(json_path, scopes=SCOPES)
    else:
        encoded = st.secrets["GOOGLE_CREDENTIALS"]
        info = json.loads(base64.b64decode(encoded))
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet():
    client = get_client()
    return client.open_by_key(st.secrets["spreadsheet_id"])


def _get_or_create_sheet(spreadsheet, name, headers):
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
    _get_or_create_sheet(ss, SHEET_NOTES, NOTES_COLUMNS)


def append_session(row):
    ss = get_spreadsheet()
    ss.worksheet(SHEET_SESSIONS).append_row([row[c] for c in SESSIONS_COLUMNS])


def append_technique_logs(rows):
    ws = get_spreadsheet().worksheet(SHEET_TECHNIQUE_LOG)
    for row in rows:
        ws.append_row([row[c] for c in TECHNIQUE_COLUMNS])


def append_note(row):
    get_spreadsheet().worksheet(SHEET_NOTES).append_row([row[c] for c in NOTES_COLUMNS])


def delete_note(note_id):
    ws = get_spreadsheet().worksheet(SHEET_NOTES)
    records = ws.get_all_records()
    for i, r in enumerate(records, start=2):
        if r["note_id"] == note_id:
            ws.delete_rows(i)
            break


@st.cache_data(ttl=60)
def load_sessions():
    ws = get_spreadsheet().worksheet(SHEET_SESSIONS)
    data = ws.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=SESSIONS_COLUMNS)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce")
    return df


@st.cache_data(ttl=60)
def load_technique_log():
    ws = get_spreadsheet().worksheet(SHEET_TECHNIQUE_LOG)
    data = ws.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=TECHNIQUE_COLUMNS)
    if not df.empty:
        df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce")
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    return df


@st.cache_data(ttl=30)
def load_notes():
    ws = get_spreadsheet().worksheet(SHEET_NOTES)
    data = ws.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(columns=NOTES_COLUMNS)
