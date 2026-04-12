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
    path('timeline/', views.reservation_timeline, name='reservation_timeline'),
    path('timeline/events/', views.timeline_events, name='timeline_events'),
    
    path('admin-lockers/', views.admin_lockers, name='admin_lockers'),
    path('admin-lockers/<int:locker_id>/maintenance/', views.set_locker_maintenance, name='set_locker_maintenance'),
    path('admin-lockers/<int:locker_id>/reopen/', views.reopen_locker, name='reopen_locker'),
    path('admin-lockers/<int:locker_id>/disable/', views.disable_locker, name='disable_locker'),
    
    path("api/test-ping/", views.api_test_ping, name="api_test_ping"),
    path("api/test-verify-qr/", views.api_test_verify_qr, name="api_test_verify_qr"),
    path("api/verify-qr/", views.api_verify_qr, name="api_verify_qr"),
    path("api/lockers/", views.api_lockers, name="api_lockers"),
    path("api/lockers/<str:locker_number>/", views.api_locker_detail, name="api_locker_detail"),
    path("api/locker-current/<str:locker_number>/", views.api_locker_current, name="api_locker_current"),
    path("api/reservation/<int:reservation_id>/", views.api_reservation_detail, name="api_reservation_detail"),
    path("api/my-active-reservation/", views.api_my_active_reservation, name="api_my_active_reservation"),
    path("api/locker-status/", views.api_locker_status, name="api_locker_status"),
    path("api/unlock-result/", views.api_unlock_result, name="api_unlock_result"),
]