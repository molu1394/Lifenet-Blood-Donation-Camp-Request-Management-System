# camp/models.py
from django.db import models
from django.utils import timezone
from datetime import datetime, time
from users.models import DonorProfile,BloodBankProfile,OrganizationProfile

class Camp(models.Model):
    STATUS_CHOICES = [
        ("UPCOMING", "Upcoming"),
        ("CURRENT", "Current"),
        ("DONE", "Done"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="UPCOMING")

    bloodbank = models.ForeignKey(
        BloodBankProfile, on_delete=models.CASCADE, related_name="camps", null=True, blank=True
    )
    organization = models.ForeignKey(
        OrganizationProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="camps"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state} ({self.date})"

    def update_status(self):
        """Auto-update status based on time, unless it's DONE or has been manually changed to CURRENT."""
        now = timezone.localtime()
        camp_start = timezone.make_aware(
            timezone.datetime.combine(self.date, self.start_time),
            timezone.get_current_timezone()
        )
        camp_end = timezone.make_aware(
            timezone.datetime.combine(self.date, self.end_time),
            timezone.get_current_timezone()
        )

        # Respect DONE (don’t revert back)
        if self.status == "DONE":
            return

        # Auto-update only if still UPCOMING
        if self.status == "UPCOMING":
            if camp_start <= now <= camp_end:
                self.status = "CURRENT"
                self.save()
            elif now > camp_end:
                self.status = "DONE"
                self.save()

        # Auto-update CURRENT only if time has passed the end
        elif self.status == "CURRENT":
            if now > camp_end:
                self.status = "DONE"
                self.save()


# NEW: Camp Slots
class CampSlot(models.Model):
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name="slots")
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=10)  # how many donors can book this slot
    booked_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.camp.name} [{self.start_time} - {self.end_time}]"

    def is_available(self):
        return self.booked_count < self.capacity


# Donor Appointment (slot booking)
class CampAppointment(models.Model):
    STATUS_CHOICES = [
        ("BOOKED", "Booked"),
        ("VISITED", "Visited"),
        ("CANCELLED", "Cancelled"),
    ]

    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name="appointments")
    slot = models.ForeignKey(CampSlot, on_delete=models.CASCADE, related_name="appointments")
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name="camp_appointments")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="BOOKED")
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("slot", "donor")  # donor can book only one slot per camp

    def __str__(self):
        return f"{self.donor.user.get_full_name()} → {self.camp.name} ({self.status})"
    

