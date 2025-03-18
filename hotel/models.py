from django.db import models
from shortuuid.django_fields import ShortUUIDField


class RoomType(models.Model):
    image = models.ImageField(upload_to='hotel_room_image/')
    name = models.CharField(max_length=100)
    description = models.TextField() 
    size = models.PositiveIntegerField(default=1)
    capacity = models.PositiveIntegerField(default=1)
    service =  models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

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


class Booking(models.Model):
    booking_uid = ShortUUIDField(
        length=6,
        max_length=6,
        prefix="",
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        unique=True,
        editable=False
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    booking_uid = models.CharField(max_length=6, unique=True, editable=False)

    is_active = models.BooleanField(default=True)  # Booking status

    def save(self, *args, **kwargs):
        """Override save to mark the room as unavailable when booked"""
        if self.is_active:  # Only update if booking is active
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
        return f"Booking {self.booking_uid} - {self.room.room_type} ({self.check_in_date} to {self.check_out_date})"
    
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