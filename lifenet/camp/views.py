# camp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Camp, CampSlot, CampAppointment
from .forms import CampForm,CampSlotForm,DonorCampRegistrationForm,CampSlotFormSet,CampSearchForm
from django.forms import modelformset_factory
from django.db.models import Case, When, Value, IntegerField
from users.models import DonorProfile
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError

# Donor: List upcoming camps
class DonorUpcomingCampsView(LoginRequiredMixin, ListView):
    model = Camp
    template_name = "camp/donor_upcoming_camps.html"
    context_object_name = "camps"

    def get_queryset(self):
        donor = getattr(self.request.user, "donorprofile", None)

        # Start with upcoming (not done) camps only
        camps = Camp.objects.exclude(status="DONE")

        if donor and donor.address:
            donor_city = donor.address.strip()
            # Match both exact city and partial match
            camps = camps.filter(
                Q(city__icontains=donor_city)
            )

        return camps

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        donor = getattr(self.request.user, "donorprofile", None)
        if donor:
            # Only include camps with active booking
            registered_camps = CampAppointment.objects.filter(
                donor=donor, status="BOOKED"
            ).values_list("camp_id", flat=True)
            context["registered_camps"] = set(registered_camps)
        else:
            context["registered_camps"] = set()
        return context

# Donor: Register for a camp slot
class DonorRegisterCampView(LoginRequiredMixin, View):
    template_name = "camp/donor_register_camp.html"

    def get(self, request, pk):
        camp = get_object_or_404(Camp, pk=pk)
        form = DonorCampRegistrationForm(camp=camp)
        return render(request, self.template_name, {"form": form, "camp": camp})

    def post(self, request, pk):
        camp = get_object_or_404(Camp, pk=pk)
        form = DonorCampRegistrationForm(request.POST, camp=camp)

        if form.is_valid():
            slot = form.cleaned_data["slot"]
            donor = request.user.donorprofile

            # prevent double booking
            if CampAppointment.objects.filter(camp=camp, donor=donor, status="BOOKED").exists():
                messages.error(request, "You have already booked a slot for this camp.")
                return redirect("camp:donor_registered_camp")

            try:
                appointment = CampAppointment.objects.create(
                    camp=camp,
                    slot=slot,
                    donor=donor,
                    status="BOOKED"
                )
            except IntegrityError:
                # Safety net in case of race condition
                messages.error(request, "You already have a booking for this slot.")
                return redirect("camp:donor_registered_camp")

            # update slot count
            slot.booked_count += 1
            slot.save()

            send_mail(
                subject="Blood Donation Camp Detials",
                message=f""" 
Dear {donor.first_name},
Congratulations! Your registration for the blood donation camp has been confirmed.
Camp Details:
Name: {camp.name}
Date: {camp.date}
Time:{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}
Location: {camp.address}

Please make sure to arrive on time and follow the guidelines.

Thank you for supporting our mission!

Regards,
Lifenet Team""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[donor.user.email],
                fail_silently=False,
                )
            messages.success(request, "Your appointment has been booked successfully.")
            return redirect("camp:donor_registered_camp")

        return render(request, self.template_name, {"form": form, "camp": camp})

# Donor: View registered camps
class DonorRegisteredCampsView(LoginRequiredMixin,ListView):
    model = CampAppointment
    template_name = "camp/donor_registered_camps.html"
    context_object_name = "appointments"

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "donorprofile"):
            details= CampAppointment.objects.filter(donor=user.donorprofile).order_by("-camp__date")
            return details
        else:
            messages.error(self.request, "You must have a donor profile to view this page.")
            return CampAppointment.objects.none()

class DonorCancelCampView(LoginRequiredMixin, View):
    def post(self, request, pk):
        camp = get_object_or_404(Camp, pk=pk)
        donor = request.user.donorprofile

        # find booked appointment
        appointment = CampAppointment.objects.filter(
            camp=camp, donor=donor, status="BOOKED"
        ).first()

        if not appointment:
            messages.error(request, "You don’t have any active booking for this camp.")
            return redirect("camp:donor_registered_camp")

        # update status
        appointment.status = "CANCELLED"
        appointment.save()

        # update slot count
        if appointment.slot.booked_count > 0:
            appointment.slot.booked_count -= 1
            appointment.slot.save()

        messages.success(request, "Your appointment has been cancelled successfully.")
        return redirect("camp:donor_registered_camp")

# Organizer: Create camp (with slots)
class OrganizerCampCreateView(LoginRequiredMixin, View):
    template_name = "camp/organizer_camp_form.html"

    def get(self, request):
        form = CampForm()
        SlotFormSet = modelformset_factory(CampSlot, form=CampSlotForm, extra=3, can_delete=False)
        formset = SlotFormSet(queryset=CampSlot.objects.none())

        # Pre-fill and disable org/bloodbank fields
        if hasattr(request.user, "organizationprofile"):
            form.fields["organization"].initial = request.user.organizationprofile
            form.fields["organization"].disabled = True

        if hasattr(request.user, "bloodbankprofile"):
            form.fields["bloodbank"].initial = request.user.bloodbankprofile
            form.fields["bloodbank"].disabled = True
        
        elif hasattr(request.user, "staffprofile"):
            form.fields["bloodbank"].initial = request.user.staffprofile.bloodbank_name
            form.fields["bloodbank"].disabled = True

        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request):
        form = CampForm(request.POST)
        SlotFormSet = modelformset_factory(CampSlot, form=CampSlotForm, extra=3, can_delete=False)
        formset = SlotFormSet(request.POST, queryset=CampSlot.objects.none())

        user = request.user

        # Pre-fill and disable org/bloodbank fields even on POST
        if hasattr(user, "organizationprofile"):
            form.fields["organization"].initial = user.organizationprofile
            form.fields["organization"].disabled = True

        if hasattr(user, "bloodbankprofile"):
            form.fields["bloodbank"].initial = user.bloodbankprofile
            form.fields["bloodbank"].disabled = True

        elif hasattr(user, "staffprofile"):
            form.fields["bloodbank"].initial = user.staffprofile.bloodbank_name
            form.fields["bloodbank"].disabled = True

        if form.is_valid() and formset.is_valid():
            camp = form.save(commit=False)
            camp.status = "UPCOMING"   # enforce here

            if hasattr(user, "organizationprofile"):
                camp.organization = user.organizationprofile
                if not camp.bloodbank:  # if no bloodbank selected
                    messages.error(request, "Organization must select a Blood Bank to create a camp.")
                    return render(request, self.template_name, {"form": form, "formset": formset})
            
            # Auto attach org/bloodbank
            if hasattr(user, "organizationprofile"):
                camp.organization = user.organizationprofile
            if hasattr(user, "bloodbankprofile"):
                camp.bloodbank = user.bloodbankprofile

            # Check at least one slot filled
            has_slot = any(slot_form.cleaned_data for slot_form in formset)
            if not has_slot:
                messages.error(request, "Please enter at least one slot for the camp.")
                return render(request, self.template_name, {"form": form, "formset": formset})
            camp.save()

            for slot_form in formset:
                if slot_form.cleaned_data:
                    slot = slot_form.save(commit=False)
                    slot.camp = camp
                    slot.save()

            messages.success(request, "Camp created successfully with slots.")
            return redirect("camp:organizer_camp_list")

        # If invalid, re-render with pre-filled fields
        return render(request, self.template_name, {"form": form, "formset": formset})

# Organizer: List camps they organize
class OrganizerCampListView(LoginRequiredMixin, View):
    template_name = "camp/organizer_camp_list.html"

    def get(self, request):
        if request.user.role == "BLOODBANK":
            camps = Camp.objects.filter(bloodbank=request.user.bloodbankprofile)
        elif request.user.role == "STAFF":
            camps = Camp.objects.filter(bloodbank=request.user.staffprofile.bloodbank_name)
        elif request.user.role == "ORG":
            camps = Camp.objects.filter(organization=request.user.organizationprofile)
        else:
            camps = Camp.objects.none()
        
        # Update statuses automatically
        for camp in camps:
            camp.update_status()

        # Custom ordering: UPCOMING → CURRENT → DONE
        status_order = Case(
            When(status="UPCOMING", then=Value(1)),
            When(status="CURRENT", then=Value(2)),
            When(status="DONE", then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )

        camps = camps.order_by(status_order, "date", "start_time")

        return render(request, self.template_name, {"camps": camps})

# Organizer: Update camp
class OrganizerCampUpdateView(LoginRequiredMixin, View):
    template_name = "camp/organizer_camp_form.html"

    def get(self, request, pk):
        camp = get_object_or_404(Camp, id=pk)
        form = CampForm(instance=camp)
        return render(request, self.template_name, {"form": form, "camp": camp})

    def post(self, request, pk):
        camp = get_object_or_404(Camp, id=pk)
        form = CampForm(request.POST, instance=camp)

        if form.is_valid():
            form.save()
            messages.success(request, "Camp updated successfully.")
            return redirect("camp:organizer_camp_list")

        return render(request, self.template_name, {"form": form, "camp": camp})
    
class UpdateCampStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        camp = get_object_or_404(Camp, id=pk)

        # Don't allow changing if DONE
        if camp.status == "DONE":
            messages.error(request, "Cannot change status of a completed camp.")
            return redirect("camp:organizer_camp_list")

        new_status = request.POST.get("status")
        if new_status in dict(Camp.STATUS_CHOICES).keys():
            camp.status = new_status
            camp.save()
            messages.success(request, "Camp status updated successfully.")
        return redirect("camp:organizer_camp_list")
          
# Organizer: Cancel camp
class OrganizerCampCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        camp = get_object_or_404(Camp, id=pk)
        camp.delete()
        messages.success(request, "Camp cancelled successfully.")
        return redirect("camp:organizer_camp_list")

# Organizer: View booked donors
class OrganizerCampDonorsView(LoginRequiredMixin, View):
    template_name = "camp/organizer_camp_donors.html"
    def get(self, request, pk):
        camp = get_object_or_404(Camp, id=pk)
        status_order = Case(
            When(status="BOOKED", then=Value(1)),
            When(status="VISITED", then=Value(2)),
            When(status="CANCELLED", then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
        appointments = CampAppointment.objects.filter(camp=camp).select_related("donor", "slot").order_by(status_order)
        return render(request, self.template_name, {"camp": camp, "appointments": appointments})

class PublicUpcomingCampsView(ListView):
    model = Camp
    template_name = "camp/public_upcoming_camps.html"
    context_object_name = "camps"
    form_class = CampSearchForm

    def get_queryset(self):
        # Start with upcoming camps (exclude DONE)
        camps = Camp.objects.exclude(status="DONE")
        self.form = self.form_class(self.request.GET or None)

        if self.form.is_valid():
            location = self.form.cleaned_data.get("location")
            if location:
                camps = camps.filter(
                    Q(city__iexact=location) | Q(city__icontains=location)
                )

        return camps

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pass search form to template
        context["form"] = self.form
        return context
    
class UpdateAppointmentStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        appointment = get_object_or_404(CampAppointment, id=pk)

        if appointment.status == "VISITED":
            messages.info(request, "This donor is already marked as Visited.")
        elif appointment.status == "CANCELLED":
            messages.error(request, "Cannot mark a cancelled appointment as Visited.")
        else:
            appointment.status = "VISITED"
            appointment.save()
            messages.success(request, f"{appointment.donor.user.get_full_name()} marked as Visited.")

        return redirect(request.META.get("HTTP_REFERER", "camp:organizer_camp_list"))