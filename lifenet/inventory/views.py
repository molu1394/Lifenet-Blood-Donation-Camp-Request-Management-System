from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Camp, CampInventory,BloodBankInventory
from .forms import CampInventoryForm,CampInventoryFormSet,InventoryUpdateForm
from django.urls import reverse
from users.models import BloodBankProfile,StaffProfile
from django.views.decorators.http import require_POST

# View Inventory
class CampInventoryListView(LoginRequiredMixin, ListView):
    model = CampInventory
    template_name = "inventory/camp_inventory_list.html"
    context_object_name = "inventory"

    def get_queryset(self):
        camp_id = self.kwargs["camp_id"]
        return CampInventory.objects.filter(camp_id=camp_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camp_id = self.kwargs["camp_id"]
        context["camp"] = get_object_or_404(Camp, id=camp_id)
        return context

def camp_inventory_update(request, camp_id):
    camp = get_object_or_404(Camp, id=camp_id)
    inventory = CampInventory.objects.filter(camp=camp)

    if request.method == "POST":
        for inv in inventory:
            new_value = request.POST.get(f"units_{inv.id}")
            if new_value is not None and new_value.isdigit():
                inv.units_collected = int(new_value)   
                inv.save()
                updated = True
        if updated:
            messages.success(request, f"Inventory for {camp.name} updated successfully!")  # Add success message
        else:
            messages.info(request, "No changes were made to the inventory.") 
        return redirect("inventory:camp_inventory_list", camp_id=camp.id)

    return render(
        request,
        "inventory/camp_inventory_update.html",
        {"camp": camp, "inventory": inventory},
    )

# Add Inventory
class CampInventoryCreateView(View):
    template_name = "inventory/camp_inventory_form.html"
    

    def get(self, request, camp_id):
        form = CampInventoryForm()
        camp = get_object_or_404(Camp, id=camp_id)
        return render(request, self.template_name, {"form": form, "camp": camp})

    def post(self, request, camp_id):
        camp = get_object_or_404(Camp, id=camp_id)
        form = CampInventoryForm(request.POST)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.camp = camp
            inventory.save()
            messages.success(request, "Blood stock added successfully!")
            return redirect("inventory:camp_inventory_list", camp_id=camp.id)
        return render(request, self.template_name, {"form": form, "camp": camp})

    
class InventoryListView(ListView):
    model = BloodBankInventory
    template_name = "inventory/bloodbank_inventory_list.html"
    context_object_name = "bankinventory"

    def get_queryset(self):
        user=self.request.user
        if user.role=="BLOODBANK":
            bloodbank = get_object_or_404(BloodBankProfile, user=user)
        elif user.role=="STAFF":
            staff = get_object_or_404(StaffProfile, user=user)
            bloodbank=staff.bloodbank_name
        else:
            return BloodBankInventory.objects.none()
        
        self.bloodbank = bloodbank
        return BloodBankInventory.objects.filter(bloodbank=bloodbank)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use self.bloodbank from queryset
        context["bloodbank"] = getattr(self, "bloodbank", None)
        return context


@login_required
def bloodbank_inventory_update(request):
    user = request.user

    if user.role == "BLOODBANK":
        bloodbank = get_object_or_404(BloodBankProfile, user=user)
    elif user.role == "STAFF":
        staff = get_object_or_404(StaffProfile, user=user)
        bloodbank = staff.bloodbank_name
    else:
        return redirect("inventory:inventory_list")

    # Get all inventory items for this bloodbank
    inventory = BloodBankInventory.objects.filter(bloodbank=bloodbank)

    if request.method == "POST":
        for inv in inventory:
            new_value = request.POST.get(f"units_{inv.id}")
            if new_value is not None and new_value.isdigit():
                inv.units_available = int(new_value)  
                inv.save()
        messages.success(request, "Inventory updated successfully")
        return redirect("inventory:inventory_list")

    return render(
        request,
        "inventory/bloodbank_inventory_update.html",
        {"bloodbank": bloodbank, "inventory": inventory},
    )

