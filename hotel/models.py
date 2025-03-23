from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from shortuuid.django_fields import ShortUUIDField

class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Enter discount percentage (e.g., 10 for 10%)")
    expiry_date = models.DateTimeField()

    def is_valid(self):
        return self.expiry_date > timezone.now()

    def __str__(self):
        return f"{self.code} - {self.percentage}%"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number  = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username

class RoomType(models.Model):
    image = models.ImageField(upload_to='hotel_room_image/')
    name = models.CharField(max_length=100)
    description = models.TextField() 
    size = models.PositiveIntegerField(default=1)
    capacity = models.PositiveIntegerField(default=1)
    service =  models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def __str__(self): 
        return self.name


class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room_number} ({self.room_type.name})"


class Guest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# test


class Booking(models.Model):
    booking_uid = ShortUUIDField(
        length=6,
        max_length=6,
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        unique=True,
        editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Logged-in users  
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, null=True, blank=True)  # Non-logged-in users  
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    is_active = models.BooleanField(default=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)

    total_nights = models.IntegerField()     
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """Calculate total price and mark room as unavailable when booking is active"""
        self.total_nights = (self.check_out_date - self.check_in_date).days
        base_price = self.total_nights * self.room.price_per_night
        
        if self.discount_code:
            try:
                discount = Discount.objects.get(code=self.discount_code)
                if discount.is_valid():
                    discount_amount = (discount.percentage / 100) * base_price
                    self.final_price = base_price - discount_amount
                else:
                    self.final_price = base_price  # No discount if expired
            except Discount.DoesNotExist:
                self.final_price = base_price  # No discount if invalid
        else:
            self.final_price = base_price  # No discount applied

        if self.is_active:
            self.room.is_available = False  # Set room as booked
            self.room.save()

        super().save(*args, **kwargs)

    def cancel_booking(self):
        """Function to cancel a booking and make the room available again"""
        self.is_active = False
        self.room.is_available = True
        self.room.save()
        self.save()

    def __str__(self):
        if self.user:
            return f"Booking {self.booking_uid} - {self.user.username} (from {self.check_in_date} to {self.check_out_date})"
        elif self.guest:
            return f"Booking {self.booking_uid} - {self.guest.first_name} {self.guest.last_name} (from {self.check_in_date} to {self.check_out_date})"
        else:
            return f"Booking {self.booking_uid} - Unassigned (from {self.check_in_date} to {self.check_out_date})"
class Review(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, blank=True, null=True)  # Non-authenticated user
    email = models.EmailField(blank=True, null=True)
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=1)  # Rating out of 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Check if the user is None before accessing the username
        user_str = self.user.username if self.user else self.name or "Guest"
        return f"{user_str}'s review for {self.room}"
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.booking}"



