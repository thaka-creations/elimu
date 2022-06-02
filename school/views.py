from word2number import w2n
from django.shortcuts import render, redirect
from django.views import View
from school import models as school_models


class FormView(View):
    template_name = 'school/form.html'

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

        qs = school_models.SubjectModel.objects.all()
        context = {"subjects": qs, "instance": inst, "num": num}
        return render(request, self.template_name, context=context)

class SubjectView(View):
    template_name = "school/subjects/index.html"

    def get(self, request, pk):
        try:
            instance = school_models.SubjectModel.objects.get(pk=pk)
        except school_models.SubjectModel.DoesNotExist:
            return redirect("/")

        units = school_models.UnitModel.objects.filter(subject=instance)
        context = {"units": units, "subject": instance}
        return render(request, self.template_name, context=context)     

class UnitView(View): 
    template_name = "school/subjects/units/index.html"

    def get(self, request, pk):
        try:
            instance = school_models.UnitModel.objects.get(pk=pk)
        except school_models.UnitModel.DoesNotExist:
            return redirect("/")

        qs = school_models.VideoModel.objects.filter(unit=instance)
        context = {"videos": qs}
        return render(request, self.template_name, context=context)



