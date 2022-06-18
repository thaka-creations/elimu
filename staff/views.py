import requests
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.conf import settings
from django.views.generic import ListView
from school import models as school_models
from payments import models as payment_models
from staff import forms, models as staff_models
from django.contrib.auth.mixins import UserPassesTestMixin
from users import models as user_models

CALLBACK_URL = settings.SERVICES_URLS['callback_url']


class AdminMixin(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_admin


# Create your views here.
class Admin(AdminMixin):
    template_name = "admin/index.html"
    login_url = "/login"

    def get(self, request):
        return render(request, self.template_name)


class ListVideos(AdminMixin):
    template_name = "admin/videos/index.html"
    login_url = "/login"

    def get(self, request):
        unit = request.GET.get("unit", False)
        video = request.GET.get("video", False)
        if not unit:
            return redirect("/admin")

        try:
            instance = school_models.UnitModel.objects.get(id=unit)
        except school_models.UnitModel.DoesNotExist:
            return redirect("/admin")

        videos = school_models.VideoModel.objects.filter(unit=instance).order_by('index')
        if not videos.exists():
            otp = False
            return render(request, self.template_name, {"videos": videos, "unit": instance, "otp": otp})

        if video:
            try:
                video = school_models.VideoModel.objects.get(videoid=video)
            except school_models.VideoModel.DoesNotExist:
                return redirect("/admin")
            video_id = video.videoid
        else:
            video_id = videos.first().videoid

        url = CALLBACK_URL + 'video/get-video-otp'
        headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}

        resp = requests.get(url, params={"video_id": video_id}, headers=headers)
        res = resp.json()
        if not res:
            return redirect("/")

        otp = res['otp']
        playback = res['playbackInfo']

        return render(request, self.template_name,
                      {"videos": videos, "unit": instance, "otp": otp, "playback": playback})


class AddVideo(AdminMixin):
    form_class = forms.AddVideoForm
    template_name = "admin/videos/create.html"
    login_url = "/login"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            pass
        return render(request, self.template_name)


class ListSubjects(AdminMixin, ListView):
    model = school_models.SubjectModel
    template_name = "admin/subjects/index.html"
    context_object_name = "subjects"
    login_url = "/login"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddSubjectForm
        return context


class AddSubject(AdminMixin):
    form_class = forms.AddSubjectForm
    login_url = "/"

    def post(self, request):
        subjects = school_models.SubjectModel.objects.all()
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            school_models.SubjectModel.objects.create(**data)
            context = {"details": "Subject added successfully", "subjects": subjects}
            return redirect("/admin/subjects", context=context)
        return redirect("/admin/subjects", {"form": form, "subjects": subjects})


class RetrieveSubject(AdminMixin):
    template_name = "admin/subjects/detail.html"
    login_url = "/"

    def get(self, request, pk):
        try:
            subject = school_models.SubjectModel.objects.get(id=pk)
        except school_models.SubjectModel.DoesNotExist:
            return redirect("/admin")
        qs = school_models.FormModel.objects.all()
        form = forms.AddSubjectAmount
        amounts = payment_models.SubjectAmount.objects.filter(subject=subject)
        context = {"subject": subject, "queryset": qs, "form": form, "amounts": amounts}
        return render(request, self.template_name, context)


class ListForm(AdminMixin, ListView):
    model = school_models.FormModel
    template_name = "admin/forms/index.html"
    context_object_name = "qs"
    login_url = "/login"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddForm
        return context


class AddForm(AdminMixin):
    form_class = forms.AddForm
    template_name = "admin/forms/create.html"
    login_url = "/login"

    def post(self, request):
        form = self.form_class(request.POST)
        qs = school_models.FormModel.objects.all()

        if form.is_valid():
            data = form.cleaned_data
            school_models.FormModel.objects.create(**data)
            context = {"details": "Form added successfully", "qs": qs}
            return redirect("/admin/forms", context=context)

        return redirect("/admin/forms", {"qs": qs, "form": form})


class ListUnits(AdminMixin, ListView):
    model = school_models.UnitModel
    template_name = "admin/units/index.html"
    context_object_name = "units"
    login_url = "/login"


class AddUnit(AdminMixin):
    form_class = forms.AddUnitForm
    template_name = "admin/units/create.html"
    login_url = "/login"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            school_models.UnitModel.objects.create(**data)
            context = {"details": "Unit added successfully"}
            return redirect("/admin/units", context=context)
        return render(request, self.template_name, {"form": form})


