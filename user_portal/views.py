from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    authenticate,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from .models import Slot
from django.utils.timezone import datetime

User = get_user_model()  # Custom User model


def home(request):
    """
    Render the homepage.
    If the user is authenticated, show a personalized homepage.
    """
    if request.user.is_authenticated:
        user_id = request.session.get("user_id")  # Retrieve the user ID from session

        if user_id:
            user = User.objects.get(
                id=user_id
            )  # Query the user from the database using the ID
            username = user.name  # Retrieve the username
        else:
            username = None  # Fallback in case there's no user ID in the session
        return render(request, "home.html", {"user": request.user})
    return render(request, "home.html", {"user": None})


def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check if all fields are filled
        if not all([name, email, phone, password, confirm_password]):
            messages.error(request, "Please fill in all fields.")
            return redirect("signup")

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        # Check if email or phone already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered. Proceed to Login.")
            return redirect("login")

        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number is already registered.")
            return redirect("signup")

        # Create the user
        try:
            user = User.objects.create_user(
                name=name, email=email, phone=phone, password=password
            )
            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return redirect("signup")

    return render(request, "signup.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")  # Email is used as the username
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Store the user ID in the session
            request.session["user_id"] = user.id
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials.")
            return redirect("login")

    return render(request, "login.html")


def logout(request):
    auth_logout(request)
    request.session.flush()  # This clears all session data
    messages.success(request, "You have been logged out.")
    return redirect("home")


def service_detail(request, service_id):
    # Fetch service details from database based on service_id (or hardcode for now)
    return render(request, "service_detail.html", {"service_id": service_id})


@login_required
def slot_booking(request):
    if request.method == "POST":
        selected_date = request.POST.get("selected_date")  # Get selected date from form
        try:
            selected_date = datetime.strptime(
                selected_date, "%Y-%m-%d"
            ).date()  # Convert to date object
        except ValueError:
            selected_date = None

        if selected_date:
            # Check if slots already exist for the selected date
            existing_slots = Slot.objects.filter(date=selected_date)

            if not existing_slots:
                # If no slots are available for that date, create and populate 6 slots with start_time and end_time
                start_time = datetime.strptime("00:00", "%H:%M").time()
                for i in range(6):
                    end_time = (
                        datetime.combine(datetime.today(), start_time)
                        + timedelta(hours=4)
                    ).time()
                    Slot.objects.create(
                        date=selected_date,
                        slot_number=i + 1,
                        start_time=start_time,
                        end_time=end_time,
                        status=False,  # Set status as False (free)
                    )
                    # Update start_time for the next slot
                    start_time = (
                        datetime.combine(datetime.today(), start_time)
                        + timedelta(hours=4)
                    ).time()

            # Fetch the slots for the selected date
            slots = Slot.objects.filter(date=selected_date)
        else:
            slots = Slot.objects.none()  # No slots if no valid date

        return render(
            request,
            "slot_booking.html",
            {"slots": slots, "selected_date": selected_date},
        )

    return render(request, "slot_booking.html")  # Initial GET request for the form


@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)

    if not slot.status:  # Check if the slot is available
        # Book the slot for the user
        slot.status = True
        slot.user = request.user
        slot.save()

        # Redirect to My Slots or a confirmation page
        return redirect("my_slots")  # Redirect to the "My Slots" page

    return redirect("home")  # Redirect back to home if the slot was already booked


@login_required
def my_slots(request):
    # Get the user from the request
    user = request.user

    # Fetch all the slots booked by the current user
    booked_slots = Slot.objects.filter(
        user=user, status=True
    )  # Assuming `status=True` means booked

    return render(request, "my_slots.html", {"booked_slots": booked_slots})


@login_required
def free_slot(request, slot_id):
    # Get the slot object
    slot = get_object_or_404(Slot, id=slot_id)

    # Check if the current user is the one who booked this slot
    if slot.user == request.user:
        # Free the slot (set status to False and remove the user)
        slot.status = False
        slot.user = None
        slot.save()

    # Redirect the user back to the "My Slots" page
    return redirect("my_slots")
