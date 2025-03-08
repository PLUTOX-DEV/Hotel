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
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking_uid = models.CharField(max_length=6, unique=True, blank=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.guest} - {self.room}"


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.booking}"
