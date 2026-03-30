from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout_fun, name='logout'),

    path('book/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.view_appointments, name='view_appointments'),
    path('update/<int:id>/', views.update_appointment, name='update_appointment'),
    path('cancel/<int:id>/', views.cancel_appointment, name='cancel_appointment'),
    path('profile/edit/', views.update_profile, name='update_profile'),
]