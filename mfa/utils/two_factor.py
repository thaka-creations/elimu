import random
from mfa import models as mfa_models
from django.utils import timezone


class MultiFactorAuthentication:

    @staticmethod
    def generate_code():
        otp_code = ""
        for i in range(6):
            otp_code += str(random.randint(1, 9))

        return otp_code

    def generate_otp_code(self):
        new_otp_code = self.generate_code()
        otp_exists = mfa_models.OtpCode.objects.filter(code=new_otp_code).exists()

        if otp_exists:
            self.generate_otp_code()
        return new_otp_code

    @staticmethod
    def verify_otp_code(otp, send_to):
        code_verification = mfa_models.OtpCode.objects.filter(
            code=otp, send_to=send_to, status__iexact='PENDING')

        if code_verification:

            if code_verification.count() == 1:
                otp_instance = code_verification.first()
                current_time = timezone.now()
                expiry_time = otp_instance.expiry_date
                otp_state = current_time > expiry_time
                otp_instance.status = "REVOKED"
                otp_instance.save()

                if otp_state:  # expired
                    return False, "Otp Code has expired"

                return True, "Otp Code is ok"

        return False, "Invalid Otp Code"
