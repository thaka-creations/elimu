import requests
from django.views import View
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from users import forms, models as user_models
from users.utils import system_utils
from school import models as school_models

oauth2_user = system_utils.ApplicationUser()
CALLBACK_URL = settings.SERVICES_URLS['callback_url']


def logout_view(request):
    logout(request)
    return redirect("/login")


@require_http_methods(["GET"])
def account_settings(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    return render(request, "school/accounts/setting.html")


@require_http_methods(["GET"])
def account_activity(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    page = "account_activity"
    context = {"page": page}
    return render(request, "school/accounts/activity.html", context)


class RegistrationView(View):
    form_class = forms.RegistrationForm
    template_name = "users/registration.html"

    def get(self, request):
        params = request.GET
        if "code" in params.keys():
            code = request.GET['code']
            try:
                instance = user_models.Agent.objects.get(code=code)
                form = self.form_class(initial={"code": instance})
            except user_models.Agent.DoesNotExist:
                return redirect("/registration")
        else:
            if len(params.keys()) != 0:
                return redirect("/registration")
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
            code = data['code']

            user = user_models.User.objects.create(
                username=email,
                name=name,
                email_verified=True
            )

            # create public user
            user_models.PublicUser.objects.create(
                user=user,
                school=school,
                county=county
            )
            code.subscribers.add(user)
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
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                if request.user.is_admin:
                    return redirect("/admin")
                elif request.user.is_agent:
                    return redirect("/agent")
                else:
                    return redirect("/")

        errors = "Invalid username or password"
        context = {"errors": errors, "form": form}
        return render(request, self.template_name, context)


class ResetPasswordView(View):
    template_name = "users/reset_password.html"
    form_class = forms.ResetPasswordForm

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            url = CALLBACK_URL + "mfa/otp/generate"
            data = form.cleaned_data
            email = data['email']
            payload = {"send_to": email, "expiry_time": 600}
            resp = requests.post(url, json=payload)

            if not resp:
                return redirect("/reset-password", {"form": form, "message": "An error occurred"})
            messages.success(request, _("Reset password otp has been sent to your email"))
            return redirect("/forgot-password")
        return render(request, self.template_name, {"form": form})


class ForgotPassword(View):
    template_name = "users/forgot_password.html"
    form_class = forms.ForgotPasswordForm

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            password = data['password']
            try:
                instance = user_models.User.objects.get(username__iexact=email)
            except user_models.User.DoesNotExist:
                return redirect("/reset-password")

            instance.set_password(password)
            instance.save()
            return redirect("/login", {"message": "Password updated successfully"})
        print("error")
        return render(request, self.template_name, {"form": form})


class ProtectedView(View):
    template_name = "school/client.html"

    def get(self, request):
        qs = school_models.FormModel.objects.all()[0:4]
        context = {"forms": qs, "page": "index"}
        url = CALLBACK_URL + 'video/get-video-otp'
        headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}
        vid_exist = school_models.CoverVideo.objects.exists()
        if not vid_exist:
            otp = False
            playback = False
        else:
            video_id = school_models.CoverVideo.objects.last().videoid
            resp = requests.get(url, params={"video_id": video_id}, headers=headers)
            res = resp.json()
            try:
                otp = res['otp']
                playback = res['playbackInfo']
            except Exception as e:
                otp = False
                playback = False

        context.update({"otp": otp, "playback": playback})
        return render(request, self.template_name, context=context)
