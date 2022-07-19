import requests
import uuid
import json
from word2number import w2n
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, Http404, JsonResponse
from django.core.exceptions import ValidationError
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
        except (school_models.FormModel.DoesNotExist, ValidationError):
            raise Http404("Form does not exist")

        try:
            val = inst.name.split(' ')[1]
            num = w2n.word_to_num(val)
        except Exception as e:
            return HttpResponseBadRequest

        # qs = school_models.SubjectModel.objects. \
        #     filter(form_units__videos__isnull=False, form_units__form=inst).distinct()
        qs = school_models.SubjectModel.objects.all()
        amounts = payment_models.FormAmount.objects.filter(form=inst)
        context = {"subjects": qs, "instance": inst, "num": num, "amounts": amounts, "subscribed": False}
        # check status
        units = school_models.UnitModel.objects.filter(topic__form=inst).values_list("id", flat=True)
        if units:
            subscription_qs = payment_models.Subscription.objects.filter(
                user=self.request.user, status="ACTIVE", invoiceunits__unit_id__in=units
            )
            if subscription_qs:
                if len(units) == qs.count():
                    context.update({"subscribed": True})
        return render(request, self.template_name, context=context)


class SubjectView(LoginRequiredMixin, View):
    template_name = "school/subjects/index.html"
    login_url = "/login"

    def get(self, request, slug, pk):
        try:
            instance = school_models.SubjectModel.objects.get(pk=pk)
        except (school_models.SubjectModel.DoesNotExist, ValidationError):
            raise Http404("Subject does not exist")

        topics = school_models.TopicModel.objects.filter(subject=instance)

        try:
            form = school_models.FormModel.objects.get(name__iexact=slug.replace("-", " "))
        except (school_models.FormModel.DoesNotExist, school_models.FormModel.MultipleObjectsReturned, ValidationError):
            raise Http404("Form does not exist")
        amounts = payment_models.SubjectAmount.objects.filter(subject=instance, form=form)
        context = {"topics": topics, "subject": instance, "form": form, "user": request.user, "amounts": amounts}
        return render(request, self.template_name, context=context)


class TopicView(LoginRequiredMixin, View):
    template_name = "school/subjects/topics/index.html"
    login_url = "/login"

    def get(self, request, slug, subject, pk):
        try:
            form_instance = school_models.FormModel.objects.get(name__iexact=slug.replace("-", " "))
        except (school_models.FormModel.DoesNotExist, school_models.FormModel.MultipleObjectsReturned, ValidationError):
            raise Http404("Form does not exist")

        try:
            subject = school_models.SubjectModel.objects.get(name__iexact=subject.replace("_", ""))
        except (school_models.SubjectModel.DoesNotExist, school_models.SubjectModel.MultipleObjectsReturned,
                ValidationError):
            raise Http404("Subject does not exist")

        try:
            instance = school_models.TopicModel.objects.get(id=pk)
        except (school_models.TopicModel.DoesNotExist, ValidationError):
            raise Http404("Topic does not exist")

        amounts = payment_models.TopicAmount.objects.filter(topic=instance)
        context = {"topic": instance, "subject": subject, "form": form_instance, "amounts": amounts}
        return render(request, self.template_name, context=context)


class UnitView(LoginRequiredMixin, View):
    template_name = "school/subjects/units/index.html"
    login_url = "/login"

    def get(self, request, pk):
        videoid = request.GET.get("videoid", False)
        try:
            instance = school_models.UnitModel.objects.get(pk=pk)
        except (school_models.UnitModel.DoesNotExist, ValidationError):
            raise Http404("Unit does not exist")

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
        url = 'https://dev.vdocipher.com/api/videos/{}/otp'.format(video_id)
        payload = json.dumps({
            "annotate": json.dumps([
                {'type': 'text', 'text': request.user.username, 'alpha': '0.60', 'color': '0xFF0000', 'size': '15',
                 'interval': '5000', 'x': '300', 'y': '20'}
            ])
        })
        headers = {
            'Authorization': "Apisecret " + settings.VDOCIPHER_SECRET,
            'Content-Type': "application/json",
            'Accept': "application/json"
        }

        resp = requests.request("POST", url, data=payload, headers=headers).json()
        if not resp:
            return redirect("/")
        else:
            otp = resp['otp']
            playback = resp['playbackInfo']

        context = {"videos": qs, 'unit': instance, 'otp': otp, 'playback': playback, 'video_id': video_id}
        return render(request, self.template_name, context=context)


class CartView(LoginRequiredMixin, View):
    template_name = "school/cart/index.html"
    login_url = "/login"

    def get(self, request):
        pass

    def post(self, request):
        data = request.body.decode('utf-8')
        _type = data['type']
        request_id = data['request_id']
        amount = data['amount']
        _form = data['form']
        cart = request.session['cart']
        if _type == "subject":
            try:
                instance = school_models.SubjectModel.objects.get(id=request_id)
            except school_models.SubjectModel.DoesNotExist:
                return JsonResponse({"error": False})
            cart_items = cart['subject']
            subjects = cart_items['items']

            if str(instance.id) in subjects:
                pass
            else:
                if len(subjects) >= 1:
                    subjects.append(str(instance.pk))
                else:
                    {"item": str(instance.pk), "amount": amount, "form": instance.form.name}

        return JsonResponse({"details": "test"})
