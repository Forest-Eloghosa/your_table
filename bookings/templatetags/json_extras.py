from django import template
from django.utils.html import escape
import json

register = template.Library()


@register.filter(is_safe=False)
def pretty_json(value):
    """Pretty-print a Python dict/JSON-like value for display in templates.

    Returns a JSON-formatted string with indentation. The template will
    escape the result, so it's safe to render inside <pre>.
    """
    try:
        # If it's already a string that contains JSON, try to parse it
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except Exception:
                # not JSON, just return the escaped string
                return escape(value)
        else:
            parsed = value
        return escape(json.dumps(parsed, indent=2, ensure_ascii=False, default=str))
    except Exception:
        # Fallback: stringify and escape
        return escape(str(value))
