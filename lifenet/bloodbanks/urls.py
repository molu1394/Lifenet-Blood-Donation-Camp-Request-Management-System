from django.urls import path
from . import views

app_name='bloodbanks'

urlpatterns = [
    path("dashboard/bloodbank/",views.BloodBankDashboardView.as_view(), name="bloodbank_dashboard"),
    path("dashboard/staff/",views.StaffDashboardView.as_view(), name="staff_dashboard"),
    path('update/', views.BloodBankProfileUpdateView.as_view(), name='bloodbank_profile_update'),
    path('staff/update/', views.StaffProfileUpdateView.as_view(), name='staff_profile_update'),
    path('requests/<int:pk>/<str:action>',views.BloodBankRequestActionView.as_view(),name='bloodbank_request_action'),
    path("requests/",views.BloodBankRequestListView.as_view(),name="patients_requests"),
    path("donors/",views.BloodBankDonorListView.as_view(), name="donor_list"), 
    path("staff/approvals/", views.StaffApprovalListView.as_view(), name="staff-approval-list"),
    path("staff/approve/<int:staff_id>/<str:action>/", views.StaffApprovalActionView.as_view(), name="staff-approval-action"),
]
