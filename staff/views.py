import logging

import requests
import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from threading import Thread
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.views import View
from django.conf import settings
from django.views.generic import ListView
from school import models as school_models
from school.utils import video_util
from payments import models as payment_models
from staff import forms, util
from django.contrib.auth.mixins import UserPassesTestMixin
from users import models as user_models
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

CALLBACK_URL = settings.SERVICES_URLS['callback_url']
password_manager = util.PasswordManager()
service_manager = util.ServiceManager()


class AdminMixin(UserPassesTestMixin, View):
    def test_func(self):
        if self.request.user.is_anonymous:
            raise PermissionDenied
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
        data = form.data
        video_id = data['file']
        unit_id = data['subtopic']
        try:
            video_instance = school_models.VideoModel.objects.get(videoid=video_id)
        except school_models.VideoModel.DoesNotExist:
            return HttpResponseBadRequest

        try:
            unit = school_models.UnitModel.objects.get(id=unit_id)
        except school_models.UnitModel.DoesNotExist:
            return HttpResponseBadRequest

        video_instance.unit = unit
        video_instance.index = data['index']
        video_instance.label = data['label']
        video_instance.save()
        messages.success(request, _("Video added successfully"))

        return redirect("/admin/videos/add-video")


@csrf_exempt
def add_videoid(request):
    url = "https://dev.vdocipher.com/api/videos"
    headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    name = body['name']
    querystring = {"title": name}
    resp = requests.request("PUT", url, headers=headers, params=querystring)
    upload_info = resp.json()
    school_models.VideoModel.objects.create(videoid=upload_info['videoId'])
    return JsonResponse(upload_info)


@csrf_exempt
def cover_videoid(request):
    url = "https://dev.vdocipher.com/api/videos"
    headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    name = body['name']
    video_instance = school_models.CoverVideo.objects.create(label="cover")
    try:
        name_list = name.split(".")
        vid_name = str(video_instance.id) + "." + name_list[-1]
    except Exception as e:
        vid_name = name
    querystring = {"title": vid_name}
    resp = requests.request("PUT", url, headers=headers, params=querystring)
    upload_info = resp.json()
    video_instance.videoid = upload_info['videoId']
    video_instance.save()
    return JsonResponse(upload_info)


class CoverVideo(AdminMixin):
    template_name = "admin/videos/cover.html"
    form_class = forms.CoverVideoForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        print("Testing")
        print(request.__dict__)
        video_instance = school_models.CoverVideo.objects.create(label="cover")
        vid = request.FILES['file']
        try:
            name_list = vid.name.split(".")
            vid_name = str(video_instance.id) + "." + name_list[-1]
        except Exception as e:
            vid_name = vid.name

        fs = FileSystemStorage()
        file = fs.save(vid_name, vid)
        file_url = fs.url(file)

        filepath = "media/" + os.path.basename(file_url)
        Thread(target=video_util.upload_video, args=(filepath, vid_name, video_instance)).start()
        return JsonResponse({"message": "Uploaded successfully"})


class ListSubjects(AdminMixin, ListView):
    model = school_models.SubjectModel
    template_name = "admin/subjects/index.html"
    context_object_name = "subjects"
    login_url = "/login"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddSubjectForm
        return context


@csrf_exempt
@require_http_methods(["POST"])
def delete_subject(request):
    body_unicode = request.body.decode('utf-8')
    try:
        instance = school_models.SubjectModel.objects.get(id=body_unicode)
    except school_models.FormModel.DoesNotExist:
        return HttpResponseBadRequest

    instance.delete()
    return JsonResponse({"message": "Successful"})


class UpdateSubject(AdminMixin, View):
    def post(self, request):
        data = request.POST
        pk = data['id']
        name = data['name']
        try:
            instance = school_models.SubjectModel.objects.get(id=pk)
        except school_models.SubjectModel.DoesNotExist:
            return redirect("/admin/subjects/" + pk)
        instance.name = name
        instance.save()
        return redirect("/admin/subjects/" + pk)


