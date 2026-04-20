import json, base64
with open(r'C:\Users\yucai\Documents\credentials.json', 'rb') as f:
    encoded = base64.b64encode(f.read()).decode()
print(f'GOOGLE_CREDENTIALS = "{encoded}"')
print('spreadsheet_id = "1th7TC_CcQHMQbQ9SKi_VD-MOYpWMet2nC6pOefYq580"')