from django import forms


class RegistrationForm(forms.Form):
    name = forms.CharField(label="Full Name", max_length=255,
                           widget=forms.TextInput(attrs={"class": "form-control shadow-none rounded-0"}))
    email = forms.EmailField(label="Email Address",
                             widget=forms.EmailInput(attrs={"class": "form-control shadow-none rounded-0"}))
    password = forms.CharField(label="Password", max_length=100,
                               widget=forms.PasswordInput(attrs={"class": "form-control shadow-none rounded-0"}))
    confirm_password = forms.CharField(label="Confirm Password", max_length=100,
                                       widget=forms.PasswordInput(
                                           attrs={"class": "form-control shadow-none rounded-0"}))


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email Address",
                             widget=forms.EmailInput(attrs={"class": "form-control shadow-none rounded-0"}))
    password = forms.CharField(label="Password", max_length=100,
                               widget=forms.PasswordInput(attrs={"class": "form-control shadow-none rounded-0"}))