from celery import shared_task
from django.contrib.sessions.models import Session
from .models import Order
import datetime
from travel_site.views import update_available_seats


# @shared_task(bind=True)
# def clear_cart(self):
#     print('TEST')
#     return 'DONE'

@shared_task(bind=True)
def clear_cart(self):
    sessions = Session.objects.all()
    orders = Order.objects.all()
    for session in sessions:
        data = session.get_decoded()
        # Очищаем данные
        if data.get('cart', False):
            print(data.get('cart', False))
            time_cart = datetime.datetime.fromisoformat(data['cart']['create_time'])
            print(time_cart)
            print((time_cart + datetime.timedelta(minutes=30) - datetime.datetime.now()))
            if (time_cart + datetime.timedelta(minutes=30) - datetime.datetime.now()).total_seconds() < 0:
                tours = data['cart']['tours']
                for tour in tours.values():
                    update_available_seats(tour['id'], 'delete_product', tour['count'])
                data.pop('cart', None)
                session.session_data = data
                session.save()
    for book in orders:
        if (book.date_created.date() < datetime.datetime.now().date()) and (book.date_created.time() < datetime.datetime.now().time()) and book.status:
            book.delete()