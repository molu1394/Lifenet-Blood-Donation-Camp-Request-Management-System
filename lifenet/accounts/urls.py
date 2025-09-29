from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm 
from .forget_password import ForgotPasswordView,ResetPasswordView

app_name='accounts'

urlpatterns = [
    path("login/<str:role>/",views.UserLoginView.as_view(authentication_form=CustomAuthenticationForm), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("register/donor/",views.DonorRegisterView.as_view(), name="register-donor"),
    path("register/patient/",views.PatientRegisterView.as_view(), name="register-patient"),
    path("register/bloodbank/",views.BloodBankRegisterView.as_view(), name="register-bloodbank"),
    path("register/Organizations/",views.OrganizationRegisterView.as_view(), name="register-org"),
    path("register/staff/",views.StaffRegisterView.as_view(), name="register-staff"),
    #path("register/admin/",views.AdminRegisterView.as_view(), name="register-admin"),
    path("profile/",views.ProfileView.as_view(),name='profile'),
    
    #forget password
    path("forgot-password/<str:role>/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/<uidb64>/<token>/",ResetPasswordView.as_view(),name="reset_password",
)
]

