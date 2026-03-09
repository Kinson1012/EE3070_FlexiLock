from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path('reserve/<int:locker_id>/', views.reserve_locker, name='reserve_locker'),
    path('reservation/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservation/<int:reservation_id>/qr/', views.reservation_qr, name='reservation_qr'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
]