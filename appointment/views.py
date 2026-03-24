from django.shortcuts import render, redirect
from appointment.models import Doctor, Appointment
from django.http import HttpResponse
import re
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'views.html', {'appointments': appointments})

# Update
@login_required(login_url='/signin/')
def update_appointment(request, id):
    appointment = Appointment.objects.get(id=id)

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
            return render(request, 'register.html')
        
        if len(password) < 8:
            return HttpResponse("Password must be atleast 8 characters long.")
        
        if not re.search(r'[A-Z]', password):
            return HttpResponse("Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', password):
            return HttpResponse("Password must contain at least one number.")
        
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
            return redirect('home')
        else:
            return HttpResponse("Username or password is incorrect")

    return render(request, 'signin.html')

def logout_fun(request):
    logout(request)
    return redirect('signin')


def home(request):
    return render(request, 'home.html')

