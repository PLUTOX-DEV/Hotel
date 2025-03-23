from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import RoomType, Room, Guest, Booking, Payment , Contact , Profile, Review , Discount

@admin.register(Review)
class ReviewAdminClass(ModelAdmin):
    pass
@admin.register(Profile)
class ProfileAdminClass(ModelAdmin):
    pass
@admin.register(Room)
class RoomAdminClass(ModelAdmin):
    pass
@admin.register(RoomType)
class RoomtypeAdminClass(ModelAdmin):
    pass
@admin.register(Guest)
class GuestAdminClass(ModelAdmin):
    pass
@admin.register(Booking)
class bookingAdminClass(ModelAdmin):
        search_fields = ['booking_uid']  
@admin.register(Payment)
class PaymentAdminClass(ModelAdmin):
    pass
@admin.register(Contact)
class ContactAdminClass(ModelAdmin):
    pass
@admin.register(Discount)
class DiscountAdminClass(ModelAdmin):
    pass