"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import multiprocessing
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

application = get_wsgi_application()
def run_schedule():
    from utils.parse_news import run_parse_all
    import schedule
    schedule.every().hour.do(run_parse_all)


proc = multiprocessing.Process(group=None, target=run_schedule,
                               name=None, args=(),
                               kwargs={}, daemon=None)

proc.start()