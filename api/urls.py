from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path, include


# ✅ Use a router for ViewSet
# ✅ Create a Router and register ViewSets for CRUD operations
router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"patients", views.PatientProfileViewSet, basename="patient")
router.register(
    r"medical-info", views.PatientMedicalInfoViewSet, basename="medical-info"
)
router.register(r"doctors", views.DoctorProfileViewSet, basename="doctor")
router.register(r"medical-images", views.MedicalImageViewSet, basename="medical-image")


# ✅ Include router-generated URLs
urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),  # Enables Login UI
    path("routes/", views.getRoutes, name="get_routes"),
    path(
        "", include(router.urls)
    ),  # Automatically includes all CRUD routes from the router
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path(
        "token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),  # JWT token refresh
]
