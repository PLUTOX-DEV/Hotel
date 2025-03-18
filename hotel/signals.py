from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking

@receiver(post_save, sender=Booking)
def handle_booking_creation(sender, instance, created, **kwargs):
    print(f"📢 Signal Triggered for Booking ID: {instance.booking_uid}")  

    if created and instance.is_active:
        print(f"✅ Booking successfully created for {instance.guest.first_name} (ID: {instance.booking_uid})")
