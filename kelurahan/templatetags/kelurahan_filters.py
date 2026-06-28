from django import template

register = template.Library()

@register.filter(name='currency')
def currency(value):
    try:
        value = float(value)
        return f"Rp {value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return value

@register.filter(name='split')
def split(value, key):
    """
    Returns the value turned into a list.
    """
    try:
        return value.split(key)
    except Exception:
        return value
