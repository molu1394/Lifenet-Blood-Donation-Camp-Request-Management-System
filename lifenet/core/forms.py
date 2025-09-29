from django import forms 
from users.models import AdminProfile
from .models import ContactQuery

class AdminProfileUpdateForm(forms.ModelForm):
    class Meta:
        model=AdminProfile
        fields=['first_name','last_name']
        widgets={
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }



class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactQuery
        fields = ["firstname", "lastname", "email", "subject", "message"]

        widgets = {
            "firstname": forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name",'required': True}),
            "lastname": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name",'required': True}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email",'required': True}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject",'required': True}),
            "message": forms.Textarea(attrs={"class": "form-control", "placeholder": "Your Message",'required': True,"rows": 4}),
        }