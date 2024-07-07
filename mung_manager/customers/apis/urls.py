from django.urls import path

from mung_manager.customers.apis.api_managers import (
    CustomerTicketCountAPIManager,
    CustomerTicketPurchaseListAPIManager,
    ReservationListAPIManager,
)

urlpatterns = [
    path(
        "/tickets/count",
        CustomerTicketCountAPIManager.as_view(),
        name="customer-ticket-count",
    ),
    path(
        "/reservations",
        ReservationListAPIManager.as_view(),
        name="customer-reservation-list",
    ),
    path(
        "/tickets/purchases",
        CustomerTicketPurchaseListAPIManager.as_view(),
        name="customer-ticket-purchase-list",
    ),
]
