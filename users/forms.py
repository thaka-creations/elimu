from django import forms
from users.models import County
from users import validators


class RegistrationForm(forms.Form):
    name = forms.CharField(label="Full Name", max_length=255, required=True, label_suffix="",
                           widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0"}))
    email = forms.EmailField(label="Email Address", required=True, label_suffix="",
                             widget=forms.EmailInput(attrs={"class": "form-control shadow-none rounded-0"}))
    school = forms.CharField(label="School", max_length=255, required=True, label_suffix="",
                             widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0"}))
    county = forms.ModelChoiceField(queryset=County.objects.filter(status=True), label="County", label_suffix="",
                                    required=True, validators=[validators.validate_county],
                                    widget=forms.Select(attrs={"class": "form-control shadow-none rounded-0"}))
    password = forms.CharField(label="Password", max_length=100, required=True, label_suffix="",
                               widget=forms.PasswordInput(attrs={"class": "form-control shadow-none rounded-0"}))
    confirm_password = forms.CharField(label="Confirm Password", max_length=100, required=True, label_suffix="",
                                       widget=forms.PasswordInput(
                                           attrs={"class": "form-control shadow-none rounded-0"}))


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email Address",
                             widget=forms.EmailInput(attrs={"class": "form-control shadow-none rounded-0"}))
    password = forms.CharField(label="Password", max_length=100,
                               widget=forms.PasswordInput(attrs={"class": "form-control shadow-none rounded-0"}))