class UpdateTopic(AdminMixin, View):
    def post(self, request):
        data = request.POST
        pk = data['id']
        name = data['name']
        subject_id = data['subject']
        form_id = data['form_id']

        try:
            form_inst = school_models.FormModel.objects.get(id=form_id)
        except school_models.FormModel.DoesNotExist:
            return redirect("/admin/topics/view?unit=" + pk)

        try:
            subject = school_models.SubjectModel.objects.get(id=subject_id)
        except school_models.SubjectModel.DoesNotExist:
            return redirect("/admin/topics/view?unit=" + pk)

        try:
            instance = school_models.TopicModel.objects.get(id=pk)
        except school_models.TopicModel.DoesNotExist:
            return redirect("/admin/topics/view?unit=" + pk)

        instance.name = name
        instance.subject = subject
        instance.form = form_inst
        instance.save()
        return redirect("/admin/topics/view?unit=" + pk)


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


class RetrieveForm(AdminMixin):
    template_name = "admin/forms/detail.html"

    def get(self, request, pk):
        try:
            instance = school_models.FormModel.objects.get(id=pk)
        except school_models.FormModel.DoesNotExist:
            return redirect("/admin")
        subjects = school_models.SubjectModel.objects.all()
        form = forms.AddFormAmount
        amounts = payment_models.FormAmount.objects.all()
        context = {"form_inst": instance, "queryset": subjects, "form": form, "amounts": amounts}
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


class UpdateForm(AdminMixin, View):
    def post(self, request):
        data = request.POST
        pk = data['id']
        name = data['name']
        try:
            instance = school_models.FormModel.objects.get(id=pk)
        except school_models.FormModel.DoesNotExist:
            return redirect("/admin/forms/" + pk)
        instance.name = name
        instance.save()
        return redirect("/admin/forms/" + pk)


@csrf_exempt
@require_http_methods(["POST"])
def delete_form(request):
    body_unicode = request.body.decode('utf-8')
    try:
        instance = school_models.FormModel.objects.get(id=body_unicode)
    except school_models.FormModel.DoesNotExist:
        return HttpResponseBadRequest

    instance.delete()
    return JsonResponse({"message": "Successful"})


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


class ListTopics(AdminMixin, ListView):
    model = school_models.TopicModel
    template_name = "admin/topics/index.html"
    context_object_name = "topics"
    login_url = "/login"


@csrf_exempt
@require_http_methods(["POST"])
def delete_topic(request):
    body_unicode = request.body.decode('utf-8')
    try:
        instance = school_models.TopicModel.objects.get(id=body_unicode)
    except school_models.TopicModel.DoesNotExist:
        return HttpResponseBadRequest

    instance.delete()
    return JsonResponse({"message": "Successful"})


class AddTopic(AdminMixin):
    form_class = forms.AddTopicForm
    template_name = "admin/topics/create.html"
    login_url = "/login"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            school_models.TopicModel.objects.create(**data)
            context = {"details": "Topic added successfully"}
            return redirect("/admin/topics", context=context)
        return render(request, self.template_name, {"form": form})


class TopicDetailView(AdminMixin):
    template_name = "admin/topics/detail.html"
    login_url = "/login"

    def get(self, request):
        topic = request.GET.get("topic", False)

        if not topic:
            return redirect("/admin/topics")

        try:
            instance = school_models.TopicModel.objects.get(id=topic)
        except school_models.TopicModel.DoesNotExist:
            return redirect("/admin/topics")

        # videos = instance.videos.all()
        amounts = payment_models.TopicAmount.objects.filter(topic=instance)
        subjects = school_models.SubjectModel.objects.all()
        form_qs = school_models.FormModel.objects.all()
        form = forms.AddTopicAmount
        context = {"topic": instance, "amounts": amounts, "otp": False, "form": form, "form_qs": form_qs,
                   "subjects": subjects}
        # if not videos.exists:
        #     return render(request, self.template_name, context)

        # video_id = videos.first()
        # url = CALLBACK_URL + 'video/get-video-otp'
        # headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}
        #
        # resp = requests.get(url, params={"video_id": video_id}, headers=headers)
        # res = resp.json()
        #
        # if not resp:
        #     return render(request, self.template_name, context)

        # otp = res['otp']
        # playback = res['playbackInfo']
        # context.update({"otp": otp, "playback": playback})
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


@csrf_exempt
def delete_topic_amount(request):
    body_unicode = request.body.decode('utf-8')
    try:
        instance = payment_models.TopicAmount.objects.get(id=body_unicode)
    except payment_models.TopicAmount.DoesNotExist:
        return HttpResponseBadRequest

    instance.delete()
    return JsonResponse({"message": "Successful"})


