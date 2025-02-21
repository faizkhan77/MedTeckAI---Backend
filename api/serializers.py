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
            patient_profile = PatientProfile.objects.filter(user=obj).first()
            return (
                PatientProfileSerializer(patient_profile).data
                if patient_profile
                else None
            )
        elif obj.role == "doctor":
            doctor_profile = DoctorProfile.objects.filter(user=obj).first()
            return (
                DoctorProfileSerializer(doctor_profile).data if doctor_profile else None
            )
        return None


class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = "__all__"


class PatientMedicalInfoSerializer(serializers.ModelSerializer):
    patient = PatientProfileSerializer(read_only=True)

    class Meta:
        model = PatientMedicalInfo
        fields = "__all__"


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = "__all__"


class MedicalImageSerializer(serializers.ModelSerializer):
    patient = PatientProfileSerializer(read_only=True)

    class Meta:
        model = MedicalImage
        fields = "__all__"
