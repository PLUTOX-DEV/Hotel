from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import RoomType, Room, Guest, Booking, Payment , Contact , Profile, Review , Discount , News , Record
@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('room', 'rating', 'created_at')
    search_fields = ['user__username', 'room__room_number', 'rating']
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'room')  # ✅ Remove 'guest'

    def get_reviewer_name(self, obj):
        return obj.user.username if obj.user else "Guest"
    get_reviewer_name.short_description = "Reviewer Name"
    
@admin.register(Profile)
class ProfileAdminClass(ModelAdmin):
    list_display = ('user','phone_number')  # ✅ Ensure it displays relevant fields
    search_fields = ('user__username', 'phone_number ')  # ✅ Enable search
    list_filter = ('user',)  # ✅ Add filters

@admin.register(Room)
class RoomAdmin(ModelAdmin):
    list_display = ('room_number', 'get_room_type', 'get_capacity', 'get_size',  'get_price', 'is_available')
    search_fields = ['room_number', 'room_type__name',]
    list_filter = ('room_type__capacity', 'room_type__size', 'room_type__service', 'room_type__price_per_night', 'is_available')

    def get_queryset(self, request):
        """Optimize admin performance by prefetching related fields"""
        return super().get_queryset(request).select_related('room_type')

    def get_room_type(self, obj):
        return obj.room_type.name
    get_room_type.short_description = "Room Type"

    def get_capacity(self, obj):
        return obj.room_type.capacity
    get_capacity.short_description = "Capacity"

    def get_size(self, obj):
        return f"{obj.room_type.size} sqm"
    get_size.short_description = "Size"

    def get_service(self, obj):
        return obj.room_type.service
    get_service.short_description = "Service"

    def get_price(self, obj):
        return f"${obj.room_type.price_per_night}"
    get_price.short_description = "Price/Night"

@admin.register(RoomType)
class RoomtypeAdminClass(ModelAdmin):
    pass
@admin.register(Guest)
class GuestAdminClass(ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')  # ✅ Display fields
    search_fields = ('first_name', 'last_name', 'email')  # ✅ Enable search
@admin.register(Booking)
class BookingAdmin(ModelAdmin):
    list_display = ('booking_uid', 'get_booking_name', 'room', 'check_in_date', 'check_out_date', 'is_active', 'final_price')
    search_fields = ['booking_uid', 'user__username', 'guest__first_name', 'guest__last_name']
    list_filter = ('is_active', 'check_in_date', 'check_out_date')

    def get_queryset(self, request):
        """Optimize admin performance by prefetching related fields"""
        return super().get_queryset(request).select_related('user',  'room')

    def get_booking_name(self, obj):
        """Show the authenticated user's name or guest's name"""
        if obj.user:
            return obj.user.username  # Show username if user is authenticated
        elif obj.guest:
            return f"{obj.guest.first_name} {obj.guest.last_name}"  # Show guest's name if not authenticated
        return "Unassigned"

    get_booking_name.short_description = "Booked By"  # Column name in admin

@admin.register(Payment)
class PaymentAdminClass(ModelAdmin):
    pass
@admin.register(Contact)
class ContactAdminClass(ModelAdmin):
    list_display = ('name', 'email', 'created_at')  # Display these fields in the admin list view
    search_fields = ('name', 'email', 'message')  # Enable search functionality
    list_filter = ('created_at',)  # Filter contacts by date
    ordering = ('-created_at',)  # Show newest messages first
    readonly_fields = ('created_at',)  # Prevent modification of creation date

@admin.register(Discount)
class DiscountAdminClass(ModelAdmin):
      list_display = ('code', 'percentage', 'expiry_date', 'status') 
@admin.register(News)
class NewsAdminClass(ModelAdmin):
    pass
@admin.register(Record)
class RecordAdminClass(ModelAdmin):
    pass