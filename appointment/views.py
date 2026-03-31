from datetime import date, datetime
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

# Create your views here.
# Create
@login_required(login_url='/signin/')
def book_appointment(request):
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')

        if not doctor_id or not date or not time:
            return render(request, 'book.html', {'doctors': doctors, 'error': 'All fields are required'})
        
        selected_date = request.POST.get('selected_date')
        
        if selected_date < str(dt_date.today()):
            return HttpResponse("Cannot book past dates")

        doctor = Doctor.objects.get(id=doctor_id)

        if Appointment.objects.filter(Doctor=doctor, date=date, time=time).exists():
            return HttpResponse("Slot is already booked.")

        Appointment.objects.create(
            user = request.user,
            Doctor = doctor,
            date = date,
            time = time,
        )

        return redirect('view_appointments')
    return render(request, 'book.html', {'doctors': doctors})
    
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

@login_required(login_url='signin')
def dashboard(request):
    return render(request, 'dashboard.html', {'username': request.user.username})

@login_required
def user_dashboard(request):
    user = request.user

    today = date.today()

    upcoming = Appointment.objects.filter(user=user, date__gte=today).order_by('date')
    past = Appointment.objects.filter(user=user, date__lt=today).order_by('-date')

    total = Appointment.objects.filter(user=user).count()
    completed = Appointment.objects.filter(user=user, status='completed').count()
    cancelled = Appointment.objects.filter(user=user, status='cancelled').count()

    appointments = Appointment.objects.filter(user=user)
    doctors = [a.Doctor for a in appointments]

    if doctors:
        most_common = Counter(doctors).most_common(1)[0][0]  # Doctor object
    else:
        most_common = None

    context = {
        'upcoming': upcoming,
        'past': past,
        'total': total,
        'completed': completed,
        'cancelled': cancelled,
        'recommended_doctor': most_common,  
    }

    return render(request, 'dashboard.html', context)

@login_required(login_url='/signin/')
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        if username and email:
            user.username = username
            user.email = email
            user.save()

            messages.success(request, "Profile updated successfully ✅")
            return redirect('dashboard')  
        else:
            messages.error(request, "All fields are required ❌")

    return render(request, 'update_profile.html', {'user': user})