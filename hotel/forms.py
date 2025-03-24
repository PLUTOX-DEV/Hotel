from django import forms
from django.core.exceptions import ValidationError
from .models import Booking, Guest , RoomType , Contact, Review , News

from django import forms
from django.core.exceptions import ValidationError
from .models import Booking

class BookingForm(forms.ModelForm):
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'})
    )
    discount_code = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300', 'placeholder': 'Enter discount code (if any)'})
    )

    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'})
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'})
    )

    class Meta:
        model = Booking
        fields = ['room', 'check_in_date', 'check_out_date', 'discount_code']
        widgets = {
            'room': forms.Select(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get user from view
        super().__init__(*args, **kwargs)

        # If the user is logged in, remove the guest fields
        if self.user and self.user.is_authenticated:
            self.fields.pop('first_name')
            self.fields.pop('last_name')
            self.fields.pop('email')
            self.fields.pop('phone_number')
        else:
            # Require guest fields if the user is not logged in
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True
            self.fields['email'].required = True
            self.fields['phone_number'].required = True

    def clean(self):
        data = super().clean()
        room = data.get('room')
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        discount_code = data.get('discount_code')

        if check_in and check_out and check_in >= check_out:
            raise ValidationError("Check-out date must be after check-in date.")

        if room:
            overlapping = Booking.objects.filter(
                room=room,
                check_in_date__lt=check_out,
                check_out_date__gt=check_in,
                is_active=True
            ).exists()

            if overlapping:
                raise ValidationError("This room is already booked for those dates.")

        # Validate discount code if entered
        if discount_code:
            from .models import Discount  # Import here to avoid circular imports
            try:
                discount = Discount.objects.get(code=discount_code)
                if not discount.is_valid():
                    raise ValidationError("This discount code is expired or invalid.")
            except Discount.DoesNotExist:
                raise ValidationError("Invalid discount code.")

        return data

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'}),
            'last_name': forms.TextInput(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'}),
            'email': forms.EmailInput(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'}),
            'phone_number': forms.TextInput(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'}),
        }


class RoomSearchForm(forms.Form):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    rooms = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        initial=1
    )
    
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message'}),
        }
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class GuestReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'rating', 'comment']
        
        
        
class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False)
    
class NewsletterForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['email']