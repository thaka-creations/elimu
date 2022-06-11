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
