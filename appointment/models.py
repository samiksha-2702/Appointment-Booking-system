from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    availability = models.TimeField()
    available_to = models.TimeField()

    def __str__(self):
        return self.name
    
TIME_SLOTS = [
    ('10:00 AM', '10:00 AM'),
    ('11:00 AM', '11:00 AM'),
    ('12:00 PM', '12:00 PM'),
    ('02:00 PM', '02:00 PM'),
    ('03:00 PM', '03:00 PM'),
]

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Booked', 'Booking'),
        ('Completed', 'Completed'),
        ('Canclled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Booked')

    def __str__(self):
        return f"{self.user.username} - {self.Doctor.name}"