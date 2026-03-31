from datetime import date, datetime, timezone
from django.shortcuts import get_object_or_404, render, redirect
from appointment.models import Doctor, Appointment
from django.http import HttpResponse
import re
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import date as dt_date
from collections import Counter
from django.contrib import messages
from .forms import UpdateProfileForm
from django.utils import timezone
from django.db.models import Q


# Create your views here.
# Create
@login_required(login_url='/signin/')
def book_appointment(request,doctor_id=None):
    doctors = Doctor.objects.all()
    selected_doctor = None

    if doctor_id:
        selected_doctor = Doctor.objects.get(id=doctor_id)

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')

        # Step 1: Check empty
        if not doctor_id or not date_str or not time_str:
            return render(request, 'book.html', {
                'doctors': doctors,
                'error': 'All fields are required'
            })

        #  Step 2: Convert string → date
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        #  Step 3: Validate past date
        if appointment_date < dt_date.today():
            return render(request, 'book.html', {
                'doctors': doctors,
                'error': 'Cannot book past dates'
            })

        doctor = Doctor.objects.get(id=doctor_id)

        #  Step 4: Prevent duplicate booking
        if Appointment.objects.filter(
            Doctor=doctor,
            date=appointment_date,
            time=time_str
        ).exists():
            return render(request, 'book.html', {
                'doctors': doctors,
                'error': 'Slot already booked'
            })

        time_input = request.POST.get('time')
        if "AM" in time_input or "PM" in time_input:
            time_obj = datetime.strptime(time_input, "%I:%M %p").time()
        else:
            time_obj = datetime.strptime(time_input, "%H:%M").time()
        #  Step 5: Save appointment
        Appointment.objects.create(
            user=request.user,
            Doctor=doctor,
            date=appointment_date,
            time=time_obj,
        )

        return redirect('view_appointments')

    return render(request, 'book.html', {
        'doctors': doctors, 
        'selected_doctor': selected_doctor
        })
    
# Read
@login_required(login_url='/signin/')
def view_appointments(request):
    status = request.GET.get('status')

    appointments = Appointment.objects.filter(user=request.user)
    if status:
        appointments = appointments.filter(status=status)

    # Add user to context for profile info
    context = {
        'appointments': appointments,
        'user': request.user,
    }

    return render(request, 'views.html', context)

# Update
@login_required(login_url='/signin/')
def update_appointment(request, id):
    appointment = Appointment.objects.get(id=id, user=request.user)

    if request.method == 'POST':
        appointment.date = request.POST.get('date')
        appointment.time = request.POST.get('time')
        appointment.save()

        return redirect('view_appointments')
    
    return render(request, 'update.html', {'appointment': appointment})

# Delete
@login_required(login_url='/signin/')
def cancel_appointment(request, id):
    appointment = Appointment.objects.get(id=id)
    appointment.status = 'Cancelled'
    appointment.save()

    return redirect('view_appointments')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_pass = request.POST.get('confirm_pass')

        if password != confirm_pass:
            return HttpResponse("Passwords do not match")
        
        if len(password) < 8:
            return HttpResponse("Password must be atleast 8 characters long.")
        
        if not re.search(r'[A-Z]', password):
            return HttpResponse("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[0-9]', password):
            return HttpResponse("Password must contain at least one number.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return HttpResponse("Password must contain at least one special character.")
        
        my_user = User.objects.create_user(username, email, password)
        my_user.save()

        return redirect('signin')
    return render(request, 'register.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user=authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return HttpResponse("Username or password is incorrect")

    return render(request, 'signin.html')

def logout_fun(request):
    logout(request)
    return redirect('signin')



@login_required(login_url='/signin/')
def user_dashboard(request):
    user = request.user
    now = timezone.now()

    upcoming = Appointment.objects.filter(
        user=user,
        date__gte=now.date()
    ).order_by('date', 'time')

    past = Appointment.objects.filter(
        user=user,
        date__lt=now.date()
    ).order_by('-date', '-time')


    total = Appointment.objects.filter(user=user).count()
    completed = Appointment.objects.filter(user=user, status='completed').count()
    cancelled = Appointment.objects.filter(user=user, status='cancelled').count()

    appointments = Appointment.objects.filter(user=user)
    doctors = [a.Doctor for a in appointments]  

    most_common = Counter(doctors).most_common(1)[0][0] if doctors else None

    doctors = Doctor.objects.all()

    context = {
        'upcoming': upcoming,
        'past': past,
        'total': total,
        'completed': completed,
        'cancelled': cancelled,
        'recommended_doctor': most_common,
        'doctors': doctors,
    }
    print("LOGGED IN USER ID:", request.user.id)
    return render(request, 'dashboard.html', context)

@login_required(login_url='/signin/')
def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()

            # save profile image separately
            profile = request.user.profile
            if request.FILES.get('image'):
                profile.image = request.FILES.get('image')
                profile.save()

    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, 'update_profile.html', {'form': form})


###  API VIEWS ###
from rest_framework import viewsets
from .serializers import DoctorSerializer, AppointmentSerializer
from .models import Doctor, Appointment
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        doctors = Doctor.objects.all().values('id', 'name', 'specialty')
        return Response(doctors)

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    

    def get_queryset(self):
        # Only show appointments for the logged-in user
        return Appointment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user
        serializer.save(user=self.request.user)