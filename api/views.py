from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from .models import PatientProfile, PatientMedicalInfo, DoctorProfile, MedicalImage
from .serializers import (
    PatientProfileSerializer,
    PatientMedicalInfoSerializer,
    DoctorProfileSerializer,
    MedicalImageSerializer,
    UserSerializer,
)
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import viewsets, permissions


@api_view(["GET"])
def getRoutes(request):
    routes = [
        {"GET": "/api/patients/"},
        {"GET": "/api/patients/<id>/"},
        {"GET": "/api/patients/<id>/medical-info/"},
        {"GET": "/api/doctors/"},
        {"GET": "/api/doctors/<id>/"},
        {"GET": "/api/medical-images/"},
        {"GET": "/api/medical-images/<id>/"},
    ]
    return Response(routes)


# Patient Views
class PatientProfileListView(generics.ListCreateAPIView):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer


class PatientProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer


class PatientMedicalInfoDetailView(generics.RetrieveUpdateAPIView):
    queryset = PatientMedicalInfo.objects.all()
    serializer_class = PatientMedicalInfoSerializer


# Doctor Views
class DoctorProfileListView(generics.ListCreateAPIView):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer


class DoctorProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer


# Medical Image Views
class MedicalImageListView(generics.ListCreateAPIView):
    queryset = MedicalImage.objects.all()
    serializer_class = MedicalImageSerializer


class MedicalImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MedicalImage.objects.all()
    serializer_class = MedicalImageSerializer


# ✅ User ViewSet (Handles User & Profile)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Handles listing and retrieving users (Read-Only)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


@api_view(["POST"])
@permission_classes([AllowAny])  # Allows access without authentication
def signup_view(request):
    username = request.data.get("username")
    # email = request.data.get("email")
    password = request.data.get("password")
    confirm_password = request.data.get("confirm_password")

    if password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=400)

    user = User.objects.create_user(username=username, password=password)
    user.save()

    # Automatically log in the user after signup
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])  # Allows access without authentication
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }
        )
    return Response({"error": "Invalid Credentials"}, status=400)
