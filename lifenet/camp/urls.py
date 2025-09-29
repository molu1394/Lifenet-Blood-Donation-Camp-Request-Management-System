from django.urls import path
from . import views

app_name = "camp"

urlpatterns = [

    # ---------------- Organizer Routes ----------------
    path("organizer/camps/",views.OrganizerCampListView.as_view(),name="organizer_camp_list"),

    path("organizer/camps/create/",views.OrganizerCampCreateView.as_view(),name="organizer_camp_create"),
    
    path("organizer/camps/<int:pk>/update/",views.OrganizerCampUpdateView.as_view(),name="organizer_camp_update"),

    path("organizer/camps/<int:pk>/cancel/",views.OrganizerCampCancelView.as_view(),name="organizer_camp_cancel"),

    path("organizer/camps/<int:pk>/donors/",views.OrganizerCampDonorsView.as_view(),name="organizer_camp_donors"),

    path("organizer/camps/<int:pk>/status/",views.UpdateCampStatusView.as_view(),name="update_status"),

    path("appointment/<int:pk>/attend/", views.UpdateAppointmentStatusView.as_view(), name="mark_visited"),

    # ---------------- Donor Routes ----------------
    path("donor/camps/upcoming/",views.DonorUpcomingCampsView.as_view(),name="donor_upcoming_camp"),

    path("donor/camps/<int:pk>/register/",views.DonorRegisterCampView.as_view(),name="donor_register_camp"),

    path("donor/camps/registered/",views.DonorRegisteredCampsView.as_view(),name="donor_registered_camp"),

    path("upcoming-camps/", views.PublicUpcomingCampsView.as_view(), name="public_upcoming_camps"),

    path("cancel/<int:pk>/", views.DonorCancelCampView.as_view(), name="donor_cancel_camp"),
]
