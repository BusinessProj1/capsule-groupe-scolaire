"""
WSGI config for capsule_project project.

It exposes the WSGI callable as a module-level variable named ``application``.
Vercel requires the variable to be named ``app``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capsule_project.settings')

application = get_wsgi_application()
app = application  # Vercel looks for `app`
