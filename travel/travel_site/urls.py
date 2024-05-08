from django.urls import path
from .views import *

app_name = 'travel_site'


urlpatterns = [
    path('location_detail/<slug:location_detail_slug>/', location_detail, name='location_detail'),
    path('tour_detail/<slug:tour_detail_slug>/', tour_detail, name='tour_detail'),
    path('blogs/<slug:blog_detail_slug>/', blog_detail, name='blog_detail'),
    path('where_to_go/', where_to_go, name='where_to_go'),
    path('rental/', rental, name='rental'),
    path('go_group/', go_group, name='go_group'),
    path('profile/', profile, name='profile'),
    path('blogs/', blog, name='blogs'),
    path('logout/', user_logout, name='user_logout'),
    path('cart/', cart, name='cart'),
    path('reset/<uidb64>/<token>/<str:mail>/', password_reset, name='password_reset'),
    path('activate/<uidb64>/<token>/<str:mail>/', email_activate, name='email_activate'),
    path('', home, name='home'),
    path('question_description_fetch/', question_description_fetch),
    path('cart_fetch/', cart_fetch),
    path('where_to_go_fetch/', where_to_go_fetch),
]
