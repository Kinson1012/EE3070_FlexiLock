from pathlib import Path
from io import BytesIO
from datetime import timedelta

import qrcode

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Count, Q
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .models import Locker, Reservation, ReservationLog


def write_reservation_log(user, locker, action, extra_message=""):
    """
    Save reservation activity into a physical log file.
    Example path: BASE_DIR/logs/reservation.log
    """
    log_dir = Path(settings.BASE_DIR) / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "reservation.log"

    timestamp = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
    username = user.username if user else "Unknown User"
    locker_number = locker.locker_number if locker else "Unknown Locker"

    line = f"[{timestamp}] user={username} locker={locker_number} action={action}"
    if extra_message:
        line += f" | {extra_message}"
    line += "\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


def sync_locker_statuses():
    """
    Keep locker status aligned with current active reservations.
    - maintenance stays maintenance
    - occupied if there is a current reservation now
    - otherwise available
    """
    now = timezone.now()

    # Close expired reservations
    expired_reservations = Reservation.objects.filter(
        active=True,
        end_time__lt=now
    )
    expired_reservations.update(active=False)

    # Find lockers currently occupied by active reservations
    current_locker_ids = set(
        Reservation.objects.filter(
            active=True,
            start_time__lte=now,
            end_time__gte=now
        ).values_list("locker_id", flat=True)
    )

    # Update locker statuses except maintenance lockers
    for locker in Locker.objects.exclude(status__in=["maintenance", "disabled"]):
        locker.status = "occupied" if locker.id in current_locker_ids else "available"
        locker.save(update_fields=["status"])


