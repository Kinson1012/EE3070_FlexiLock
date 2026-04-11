from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('reserve/<int:locker_id>/', views.reserve_locker, name='reserve_locker'),
    path('reservation/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservation/<int:reservation_id>/qr/', views.reservation_qr, name='reservation_qr'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('campus-map/', views.campus_map, name='campus_map'),
    path('api/verify-qr/', views.verify_qr, name='verify_qr'),
    path('timeline/', views.reservation_timeline, name='reservation_timeline'),
    path('timeline/events/', views.timeline_events, name='timeline_events'),
    path('admin-lockers/', views.admin_lockers, name='admin_lockers'),
    path('admin-lockers/<int:locker_id>/maintenance/', views.set_locker_maintenance, name='set_locker_maintenance'),
    path('admin-lockers/<int:locker_id>/reopen/', views.reopen_locker, name='reopen_locker'),
    path('admin-lockers/<int:locker_id>/disable/', views.disable_locker, name='disable_locker'),
]