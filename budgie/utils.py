from markupsafe import Markup
from datetime import datetime
from pytz import timezone
from .config import settings


def mark_safe(value):
    return Markup(value)


def now():
    return datetime.now(timezone(settings.TIMEZONE))
