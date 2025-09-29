from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, RedirectView,TemplateView,View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm
from .models import CustomUser
from users.forms import *
from django.contrib import messages
from core.views import DashboardRedirectView
from users.models import *
from django.db import IntegrityError,transaction
# Create your views here.

#Login View
class UserLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = self.kwargs.get("role").upper()
        context["role"] = role.lower()
        return context

    def form_valid(self, form):
        user = form.get_user()
        role = self.kwargs.get("role").upper()

        # Role mismatch
        if user.role != role:
            messages.error(self.request, f"You are not authorized to login as {role.title()}.")
            return redirect("accounts:login", role=role.lower())

        # BLOODBANK check
        if user.role == "BLOODBANK":
            if not hasattr(user, "bloodbankprofile") or user.bloodbankprofile.approval_status != "Approved":
                messages.error(self.request, "Your BloodBank account is not approved yet.")
                return redirect("accounts:login", role="bloodbank")

        # ORGANIZATION check
        if user.role == "ORG":
            if not hasattr(user, "organizationprofile") or user.organizationprofile.approval_status != "Approved":
                messages.error(self.request, "Your Organization account is not approved yet.")
                return redirect("accounts:login", role="org")

        # STAFF check
        if user.role == "STAFF":
            if not hasattr(user, "staffprofile") or user.staffprofile.approval_status != "Approved":
                messages.error(self.request, "Your Staff account is not approved yet by your BloodBank.")
                return redirect("accounts:login", role="staff")
        
        if user.role == "ADMIN":
            if not hasattr(user, "adminprofile"):
                messages.error(self.request, "Admin profile not found. Please contact support.")
                return redirect("accounts:login", role="admin")
        
        messages.success(self.request, f"You are successfully logged in as {user.role.title()}.")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("core:dashboard")

# Registration View
class BaseRegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm

    role = None
    profile_form_class = None  # set this in subclasses, e.g. DonorProfileForm
    object=None

    def get_success_url(self):
        return reverse_lazy("accounts:login", kwargs={"role": self.role.lower()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If view passed in profile_form explicitly, use it; otherwise create an empty one
        context["profile_form"] = kwargs.get(
            "profile_form",
            self.profile_form_class()
        )
        context["role"] = self.role
        return context

    def post(self, request, *args, **kwargs):
        # bind the user form using CreateView machinery
        user_form = self.get_form()  # bound with request.POST by default
        # bind profile form with POST and FILES
        profile_form = self.profile_form_class(request.POST, request.FILES)

        # If either form is invalid -> show errors and DO NOT save anything
        if not user_form.is_valid() or not profile_form.is_valid():
            # Set autofocus on the first field that has an error (user_form preferred)
            if not user_form.is_valid():
                first_field = list(user_form.errors.keys())[0]
                if first_field in user_form.fields:
                    user_form.fields[first_field].widget.attrs.update({"autofocus": "autofocus"})
            else:
                first_field = list(profile_form.errors.keys())[0]
                if first_field in profile_form.fields:
                    profile_form.fields[first_field].widget.attrs.update({"autofocus": "autofocus"})

            messages.error(request, "Please correct the errors below.")
            return self.render_to_response(
                self.get_context_data(form=user_form, profile_form=profile_form)
            )

        # Both forms valid -> save both inside a transaction
        try:
            with transaction.atomic():
                # Save user (UserCreationForm handles password hashing)
                user = user_form.save(commit=False)
                user.role = self.role
                user.save()
                
                try:
                    user_form.save_m2m()
                except Exception:
                    
                    pass

                
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.full_clean()
                profile.save()
                try:
                    profile_form.save_m2m()
                except Exception:
                    pass

        except IntegrityError:
            messages.error(request, "Something went wrong. Please try again.")
            return self.render_to_response(
                self.get_context_data(form=user_form, profile_form=profile_form)
            )

        messages.success(request, f"{self.role} account created successfully! You can now log in.")
        return HttpResponseRedirect(self.get_success_url())
    
class DonorRegisterView(BaseRegisterView):
    role = "DONOR"
    profile_form_class = DonorProfileForm
    template_name = "accounts/register_donor.html"

class PatientRegisterView(BaseRegisterView):
    role = "PATIENT"
    profile_form_class = PatientProfileForm
    template_name = "accounts/register_patient.html"

class BloodBankRegisterView(BaseRegisterView):
    role = "BLOODBANK"
    profile_form_class = BloodBankProfileForm
    template_name = "accounts/register_bloodbank.html"

class OrganizationRegisterView(BaseRegisterView):
    role = "ORG"
    profile_form_class = OrganizationProfileForm
    template_name = "accounts/register_org.html"

class StaffRegisterView(BaseRegisterView):
    role = "STAFF"
    profile_form_class = StaffProfileForm
    template_name = "accounts/register_staff.html"

'''class AdminRegisterView(BaseRegisterView):
    role = "ADMIN"
    profile_form_class = AdminProfileForm
    template_name = "accounts/register_admin.html"'''

# Logout View
class UserLogoutView(LogoutView):
    next_page = reverse_lazy("homepage")

#View Profile
class ProfileView(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'accounts/profile.html'

    def get(self, request, *args, **kwargs):
        # fetch user with related profiles in one query
        user = get_object_or_404(
            CustomUser.objects.select_related(
                "donorprofile",
                "patientprofile",
                "organizationprofile",
                "bloodbankprofile",
                "staffprofile",
                "adminprofile"
            ),
            id=request.user.id,
        )
        return render(request, self.template_name, {"user": user})