class AddTopicAmountView(AdminMixin):
    form_class = forms.AddTopicAmount
    template_name = "admin/topics/detail.html"

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            topic = data['topic']
            payment_models.TopicAmount.objects.create(**data)
            context = {"details": "Topic Amount added successfully"}
            return redirect("/admin/topics/view?topic={}".format(topic.id))
        return redirect("/admin")


@csrf_exempt
def delete_subtopic_amount(request):
    body_unicode = request.body.decode('utf-8')
    try:
        instance = payment_models.UnitAmount.objects.get(id=body_unicode)
    except payment_models.UnitAmount.DoesNotExist:
        return HttpResponseBadRequest

    instance.delete()
    return JsonResponse({"message": "Successful"})


class AddSubtopicAmountView(AdminMixin):
    form_class = forms.AddUnitAmount

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            subtopic = data['unit']
            try:
                payment_models.UnitAmount.objects.create(**data)
            except Exception as e:
                logging.error(e)
                return HttpResponseBadRequest
            return redirect("/admin/subtopics/{}".format(subtopic.pk))
        return redirect("/admin")


@csrf_exempt
def delete_subject_amount(request):
    body_unicode = request.body.decode('utf-8')
    try:
        instance = payment_models.SubjectAmount.objects.get(id=body_unicode)
    except payment_models.SubjectAmount.DoesNotExist:
        return HttpResponseBadRequest

    instance.delete()
    return JsonResponse({"message": "Successful"})


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


@csrf_exempt
def delete_form_amount(request):
    body_unicode = request.body.decode('utf-8')
    try:
        instance = payment_models.FormAmount.objects.get(id=body_unicode)
    except payment_models.FormAmount.DoesNotExist:
        return HttpResponseBadRequest

    instance.delete()
    return JsonResponse({"message": "Successful"})


class AddFormAmountView(AdminMixin):
    form_class = forms.AddFormAmount

    def post(self, request):
        form = self.form_class(request.POST)
        form_ = request.POST["form"]
        url = '/admin/forms/{}'.format(form_)

        if form.is_valid():
            data = form.cleaned_data
            payment_models.FormAmount.objects.create(**data)
            context = {"details": "Form Amount added successfully"}
            return redirect(url)
        return redirect(url)


class ListAgents(AdminMixin, ListView):
    model = user_models.User
    template_name = "admin/users/agents/index.html"
    context_object_name = "agents"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddAgent
        return context

    def get_queryset(self):
        return super().get_queryset().filter(is_agent=True)


class AgentDetails(AdminMixin, View):
    template_name = "admin/users/agents/detail.html"

    def get(self, request, pk):
        try:
            agent = user_models.User.objects.get(id=pk)
        except user_models.User.DoesNotExist:
            return redirect("/admin")
        users = agent.agent_user.subscribers.all()
        invoices = payment_models.Invoice.objects.filter(user__in=users)
        start_date = datetime.now().replace(day=1)
        end_date = start_date + relativedelta(months=1)
        default_invoices = invoices.filter(commission__isnull=False, transaction_date__gte=start_date,
                                           transaction_date__lte=end_date)
        commission = 0
        if default_invoices.exists():
            for invoice in default_invoices:
                commission += invoice.commission

        context = {"users": users, "invoices": invoices, "agent": agent, "start_date": start_date.strftime("%Y-%m-%d"),
                   "end_date": end_date.strftime("%Y-%m-%d"), "commission": commission}
        return render(request, self.template_name, context)

    def post(self, request, pk):
        data = request.POST
        agent_id = data['agent']
        format_ = '%Y-%m-%d'
        date_from = datetime.strptime(data['date_from'], format_)
        date_to = datetime.strptime(data['date_to'], format_)

        try:
            agent = user_models.User.objects.get(id=agent_id)
        except user_models.Agent.DoesNotExist:
            return JsonResponse({"message": "invalid agent"})

        users = list(agent.agent_user.subscribers.values_list("id", flat=True))
        invoices = payment_models.Invoice.objects.filter(
            user__id__in=users, commission__isnull=False, transaction_date__date__gte=date_from,
            transaction_date__date__lte=date_to)

        commission = 0
        if invoices.exists():
            for invoice in invoices:
                commission += invoice.commission
        return JsonResponse({"commission": commission})


