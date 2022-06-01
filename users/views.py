from django.views import View
from django.shortcuts import render, redirect
from users import forms


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
            pass
        return render(request, self.template_name, {"form": form})
