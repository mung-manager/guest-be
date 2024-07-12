from django.urls import path

from mung_manager.reservations.apis.api_managers import (
    ReservationCustomerPetListAPIManager,
    ReservationCustomerTicketListAPIManager,
    ReservationCustomerTicketTypeDetailAPIManager,
    ReservationTicketCheckExpirationAPIManager,
)

urlpatterns = [
    path(
        "/customers/pets",
        ReservationCustomerPetListAPIManager.as_view(),
        name="customer-pet-list",
    ),
    path(
        "/customers/tickets",
        ReservationCustomerTicketListAPIManager.as_view(),
        name="customer-ticket-list",
    ),
    path(
        "/customers/ticket-types/details",
        ReservationCustomerTicketTypeDetailAPIManager.as_view(),
        name="customer-ticket-type-detail",
    ),
    path(
        "/<int:reservation_id>/tickets/check-expiration",
        ReservationTicketCheckExpirationAPIManager.as_view(),
        name="ticket-check-expiration",
    ),
]
