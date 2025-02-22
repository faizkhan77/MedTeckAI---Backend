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

    def perform_create(self, serializer):
        """Automatically assign the authenticated user’s patient profile"""
        patient_profile = PatientProfile.objects.get(
            user=self.request.user
        )  # Get the PatientProfile
        serializer.save(patient=patient_profile)  # Assign the patient field


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
import google.generativeai as genai  # Correct way to import
from django.conf import settings
import shutil

# Load the YOLOv11 model
model = YOLO("best.pt")


import glob


class MedicalImageViewSet(viewsets.ModelViewSet):
    queryset = MedicalImage.objects.all()
    serializer_class = MedicalImageSerializer

    @action(detail=False, methods=["post"])
    def detect_image(self, request):
        """Handles image upload, runs YOLO detection, saves results in the database, and returns detected label."""
        if "image" not in request.FILES:
            return Response(
                {"error": "No image uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        image_file = request.FILES["image"]
        image_type = request.data.get("image_type", "Unknown")
        patient_id = request.data.get("patient_id")

        try:
            patient = PatientProfile.objects.get(id=patient_id)
        except PatientProfile.DoesNotExist:
            return Response(
                {"error": "Invalid patient ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Save uploaded image
        image_path = default_storage.save(
            f"medical_images/{image_file.name}", ContentFile(image_file.read())
        )
        image_full_path = os.path.join(settings.MEDIA_ROOT, image_path)

        # Run YOLO detection
        prediction = model.predict(source=image_full_path, save=True)
        output_dir = prediction[0].save_dir  # YOLO output directory

        # Extract detected label (tumor type)
        detected_tumors = []
        for result in prediction:
            for box in result.boxes:
                tumor_label = result.names[int(box.cls)]  # Extract class label
                detected_tumors.append(tumor_label)

        if not detected_tumors:
            return Response({"error": "No tumor detected"}, status=status.HTTP_200_OK)

        tumor_type = detected_tumors[0]  # Assuming the first detected tumor is primary

        # Find the processed image in output_dir
        processed_images = glob.glob(os.path.join(output_dir, "*"))
        processed_images = [
            img for img in processed_images if img.endswith((".jpg", ".png"))
        ]

        if not processed_images:
            return Response(
                {"error": "Processed image not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        processed_image_path = processed_images[0]  # Get the first detected image
        processed_filename = os.path.basename(processed_image_path)

        # Copy processed image to media folder
        processed_image_dest = os.path.join(
            settings.MEDIA_ROOT, "medical_images", processed_filename
        )
        shutil.copy(processed_image_path, processed_image_dest)

        # Save record in MedicalImage model
        medical_image = MedicalImage.objects.create(
            patient=patient,
            image=f"medical_images/{processed_filename}",
            image_type=image_type,
        )

        return Response(
            {
                "original_image": request.build_absolute_uri(
                    default_storage.url(image_path)
                ),
                "processed_image": request.build_absolute_uri(
                    settings.MEDIA_URL + f"medical_images/{processed_filename}"
                ),
                "image_id": medical_image.id,
                "tumor_type": tumor_type,  # ✅ Only returning the detected tumor type
            },
            status=status.HTTP_200_OK,
        )


from django.http import JsonResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@api_view(["GET"])
@permission_classes([AllowAny])
def recommend_doctors(request):
    """API endpoint to recommend doctors based on patient profile."""
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated"}, status=401)

    try:
        patient_profile = PatientProfile.objects.get(user=user)
        medical_info = patient_profile.medical_info
    except PatientProfile.DoesNotExist:
        return JsonResponse({"error": "Patient profile not found"}, status=404)
    except AttributeError:
        return JsonResponse({"error": "Medical information not found"}, status=404)

    # Combine patient medical info fields into one string
    patient_data = " ".join(
        filter(
            None,
            [
                medical_info.allergies,
                medical_info.current_medications,
                medical_info.history_of_disease,
                medical_info.medical_history,
                medical_info.existing_medical_conditions,
                medical_info.past_surgeries,
                medical_info.genetic_disorders,
            ],
        )
    ).lower()

    # Fetch all doctors
    doctors = DoctorProfile.objects.all()
    if not doctors.exists():
        return JsonResponse({"error": "No doctors found"}, status=404)

    # Prepare doctor data
    doctor_data = [
        " ".join(filter(None, [doctor.specialization, doctor.bio])).lower()
        for doctor in doctors
    ]

    # Vectorizing patient data and doctor data using TF-IDF
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([patient_data] + doctor_data)

    # Compute cosine similarity between patient profile and all doctors
    similarities = cosine_similarity(vectors[0], vectors[1:]).flatten()

    # Sort doctors based on similarity scores
    doctor_scores = list(zip(doctors, similarities))
    doctor_scores.sort(key=lambda x: x[1], reverse=True)

    # Serialize top 5 recommended doctors
    recommended_doctors = DoctorProfileSerializer(
        [doctor for doctor, score in doctor_scores[:5] if score > 0], many=True
    ).data

    return JsonResponse({"recommended_doctors": recommended_doctors})
