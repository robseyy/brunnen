import requests
import os
import sys

TOKEN = os.environ["DATACAKE_TOKEN"]
DEVICE_ID = os.environ["DATACAKE_DEVICE_ID"]
WORKSPACE_ID = os.environ["DATACAKE_WORKSPACE_ID"]

HEADERS = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}


def get_value(field_name):
    query = f'''
    query {{
      allDevices(inWorkspace: "{WORKSPACE_ID}") {{
        id
        currentMeasurements(allActiveFields: true) {{
          value
          field {{ fieldName }}
        }}
      }}
    }}
    '''
    r = requests.post("https://api.datacake.co/graphql/", json={"query": query}, headers=HEADERS)
    data = r.json()
    for device in data["data"]["allDevices"]:
        if device["id"] == DEVICE_ID:
            for m in device["currentMeasurements"]:
                if m["field"]["fieldName"] == field_name:
                    return float(m["value"])
    return None


def write_value(field_name, value):
    url = f"https://api.datacake.co/v1/devices/{DEVICE_ID}/record/?batch=true"
    payload = [{"field": field_name, "value": value}]
    r = requests.post(url, json=payload, headers=HEADERS)
    print(r.status_code, r.text)


mode = sys.argv[1]

if mode == "snapshot":
    v = get_value("VOLUMEN_LITER")
    write_value("VOLUMEN_2300", v)
    print(f"Snapshot gespeichert: {v} L")
elif mode == "calculate":
    now = get_value("VOLUMEN_LITER")
    snapshot = get_value("VOLUMEN_2300")
    diff = round(now - snapshot, 1)
    write_value("NACHTZUFLUSS_LITER", diff)
    print(f"Nachtzufluss: {diff} L")