class AddAgent(AdminMixin):
    form_class = forms.AddAgent
    template_name = "admin/users/agents/index.html"

    def post(self, request):
        form = self.form_class(request.POST)
        qs = user_models.User.objects.filter(is_agent=True)

        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            name = data['name']
            code = data['code']

            with transaction.atomic():
                user = user_models.User.objects.create(
                    name=name, username=email, is_agent=True, email_verified=True)

                user_models.Agent.objects.create(
                    user=user,
                    code=code
                )

                password = password_manager.generate_password()
                user.set_password(password)
                user.save()

                # send email
                try:
                    service_manager.send_email(
                        subject="TAFA AGENT REGISTRATION",
                        message="Dear agent, your Tafa account password is %s" % password,
                        recipient=email
                    )
                except Exception as e:
                    logging.error(e)
                    return redirect("/admin/agents", {"agents": qs, "form": form, "message": "An error occurred. Try "
                                                                                             "again later"})

                context = {"details": "Agent added successfully", "agents": qs, "form": form}
                return redirect("/admin/agents", context=context)

        return redirect("/admin/agents", {"agents": qs, "form": form})


class ListUsers(AdminMixin, ListView):
    model = user_models.User
    template_name = "admin/users/index.html"
    context_object_name = "users"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return super().get_queryset().filter(is_admin=False, is_staff=False, is_agent=False)


class ListAgentCommission(AdminMixin, ListView):
    model = payment_models.Commission
    template_name = "admin/payments/commission.html"
    context_object_name = "commissions"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddCommissionForm
        return context


class AddAgentCommission(AdminMixin):
    form_class = forms.AddCommissionForm

    def post(self, request):
        form = self.form_class(request.POST)
        commissions = payment_models.Commission.objects.all()
        context = {"commissions": commissions, "form": form}
        if form.is_valid():
            data = form.cleaned_data
            payment_models.Commission.objects.create(**data)
            context.update({"message": "Commission added successfully"})

        else:
            context.update({"message": "Invalid data"})

        return redirect("/admin/payments/agent-commission", context)


@csrf_exempt
def delete_commission(request):
    body_unicode = request.body.decode('utf-8')
    try:
        instance = payment_models.Commission.objects.get(id=body_unicode)
    except payment_models.Commission.DoesNotExist:
        return HttpResponseBadRequest

    instance.delete()
    return JsonResponse({"message": "Successful"})


class SubtopicView(AdminMixin):
    template_name = "admin/subtopics/index.html"
    form_class = forms.AddSubtopicForm

    def get(self, request):
        subtopics = school_models.UnitModel.objects.all()
        context = {"subtopics": subtopics, "form": self.form_class}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            school_models.UnitModel.objects.create(**data)

        return redirect("/admin/subtopics")


class RetrieveUpdateSubtopic(AdminMixin):
    template_name = "admin/subtopics/detail.html"
    form_class = forms.AddSubtopicForm
    amount_form_class = forms.AddUnitAmount

    def get(self, request, pk):
        try:
            instance = school_models.UnitModel.objects.get(id=pk)
        except school_models.UnitModel.DoesNotExist:
            return Http404

        amounts = payment_models.UnitAmount.objects.filter(unit=instance)
        videos = instance.videos.all()
        context = {"subtopic": instance, "amounts": amounts, "amount_form": self.amount_form_class,
                   "form": self.form_class(initial={"name": instance.name,
                                                    "topic": instance.topic})}

        if videos.exists():
            video_id = videos.first()
            url = CALLBACK_URL + 'video/get-video-otp'
            headers = {"Authorization": "Apisecret " + settings.VDOCIPHER_SECRET}

            resp = requests.get(url, params={"video_id": video_id}, headers=headers)
            res = resp.json()

            if resp:
                otp = res['otp']
                playback = res['playbackInfo']
                context.update({"otp": otp, "playback": playback})

        return render(request, self.template_name, context)

    def post(self, request, pk):
        try:
            instance = school_models.UnitModel.objects.get(id=pk)
        except school_models.UnitModel.DoesNotExist:
            raise Http404("Subtopic does not exist")

        form = self.form_class(request.POST, instance)
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            topic = data['topic']
            instance.name = name
            instance.topic = topic
            instance.save()

        return redirect("/admin/subtopics/{}".format(pk))


@csrf_exempt
def delete_subtopic(request):
    body_unicode = request.body.decode('utf-8')
    try:
        instance = school_models.UnitModel.objects.get(id=body_unicode)
    except school_models.UnitModel.DoesNotExist:
        return HttpResponseBadRequest

    instance.delete()
    return JsonResponse({"message": "Successful"})
