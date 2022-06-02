from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from oauth2_provider.models import get_application_model
from users import forms, models as user_models
from users.utils import system_utils
from  school import models as school_models

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
            data = form.cleaned_data
            name = data['name'].upper()
            email = data['email']
            password = data['password']

            user = user_models.User.objects.create(
                username=email,
                name=name
            )
            user.set_password(password)
            oauth2_user.create_application_user(user)
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

            login(request, user)
            return redirect("/")

        return render(request, self.template_name, {"form": form})


class ProtectedView(View):
    template_name = "school/client.html"

    @method_decorator(login_required)
    def get(self, request):
        qs = school_models.FormModel.objects.all()
        context = {"forms": qs}
        return render(request, self.template_name, context=context)
