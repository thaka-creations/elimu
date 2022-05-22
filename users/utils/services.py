import requests
from django.conf import settings

CALLBACK_URL = settings.SERVICES_URLS()

def generate_otp_code(payload):
    url =