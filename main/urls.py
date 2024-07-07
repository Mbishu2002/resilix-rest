from django.urls import path
from .views import (
    ListDisasterFeedback,
    ListLocations,
    VerifyPhoneView,
    EmergencyAlertChoicesView,
    UserRegistration,
    UserLogin,
    AlertListCreateView,
    ChatbotAPIView
)

urlpatterns = [
    path("user/signup/", UserRegistration.as_view(), name="user-registration"),
    path("login/", UserLogin.as_view(), name="login"),
    path("resilix/disaster/feedbacks/", ListDisasterFeedback.as_view(), name="feedbacks"),
    path("resilix/locations/", ListLocations.as_view(), name="locations"),
    path("emergency/choices/", EmergencyAlertChoicesView.as_view(), name="create-emergency"),
    path("alerts/", AlertListCreateView.as_view(), name="alert-list-create"),
    path("verify_phone/", VerifyPhoneView.as_view(), name="verify-phone"),
    path("chatbot/", ChatbotAPIView.as_view(), name="chatbot-api"),
]
