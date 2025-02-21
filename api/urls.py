from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("", views.getRoutes, name="get_routes"),
    path("patients/", views.PatientProfileListView.as_view(), name="patient_list"),
    path(
        "patients/<int:pk>/",
        views.PatientProfileDetailView.as_view(),
        name="patient_detail",
    ),
    path(
        "patients/<int:pk>/medical-info/",
        views.PatientMedicalInfoDetailView.as_view(),
        name="patient_medical_info",
    ),
    path("doctors/", views.DoctorProfileListView.as_view(), name="doctor_list"),
    path(
        "doctors/<int:pk>/",
        views.DoctorProfileDetailView.as_view(),
        name="doctor_detail",
    ),
    path(
        "medical-images/",
        views.MedicalImageListView.as_view(),
        name="medical_image_list",
    ),
    path(
        "medical-images/<int:pk>/",
        views.MedicalImageDetailView.as_view(),
        name="medical_image_detail",
    ),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    # 🔥 Add the token refresh endpoint here
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
