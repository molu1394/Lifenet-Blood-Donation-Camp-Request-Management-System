from django.urls import path
from . import views

app_name='organizations'

urlpatterns = [
    path("dashboard/organizations/",views.OrgDashboardView.as_view(), name="organizations-dashboard"),
    path('update/', views.OrgProfileUpdateView.as_view(), name='org_profile_update'),

    
]