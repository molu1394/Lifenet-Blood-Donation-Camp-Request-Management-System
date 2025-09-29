from django.urls import path
from . import views

app_name='donors'

urlpatterns = [
    path("dashboard/donors/",views.DonorDashboardView.as_view(), name="donor-dashboard"),
    path("requests",views.DonorRequestListView.as_view(),name="donor_requests"),
    path("requests/<int:pk>/<str:action>",views.DonorRequestActionView.as_view(),name="donor_request_action"),
    path('update/', views.DonorProfileUpdateView.as_view(), name='donor_profile_update'),
]
