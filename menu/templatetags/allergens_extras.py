from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a comma-separated string into a list of trimmed values.

    Returns an empty list for falsy input. Leading/trailing whitespace is stripped
    and empty components are omitted.
    """
    if not value:
        return []
    try:
        parts = [p.strip() for p in value.split(delimiter)]
        return [p for p in parts if p]
    except Exception:
        return []
