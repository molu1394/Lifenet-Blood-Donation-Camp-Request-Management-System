from django.urls import path
from . import views

app_name='patients'

urlpatterns = [
    path("dashboard/patients/",views.PatientDashboardView.as_view(), name="patient-dashboard"),
    path('update/', views.PatientProfileUpdateView.as_view(), name='patient_profile_update'),
    path("search/donors/",views.DonorSearchView.as_view(), name="search-donors"),
    path("search/bloodbanks/",views.BloodBankSearchView.as_view(), name="search-bloodbanks"),
    path("send-request/", views.SendBloodRequestView.as_view(), name="send-request"),
    path("my-requests/",views.MyRequestsView.as_view(), name="patient-requests"),
    path("notifications/",views.PatientNotificationsView.as_view(),name="notifications"),
    path("serchbloodbanks/", views.PublicBloodBankSearchView.as_view(), name="public_bloodbank_search"),
    path('requests/', views.BloodRequestListView.as_view(), name='request_list'),
    path("make-request/", views.BloodRequestView.as_view(), name="make_request"),
    path('accept-request/<int:pk>/', views.AcceptRequestView.as_view(), name='accept_request'),
]
