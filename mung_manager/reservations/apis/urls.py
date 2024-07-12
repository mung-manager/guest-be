from django.urls import path

from mung_manager.reservations.apis.api_managers import (
    ReservationCustomerPetListAPIManager,
    ReservationCustomerTicketListAPIManager,
    ReservationCustomerTicketTypeDetailAPIManager,
    ReservationPetKindergardenAvailableDatesAPIManager,
    ReservationCustomerTicketTypesAPIManager,
    ReservationTicketCheckExpirationAPIManager,
)

urlpatterns = [
    path(
        "/customers/pets",
        ReservationCustomerPetListAPIManager.as_view(),
        name="customer-pet-list",
    ),
    path(
        "/customers/ticket-types",
        ReservationCustomerTicketTypesAPIManager.as_view(),
        name="customer-ticket-types",
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
    path(
        "/pet-kindergardens/available-dates",
        ReservationPetKindergardenAvailableDatesAPIManager.as_view(),
        name="pet-kindergarden-available-dates",
    ),
]
