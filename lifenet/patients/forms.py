from django import forms
from users.models import PatientProfile,BLOOD_GROUP_CHOICES,BloodBankProfile,DonorProfile
from .models import BloodRequest,GeneralBloodRequest
from django.core.exceptions import ValidationError

BLOOD_GROUPS = [
    ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"),
    ("AB+", "AB+"), ("AB-", "AB-"),
    ("O+", "O+"), ("O-", "O-"),
]

class PatientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['first_name','last_name','mobile_number', 'blood_group_req','address','profile_pic']
        widgets = {
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group_req': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DonorSearchForm(forms.Form):
    location = forms.CharField(required=False, label="Location",widget=forms.TextInput(attrs={"placeholder": "Enter location"}))
    blood_group = forms.ChoiceField(
        choices=[("", "-- Select Blood Group --")] + BLOOD_GROUPS,
        required=False, label="Blood Group"
    )

class BloodBankSearchForm(forms.Form):
    location = forms.CharField(max_length=255, required=True,widget=forms.TextInput(attrs={ "placeholder": "Enter location"}))
    blood_group = forms.ChoiceField(choices=[("", "-- Select Blood Group --")] + BLOOD_GROUPS, required=True)

class PublicBloodBankSearchForm(forms.Form):
    location = forms.CharField(
        required=False,
        label="Location",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter location"})
    )
    blood_group = forms.ChoiceField(
        required=False,
        label="Blood Group",
        choices=[("", "-- Select Blood Group --")] + BLOOD_GROUPS,
        widget=forms.Select(attrs={"class": "form-control"})
    )

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = GeneralBloodRequest
        fields = ['blood_group', 'location']
        widgets = {
            'blood_group': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
        }