from django import template

register = template.Library()


@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    total = int(qty) * unit_price
    if int(total) == total:
        total = int(total)
    return str(total).replace(".", ",")
