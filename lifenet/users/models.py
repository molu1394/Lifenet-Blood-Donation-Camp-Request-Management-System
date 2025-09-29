from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date
from django.core.validators import RegexValidator
# Create your models here.
# Common choices
BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('O+', 'O+'), ('O-', 'O-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]
# Donor Profile
class DonorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    mobile_number = models.CharField(
        max_length=15, blank=False, null=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    dob = models.DateField(blank=False, null=False)
    age = models.PositiveIntegerField(editable=False, default=18)  # auto-calculated
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField(blank=False, null=False)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    ready_to_donate = models.BooleanField(blank=False, null=False)

    def clean(self):
        """Custom validation: enforce minimum age = 18"""
        if self.dob:
            today = date.today()
            calculated_age = (
                today.year - self.dob.year -
                ((today.month, today.day) < (self.dob.month, self.dob.day))
            )
            if calculated_age < 18:
                raise ValidationError("Donor must be at least 18 years old.")

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean()

        if self.dob:
            today = date.today()
            self.age = (
                today.year - self.dob.year -
                ((today.month, today.day) < (self.dob.month, self.dob.day))
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Donor: {self.user.username}"

# Patient Profile
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50,blank=False, null=False)
    last_name = models.CharField(max_length=50,blank=False, null=False)
    mobile_number = models.CharField(max_length=15,blank=False, null=False,
                                     validators=[
                                        RegexValidator(
                                            regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
                                            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
                                        ])
    blood_group_req = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES,blank=False, null=False)
    address = models.TextField(blank=False, null=False)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return f"Patient: {self.user.username}"

# BloodBank Profile
class BloodBankProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bloodbank_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15,blank=False, null=False,
                                     validators=[
                                        RegexValidator(
                                            regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
                                            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
                                        ])
    address = models.TextField(blank=False, null=False)
    authorize_number = models.IntegerField(unique=True)
    approval_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')],
        default='Pending'
    )

    def __str__(self):
        return f"BloodBank: {self.bloodbank_name}"

class OrganizationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100)
    organization_type = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15,blank=False, null=False,validators=[
                                        RegexValidator(
                                            regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
                                            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
                                        ])
    authorize_number = models.CharField(max_length=50, unique=True)
    approval_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')],
        default='Pending'
    )

    def __str__(self):
        return f"Organizations:{self.organization_name}"

# Staff Profile
class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50,blank=False, null=False)
    last_name = models.CharField(max_length=50,blank=False, null=False)
    mobile_number = models.CharField(max_length=15,blank=False, null=False,
                                     validators=[
                                        RegexValidator(
                                            regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
                                            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
                                        ])
    bloodbank_name = models.ForeignKey(
        BloodBankProfile, 
        on_delete=models.CASCADE,
        related_name="staff_members"
    )
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    approval_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')],
        default='Pending'
    )
    def __str__(self):
        return f"Staff: {self.user.username}"


# Admin Profile (optional, since Django superuser exists)
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50,blank=False, null=False)
    last_name = models.CharField(max_length=50,blank=False, null=False)

    def __str__(self):
        return f"Admin: {self.user.username}"