from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from oauth2_provider.models import get_application_model
from users import forms
from users.utils import system_utils

oauth2_user = system_utils.ApplicationUser()


class RegistrationView(View):
    form_class = forms.RegistrationForm
    template_name = "users/registration.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            pass
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    form_class = forms.LoginForm
    template_name = "users/login.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['email']
            password = data['password']

            user = authenticate(username=username, password=password)

            if user is None:
                print("Invalid email or password")
                return redirect("/login")

            try:
                instance = get_application_model().objects.get(user=user)
            except get_application_model().DoesNotExist:
                print("Invalid client")
                return redirect("/login")

            dt = {
                "grant_type": "password",
                "username": user.username,
                "password": password,
                "client_id": instance.client_id,
                "client_secret": instance.client_secret
            }

            resp = oauth2_user.get_client_details(dt)

            if not resp:
                return redirect("/login")

            userinfo = {
                "access_token": resp['access_token'],
                "expires_in": resp['expires_in'],
                "token_type": resp['token_type'],
                "refresh_token": resp['refresh_token'],
                "jwt_token": oauth2_user.generate_jwt_token(user)
            }

            return redirect("/registration")

        return render(request, self.template_name, {"form": form})
