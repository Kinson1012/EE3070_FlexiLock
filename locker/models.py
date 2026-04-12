import uuid

from django.db import models
from django.contrib.auth.models import User


class Locker(models.Model):
    STATUS_CHOICES = [
    ('available', 'Available'),
    ('occupied', 'Occupied'),
    ('maintenance', 'Maintenance'),
    ('disabled', 'Disabled'),
    ]

    locker_number = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.locker_number} - {self.location}"


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    locker = models.ForeignKey(Locker, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    active = models.BooleanField(default=True)
    qr_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        state = "Active" if self.active else "Closed"
        return f"{self.user.username} -> {self.locker.locker_number} ({state})"

    @property
    def is_current(self):
        from django.utils import timezone
        now = timezone.now()
        return self.active and self.start_time <= now <= self.end_time

    @property
    def is_upcoming(self):
        from django.utils import timezone
        now = timezone.now()
        return self.active and self.start_time > now


class ReservationLog(models.Model):
    ACTION_CHOICES = [
    ('reserve', 'Reserve'),
    ('cancel', 'Cancel'),
    ('maintenance', 'Maintenance'),
    ('reopen', 'Reopen'),
    ('disable', 'Disable'),
    ('qr_verify', 'QR Verify'),
    ('unlock_result', 'Unlock Result'),
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
    
class LockerDeviceStatus(models.Model):
    LOCK_STATE_CHOICES = [
        ('locked', 'Locked'),
        ('unlocked', 'Unlocked'),
        ('unknown', 'Unknown'),
    ]

    DEVICE_STATE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]

    locker = models.OneToOneField(Locker, on_delete=models.CASCADE)
    device_state = models.CharField(max_length=20, choices=DEVICE_STATE_CHOICES, default='offline')
    lock_state = models.CharField(max_length=20, choices=LOCK_STATE_CHOICES, default='unknown')
    last_seen = models.DateTimeField(auto_now=True)
    last_action = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.locker.locker_number} - {self.device_state} / {self.lock_state}"