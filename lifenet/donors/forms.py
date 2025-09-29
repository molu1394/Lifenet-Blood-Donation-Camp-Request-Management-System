from django import forms
from users.models import DonorProfile

class DonorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        # Only allow updating certain fields
        fields = ['first_name','last_name','mobile_number', 'blood_group','dob','gender','address','ready_to_donate','profile_pic']
        widgets = {
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),  
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            "dob": forms.DateInput(attrs={"type": "date"}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'ready_to_donate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        