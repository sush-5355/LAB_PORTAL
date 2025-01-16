from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path(
        "signup/", view=views.signup, name="signup"
    ),  # Changed to 'signup' instead of 'Sign Up'
    path("login/", view=views.login, name="login"),  # Changed to 'login' as well
    path("", view=views.home, name="home"),
    path("logout/", views.logout, name="logout"),  # Changed to 'login' as well
    # path("service/<int:service_id>/", views.service_detail, name="service_detail"),
    path("slot-booking/", views.slot_booking, name="slot_booking"),
    path("book-slot/<int:slot_id>/", views.book_slot, name="book_slot"),
      path('my_slots/', views.my_slots, name='my_slots'),
       path('free_slot/<int:slot_id>/', views.free_slot, name='free_slot'),
]
