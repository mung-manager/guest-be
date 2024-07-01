from django.urls import path

from mung_manager.reservations.apis.api_managers import (
    ReservationCalendarDateListAPIManager,
    ReservationCustomerPetListAPIManager,
    ReservationCustomerTicketListAPIManager,
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
        "/calender/dates",
        ReservationCalendarDateListAPIManager.as_view(),
        name="calender-date-list",
    ),
]
