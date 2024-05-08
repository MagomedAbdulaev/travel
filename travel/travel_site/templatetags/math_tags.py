from django import template

register = template.Library()


@register.filter(name='get_subtract')
def get_subtract(value, arg):
    return value - arg


@register.filter(name='get_divide')
def get_divide(value, arg):
    return value % arg