class UnitDetailView(AdminMixin):
    template_name = "admin/units/detail.html"
    login_url = "/login"

    def get(self, request):
        unit = request.GET.get("unit", False)

        if not unit:
            return redirect("/admin/units")

        try:
            instance = school_models.UnitModel.objects.get(id=unit)
        except school_models.UnitModel.DoesNotExist:
            return redirect("/admin/units")

        videos = instance.videos.all()
        amounts = payment_models.UnitAmount.objects.filter(unit=instance)
        form = forms.AddUnitAmount
        context = {"unit": instance, "amounts": amounts, "otp": False, "form": form}
        if not videos.exists:
            return render(request, self.template_name, context)

        video_id = videos.first()
        url = CALLBACK_URL + 'video/get-video-otp'
        headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}

        resp = requests.get(url, params={"video_id": video_id}, headers=headers)
        res = resp.json()

        if not resp:
            return render(request, self.template_name, context)

        otp = res['otp']
        playback = res['playbackInfo']
        context.update({"otp": otp, "playback": playback})
        return render(request, self.template_name, context)


class ListInvoices(AdminMixin, ListView):
    model = payment_models.Invoice
    template_name = "admin/payments/invoices.html"
    context_object_name = "invoices"
    login_url = "/login"


class ListTransactions(AdminMixin, ListView):
    model = payment_models.Transaction
    template_name = "admin/payments/transactions.html"
    context_object_name = "transactions"
    login_url = "/login"


class ListCurrentSubscription(AdminMixin, ListView):
    model = payment_models.Subscription
    template_name = "admin/subscriptions/index.html"
    context_object_name = "subscriptions"
    login_url = "/login"

    def get_context_data(self, *, object_list=None, **kwargs):
        qs = payment_models.Subscription.objects.filter(status="ACTIVE")
        return {"subscriptions": qs, "status": "Active"}


class ListExpiredSubscriptions(AdminMixin, ListView):
    model = payment_models.Subscription
    template_name = "admin/subscriptions/index.html"
    context_object_name = "subscriptions"
    login_url = "/login"

    def get_context_data(self, *, object_list=None, **kwargs):
        qs = payment_models.Subscription.objects.filter(status="EXPIRED")
        return {"subscriptions": qs, "status": "Expired"}


class ListRevokedSubscriptions(AdminMixin, ListView):
    model = payment_models.Subscription
    template_name = "admin/subscriptions/index.html"
    context_object_name = "subscriptions"
    login_url = "/login"

    def get_context_data(self, *, object_list=None, **kwargs):
        qs = payment_models.Subscription.objects.filter(status="REVOKED")
        return {"subscriptions": qs, "status": "Revoked"}


class ListCounties(AdminMixin, ListView):
    model = user_models.County
    template_name = "admin/users/counties/index.html"
    context_object_name = "counties"
    login_url = "/login"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddCountyForm
        return context


class AddCounty(AdminMixin):
    form_class = forms.AddCountyForm
    template_name = "admin/users/counties/index.html"
    login_url = "/login"

    def post(self, request):
        form = self.form_class(request.POST)
        qs = user_models.County.objects.all()

        if form.is_valid():
            data = form.cleaned_data
            user_models.County.objects.create(**data)
            context = {"details": "County added successfully", "qs": qs}
            return redirect("/admin/counties", context=context)

        return redirect("/admin/counties/add-county", {"qs": qs, "form": form})


class AddUnitAmountView(AdminMixin):
    form_class = forms.AddUnitAmount
    template_name = "admin/units/detail.html"
    login_url = "/login"

    def post(self, request):
        form = self.form_class(request.POST)
        qs = user_models.County.objects.all()

        if form.is_valid():
            data = form.cleaned_data
            payment_models.UnitAmount.objects.create(**data)
            context = {"details": "Unit Amount added successfully"}
            return redirect("/admin")
        return redirect("/")


class AddSubjectAmountView(AdminMixin):
    form_class = forms.AddSubjectAmount

    def post(self, request):
        form = self.form_class(request.POST)
        subject = request.POST["subject"]
        url = '/admin/subjects/{}'.format(subject)

        if form.is_valid():
            data = form.cleaned_data
            payment_models.SubjectAmount.objects.create(**data)
            context = {"details": "Subject Amount added successfully"}
            return redirect(url)
        return redirect(url)


class ListRegistrationCodes(AdminMixin, ListView):
    model = staff_models.RegistrationCodes
    template_name = "admin/users/registration_codes.html"
    context_object_name = "codes"
    login_url = "/login"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddRegistrationCodes
        return context


class AddRegistrationCodes(AdminMixin):
    form_class = forms.AddRegistrationCodes
    template_name = "admin/users/counties/index.html"
    login_url = "/login"

    def post(self, request):
        form = self.form_class(request.POST)
        qs = staff_models.RegistrationCodes.objects.all()

        if form.is_valid():
            data = form.cleaned_data
            staff_models.RegistrationCodes.objects.create(**data)
            context = {"details": "Code added successfully", "qs": qs}
            return redirect("/admin/registration-codes", context=context)

        return redirect("/admin/registration-codes", {"qs": qs, "form": form})
