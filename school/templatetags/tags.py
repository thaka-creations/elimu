from django import template
from datetime import datetime

register = template.Library()


@register.simple_tag(name="current_year")
def current_year():
    return datetime.now().year
