from django.db import models
from users.models import PatientProfile,DonorProfile,BloodBankProfile,StaffProfile
from django.utils import timezone
from django.conf import settings

# Create your models here.
BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('O+', 'O+'), ('O-', 'O-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
]
class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requests"
    )
    donor = models.ForeignKey(
        "users.DonorProfile",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="requests"
    )
    bloodbank = models.ForeignKey(
        "users.BloodBankProfile",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="requests"
    )
    accepted_by = models.ForeignKey(   
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="accepted_requests"
    )
    decline_by = models.ForeignKey(   
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="decline_requests"
    )
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.id} - {self.patient.username} ({self.blood_group})"
    
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:30]}"
    
class GeneralBloodRequest(models.Model):
    requested_by = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    location = models.CharField(max_length=200)
    date_requested = models.DateTimeField(auto_now_add=True)

    accepted_by = models.ForeignKey(DonorProfile, on_delete=models.SET_NULL, null=True, blank=True)

    def donor_name(self):
        if self.accepted_by:
            return f"{self.accepted_by.first_name} {self.accepted_by.last_name}"
        return None

    def donor_mobile(self):
        if self.accepted_by:
            return self.accepted_by.mobile_number
        return None
    
    def donor_address(self):
        if self.accepted_by:
            return self.accepted_by.address
        return None

