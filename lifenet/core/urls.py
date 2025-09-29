from django.urls import path,include
from . import views

app_name='core'

urlpatterns = [
    path("dashboard/",views.DashboardRedirectView.as_view(), name="dashboard"),

    path("dashboard/admin/",views.AdminDashboardView.as_view(), name="admin-dashboard"),

    path('accounts/', include("accounts.urls", namespace="accounts")),

    path('update/',views.AdminProfileUpdateView.as_view(),name='admin_profile_update'),
    path("admin/approvals/",views.AdminApprovalListView.as_view(), name="admin-approval-list"),
    path("admin/approvals/<str:model_name>/<int:pk>/action/",views.AdminApprovalActionView.as_view(), name="admin-approval-action"),
    path("",views.contact_view,name='contactus'),
    path("queries/", views.ContactQueryListView.as_view(), name="contact_queries_list"),
]