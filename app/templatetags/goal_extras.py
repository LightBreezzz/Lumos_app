from django import template
register = template.Library()

@register.filter
def duration(td):
    if not td:
        return '0ч'
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}ч {minutes}м"
    elif minutes:
        return f"{minutes}м {seconds}с"
    else:
        return f"{seconds}с" 