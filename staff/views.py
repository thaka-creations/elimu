from django.shortcuts import render
from django.views import View


# Create your views here.
class Admin(View):
    template_name = "admin/index.html"

    def get(self, request):
        return render(request, self.template_name)
