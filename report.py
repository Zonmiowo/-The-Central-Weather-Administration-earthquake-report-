import asyncio
import websockets
import requests
import json
from datetime import datetime

def fetch_earthquake_report(api_url):
    response = requests.get(api_url)
    data_json = response.json()

    if 'records' in data_json and 'Earthquake' in data_json['records']:
        latest_quake = data_json['records']['Earthquake'][0]
        return {
            "time": latest_quake['EarthquakeInfo']['OriginTime'],
            "location": latest_quake['EarthquakeInfo']['Epicenter']['Location'],
            "magnitude": latest_quake['EarthquakeInfo']['EarthquakeMagnitude']['MagnitudeValue'],
            "FocalDepth": latest_quake['EarthquakeInfo']['FocalDepth']
        }
    return None

def parse_time(time_str):
    return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

def get_latest_report():
    api_url_1 = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization=CWA-62E18FDA-413D-4429-8AE2-34DDA8378A3E&limit=1&offset=0&format=JSON'
    api_url_2 = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization=CWA-62E18FDA-413D-4429-8AE2-34DDA8378A3E&limit=1&format=JSON'

    report_1 = fetch_earthquake_report(api_url_1)
    report_2 = fetch_earthquake_report(api_url_2)

    if report_1 and report_2:
        latest_report = max(report_1, report_2, key=lambda x: parse_time(x['time']))
    elif report_1:
        latest_report = report_1
    elif report_2:
        latest_report = report_2
    else:
        latest_report = None

    return json.dumps([latest_report]) if latest_report else json.dumps([])

async def handler(websocket, path):
    try:
        while True:
            json_content = get_latest_report()
            print("Sending JSON:", json_content) 
            if websocket.open:
                await websocket.send(json_content)
            await asyncio.sleep(3000)  
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed normally.")
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(main())
