from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import Room, Booking, Guest
from .serializers import RoomSerializer, BookingSerializer, GuestSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def available(self, request):
        rooms = Room.objects.filter(is_available=True)
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def validate_uid(self, request):
        uid = request.data.get('uid')
        try:
            booking = Booking.objects.get(booking_uid=uid)
            return Response({
                'valid': True,
                'room_number': booking.room.room_number,
                'check_in': booking.check_in_date,
                'check_out': booking.check_out_date
            })
        except Booking.DoesNotExist:
            return Response({'valid': False}, status=404)


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [permissions.IsAdminUser]

    # views.py


@action(detail=False, methods=['get'])
def calendar(self, request):
    start_date = request.query_params.get('start')
    end_date = request.query_params.get('end')
    bookings = Booking.objects.filter(
        check_in_date__lte=end_date,
        check_out_date__gte=start_date
    )
    serializer = self.get_serializer(bookings, many=True)
    return Response(serializer.data)
