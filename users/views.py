import requests
from django.views import View
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from users import forms, models as user_models
from users.utils import system_utils
from school import models as school_models

oauth2_user = system_utils.ApplicationUser()
CALLBACK_URL = settings.SERVICES_URLS['callback_url']


def logout_view(request):
    logout(request)
    return redirect("/login")


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
            school = data['school']
            county = data['county']

            user = user_models.User.objects.create(
                username=email,
                name=name,
                school=school,
                county=county
            )
            user.set_password(password)
            user.save()
            oauth2_user.create_application_user(user)
            return redirect("/login")
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
            print(username, password)
            user = authenticate(username=username, password=password)

            if user is None:
                print("Invalid email or password")
                return redirect("/login")

            login(request, user)

            if request.user.is_admin:
                return redirect("/admin")
            else:
                return redirect("/")

        return render(request, self.template_name, {"form": form})


class ProtectedView(View):
    template_name = "school/client.html"

    @method_decorator(login_required)
    def get(self, request):
        qs = school_models.FormModel.objects.all()[0:4]
        context = {"forms": qs}
        video_id = "73e935bd2fe44c9c95ceea1524f0501c"
        url = CALLBACK_URL + 'video/get-video-otp'
        headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}

        resp = requests.get(url, params={"video_id": video_id}, headers=headers)
        res = resp.json()
        if not res:
            otp = False
            playback = False
        else:
            otp = res['otp']
            playback = res['playbackInfo']

        context.update({"otp": otp, "playback": playback})
        return render(request, self.template_name, context=context)
