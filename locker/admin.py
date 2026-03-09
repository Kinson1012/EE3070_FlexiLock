from django.contrib import admin
from .models import Locker, Reservation, ReservationLog

admin.site.register(Locker)
admin.site.register(Reservation)
admin.site.register(ReservationLog)