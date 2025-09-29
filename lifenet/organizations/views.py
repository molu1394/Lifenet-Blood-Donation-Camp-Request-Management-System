from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import TemplateView,View
from users.models import OrganizationProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from accounts.forms import CustomUserUpdateForm,CustomPasswordChangeForm
from .forms import OrgProfileUpdateForm
from django.contrib.auth import update_session_auth_hash


# Create your views here.
class OrgDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "organizations/org_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org= get_object_or_404(OrganizationProfile, user=self.request.user)
        context["organizations"] = org
        return context
    
class OrgProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'organizations/org_update_profile.html'

    def get(self, request):
        try:
            profile = request.user.organizationprofile
        except OrganizationProfile.DoesNotExist:
            messages.error(request, "ORG profile does not exist. Contact admin.")
            return redirect('accounts:profile')

        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = OrgProfileUpdateForm(instance=profile)
        password_form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form
        })

    def post(self, request):
        try:
            profile = request.user.organizationprofile
        except OrganizationProfile.DoesNotExist:
            messages.error(request, "ORG profile does not exist. Contact admin.")
            return redirect('accounts:profile')

        user_form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = OrgProfileUpdateForm(request.POST, instance=profile)
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