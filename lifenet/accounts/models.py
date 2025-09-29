from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('DONOR', 'Donor'),
        ('PATIENT', 'Patient'),
        ('BLOODBANK', 'Blood Bank'),
        ('ORG', 'org'),
        ('STAFF', 'Staff'),
        ('ADMIN', 'Admin'),
    ]
    email = models.EmailField(max_length=191,unique=True) 
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def save(self, *args, **kwargs):
        # Force email to lowercase before saving
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.role})"