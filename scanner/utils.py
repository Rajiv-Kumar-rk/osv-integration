import requests
from django.conf import settings

def call_osv_api(name, version):
    payload = {
        "package": {
            "name": name,
            "ecosystem": "npm"
        },
        "version": version
    }
    response = requests.post(settings.OSV_API, json=payload)
    print("osv response: ", response.text)
    return response.json()

def send_slack_message(text):
    headers = {
        "Authorization": f"Bearer {settings.SLACK_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "channel": settings.SLACK_USER_ID,
        "text": text
    }
    res =  requests.post(settings.SLACK_API, json=data, headers=headers)
    print("slack response: ", res.text)
    return res
