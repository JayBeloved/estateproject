from django import template
from ..models import Residents

register = template.Library()


@register.filter(name='get_res_id', is_safe=True)
def get_res_id(resident_code):
    res_id = Residents.objects.get(resident_code=resident_code).id

    return res_id