def index(request):
    sync_locker_statuses()
    lockers = Locker.objects.all().order_by("locker_number")[:4]
    return render(request, "locker/index.html", {"lockers": lockers})


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password or not confirm_password:
            messages.error(request, "Please fill in all fields.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "locker/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")
        return redirect("login")

    return render(request, "locker/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


@login_required(login_url="login")
def dashboard(request):
    sync_locker_statuses()
    now = timezone.now()

    lockers = Locker.objects.all().order_by("location", "locker_number")

    current_user_reservation = Reservation.objects.filter(
    user=request.user,
    active=True,
    start_time__lte=now,
    end_time__gte=now
    ).order_by("start_time").first()

    upcoming_user_reservations = Reservation.objects.filter(
    user=request.user,
    active=True,
    start_time__gt=now
    ).order_by("start_time")

    next_reservation = current_user_reservation or upcoming_user_reservations.first()

    reservation_history = Reservation.objects.filter(
        user=request.user
    ).order_by("-start_time")

    context = {
    "lockers": lockers,
    "user_reservation": current_user_reservation,
    "upcoming_reservations": upcoming_user_reservations,
    "next_reservation": next_reservation,
    "reservation_history": reservation_history,
    }
    return render(request, "locker/dashboard.html", context)


@login_required(login_url="login")
def reserve_locker(request, locker_id):
    sync_locker_statuses()
    locker = get_object_or_404(Locker, id=locker_id)

    if locker.status == "maintenance":
        messages.error(request, "This locker is under maintenance.")
        return redirect("dashboard")

    if request.method == "POST":
        start_time_str = request.POST.get("start_time")
        duration_seconds = request.POST.get("duration_seconds")

        if not start_time_str or not duration_seconds:
            messages.error(request, "Please fill in all reservation details.")
            return redirect("reserve_locker", locker_id=locker.id)

        try:
            naive_start = timezone.datetime.fromisoformat(start_time_str)
            start_time = timezone.make_aware(naive_start, timezone.get_current_timezone())
            duration_seconds = int(duration_seconds)
        except (ValueError, TypeError):
            messages.error(request, "Invalid date or duration.")
            return redirect("reserve_locker", locker_id=locker.id)

        if start_time < timezone.now():
            messages.error(request, "Start time cannot be in the past.")
            return redirect("reserve_locker", locker_id=locker.id)

        if duration_seconds <= 0:
            messages.error(request, "Duration must be greater than 0.")
            return redirect("reserve_locker", locker_id=locker.id)

        if duration_seconds > 604800:  # 7 days
            messages.error(request, "Maximum booking duration is 7 days.")
            return redirect("reserve_locker", locker_id=locker.id)

        end_time = start_time + timedelta(seconds=duration_seconds)

        # Check overlap on the same locker
        conflicting_reservation = Reservation.objects.filter(
            locker=locker,
            active=True,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if conflicting_reservation:
            messages.error(request, "This locker is already booked for the selected time slot.")
            return redirect("reserve_locker", locker_id=locker.id)

        reservation = Reservation.objects.create(
            user=request.user,
            locker=locker,
            start_time=start_time,
            end_time=end_time,
            active=True
        )

        # If reservation is currently active now, update locker status immediately
        now = timezone.now()
        if start_time <= now <= end_time and locker.status != "maintenance":
            locker.status = "occupied"
            locker.save(update_fields=["status"])

        ReservationLog.objects.create(
            user=request.user,
            locker=locker,
            action="reserve",
            details=(
                f"Reservation ID {reservation.id} created. "
                f"Start: {start_time}, End: {end_time}, QR Token: {reservation.qr_token}"
            )
        )

        write_reservation_log(
            user=request.user,
            locker=locker,
            action="reserve",
            extra_message=(
                f"reservation_id={reservation.id} "
                f"start={start_time} end={end_time} qr_token={reservation.qr_token}"
            )
        )

        messages.success(request, f"You have reserved locker {locker.locker_number}.")
        return redirect("reservation_detail", reservation_id=reservation.id)

    return render(request, "locker/reserve_form.html", {"locker": locker})


@login_required(login_url="login")
def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        user=request.user
    )
    return render(request, "locker/reservation_detail.html", {"reservation": reservation})


@login_required(login_url="login")
def reservation_qr(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        user=request.user
    )

    qr_data = (
        f"locker_id={reservation.locker.id};"
        f"locker_number={reservation.locker.locker_number};"
        f"user={request.user.username};"
        f"reservation_id={reservation.id};"
        f"token={reservation.qr_token};"
        f"start={reservation.start_time.isoformat()};"
        f"end={reservation.end_time.isoformat()}"
    )

    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


@login_required(login_url="login")
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        user=request.user,
        active=True
    )

    locker = reservation.locker
    reservation.active = False
    reservation.save(update_fields=["active"])

    sync_locker_statuses()

    ReservationLog.objects.create(
        user=request.user,
        locker=locker,
        action="cancel",
        details=f"Reservation ID {reservation.id} cancelled."
    )

    write_reservation_log(
        user=request.user,
        locker=locker,
        action="cancel",
        extra_message=f"reservation_id={reservation.id}"
    )

    messages.success(request, f"Reservation for locker {locker.locker_number} has been cancelled.")
    return redirect("my_reservations")


@login_required(login_url="login")
def campus_map(request):
    sync_locker_statuses()

    buildings = Locker.objects.values("location").annotate(
        total_lockers=Count("id"),
        available_lockers=Count("id", filter=Q(status="available")),
        occupied_lockers=Count("id", filter=Q(status="occupied")),
        maintenance_lockers=Count("id", filter=Q(status="maintenance")),
    ).order_by("location")

    selected_location = request.GET.get("location")
    lockers = None

    if selected_location:
        lockers = Locker.objects.filter(location=selected_location).order_by("locker_number")

    context = {
        "buildings": buildings,
        "selected_location": selected_location,
        "lockers": lockers,
    }
    return render(request, "locker/campus_map.html", context)


@login_required(login_url="login")
def my_reservations(request):
    sync_locker_statuses()
    now = timezone.now()

    active_reservation = Reservation.objects.filter(
        user=request.user,
        active=True,
        start_time__lte=now,
        end_time__gte=now
    ).order_by("-start_time").first()

    upcoming_reservations = Reservation.objects.filter(
        user=request.user,
        active=True,
        start_time__gt=now
    ).order_by("start_time")

    reservation_history = Reservation.objects.filter(
        user=request.user
    ).order_by("-start_time")

    context = {
        "active_reservation": active_reservation,
        "upcoming_reservations": upcoming_reservations,
        "reservation_history": reservation_history,
    }
    return render(request, "locker/my_reservations.html", context)

@login_required(login_url="login")
def reservation_timeline(request):
    buildings = Locker.objects.values_list("location", flat=True).distinct().order_by("location")
    selected_location = request.GET.get("location", "")
    return render(
        request,
        "locker/reservation_timeline.html",
        {
            "buildings": buildings,
            "selected_location": selected_location,
        },
    )


@login_required(login_url="login")
def timeline_events(request):
    selected_location = request.GET.get("location", "")

    reservations = Reservation.objects.filter(active=True).select_related("locker", "user")

    if selected_location:
        reservations = reservations.filter(locker__location=selected_location)

    events = []
    for reservation in reservations:
        now = timezone.localtime()
        if reservation.start_time <= now <= reservation.end_time:
            color = "#f59e0b"   # current
        elif reservation.start_time > now:
            color = "#4f46e5"   # upcoming
        else:
            color = "#94a3b8"   # past but still active, just in case

        events.append({
            "title": f"{reservation.locker.locker_number} • {reservation.user.username}",
            "start": timezone.localtime(reservation.start_time).isoformat(),
            "end": timezone.localtime(reservation.end_time).isoformat(),
            "color": color,
            "extendedProps": {
                "locker": reservation.locker.locker_number,
                "location": reservation.locker.location,
                "user": reservation.user.username,
                "qr_token": str(reservation.qr_token),
            }
        })

    return JsonResponse(events, safe=False)

@staff_member_required
def admin_lockers(request):
    lockers = Locker.objects.all().order_by("location", "locker_number")
    logs = ReservationLog.objects.select_related("user", "locker").order_by("-timestamp")[:50]

    context = {
        "lockers": lockers,
        "logs": logs,
    }
    return render(request, "locker/admin_lockers.html", context)


@staff_member_required
def set_locker_maintenance(request, locker_id):
    locker = get_object_or_404(Locker, id=locker_id)
    locker.status = "maintenance"
    locker.save(update_fields=["status"])

    ReservationLog.objects.create(
        user=request.user,
        locker=locker,
        action="cancel",
        details=f"Admin set locker {locker.locker_number} to maintenance."
    )

    write_reservation_log(
        user=request.user,
        locker=locker,
        action="maintenance",
        extra_message="admin_set_maintenance"
    )

    messages.success(request, f"{locker.locker_number} set to maintenance.")
    return redirect("admin_lockers")


@staff_member_required
def reopen_locker(request, locker_id):
    locker = get_object_or_404(Locker, id=locker_id)
    locker.status = "available"
    locker.save(update_fields=["status"])

    ReservationLog.objects.create(
        user=request.user,
        locker=locker,
        action="reserve",
        details=f"Admin reopened locker {locker.locker_number}."
    )

    write_reservation_log(
        user=request.user,
        locker=locker,
        action="reopen",
        extra_message="admin_reopened_locker"
    )

    messages.success(request, f"{locker.locker_number} reopened and available.")
    return redirect("admin_lockers")


@staff_member_required
def disable_locker(request, locker_id):
    locker = get_object_or_404(Locker, id=locker_id)
    locker.status = "disabled"
    locker.save(update_fields=["status"])

    ReservationLog.objects.create(
        user=request.user,
        locker=locker,
        action="cancel",
        details=f"Admin disabled locker {locker.locker_number}."
    )

    write_reservation_log(
        user=request.user,
        locker=locker,
        action="disable",
        extra_message="admin_disabled_locker"
    )

    messages.success(request, f"{locker.locker_number} disabled.")
    return redirect("admin_lockers")