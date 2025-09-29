from django.urls import path
from . import views

app_name='inventory'

urlpatterns = [
    # Camp inventory URLs
    path("camp/<int:camp_id>/inventory/update/", views.camp_inventory_update, name="camp_inventory_update"),    
    path("camp/<int:camp_id>/inventory/", views.CampInventoryListView.as_view(), name="camp_inventory_list"),
    path("camp/<int:camp_id>/inventory/add/", views.CampInventoryCreateView.as_view(), name="camp_inventory_add"),

    # BloodBank inventory URLs
    path("inventory/", views.InventoryListView.as_view(), name="inventory_list"),
    path("inventory/update/", views.bloodbank_inventory_update, name="bloodbank_inventory_update"),
    ]
