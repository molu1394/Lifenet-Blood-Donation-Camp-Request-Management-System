from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView,View,UpdateView,FormView,ListView,CreateView,DetailView
from accounts.forms import CustomUserUpdateForm,CustomPasswordChangeForm
from .forms import PatientProfileUpdateForm,DonorSearchForm, BloodBankSearchForm,PublicBloodBankSearchForm,BloodRequestForm
from users.models import PatientProfile,BloodBankProfile,DonorProfile
from inventory.models import BloodBankInventory
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import BloodRequest,Notification,GeneralBloodRequest

# Create your views here.
class PatientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "patients/patient_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_object_or_404(PatientProfile, user=self.request.user)
        context["patient"] = patient
        return context

class PatientProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'patients/patient_update_profile.html'

    def get(self, request):
        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = PatientProfileUpdateForm(instance=request.user.patientprofile)
        password_form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form
        })

    def post(self, request):
        user_form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = PatientProfileUpdateForm(request.POST, request.FILES, instance=request.user.patientprofile)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if 'update_profile' in request.POST:
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Profile updated successfully")
                return redirect('accounts:profile')
            messages.error(request, "Profile update failed")

        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # keep logged in
                messages.success(request, "Password changed successfully")
                return redirect('accounts:profile')
            messages.error(request, "Password change failed")

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form
        })
    
class DonorSearchView(LoginRequiredMixin, View):
    template_name = "patients/search_donors.html"

    def get(self, request):
        form = DonorSearchForm(request.GET or None)
        donors = DonorProfile.objects.none()  # empty initially

        if form.is_valid():
            location = form.cleaned_data.get("location")
            blood_group = form.cleaned_data.get("blood_group")

            donors = DonorProfile.objects.all()
            if location:
                donors = donors.filter(address__icontains=location)
            if blood_group:
                donors = donors.filter(blood_group=blood_group)

        return render(request, self.template_name, {
            "form": form,
            "donors": donors,
            "blood_groups": [bg for bg, _ in form.fields["blood_group"].choices if bg],
        })

# --- Search Blood Banks ---
class BloodBankSearchView(LoginRequiredMixin, ListView):
    template_name = "patients/search_bloodbanks.html"

    context_object_name = "bloodbanks"
    form_class = BloodBankSearchForm

    def get_queryset(self):
        queryset = BloodBankProfile.objects.filter(approval_status="Approved")
        request = self.request

        blood_group = request.GET.get("blood_group")
        location = request.GET.get("location")

        # Store searched blood group in session for SendBloodRequestView
        if blood_group:
            self.request.session["searched_blood_group"] = blood_group

        # Apply filters safely
        if location:
            queryset = queryset.filter(address__icontains=location)

        if blood_group:
            queryset = queryset.filter(
                inventory__blood_group=blood_group.upper(),
                inventory__units_available__gt=0
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Initialize form with GET data so values remain after search
        context["form"] = self.form_class(self.request.GET or None)
        return context

# --- Send Request ---
class SendBloodRequestView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        donor_id = request.POST.get("donor_id")
        bloodbank_id = request.POST.get("bloodbank_id")
        blood_group = request.POST.get("blood_group") or request.session.get("searched_blood_group")

        if not donor_id and not bloodbank_id:
            messages.error(request, "Invalid request.")
            return redirect("patients:patient-requests")

        if not blood_group:
            messages.error(request, "Please search again, blood group missing.")
            return redirect("patients:patient-requests")

        patient = request.user

        if donor_id and BloodRequest.objects.filter(
            patient=patient, donor_id=donor_id, status="pending"
        ).exists():
            messages.warning(request, "You already have a pending request to this donor.")
            return redirect("patients:patient-requests")

        if bloodbank_id and BloodRequest.objects.filter(
            patient=patient, bloodbank_id=bloodbank_id, status="pending"
        ).exists():
            messages.warning(request, "You already have a pending request to this bloodbank.")
            return redirect("patients:patient-requests")

        BloodRequest.objects.create(
            patient=patient,
            donor_id=donor_id if donor_id else None,
            bloodbank_id=bloodbank_id if bloodbank_id else None,
            blood_group=blood_group,
            status="pending"
        )

        messages.success(request, f"Blood request for {blood_group} sent successfully.")
        return redirect("patients:patient-requests")

class MyRequestsView(LoginRequiredMixin, ListView):
    model = BloodRequest
    template_name = "patients/my_requests.html"
    context_object_name = "requests"

    def get_queryset(self):
        return BloodRequest.objects.filter(patient=self.request.user).order_by("-created_at")
    
class PatientNotificationsView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "patients/notifications.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")
    
class PublicBloodBankSearchView(ListView):
    template_name = "patients/public_search_bloodbanks.html"
    context_object_name = "bloodbanks"

    def get_queryset(self):
        queryset = BloodBankProfile.objects.filter(approval_status="Approved")
        request = self.request

        blood_group = request.GET.get("blood_group")
        location = request.GET.get("location")

        if blood_group:
            self.request.session["searched_blood_group"] = blood_group

        if location:
            queryset = queryset.filter(Q(address__icontains=location))

        if blood_group:
            queryset = queryset.filter(
                inventory__blood_group=blood_group.upper(),
                inventory__units_available__gt=0
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["form"] = PublicBloodBankSearchForm(self.request.GET or None)
        return context

class BloodRequestListView(ListView):
    model = GeneralBloodRequest
    template_name = "patients/request_list.html"
    context_object_name = "requests"
    ordering = ["-date_requested"]

class BloodRequestView(LoginRequiredMixin, CreateView):
    model = GeneralBloodRequest
    form_class = BloodRequestForm
    template_name = "patients/make_request.html"
    context_object_name = "requests"

    def form_valid(self, form):
        patient_profile = self.request.user.patientprofile
        form.instance.requested_by = patient_profile
        form.instance.patient_name = f"{patient_profile.first_name} {patient_profile.last_name}"
        self.object = form.save()
        return redirect("patients:make_request")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            patient_profile = self.request.user.patientprofile
            context["requests"] = GeneralBloodRequest.objects.filter(
                requested_by=patient_profile
            ).order_by("-date_requested")
        except PatientProfile.DoesNotExist:
            context["requests"] = GeneralBloodRequest.objects.none()
        return context

class AcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        blood_request = get_object_or_404(GeneralBloodRequest, pk=pk)
        donor_profile = request.user.donorprofile
        blood_request.accepted_by = donor_profile
        blood_request.save()
        return redirect("patients:request_list")
