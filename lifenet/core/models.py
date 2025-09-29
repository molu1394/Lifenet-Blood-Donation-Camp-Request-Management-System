from django.db import models

# Create your models here.
class ContactQuery(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Resolved", "Resolved"),
    ]

    firstname = models.CharField(max_length=100,null=False,blank=False)
    lastname = models.CharField(max_length=100,null=False,blank=False)
    email = models.EmailField(null=False,blank=False)
    subject = models.CharField(max_length=200,null=False,blank=False)
    message = models.TextField(null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    def __str__(self):
        return f"{self.subject} ({self.firstname} {self.lastname})"