from django.db import models
from django.contrib.auth.models import User


class Locker(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]

    locker_number = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.locker_number} - {self.location}"


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    locker = models.ForeignKey(Locker, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        state = "Active" if self.active else "Closed"
        return f"{self.user.username} -> {self.locker.locker_number} ({state})"


class ReservationLog(models.Model):
    ACTION_CHOICES = [
        ('reserve', 'Reserve'),
        ('cancel', 'Cancel'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    locker = models.ForeignKey(Locker, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        username = self.user.username if self.user else "Unknown User"
        locker_no = self.locker.locker_number if self.locker else "Unknown Locker"
        return f"{self.action.upper()} - {username} - {locker_no} - {self.timestamp:%Y-%m-%d %H:%M:%S}"