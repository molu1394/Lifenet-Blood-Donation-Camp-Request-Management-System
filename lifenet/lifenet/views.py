from django.views.generic import TemplateView
from core.forms import ContactForm
from django.contrib import messages
from django.shortcuts import redirect,get_object_or_404,render


def homepage_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your query has been submitted successfully. We’ll get back to you soon.")
            return redirect("homepage")
    else:
        form = ContactForm()

    return render(request, "homepage.html", {"form": form})