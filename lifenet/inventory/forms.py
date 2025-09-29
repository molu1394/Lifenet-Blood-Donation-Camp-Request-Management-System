from django import forms
from django.forms import modelformset_factory
from .models import CampInventory,BloodBankInventory

class CampInventoryForm(forms.ModelForm):
    class Meta:
        model = CampInventory
        fields = ["blood_group", "units_collected"]
        widgets = {
            "blood_group": forms.TextInput(attrs={"readonly": "readonly"}),
        }

CampInventoryFormSet = modelformset_factory(
    CampInventory, 
    form=CampInventoryForm, 
    extra=0
)

class InventoryUpdateForm(forms.ModelForm):
    class Meta:
        model = BloodBankInventory
        fields = ["units_available"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["units_available"].widget.attrs.update({
            "class": "form-control",
            "min": 0
        })