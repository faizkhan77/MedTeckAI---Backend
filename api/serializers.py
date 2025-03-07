from rest_framework import serializers
from .models import (
    PatientProfile,
    PatientMedicalInfo,
    DoctorProfile,
    MedicalImage,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "profile"]

    def get_profile(self, obj):
        if obj.role == "patient":
            profile = PatientProfile.objects.filter(user=obj).first()
        elif obj.role == "doctor":
            profile = DoctorProfile.objects.filter(user=obj).first()
        else:
            profile = None
        return profile.id if profile else None


class PatientMedicalInfoSerializer(serializers.ModelSerializer):
    # patient = PatientProfileSerializer(read_only=True)
    patient = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.all()
    )  # ✅ Allow patient ID in request

    class Meta:
        model = PatientMedicalInfo
        fields = "__all__"


class MedicalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalImage
        fields = ["id", "patient", "image", "image_type", "uploaded_at", "result"]


class PatientProfileSerializer(serializers.ModelSerializer):
    medical_info = PatientMedicalInfoSerializer(read_only=True)
    medical_images = MedicalImageSerializer(many=True, read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "user",
            "firstname",
            "lastname",
            "age",
            "gender",
            "contact_number",
            "email",
            "medical_info",
            "medical_images",
        ]


class DoctorProfileSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = "__all__"
