from django.db import models
from users.models import BloodBankProfile,BLOOD_GROUP_CHOICES
from camp.models import Camp
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.
class CampInventory(models.Model):
    BLOOD_GROUPS = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("O+", "O+"),
        ("O-", "O-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
    ]

    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name="inventory")
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_collected = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("camp", "blood_group")  # only one row per blood group per camp

    def __str__(self):
        return f"{self.camp.name} - {self.blood_group}"
    
    @receiver(post_save, sender=Camp)
    def create_camp_inventory(sender, instance, created, **kwargs):
        if created:
            for group, _ in CampInventory.BLOOD_GROUPS:
                CampInventory.objects.create(camp=instance, blood_group=group, units_collected=0)

    
class BloodBankInventory(models.Model):
    BLOOD_GROUPS = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("O+", "O+"), ("O-", "O-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
    ]

    bloodbank = models.ForeignKey(
        BloodBankProfile, on_delete=models.CASCADE, related_name="inventory"
    )
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_available = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.bloodbank.name} - {self.blood_group}: {self.units_available} units"

    def add_units(self, units):
        """Increase stock"""
        self.units_available += units
        self.save()

    def remove_units(self, units):
        """Decrease stock but not below 0"""
        if units > self.units_available:
            raise ValueError("Not enough stock available")
        self.units_available -= units
        self.save()


@receiver(post_save, sender=BloodBankProfile)
def create_bloodbank_inventory(sender, instance, created, **kwargs):
    if created:
        for group, _ in BloodBankInventory.BLOOD_GROUPS:
            BloodBankInventory.objects.create(
                bloodbank=instance, blood_group=group, units_available=0
            )