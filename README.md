# Hotel Booking System

## Overview
This is a Django-based hotel booking system that allows users and guests to book rooms, apply discounts, and manage ongoing stays. The system tracks room availability and records the number of nights a user stays.

## Features
- User and Guest Booking
- Room Management
- Discount Application
- Booking Management
- Record Keeping for Nights Stayed

## Models

### RoomType
Defines different types of rooms with attributes such as:
- Name, Description
- Size, Capacity
- Services (WiFi, AC, TV, etc.)
- Price per Night
- Discounted Price

### Room
Represents individual rooms available for booking.

### Guest
Stores guest details for non-logged-in users.

### Booking
Handles the booking process and applies discounts if available.

### Record
Tracks:
- Number of nights a user or guest has stayed
- Ongoing bookings
- Links to Booking model

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/hotel-booking.git
   cd hotel-booking
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Access the application at:
   ```
   http://127.0.0.1:8000/
   ```

## Usage
- Admin can add rooms and manage bookings.
- Users can log in, search rooms, book a room, and apply discounts.
- Guests can book without logging in.

## License
This project is licensed under the MIT License.

## Author
Developed by Okeniyi Hakeem

