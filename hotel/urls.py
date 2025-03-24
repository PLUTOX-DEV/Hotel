from django.urls import path
from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path('room-list', views.room_list, name='room_list'),
    path('room/<int:room_id>/', views.room_details, name='room_details'),
    path('rooms/search/', views.room_list, name='room_search'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name="booking_confirmation"),
    path('blog/',views.blog, name="blog"),
    path('blog-details/',views.blog_details,name="blog_details"),
    path('contact/' , views.contact, name="contact"),
    path('about-us/',views.about_us, name='about-us'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
     path('newsletter-success/', views.newsletter_success, name='newsletter_success'),

    path('search/', views.search_view, name='search_view'),
    
]
