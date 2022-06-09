import base64
import math

import requests
import time
from requests.auth import HTTPBasicAuth
from datetime import datetime
from django.conf import settings
from phonenumber_field.phonenumber import PhoneNumber
from payments.models import Transaction


class Decorators:
    @staticmethod
    def refresh_token(decorated):
        def wrapper(gateway, *args, **kwargs):
            if (
                    gateway.access_token_expiration
                    and time.time() > gateway.access_token_expiration
            ):
                token = gateway.get_access_token()
                gateway.access_token = token
            return decorated(gateway, *args, **kwargs)

        return wrapper


class MpesaGateway:
    shortcode = None
    consumer_key = None
    consumer_secret = None
    access_token_url = None
    access_token = None
    access_token_expiration = None
    checkout_url = None
    timestamp = None

    def __init__(self):
        self.headers = None
        self.access_token_expiration = None
        self.shortcode = settings.MPESA_SHORTCODE
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.passkey = settings.MPESA_PASSKEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.password = self.generate_password()
        self.c2b_callback = settings.MPESA_CALLBACK_URL
        self.access_token_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        self.checkout_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

        try:
            self.access_token = self.get_access_token()
            if self.access_token is None:
                raise Exception("Request for access token failed.")
        except Exception as e:
            pass
        else:
            self.access_token_expiration = time.time() + 3400

    def generate_password(self):
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = self.shortcode + self.passkey + self.timestamp
        password_byte = password.encode("ascii")
        return base64.b64encode(password_byte).decode("utf-8")

    def get_access_token(self):
        try:
            res = requests.get(self.access_token_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        except Exception as e:
            raise e

        token = res.json()['access_token']
        self.headers = {"Authorization": "Bearer %s" % token}
        return token

    @Decorators.refresh_token
    def stk_push_request(self, amount, phone_number):

        req = {
            "BusinessShortCode": self.shortcode,
            "Password": self.password,
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": math.ceil(float(amount)),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.c2b_callback,
            "AccountReference": "Testing",
            "TransactionDesc": "Test",
            "headers": self.headers
        }

        res = requests.post(self.checkout_url, json=req, headers=self.headers, timeout=30)
        res_data = res.json()

        if res.ok:
            Transaction.objects.create(
                phone_number=phone_number,
                checkout_id=res_data["CheckoutRequestID"],
                amount=amount,
                reference="Test",
                description="Test"
            )

        return res_data

    @staticmethod
    def check_status(data):
        try:
            status = data["Body"]["stkCallback"]["ResultCode"]
        except Exception as e:
            status = 1
        return status

    @staticmethod
    def get_transaction_object(data):
        checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
        transaction, _ = Transaction.objects.get_or_create(checkout_id=checkout_request_id)
        return transaction

    @staticmethod
    def handle_successful_pay(data, transaction):
        items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

        for item in items:
            if item["Name"] == "Amount":
                amount = item["Value"]
            elif item["Name"] == "MpesaReceiptNumber":
                receipt_no = item["Value"]
            elif item["Name"] == "PhoneNumber":
                phone_number = item["Value"]

        transaction.amount = amount
        transaction.phone_number = PhoneNumber(raw_input=phone_number)
        transaction.receipt_no = receipt_no
        transaction.status = "APPROVED"

        return transaction

    def callback(self, data):
        status = self.check_status(data)
        transaction = self.get_transaction_object(data)

        if status == 0:
            transaction = self.handle_successful_pay(data, transaction)
        else:
            transaction.status = "PENDING"

        transaction.save()
        return True



