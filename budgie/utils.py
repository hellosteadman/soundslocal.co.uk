from markupsafe import Markup


def mark_safe(value):
    return Markup(value)
