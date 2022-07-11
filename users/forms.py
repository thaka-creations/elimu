import requests
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from django.conf import settings
from users.models import County
from users import models as user_models

CALLBACK_URL = settings.SERVICES_URLS['callback_url']

class RegistrationForm(forms.Form):
    name = forms.CharField(label="Full Name", max_length=255, required=True, label_suffix="",
                           widget=forms.TextInput(
                               attrs={"class": "form-control shadow-none rounded-0", "autocomplete": "off"}))
    email = forms.EmailField(label="Email Address", required=True, label_suffix="",
                             widget=forms.EmailInput(attrs={"class": "form-control shadow-none rounded-0",
                                                            "autocomplete": "off", "id": "in-email"}))
    school = forms.CharField(label="School", max_length=255, required=True, label_suffix="",
                             widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0",
                                                           "autocomplete": "off"}))
    county = forms.ModelChoiceField(queryset=County.objects.filter(status=True), label="County", label_suffix="",
                                    required=True,
                                    widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0",
                                                               "autocomplete": "off"}))
    code = forms.ModelChoiceField(queryset=user_models.Agent.objects.all(), label="Registration Code",
                                  label_suffix="", required=True,
                                  widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0",
                                                             "autocomplete": "off"}))
    password = forms.CharField(label="Password", max_length=100, required=True, label_suffix="", min_length=6,
                               widget=forms.PasswordInput(attrs={"class": "form-control shadow-none rounded-0",
                                                                 "autocomplete": "off"}))
    confirm_password = forms.CharField(label="Confirm Password", max_length=100, required=True, label_suffix="",
                                       min_length=6,
                                       widget=forms.PasswordInput(
                                           attrs={"class": "form-control shadow-none rounded-0",
                                                  "autocomplete": "off"}))

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email = cleaned_data.get("email")

        if password != confirm_password:
            raise ValidationError(_("Passwords don't match"))

        qs = user_models.User.objects.filter(username=email)

        if qs.exists():
            raise ValidationError(_("Email exists"))


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email Address",
                             widget=forms.EmailInput(attrs={"class": "form-control shadow-none rounded-0"}))
    password = forms.CharField(label="Password", max_length=100,
                               widget=forms.PasswordInput(attrs={"class": "form-control shadow-none rounded-0"}))


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label="Email Address",
                             widget=forms.EmailInput(attrs={"class": "form-control shadow-none rounded-0"}))

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        email = cleaned_data.get("email")

        try:
            user_models.User.objects.get(username__iexact=email)
        except user_models.User.DoesNotExist:
            raise ValidationError(_("User does not exist"))


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email Address",
                             widget=forms.EmailInput(attrs={"class": "form-control shadow-none rounded-0"}))
    password = forms.CharField(label="Password", max_length=100, required=True, label_suffix="", min_length=6,
                               widget=forms.PasswordInput(attrs={"class": "form-control shadow-none rounded-0",
                                                                 "autocomplete": "off"}))
    confirm_password = forms.CharField(label="Confirm Password", max_length=100, required=True, label_suffix="",
                                       min_length=6,
                                       widget=forms.PasswordInput(
                                           attrs={"class": "form-control shadow-none rounded-0",
                                                  "autocomplete": "off"}))
    otp = forms.CharField(label="Email OTP Code", max_length=100, required=True, label_suffix="",
                          widget=forms.TextInput(
                             attrs={"class": "form-control shadow-none rounded-0", "autocomplete": "off"}))

    def clean(self):
        cleaned_data = super(ForgotPasswordForm, self).clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        otp = cleaned_data.get("otp")
        url = CALLBACK_URL + 'mfa/otp/verify'

        try:
            user_models.User.objects.get(username__iexact=email)
        except user_models.User.DoesNotExist:
            raise ValidationError(_("User does not exist"))

        if password != confirm_password:
            raise ValidationError(_("Passwords don't match"))

        payload = {"otp": otp, "send_to": email}
        resp = requests.post(url, data=payload)

        if resp.status_code != 200:
            raise ValidationError(_("Invalid Otp Code"))





