from django.db import models
from django.contrib.auth.models import AbstractUser, User


# Patient Profile Model
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
    )
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class PatientMedicalInfo(models.Model):
    patient = models.OneToOneField(
        PatientProfile, on_delete=models.CASCADE, related_name="medical_info"
    )
    allergies = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    smoke = models.CharField(
        max_length=3, choices=[("Yes", "Yes"), ("No", "No")], default="No"
    )
    alcohol = models.CharField(
        max_length=3, choices=[("Yes", "Yes"), ("No", "No")], default="No"
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Height in cm"
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Weight in kg"
    )
    history_of_disease = models.TextField(blank=True, null=True)
    medical_history = models.TextField(
        blank=True, null=True
    )  # Summary of previous illnesses
    blood_group = models.CharField(
        max_length=5,
        choices=[
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
            ("O+", "O+"),
            ("O-", "O-"),
        ],
        blank=True,
        null=True,
    )
    existing_medical_conditions = models.TextField(blank=True, null=True)
    past_surgeries = models.TextField(blank=True, null=True)
    genetic_disorders = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Medical Info for {self.patient.user.username}"


# Doctor Profile Model
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    specialization = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField()
    certifications = models.ImageField(
        upload_to="doctor_certifications/", blank=True, null=True
    )
    license = models.ImageField(upload_to="doctor_licenses/", blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    clinic_address = models.TextField()
    verification = models.BooleanField(default=False)
    available_days = models.CharField(
        max_length=100
    )  # Example: "Monday, Wednesday, Friday"
    available_slots = models.JSONField(
        default=dict
    )  # Example: {"Monday": ["10:00 AM", "2:00 PM"]}
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.username} - {self.specialization}"


class MedicalImage(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="medical_images/")
    image_type = models.CharField(
        max_length=50, choices=[("MRI", "MRI"), ("X-Ray", "X-Ray")]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    result = models.TextField(blank=True, null=True)  # Store AI results here

    def __str__(self):
        return f"{self.image_type} - {self.patient.user.username}"


# class MedicineInfo(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     medicine_name = models.CharField(max_length=255)
#     searched_at = models.DateTimeField(auto_now_add=True)
#     ai_generated_info = models.TextField(blank=True, null=True)  # Store AI response

#     def __str__(self):
#         return f"{self.medicine_name} - {self.user.username}"


# class MedicalReport(models.Model):
#     patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
#     report_file = models.FileField(upload_to="medical_reports/")
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     summary = models.TextField(blank=True, null=True)  # AI-generated summary
#     highlighted_points = models.JSONField(
#         default=list
#     )  # Store important extracted info

#     def __str__(self):
#         return f"Report - {self.patient.user.username} - {self.uploaded_at}"
