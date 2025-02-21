from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from .models import (
    PatientProfile,
    PatientMedicalInfo,
    DoctorProfile,
    MedicalImage,
    User,
)
from .serializers import (
    PatientProfileSerializer,
    PatientMedicalInfoSerializer,
    DoctorProfileSerializer,
    MedicalImageSerializer,
    UserSerializer,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model


from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def getRoutes(request):
    routes = [
        {"GET": "/api/users/"},
        {"GET": "/api/users/<id>/"},
        {"GET": "/api/patients/"},
        {"POST": "/api/patients/"},
        {"GET": "/api/patients/<id>/"},
        {"PUT": "/api/patients/<id>/"},
        {"PATCH": "/api/patients/<id>/"},
        {"DELETE": "/api/patients/<id>/"},
        {"GET": "/api/medical-info/"},
        {"POST": "/api/medical-info/"},
        {"GET": "/api/medical-info/<id>/"},
        {"PUT": "/api/medical-info/<id>/"},
        {"PATCH": "/api/medical-info/<id>/"},
        {"DELETE": "/api/medical-info/<id>/"},
        {"GET": "/api/doctors/"},
        {"POST": "/api/doctors/"},
        {"GET": "/api/doctors/<id>/"},
        {"PUT": "/api/doctors/<id>/"},
        {"PATCH": "/api/doctors/<id>/"},
        {"DELETE": "/api/doctors/<id>/"},
        {"GET": "/api/medical-images/"},
        {"POST": "/api/medical-images/"},
        {"GET": "/api/medical-images/<id>/"},
        {"PUT": "/api/medical-images/<id>/"},
        {"PATCH": "/api/medical-images/<id>/"},
        {"DELETE": "/api/medical-images/<id>/"},
        {"POST": "/api/login/"},
        {"POST": "/api/signup/"},
        {"POST": "/api/token/refresh/"},
    ]
    return Response(routes)


# Patient Views
class PatientProfileViewSet(viewsets.ModelViewSet):
    """Handles CRUD for Patient Profiles"""

    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer


class PatientMedicalInfoViewSet(viewsets.ModelViewSet):
    """Handles CRUD for Patient Medical Info"""

    queryset = PatientMedicalInfo.objects.all()
    serializer_class = PatientMedicalInfoSerializer


# Doctor Views
class DoctorProfileViewSet(viewsets.ModelViewSet):
    """Handles CRUD for Doctor Profiles"""

    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer


# Medical Image Views
class MedicalImageViewSet(viewsets.ModelViewSet):
    """Handles CRUD for Medical Images"""

    queryset = MedicalImage.objects.all()
    serializer_class = MedicalImageSerializer


User = get_user_model()


# ✅ User ViewSet (Handles User & Profile)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Handles listing and retrieving users (Read-Only)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    role = request.data.get("role")
    if role not in ["doctor", "patient"]:
        return Response(
            {"error": "Invalid role. Must be 'doctor' or 'patient'."},
            status=400,
        )

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=request.data.get("password"),
            role=role,
        )

        if role == "patient":
            PatientProfile.objects.create(user=user)
        elif role == "doctor":
            DoctorProfile.objects.create(user=user)

        return Response(UserSerializer(user).data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([AllowAny])
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


from ultralytics import YOLO
from django.core.files.storage import default_storage
import os
from django.core.files.base import ContentFile

# Load the YOLOv11 model
model = YOLO("best.pt")


class MedicalImageViewSet(viewsets.ModelViewSet):
    queryset = MedicalImage.objects.all()
    serializer_class = MedicalImageSerializer

    @action(detail=False, methods=["post"])
    def detect_image(self, request):
        """Handles image upload and runs YOLO detection."""
        if "image" not in request.FILES:
            return Response(
                {"error": "No image uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        image_file = request.FILES["image"]
        image_type = request.data.get("image_type", "Unknown")

        # Save the uploaded image
        image_path = default_storage.save(
            f"medical_images/{image_file.name}", ContentFile(image_file.read())
        )

        # Run YOLO detection
        prediction = model.predict(
            source=os.path.join(default_storage.location, image_path), save=True
        )
        output_dir = prediction[0].save_dir  # Directory where YOLO saves the result

        # Find processed image
        processed_image_path = os.path.join(output_dir, image_file.name)

        return Response(
            {
                "original_image": request.build_absolute_uri(
                    default_storage.url(image_path)
                ),
                "processed_image": request.build_absolute_uri(
                    default_storage.url(processed_image_path)
                ),
            },
            status=status.HTTP_200_OK,
        )
