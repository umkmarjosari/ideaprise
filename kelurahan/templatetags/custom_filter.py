from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """
    Memecah string menjadi list berdasarkan delimiter.
    Contoh: {{ "a,b,c"|split:"," }} -> ["a", "b", "c"]
    """
    if value is None:
        return []
    return value.split(delimiter)
