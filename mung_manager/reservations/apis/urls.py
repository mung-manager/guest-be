from django.urls import path

from mung_manager.reservations.apis.api_managers import CustomerPetAndTicketListAPIManager

urlpatterns = [
    path(
        "/customers/pets-and-tickets",
        CustomerPetAndTicketListAPIManager.as_view(),
        name="customer-pet-and-ticket-list",
    ),
]
