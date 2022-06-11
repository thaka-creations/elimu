from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from school import models as school_models
from staff import forms


# Create your views here.
class Admin(View):
    template_name = "admin/index.html"

    def get(self, request):
        return render(request, self.template_name)


class ListVideos(ListView):
    model = school_models.VideoModel
    template_name = "admin/videos/list.html"


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


class AddSubject(View):
    form_class = forms.AddSubjectForm
    template_name = "admin/subjects/create.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            school_models.SubjectModel.objects.create(**data)
            context = {"details": "Subject added successfully"}
            return redirect("/admin/subjects", context=context)
        return render(request, self.template_name, {"form": form})


class ListForm(ListView):
    model = school_models.FormModel
    template_name = "admin/forms/index.html"


class AddForm(View):
    form_class = forms.AddForm
    template_name = "admin/forms/create.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            school_models.FormModel.objects.create(**data)
            context = {"details": "Form added successfully"}
            return redirect("/admin/form", context=context)
        return render(request, self.template_name, {"form": form})


class ListUnits(ListView):
    model = school_models.UnitModel
    template_name = "admin/units/index.html"


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
