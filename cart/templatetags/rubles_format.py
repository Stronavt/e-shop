from django import template

register = template.Library()

@register.filter
def rubles_format(value):
    if isinstance(value, (int, float)):
        return '{:,.0f}'.format(value).replace(',', ' ')
    return value