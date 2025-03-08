from django import forms
from django.core.exceptions import ValidationError
from .models import Booking, Guest , RoomType

class BookingForm(forms.ModelForm):
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'})
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'})
    )

    def clean(self):
        data = super().clean()
        room = data.get('room')
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')

        if check_in >= check_out:
            raise ValidationError("Check-out date must be after check-in date")

        if room:
            overlapping = Booking.objects.filter(
                room=room,
                check_in_date__lt=check_out,
                check_out_date__gt=check_in,
                is_active=True
            ).exists()

            if overlapping:
                raise ValidationError("This room is already booked for those dates")

        return data

    class Meta:
        model = Booking
        fields = ['room', 'check_in_date', 'check_out_date']
        widgets = {
            'room': forms.Select(attrs={'class': 'border rounded-lg p-2 w-full focus:ring focus:ring-blue-300'}),
        }


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