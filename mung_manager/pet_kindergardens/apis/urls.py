from django.urls import path

from mung_manager.pet_kindergardens.apis.api_managers import (
    PetKindergardenDetailInfoAPIManager,
    PetkindergardenListAPIManager,
    PetKindergardenSelectionAPIManager,
    PetKindergardenSummaryInfoAPIManager,
)

urlpatterns = [
    path(
        "",
        PetkindergardenListAPIManager.as_view(),
        name="pet-kindergarden-list",
    ),
    path(
        "/select",
        PetKindergardenSelectionAPIManager.as_view(),
        name="pet-kindergarden-selection",
    ),
    path(
        "/summary",
        PetKindergardenSummaryInfoAPIManager.as_view(),
        name="pet-kindergarden-summary-info",
    ),
    path(
        "/detail",
        PetKindergardenDetailInfoAPIManager.as_view(),
        name="pet-kindergarden-detail-info",
    ),
]
