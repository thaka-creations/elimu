import requests
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.views.generic import ListView
from school import models as school_models
from payments import models as payment_models
from staff import forms

CALLBACK_URL = settings.SERVICES_URLS['callback_url']


# Create your views here.
class Admin(View):
    template_name = "admin/index.html"

    def get(self, request):
        return render(request, self.template_name)


class ListVideos(View):
    template_name = "admin/videos/index.html"

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


class AddVideo(View):
    form_class = forms.AddVideoForm
    template_name = "admin/videos/create.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            pass
        return render(request, self.template_name)


class ListSubjects(ListView):
    model = school_models.SubjectModel
    template_name = "admin/subjects/index.html"
    context_object_name = "subjects"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddSubjectForm
        return context


class AddSubject(View):
    form_class = forms.AddSubjectForm
    template_name = "admin/subjects/create.html"

    def post(self, request):
        subjects = school_models.SubjectModel.objects.all()
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            school_models.SubjectModel.objects.create(**data)
            context = {"details": "Subject added successfully", "subjects": subjects}
            return redirect("/admin/subjects", context=context)
        return redirect("/admin/subjects", {"form": form, "subjects": subjects})


class ListForm(ListView):
    model = school_models.FormModel
    template_name = "admin/forms/index.html"
    context_object_name = "qs"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddForm
        return context


class AddForm(View):
    form_class = forms.AddForm
    template_name = "admin/forms/create.html"

    def post(self, request):
        form = self.form_class(request.POST)
        qs = school_models.FormModel.objects.all()

        if form.is_valid():
            data = form.cleaned_data
            school_models.FormModel.objects.create(**data)
            context = {"details": "Form added successfully", "qs": qs}
            return redirect("/admin/forms", context=context)

        return redirect("/admin/forms", {"qs": qs, "form": form})


class ListUnits(ListView):
    model = school_models.UnitModel
    template_name = "admin/units/index.html"
    context_object_name = "units"


class AddUnit(View):
    form_class = forms.AddUnitForm
    template_name = "admin/units/create.html"

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


class UnitDetailView(View):
    template_name = "admin/units/detail.html"

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
        context = {"unit": instance, "amounts": amounts, "otp": False}
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


class ListInvoices(ListView):
    model = payment_models.Invoice
    template_name = "admin/payments/invoices.html"
    context_object_name = "invoices"


class ListTransactions(ListView):
    model = payment_models.Transaction
    template_name = "admin/payments/transactions.html"
    context_object_name = "transactions"


class ListCurrentSubscription(ListView):
    model = payment_models.Subscription
    template_name = "admin/subscriptions/index.html"
    context_object_name = "subscriptions"

    def get_context_data(self, *, object_list=None, **kwargs):
        qs = payment_models.Subscription.objects.filter(status="ACTIVE")
        return {"subscriptions": qs, "status": "Active"}


class ListExpiredSubscriptions(ListView):
    model = payment_models.Subscription
    template_name = "admin/subscriptions/index.html"
    context_object_name = "subscriptions"

    def get_context_data(self, *, object_list=None, **kwargs):
        qs = payment_models.Subscription.objects.filter(status="EXPIRED")
        return {"subscriptions": qs, "status": "Expired"}


class ListRevokedSubscriptions(ListView):
    model = payment_models.Subscription
    template_name = "admin/subscriptions/index.html"
    context_object_name = "subscriptions"

    def get_context_data(self, *, object_list=None, **kwargs):
        qs = payment_models.Subscription.objects.filter(status="REVOKED")
        return {"subscriptions": qs, "status": "Revoked"}
