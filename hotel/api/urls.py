from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rooms', views.RoomViewSet)
router.register(r'bookings', views.BookingViewSet)
router.register(r'guests', views.GuestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]