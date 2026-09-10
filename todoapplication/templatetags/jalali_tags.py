from datetime import datetime
import jdatetime
from django import template

register = template.Library()

@register.filter(name="to_jalali")
def to_jalali(value):
    if not value:
        return ""

    try:
        if isinstance(value, datetime):
            return jdatetime.datetime.fromgregorian(datetime=value).strftime("%Y/%m/%d")
        return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")
    except (TypeError, ValueError, AttributeError):
        return ""
