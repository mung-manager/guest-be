from django.urls import path

from mung_manager.customers.apis.api_managers import (
    CustomerTicketCountAPIManager,
    CustomerReservationListAPIManager,
)

urlpatterns = [
    path(
        "/tickets/count",
        CustomerTicketCountAPIManager.as_view(),
        name="customer-ticket-count",
    ),
    path(
        "/reservations",
        CustomerReservationListAPIManager.as_view(),
        name="customer-reservation-list",
    ),
]
