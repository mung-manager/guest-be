from django.urls import path

from mung_manager.customers.apis.api_managers import (
    CustomerReservationCancelAPIManager,
    CustomerReservationDetailListAPIManager,
    CustomerReservationListAPIManager,
    CustomerTicketCountAPIManager,
    CustomerTicketPurchaseListAPIManager,
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
    path(
        "/reservations/detail",
        CustomerReservationDetailListAPIManager.as_view(),
        name="customer-reservation-detail-list",
    ),
    path(
        "/tickets/purchases",
        CustomerTicketPurchaseListAPIManager.as_view(),
        name="customer-ticket-purchase-list",
    ),
    path(
        "/reservations/<int:reservation_id>/cancel",
        CustomerReservationCancelAPIManager.as_view(),
        name="customer-reservation-cancel",
    ),
]
