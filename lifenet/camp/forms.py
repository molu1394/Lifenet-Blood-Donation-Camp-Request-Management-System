# camps/forms.py
from django import forms
from .models import Camp, CampSlot, CampAppointment
from django.db.models import F
from django.forms import modelformset_factory


class CampForm(forms.ModelForm):
    class Meta:
        model = Camp
        fields = [
            "name", "description", "state", "city", "address",
            "date", "start_time", "end_time", "organization", "bloodbank"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date","class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"type": "time","class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time","class": "form-control"}),
            "organization": forms.Select(attrs={"class": "form-select"}),
            "bloodbank": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # If Organizer logged in → auto set org & disable
        if hasattr(user, "organizationprofile"):
            self.fields["organization"].initial = user.organizationprofile
            self.fields["organization"].disabled = True

        # If BloodBank logged in → auto set bloodbank & disable
        if hasattr(user, "bloodbankprofile"):
            self.fields["bloodbank"].initial = user.bloodbankprofile
            self.fields["bloodbank"].disabled = True


class CampSlotForm(forms.ModelForm):
    class Meta:
        model = CampSlot
        fields = ["start_time", "end_time",'capacity']
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),   
        }

    def __init__(self, *args, **kwargs):
        self.camp = kwargs.pop("camp", None)   
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # Camp instance is passed from formset's parent (via form kwargs)
        camp = self.initial.get("camp")
        if camp and start_time and end_time:
            if not (camp.start_time <= start_time < camp.end_time and
                    camp.start_time < end_time <= camp.end_time):
                raise forms.ValidationError(
                    f"Slot {start_time}-{end_time} must be within camp timing {camp.start_time}–{camp.end_time}."
                )
        return cleaned_data

class DonorCampRegistrationForm(forms.ModelForm):
    slot = forms.ModelChoiceField(
        queryset=CampSlot.objects.none(),
        empty_label="-- Select a Slot --",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = CampAppointment
        fields = ["slot"]

    def __init__(self, *args, **kwargs):
        camp = kwargs.pop("camp", None)
        super().__init__(*args, **kwargs)
        if camp:
            self.fields["slot"].queryset = camp.slots.filter(
                booked_count__lt=F("capacity")
            )

CampSlotFormSet = modelformset_factory(
    CampSlot,
    form=CampSlotForm,
    extra=3,          # default 3 slot rows
    can_delete=False
)


class CampSearchForm(forms.Form):
    location = forms.CharField(
        required=False,
        label="Search Location",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter location..."
        })
    )
