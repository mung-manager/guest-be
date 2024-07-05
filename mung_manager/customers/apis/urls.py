from django.urls import path

from mung_manager.customers.apis.api_managers import CustomerTicketCountAPIManager

urlpatterns = [
    path(
        "/tickets/count",
        CustomerTicketCountAPIManager.as_view(),
        name="customer-ticket-count",
    ),
]
