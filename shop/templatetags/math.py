from django import template

register = template.Library()


@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    return str(int(qty) * float(unit_price.split(" ")[0])).replace(".", ",") + " руб."
