import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frinat.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Config')

from configurations.wsgi import get_wsgi_application
application = get_wsgi_application()
