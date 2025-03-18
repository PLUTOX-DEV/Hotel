from django.urls import path
from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path('room-list', views.room_list, name='room_list'),
    path('room/<int:room_id>/', views.room_details, name='room_details'),
    path('rooms/search/', views.room_list, name='room_search'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name="booking_confirmation"),
    path('blog/',views.blog, name="blog"),
    path('contact/' , views.contact, name="contact"),
    
]
