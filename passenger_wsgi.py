import os, sys
sys.path.insert(0, '/home/m/magomed487/travel.magomed487.beget.tech/travel')
sys.path.insert(1, '/home/m/magomed487/travel.magomed487.beget.tech/djangoenv/lib/python3.11/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'travel.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()