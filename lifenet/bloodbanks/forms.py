from django import forms
from users.models import BloodBankProfile,StaffProfile

class BloodBankProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = BloodBankProfile
        fields = ['mobile_number']
        widgets = {
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StaffProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = StaffProfile
        fields = ["first_name", "last_name", "mobile_number", "profile_pic"]
        widgets = {
            'profile_pic': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["email"].initial = user.email

    def save(self, commit=True):
        staff_profile = super().save(commit=False)
        if commit:
            staff_profile.save()
            # Update linked CustomUser email
            staff_profile.user.email = self.cleaned_data["email"]
            staff_profile.user.first_name = self.cleaned_data["first_name"]
            staff_profile.user.last_name = self.cleaned_data["last_name"]
            staff_profile.user.save()
        return staff_profile
        
        