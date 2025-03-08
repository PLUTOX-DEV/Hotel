from django.shortcuts import render, redirect , get_object_or_404
from .models import Room, Booking
from .forms import BookingForm, GuestForm, RoomSearchForm
from django.db.models import Q
from datetime import date
import uuid

def home(request):
    form = RoomSearchForm(request.GET or None)
    rooms = Room.objects.filter(is_available=True)
    
    if form.is_valid():
        check_in = form.cleaned_data.get('check_in')
        check_out = form.cleaned_data.get('check_out')
        room_type = form.cleaned_data.get('room_type')
        max_price = form.cleaned_data.get('max_price')

        if check_in and check_out:
            # Get overlapping bookings and extract room IDs
            overlapping_bookings = Booking.objects.filter(
                Q(check_in_date__lt=check_out) &
                Q(check_out_date__gt=check_in) &
                Q(is_active=True)
            ).values_list('room_id', flat=True)  # Fixed to get flat list of IDs
            
            rooms = rooms.exclude(id__in=overlapping_bookings)

        if room_type:
            rooms = rooms.filter(room_type=room_type)
            
        if max_price:
            rooms = rooms.filter(room_type__price_per_night__lte=max_price)
        
    
    return render(request, 'hotel/index.html',{'rooms': rooms,'form': form})

def room_details(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    return render(request, 'hotel/room-details.html',{'room': room})
def room_list(request):
    form = RoomSearchForm(request.GET or None)
    rooms = Room.objects.filter(is_available=True)

    if form.is_valid():
        check_in = form.cleaned_data.get('check_in')
        check_out = form.cleaned_data.get('check_out')
        room_type = form.cleaned_data.get('room_type')
        max_price = form.cleaned_data.get('max_price')

        if check_in and check_out:
            # Get overlapping bookings and extract room IDs
            overlapping_bookings = Booking.objects.filter(
                Q(check_in_date__lt=check_out) &
                Q(check_out_date__gt=check_in) &
                Q(is_active=True)
            ).values_list('room_id', flat=True)  # Fixed to get flat list of IDs
            
            rooms = rooms.exclude(id__in=overlapping_bookings)

        if room_type:
            rooms = rooms.filter(room_type=room_type)
            
        if max_price:
            rooms = rooms.filter(room_type__price_per_night__lte=max_price)

    return render(request, 'hotel/rooms.html', {
        'rooms': rooms,
        'form': form
    })

def book_room(request, room_id=None):
    room = Room.objects.get(id=room_id) if room_id else None
    guest_form = GuestForm(request.POST or None)
    booking_form = BookingForm(request.POST or None, initial={'room': room})

    if request.method == 'POST':
        if guest_form.is_valid() and booking_form.is_valid():
            guest = guest_form.save()
            booking = booking_form.save(commit=False)
            booking.guest = guest

            # Generate unique short UID
            while True:
                short_uid = str(uuid.uuid4())[:6].upper()
                if not Booking.objects.filter(booking_uid=short_uid).exists():
                    break
                    
            booking.booking_uid = short_uid
            booking.save()
            
            # Redirect to prevent form resubmission
            return redirect('booking_confirmation', booking_id=booking.id)


    return render(request, 'hotel/book_room.html', {
        'guest_form': guest_form,
        'booking_form': booking_form,
        'room': room
    })

def booking_confirmation(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    return render(request, 'hotel/booking_confirmation.html', {'booking': booking})