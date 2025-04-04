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

    @property
    def status(self):
        """Returns 'Expired' or 'Active' for admin display"""
        return "Expired" if not self.is_valid() else "Active"

    def __str__(self):
        return f"{self.code} - {self.percentage}% ({self.status})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number  = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username

from django.db import models

class RoomType(models.Model):
    image = models.ImageField(upload_to='hotel_room_image/', default='default_room.jpg')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField() 
    size = models.PositiveIntegerField(default=1, help_text="Size in square meters")
    capacity = models.PositiveIntegerField(default=1, help_text="Number of people the room can accommodate")
    service = models.CharField(max_length=100, help_text="E.g., WiFi, TV, AC, Breakfast")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, help_text="Standard price per night")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Discounted price, if applicable")

    def apply_discount(self, discount_percentage):
        """Apply a discount to the room price and store it in final_price."""
        self.final_price = self.price_per_night - ((discount_percentage / 100) * self.price_per_night)
        self.save()

    def __str__(self): 
        return self.name


class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="rooms")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type.name}"


class Guest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Allow null values


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
    guest = models.ForeignKey('Guest', on_delete=models.CASCADE, null=True, blank=True)  # Non-logged-in users  
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    is_active = models.BooleanField(default=True)
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True)

    discount_code = models.CharField(max_length=50, blank=True, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

def save(self, *args, **kwargs):
    """Calculate total price, update room availability, and create a record"""
    
    if self.check_out_date <= self.check_in_date:
        from django.core.exceptions import ValidationError
        raise ValidationError("Check-out date must be after check-in date.")

    num_days = max(1, (self.check_out_date - self.check_in_date).days)
    base_price = num_days * self.room.room_type.price_per_night  

    if self.discount and self.discount.is_valid():
        discount_amount = (self.discount.percentage / 100) * base_price
        self.final_price = base_price - discount_amount
    else:
        self.final_price = base_price  # No discount applied

    self.room.is_available = not self.is_active
    self.room.save()

    super().save(*args, **kwargs)

    # ✅ Create or update Record for this booking
    Record.objects.update_or_create(
        booking=self,
        defaults={
            'user': self.user,
            'guest': self.guest,
            'nights_stayed': num_days,
            'is_ongoing': self.is_active
        }
    )
    def cancel_booking(self):
        """Function to cancel a booking and make the room available again"""
        self.is_active = False
        self.room.is_available = True
        self.room.save(update_fields=['is_available'])  # Update only room availability
        self.save(update_fields=['is_active'])  # Only update is_active to avoid unnecessary database updates

    def __str__(self):
        if self.user:
            return f"Booking {self.booking_uid} - {self.user.username} (from {self.check_in_date} to {self.check_out_date})"
        elif self.guest:
            return f"Booking {self.booking_uid} - {self.guest.first_name} {self.guest.last_name} (from {self.check_in_date} to {self.check_out_date})"
        else:
            return f"Booking {self.booking_uid} - Unassigned (from {self.check_in_date} to {self.check_out_date})"



class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Logged-in users
    guest = models.ForeignKey(Guest, on_delete=models.SET_NULL, null=True, blank=True)  # Non-logged-in users
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)  # Link to Booking
    nights_stayed = models.PositiveIntegerField(default=0)  # Total nights
    is_ongoing = models.BooleanField(default=True)  # Check if the booking is still active
    created_at = models.DateTimeField(auto_now_add=True)  # Record creation time
    updated_at = models.DateTimeField(auto_now=True)  # Record update time

    def save(self, *args, **kwargs):
        """Automatically calculate nights stayed from booking dates"""
        if self.booking:
            self.nights_stayed = max(1, (self.booking.check_out_date - self.booking.check_in_date).days)
            self.is_ongoing = self.booking.is_active  # Reflects if the booking is still ongoing
        super().save(*args, **kwargs)

    def __str__(self):
        if self.user:
            return f"Record for {self.user.username} - {self.nights_stayed} Nights"
        elif self.guest:
            return f"Record for {self.guest.first_name} {self.guest.last_name} - {self.nights_stayed} Nights"
        else:
            return f"Record for Booking {self.booking.booking_uid} - {self.nights_stayed} Nights"

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



class News(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email