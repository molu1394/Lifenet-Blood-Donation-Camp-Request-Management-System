from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views import View
from .models import CustomUser  # adjust to your user model
import threading
from .forms import ResetPasswordForm

# Step 1: Request reset
class ForgotPasswordView(View):
    def get(self, request, role=None):
        return render(request, "accounts/forgot_password.html", {"role": role})

    def post(self, request, role=None):
        email = request.POST.get("email")
        if not email:
            messages.error(request, "Please enter an email.")
            return redirect("accounts:forgot_password", role=role)

        users = CustomUser.objects.filter(email=email, role__iexact=role)
        if not users.exists():
            messages.error(request, f"No {role} account found with this email.")
            return redirect("accounts:forgot_password", role=role)

        for user in users:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                                    reverse_lazy("accounts:reset_password", kwargs={
                                        "uidb64": uidb64,
                                        "token": token
                                    })
                                )

            # Send email asynchronously
            def send_email():
                try:
                    send_mail(
                        "Password Reset",
                        f"Click here to reset your password: {reset_link}",
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                    )
                except Exception as e:
                    print("Error sending email:", e)
            
            threading.Thread(target=send_email).start()

        messages.success(request, "Password reset link has been sent to your email.")
        return redirect("accounts:login", role=role)


# Step 2: Reset link → form
class ResetPasswordView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user)
            for field in form.fields.values():
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = 'Enter password'
            return render(request, "accounts/reset_password.html", {"form": form, "uidb64": uidb64, "token": token})
        else:
            messages.error(request, "Invalid or expired reset link.")
            return redirect("accounts:forgot_password")

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user, request.POST)
            for field in form.fields.values():
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = 'Enter password'
            if form.is_valid():
                form.save()
                messages.success(request, "Password reset successful! Please login.")
                return redirect("homepage")  # redirect to login page
            else:
                return render(request, "accounts/reset_password.html", {"form": form, "uidb64": uidb64, "token": token})
        else:
            messages.error(request, "Invalid reset attempt.")
            return redirect("accounts:forgot_password")