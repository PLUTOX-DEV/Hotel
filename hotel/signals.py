
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking , Profile
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)  # Prevent duplicate creation

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):  # Ensure profile exists before saving
        instance.profile.save()
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Booking)
def handle_booking_creation(sender, instance, created, **kwargs):
    logger.info(f"📢 Signal Triggered for Booking ID: {instance.booking_uid}")  

    if created and instance.is_active:
        if instance.guest:
            logger.info(f"✅ Booking successfully created for {instance.guest.first_name} (ID: {instance.booking_uid})")
        else:
            logger.warning(f"✅ Booking created (ID: {instance.booking_uid}), but no guest assigned.")
