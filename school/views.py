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

