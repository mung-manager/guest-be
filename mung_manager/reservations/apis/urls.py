from django.urls import path

from mung_manager.reservations.apis.api_managers import (
    CustomerPetListAPIManager,
    CustomerTicketListAPIManager,
)

urlpatterns = [
    path(
        "/customers/pets",
        CustomerPetListAPIManager.as_view(),
        name="customer-pet-list",
    ),
    path(
        "/customers/tickets",
        CustomerTicketListAPIManager.as_view(),
        name="customer-ticket-list",
    ),
]
