from django import template
from datetime import datetime
from school import models as school_models

register = template.Library()


@register.simple_tag(name="current_year")
def current_year():
    return datetime.now().year


@register.simple_tag(name="subject_video_count")
def subject_video_count(subject):
    return school_models.VideoModel.objects.filter(unit__subject=subject).count()


@register.simple_tag(name="form_video_count")
def form_video_count(inst):
    return school_models.VideoModel.objects.filter(unit__form=inst).count()
