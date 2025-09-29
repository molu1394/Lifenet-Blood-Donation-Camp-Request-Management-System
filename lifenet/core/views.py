from django.views.generic import TemplateView,View,ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.shortcuts import redirect,get_object_or_404,render
from users.models import AdminProfile,BloodBankProfile,OrganizationProfile
from django.contrib import messages
from accounts.forms import CustomUserUpdateForm,CustomPasswordChangeForm
from .forms import AdminProfileUpdateForm,ContactForm
from django.contrib.auth import update_session_auth_hash
from .models import ContactQuery

class DashboardRedirectView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect("accounts:login", role="donor")  # default if not logged in

        if user.role == "DONOR":
            return redirect("donors:donor-dashboard")
        elif user.role == "PATIENT":
            return redirect("patients:patient-dashboard")
        elif user.role == "BLOODBANK":
            return redirect("bloodbanks:bloodbank_dashboard")
        elif user.role == "ORG":
            return redirect("organizations:organizations-dashboard")
        elif user.role == "STAFF":
            return redirect("bloodbanks:staff_dashboard")
        elif user.role == "ADMIN":
            return redirect("core:admin-dashboard")

        return redirect("home")
    
class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin = get_object_or_404(AdminProfile, user=self.request.user)
        context["admin"] = admin
        return context
    
class AdminProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'core/admin_update_profile.html'

    def get(self, request):
        try:
            profile = request.user.adminprofile
        except AdminProfile.DoesNotExist:
            messages.error(request, "Admin profile does not exist.")
            return redirect('accounts:profile')

        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = AdminProfileUpdateForm(instance=profile)
        password_form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form
        })

    def post(self, request):
        try:
            profile = request.user.adminprofile
        except AdminProfile.DoesNotExist:
            messages.error(request, "Admin profile does not exist")
            return redirect('accounts:profile')

        user_form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = AdminProfileUpdateForm(request.POST, instance=profile)
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

class AdminApprovalListView(LoginRequiredMixin,UserPassesTestMixin, View):
    template_name = "core/admin_approval_list.html"

    def test_func(self):
        return self.request.user.role and self.request.user.role.upper() == "ADMIN"    
    def get(self, request):
        bloodbanks = BloodBankProfile.objects.all().order_by("approval_status")
        organizations = OrganizationProfile.objects.all().order_by("approval_status")

        return render(request, self.template_name, {
            "bloodbanks": bloodbanks,
            "organizations": organizations,
        })

class AdminApprovalActionView(LoginRequiredMixin,UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.role and self.request.user.role.upper() == "ADMIN"  
     
    def post(self, request, model_name, pk):
        if model_name == "bloodbank":
            obj = get_object_or_404(BloodBankProfile, pk=pk)
        elif model_name == "organization":
            obj = get_object_or_404(OrganizationProfile, pk=pk)
        else:
            messages.error(request, "Invalid type")
            return redirect("core:admin-approval-list")

        action = request.POST.get("action")
        if action == "approve":
            obj.approval_status = "Approved"
            messages.success(request, f"{model_name.capitalize()} approved successfully.")
        elif action == "deny":
            obj.approval_status = "Denied"
            messages.warning(request, f"{model_name.capitalize()} denied.")
        obj.save()
        return redirect("core:admin-approval-list")

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # saves with default is_resolved = Pending
            messages.success(request, "Your query has been submitted successfully. We’ll get back to you soon.")
            return redirect("homepage")
    else:
        form = ContactForm()
    
    return render(request, "homepage.html", {"form": form})

class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated
            and hasattr(self.request.user, "role")
            and self.request.user.role.upper() == "ADMIN"
        )

class ContactQueryListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = ContactQuery
    template_name = "core/contact_quires_list.html"
    context_object_name = "queries"
    ordering = ["-created_at"]

    def post(self, request, *args, **kwargs):
        query_id = request.POST.get("query_id")
        new_status = request.POST.get("is_resolved")
        if query_id and new_status:
            try:
                query = ContactQuery.objects.get(id=query_id)
                query.is_resolved = new_status
                query.save()
            except ContactQuery.DoesNotExist:
                pass
        return redirect("core:contact_queries_list")
    
