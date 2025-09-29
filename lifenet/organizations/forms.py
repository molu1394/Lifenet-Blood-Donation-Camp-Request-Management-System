from django import forms
from users.models import OrganizationProfile

class OrgProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = OrganizationProfile
        fields = ['mobile_number']
        widgets = {
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
