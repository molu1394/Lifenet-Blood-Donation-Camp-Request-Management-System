from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import TemplateView,View,ListView,FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import BloodBankProfile,StaffProfile,DonorProfile
from accounts.forms import CustomUserUpdateForm,CustomPasswordChangeForm
from .forms import BloodBankProfileUpdateForm,StaffProfileUpdateForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from patients.models import BloodRequest,Notification
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.
class BloodBankDashboardView(TemplateView):
    template_name = "bloodbanks/bloodbank_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Assuming each user has one BloodBankProfile
        bloodbank = get_object_or_404(BloodBankProfile, user=self.request.user)
        context["bloodbankprofile"] = bloodbank
        return context

class StaffDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "bloodbanks/staff_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff = get_object_or_404(StaffProfile, user=self.request.user)
        context["staff"] = staff
        return context
    
class StaffApprovalListView(LoginRequiredMixin, ListView):
    model = StaffProfile
    template_name = "bloodbanks/staff_approval_list.html"
    context_object_name = "staff_members"

    def get_queryset(self):
        # get the logged-in user's bloodbank profile
        try:
            bloodbank = self.request.user.bloodbankprofile
        except BloodBankProfile.DoesNotExist:
            return StaffProfile.objects.none()

        # fetch all staff linked to this bloodbank
        return StaffProfile.objects.filter(bloodbank_name=bloodbank).order_by("-approval_status")
       
class StaffApprovalActionView(LoginRequiredMixin, View):
    def post(self, request, staff_id, action):
        staff = get_object_or_404(StaffProfile, id=staff_id, bloodbank_name=request.user.bloodbankprofile)

        if action == "approve":
            staff.approval_status = "Approved"
            messages.success(request, f"{staff.user.username} has been approved.")
        elif action == "deny":
            staff.approval_status = "Denied"
            messages.warning(request, f"{staff.user.username} has been denied.")
        else:
            messages.error(request, "Invalid action.")

        staff.save()
        return redirect("bloodbanks:staff-approval-list")
    
class BloodBankProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'bloodbanks/bloodbank_update_profile.html'

    def get(self, request):
        try:
            profile = request.user.bloodbankprofile
        except BloodBankProfile.DoesNotExist:
            messages.error(request, "BloodBank profile does not exist. Contact admin.")
            return redirect('accounts:profile')

        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = BloodBankProfileUpdateForm(instance=profile)
        password_form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form
        })

    def post(self, request):
        try:
            profile = request.user.bloodbankprofile
        except BloodBankProfile.DoesNotExist:
            messages.error(request, "BloodBank profile does not exist. Contact admin.")
            return redirect('accounts:profile')

        user_form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = BloodBankProfileUpdateForm(request.POST, instance=profile)
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
                update_session_auth_hash(request, user)  # keeps user logged in
                messages.success(request, "Password changed successfully")
                return redirect('accounts:profile')
            messages.error(request, "Password change failed")

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form
        })

class StaffProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'bloodbanks/staff_update_profile.html'

    def get(self, request):
        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = StaffProfileUpdateForm(instance=request.user.staffprofile)
        password_form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form
        })

    def post(self, request):
        user_form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = StaffProfileUpdateForm(request.POST, request.FILES, instance=request.user.staffprofile)
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
                update_session_auth_hash(request, user)  # keeps user logged in
                messages.success(request, "Password changed successfully")
                return redirect('accounts:profile')
            messages.error(request, "Password change failed")

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form
        })
    
class BloodBankRequestListView(LoginRequiredMixin, ListView):
    model = BloodRequest
    template_name = "bloodbanks/bloodbanks_requests.html"
    context_object_name = "requests"

    def get_queryset(self):
        user = self.request.user

        if user.role == "BLOODBANK":
            bloodbank = get_object_or_404(BloodBankProfile, user=user)

        elif user.role == "STAFF":
            staff = get_object_or_404(StaffProfile, user=user)
            bloodbank = staff.bloodbank_name 

        else:
            return BloodRequest.objects.none()

        return BloodRequest.objects.filter(
            bloodbank=bloodbank
        ).order_by("-created_at")
    
class BloodBankRequestActionView(LoginRequiredMixin, View):
    def post(self, request, pk, action):
        user = request.user

        if user.role == "BLOODBANK":
            bank_request = get_object_or_404(BloodRequest, id=pk, bloodbank__user=user)

        elif user.role == "STAFF":
            staff = get_object_or_404(StaffProfile, user=user)
            bank_request = get_object_or_404(BloodRequest, id=pk, bloodbank=staff.bloodbank_name)

        else:
            messages.error(request, "You are not authorized to perform this action.")
            return redirect("accounts:dashboard-redirect")

        if action == "accept":
            bank_request.status = "accepted"
            bank_request.decline_by = None

            if user.role == "BLOODBANK":
                bank_request.accepted_by = user  # store the CustomUser of the blood bank
            elif user.role == "STAFF":
                staff = get_object_or_404(StaffProfile, user=user)
                bank_request.accepted_by = staff.user   # if bank admin accepts directly

            message = (
                f"Your blood request has been ACCEPTED by BloodBank "
                f"{bank_request.bloodbank.bloodbank_name}. "
                f"Contact: {bank_request.bloodbank.mobile_number}"
            )

        elif action == "decline":
            bank_request.status = "declined"
            bank_request.accepted_by = None  # clear accepted_by if declined

            if user.role == "BLOODBANK":
                bank_request.decline_by = user  # store the CustomUser of the blood bank
            elif user.role == "STAFF":
                staff = get_object_or_404(StaffProfile, user=user)
                bank_request.decline_by = staff.user

            message = (
                f"Your blood request has been DECLINED by BloodBank "
                f"{bank_request.bloodbank.bloodbank_name}."
            )
        else:
            messages.error(request, "Invalid action.")
            return redirect("bloodbanks:patients_requests")

        bank_request.save()

        Notification.objects.create(user=bank_request.patient, message=message)

        send_mail(
            subject="Update on your Blood Request",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[bank_request.patient.email],
            fail_silently=True,
        )

        messages.success(request, "Request updated and patient notified.")
        return redirect("bloodbanks:patients_requests")
    
class BloodBankDonorListView(LoginRequiredMixin, ListView):
    model = DonorProfile
    template_name = "bloodbanks/donor_list.html"
    context_object_name = "donors"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blood_groups"] = "A+ A- B+ B- O+ O- AB+ AB-".split()
        return context

    def get_queryset(self):
        queryset = DonorProfile.objects.filter(ready_to_donate=True)

        blood_group = self.request.GET.get("blood_group")
        location = self.request.GET.get("location")

        if blood_group:
            queryset = queryset.filter(blood_group__iexact=blood_group)

        if location:
            queryset = queryset.filter(address__icontains=location)

        return queryset