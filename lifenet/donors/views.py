from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView,ListView,View
from users.models import DonorProfile,PatientProfile
from patients.models import BloodRequest,Notification
from users.forms import DonorProfileForm
from accounts.forms import CustomUserUpdateForm,CustomPasswordChangeForm
from .forms import DonorProfileUpdateForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

class DonorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "donors/donor_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        donor = get_object_or_404(DonorProfile, user=self.request.user)
        context["donor"] = donor
        return context


class DonorRequestListView(LoginRequiredMixin, ListView):
    model = BloodRequest
    template_name = "donors/donor_requests.html"
    context_object_name = "requests"

    def get_queryset(self):
        donor = get_object_or_404(DonorProfile, user=self.request.user)
        return BloodRequest.objects.filter(donor=donor).order_by("-created_at")
    
class DonorRequestActionView(LoginRequiredMixin, View):
    def post(self, request, pk, action):
        donor_request = get_object_or_404(BloodRequest, id=pk, donor__user=request.user)
        
        if action == "accept":
            donor_request.status = "accepted"
            message = f"Your blood request has been ACCEPTED by donor {donor_request.donor.first_name} {donor_request.donor.last_name}. Contact: {donor_request.donor.mobile_number}"
        elif action == "decline":
            donor_request.status = "declined"
            message = f"Your blood request has been DECLINED by donor {donor_request.donor.first_name} {donor_request.donor.last_name}."
        
        donor_request.save()

        Notification.objects.create(user=donor_request.patient, message=message)
    
        send_mail(
            subject="Update on your Blood Request",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[donor_request.patient.email],
            fail_silently=True,
        )

        messages.success(request, "Request updated and patient notified.")
        return redirect("donors:donor_requests")
    
class DonorProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'donors/donor_update_profile.html'

    def get(self, request):
        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = DonorProfileUpdateForm(instance=request.user.donorprofile)
        password_form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,   
            'password_form': password_form
        })

    def post(self, request):
        user_form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = DonorProfileUpdateForm(request.POST, request.FILES, instance=request.user.donorprofile)
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