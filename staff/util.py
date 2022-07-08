import string
import random
from django.core.mail import send_mail


class PasswordManager:

    @staticmethod
    def generate_password():
        chars = string.digits + string.ascii_letters
        password = ''.join((random.choice(chars)
                            for i in range(6)))
        return password


class ServiceManager:

    @staticmethod
    def send_email(subject, message, recipient):
        sender = ""
        send_mail(
            subject,
            message,
            sender,
            [recipient],
            fail_silently=False,
        )
