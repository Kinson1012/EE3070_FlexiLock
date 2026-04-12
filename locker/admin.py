from django.contrib import admin
from .models import Locker, Reservation, ReservationLog, LockerDeviceStatus

admin.site.register(Locker)
admin.site.register(Reservation)
admin.site.register(ReservationLog)
admin.site.register(LockerDeviceStatus)