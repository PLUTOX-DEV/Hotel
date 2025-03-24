from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking , Guest , Profile , Review , Discount
from .forms import BookingForm, GuestForm, RoomSearchForm , ContactForm , ReviewForm , GuestReviewForm , SearchForm , NewsletterForm
from django.db.models import Q
from datetime import date
import uuid
import json
import requests
from django.http import JsonResponse
from .models import Payment
from django.conf import settings
from django.urls import reverse
from .models import Payment, Booking






def register_user(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        phone = request.POST["phone_number"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect("register")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Save phone number in Profile model
        user.profile.phone_number = phone
        user.profile.save()

        messages.success(request, "Registration successful! You can now log in.")
        return redirect("login")

    return render(request, "auth/register.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "auth/login.html")


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


def home(request):
    form = RoomSearchForm(request.GET or None)
    rooms = Room.objects.filter(is_available=True)[:4]

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
                # Fixed to get flat list of IDs
            ).values_list('room_id', flat=True)

            rooms = rooms.exclude(id__in=overlapping_bookings)

        if room_type:
            rooms = rooms.filter(room_type=room_type)

        if max_price:
            rooms = rooms.filter(room_type__price_per_night__lte=max_price)

    return render(request, 'hotel/index.html', {'rooms': rooms, 'form': form})


def room_details(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    reviews = room.reviews.all()  # Fetch all reviews for the room

    if request.method == "POST":
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.room = room
                review.save()
                messages.success(request, "Your review has been submitted!")
                return redirect('room_details', room_id=room.id)
        else:
            form = GuestReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.room = room
                review.save()
                messages.success(request, "Your review has been submitted!")
                return redirect('room_details', room_id=room.id)
    else:
        form = ReviewForm() if request.user.is_authenticated else GuestReviewForm()

    return render(request, 'hotel/room-details.html', {
        'room': room,
        'reviews': reviews,
        'form': form
    })
def room_list(request):
    form = RoomSearchForm(request.GET or None)
    rooms = Room.objects.filter(is_available=True)

    paginator = Paginator(rooms, 6)  # Show 5 rooms per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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
                # Fixed to get flat list of IDs
            ).values_list('room_id', flat=True)

            rooms = rooms.exclude(id__in=overlapping_bookings)

        if room_type:
            rooms = rooms.filter(room_type=room_type)

        if max_price:
            rooms = rooms.filter(room_type__price_per_night__lte=max_price)

    return render(request, 'hotel/rooms.html', {
        'page_obj': page_obj,
        'form': form
    })




def book_room(request, room_id=None):
    room = get_object_or_404(Room, id=room_id)
    guest = None  # Default to None

    # Initialize guest form only if the user is not authenticated
    guest_form = GuestForm(request.POST or None) if not request.user.is_authenticated else None
    initial_data = {'room': room}

    if request.user.is_authenticated:
        # Get user profile
        try:
            profile = Profile.objects.get(user=request.user)
            guest, created = Guest.objects.get_or_create(
                email=request.user.email,  # Use email as unique identifier
                defaults={
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'phone_number': profile.phone_number
                }
            )
            initial_data['guest'] = guest  # Assign to form
        except Profile.DoesNotExist:
            profile = None

    booking_form = BookingForm(request.POST or None, initial=initial_data)

    if request.method == 'POST':
        # Validate both forms before saving
        if (guest_form is None or guest_form.is_valid()) and booking_form.is_valid():
            booking = booking_form.save(commit=False)

            if request.user.is_authenticated:
                booking.guest = guest  # Assign the correct Guest instance
                booking.user = request.user  # Assign user
            else:
                guest = guest_form.save()  # Save the guest details for non-logged-in users
                booking.guest = guest  # Assign guest for non-logged-in users

            # Apply Discount
            discount_code = booking_form.cleaned_data.get('discount_code')
            if discount_code:
                try:
                    discount = Discount.objects.get(code=discount_code)
                    if discount.is_valid():
                        # Calculate base price
                        total_nights = (booking.check_out_date - booking.check_in_date).days
                        base_price = booking.room.price_per_night * total_nights
                        
                        # Apply discount to the base price
                        discount_amount = (discount.percentage / 100) * base_price
                        final_price = base_price - discount_amount
                        booking.discount = discount  # Link discount to booking
                        booking.final_price = final_price  # Apply the discounted price

                        # Track discount usage if applicable
                        if hasattr(discount, "used_count"):
                            discount.used_count += 1
                            discount.save()

                        if hasattr(discount, "used_by_users"):
                            discount.used_by_users.add(request.user)

                    else:
                        messages.error(request, "Discount code has expired.")
                except Discount.DoesNotExist:
                    messages.error(request, "Invalid discount code.")

            # Save the booking with applied discount
            booking.save()

            return redirect("booking_confirmation", booking_id=booking.id)

        else:
            # Display error messages for form issues
            if guest_form and not guest_form.is_valid():
                messages.error(request, "There were errors in the guest information.")
            if not booking_form.is_valid():
                messages.error(request, "There were errors in the booking form.")

    return render(request, 'hotel/book_room.html', {
        'guest_form': guest_form,
        'booking_form': booking_form,
        'room': room
    })




def booking_confirmation(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    return render(request, 'hotel/booking_confirmation.html', {'booking': booking})


def blog(request):
    return render(request, "hotel/blog.html")
def blog_details(request):
    return render(request, "hotel/blog-details.html")


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'hotel/contact.html', {'form': form})


def about_us(request):
    return render(request, 'hotel/about-us.html')


def search_view(request):
    form = SearchForm(request.GET)
    query = request.GET.get('query', '')
    rooms = []

    if form.is_valid():
        if query:
            # Adjust search based on fields available in your model
            rooms = Room.objects.filter(
                Q(room_number__icontains=query) | Q(room_type__icontains=query)
            )
    
    return render(request, 'base.html', {
        'form': form,
        'rooms': rooms,
        'query': query,
    })
    
def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Subscription successful'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid email'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)




def newsletter_success(request):
    return render(request, 'hotel/newsletter_success.html')