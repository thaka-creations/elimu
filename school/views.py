import requests
import uuid
from word2number import w2n
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.views import View
from school import models as school_models
from payments import models as payment_models

CALLBACK_URL = settings.SERVICES_URLS['callback_url']


class FormView(LoginRequiredMixin, View):
    template_name = 'school/form.html'
    login_url = "/login"

    def get(self, request, pk):
        try:
            inst = school_models.FormModel.objects.get(pk=pk)
        except school_models.FormModel.DoesNotExist:
            return redirect("/")

        try:
            val = inst.name.split(' ')[1]
            num = w2n.word_to_num(val)
        except Exception as e:
            return redirect("/")

        qs = school_models.SubjectModel.objects. \
            filter(form_units__videos__isnull=False, form_units__form=inst).distinct()
        amounts = payment_models.FormAmount.objects.filter(form=inst)
        context = {"subjects": qs, "instance": inst, "num": num, "amounts": amounts}
        return render(request, self.template_name, context=context)


class SubjectView(LoginRequiredMixin, View):
    template_name = "school/subjects/index.html"
    login_url = "/login"

    def get(self, request, pk):
        try:
            instance = school_models.SubjectModel.objects.get(pk=pk)
        except school_models.SubjectModel.DoesNotExist:
            return redirect("/")

        units = school_models.UnitModel.objects.filter(subject=instance)
        if units.exists():
            form = units.first().form
        else:
            return redirect("/")
        context = {"units": units, "subject": instance, "form": form, "user": request.user}
        return render(request, self.template_name, context=context)


class UnitView(LoginRequiredMixin, View):
    template_name = "school/subjects/units/index.html"
    login_url = "/login"

    def get(self, request, pk):
        videoid = request.GET.get("videoid", False)
        try:
            instance = school_models.UnitModel.objects.get(pk=pk)
        except school_models.UnitModel.DoesNotExist:
            return redirect("/")

        qs = school_models.VideoModel.objects.filter(unit=instance)

        if not qs.exists():
            return redirect("/")

        if videoid:
            try:
                uuid.UUID(videoid)
            except ValueError:
                return redirect("/")

            try:
                video_id = school_models.VideoModel.objects.get(id=videoid).videoid
            except school_models.VideoModel.DoesNotExist:
                return redirect("/")
        else:
            video_id = qs.first().videoid
        url = CALLBACK_URL + 'video/get-video-otp'
        headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}

        resp = requests.get(url, params={"video_id": video_id}, headers=headers)
        res = resp.json()
        if not res:
            return redirect("/")
        else:
            otp = res['otp']
            playback = res['playbackInfo']

        context = {"videos": qs, 'unit': instance, 'otp': otp, 'playback': playback, 'video_id': video_id}
        return render(request, self.template_name, context=context)
