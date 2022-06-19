from django.views import View
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
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


class CheckFormSubscriptionStatus(View):
    def post(self, request):
        payload = request.POST
        form_id = payload.get("form", False)

        if not form_id:
            return HttpResponseBadRequest("Form required")

        try:
            form = school_models.FormModel.objects.get(id=form_id)
        except school_models.FormModel.DoesNotExist:
            return HttpResponseBadRequest("Form does not exist")

        units = school_models.UnitModel.objects.filter(form=form).values_list("id", flat=True)

        if not units:
            return HttpResponseBadRequest("Form does not have units")

        qs = payment_models.Subscription.objects.filter(
            user=self.request.user, status="ACTIVE", invoiceunits__unit_id__in=units
        )
        if not qs.exists():
            return HttpResponseBadRequest("Not subscribed")

        if qs.count() != len(units):
            return HttpResponseBadRequest("Not subscribed")

        return JsonResponse({"details": "Subscribed"})
