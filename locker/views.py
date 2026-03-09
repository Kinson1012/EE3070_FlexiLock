from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

from .models import Locker, Reservation, ReservationLog


def write_reservation_log(user, locker, action, extra_message=""):
    """
    Save history into a physical log file.
    Example path: project_root/logs/reservation.log
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


def index(request):
    lockers = Locker.objects.all().order_by('locker_number')[:4]
    return render(request, 'locker/index.html', {'lockers': lockers})


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


@login_required(login_url='login')
def dashboard(request):
    lockers = Locker.objects.all().order_by('locker_number')
    user_reservation = Reservation.objects.filter(user=request.user, active=True).first()
    reservation_history = Reservation.objects.filter(user=request.user).order_by('-start_time')

    context = {
        'lockers': lockers,
        'user_reservation': user_reservation,
        'reservation_history': reservation_history,
    }
    return render(request, "locker/dashboard.html", context)


@login_required(login_url='login')
def reserve_locker(request, locker_id):
    locker = get_object_or_404(Locker, id=locker_id)

    existing_user_reservation = Reservation.objects.filter(
        user=request.user,
        active=True
    ).first()

    if existing_user_reservation:
        messages.error(request, "You already have an active locker reservation.")
        return redirect("dashboard")

    existing_locker_reservation = Reservation.objects.filter(
        locker=locker,
        active=True
    ).first()

    if existing_locker_reservation or locker.status != 'available':
        messages.error(request, "This locker is not available.")
        return redirect("dashboard")

    reservation = Reservation.objects.create(
        user=request.user,
        locker=locker,
        active=True
    )

    locker.status = 'occupied'
    locker.save()

    ReservationLog.objects.create(
        user=request.user,
        locker=locker,
        action='reserve',
        details=f"Reservation ID {reservation.id} created."
    )

    write_reservation_log(
        user=request.user,
        locker=locker,
        action="reserve",
        extra_message=f"reservation_id={reservation.id}"
    )

    messages.success(request, f"You have reserved locker {locker.locker_number}.")
    return redirect("dashboard")


@login_required(login_url='login')
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        user=request.user,
        active=True
    )

    locker = reservation.locker

    reservation.active = False
    reservation.end_time = timezone.now()
    reservation.save()

    locker.status = 'available'
    locker.save()

    ReservationLog.objects.create(
        user=request.user,
        locker=locker,
        action='cancel',
        details=f"Reservation ID {reservation.id} cancelled."
    )

    write_reservation_log(
        user=request.user,
        locker=locker,
        action="cancel",
        extra_message=f"reservation_id={reservation.id}"
    )

    messages.success(request, f"Reservation for locker {locker.locker_number} has been cancelled.")
    return redirect("dashboard")