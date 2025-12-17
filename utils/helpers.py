from datetime import datetime

def format_datetime(dt, format='%d/%m/%Y %H:%M'):
    if dt is None:
        return '-'
    return dt.strftime(format)

def time_ago(dt):
    if dt is None:
        return '-'
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'À l\'instant'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'Il y a {minutes} min'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'Il y a {hours}h'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'Il y a {days}j'
    else:
        return dt.strftime('%d/%m/%Y')

def truncate(text, length=100):
    if text is None:
        return ''
    if len(text) <= length:
        return text
    return text[:length] + '...'
