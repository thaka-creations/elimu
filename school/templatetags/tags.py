import uuid
from django import template
from datetime import datetime
from school import models as school_models
from users import models as user_models
from payments import models as payment_models

register = template.Library()


@register.simple_tag(name="current_year")
def current_year():
    return datetime.now().year


@register.simple_tag(name="subject_video_count")
def subject_video_count(subject):
    return school_models.VideoModel.objects.filter(unit__topic__subject=subject).count()


@register.simple_tag(name="form_video_count")
def form_video_count(inst):
    return school_models.VideoModel.objects.filter(unit__topic__form=inst).count()


@register.simple_tag(name="topic_video_count")
def topic_video_count(inst):
    return school_models.VideoModel.objects.filter(unit__topic__id=inst).count()


@register.simple_tag(name="get_unit")
def get_unit(pk):
    try:
        uuid.UUID(str(pk))
    except ValueError:
        return None
    try:
        unit = user_models.User.objects.get(id=pk)
    except user_models.User.DoesNotExist:
        return None
    return unit.name


@register.simple_tag(name="get_invoice_units")
def get_invoice_units(invoice):
    qs = payment_models.InvoiceUnit.objects.filter(invoice=invoice)

    if not qs.exists():
        return None

    units = [i.unit.name for i in qs]
    units = " ,".join(units)
    return units
