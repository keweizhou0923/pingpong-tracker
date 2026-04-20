import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds_dict = {
    "type": "service_account",
    "project_id": "table-493901",
    "private_key_id": "fd381e478ae59fb1a68c35465ab217d6dbe9cbc8",
    "private_key": "把你的private_key粘贴到这里",
    "client_email": "pingpong-sheets@table-493901.iam.gserviceaccount.com",
    "client_id": "102588038020825199350",
    "token_uri": "https://oauth2.googleapis.com/token",
}

creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
client = gspread.authorize(creds)
ss = client.open_by_key("1th7TC_CcQHMQbQ9SKi_VD-MOYpWMet2nC6pOefYq580")
print("成功！", ss.title)