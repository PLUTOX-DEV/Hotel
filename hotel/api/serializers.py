from rest_framework import serializers
from ..models import Room, Booking, Guest

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'is_available']

class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    guest = serializers.StringRelatedField()
    
    class Meta:
        model = Booking
        fields = ['id', 'guest', 'room', 'check_in_date', 
                 'check_out_date', 'booking_uid', 'is_active']

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number']