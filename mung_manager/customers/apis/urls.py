from django.urls import path

from mung_manager.customers.apis.api_managers import (
    CustomerActiveStatusAPIManager,
    CustomerReservationAPIManager,
    CustomerReservationCancelAPIManager,
    CustomerReservationDetailListAPIManager,
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
        CustomerReservationAPIManager.as_view(),
        name="customer-reservation",
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
    path(
        "/active",
        CustomerActiveStatusAPIManager.as_view(),
        name="customer-active-status",
    ),
]
