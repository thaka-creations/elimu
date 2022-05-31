import requests
from django.conf import settings

CALLBACK_URL = settings.SERVICES_URLS['callback_url']


def generate_otp_code(payload):
    url = CALLBACK_URL + 'mfa/otp/generate'
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return resp.json()
    return False


def verify_otp_code(payload):
    url = CALLBACK_URL + 'mfa/otp/verify'
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return True, resp.json()
    return False, resp.json()


def get_client_details(payload):
    url = CALLBACK_URL + 'o/token'
    resp = requests.post(url, data=payload)

    if resp.status_code == 200:
        return resp.json()
    return False
