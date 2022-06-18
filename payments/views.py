from django.views import View
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest,HttpResponseForbidden
from django.shortcuts import redirect, render
from payments import models as payment_models
from school import models as school_models


@require_http_methods(["GET"])
def check_status(request):
    if request.user is None:
        return HttpResponseForbidden
    request_id = request.GET.get("request_id", False)
    if request_id:
        qs = payment_models.Subscription.objects.filter(
            user=request.user, status="ACTIVE", invoiceunits__unit_id=request_id)
        if not qs.exists():
            return HttpResponseBadRequest("Not subscribed")
        else:
            try:
                unit = school_models.UnitModel.objects.get(id=request_id)
            except school_models.UnitModel.DoesNotExist:
                return redirect("/")

            # get videos
            videos = school_models.VideoModel.objects.filter(unit=unit)
            context = {"videos": videos}
            return render(request, "school/subjects/units/index.html", context)
    else:
        return redirect("/")


class SubscriptionView(View):
    def check_status(self, request):
        pass
