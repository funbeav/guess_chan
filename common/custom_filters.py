from django.template import Library

register = Library()


@register.filter
def range_int(value):
    return range(int(value))
