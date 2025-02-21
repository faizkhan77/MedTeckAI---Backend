from django.contrib import admin
from .models import PatientProfile, DoctorProfile, MedicalImage, PatientMedicalInfo

admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
admin.site.register(MedicalImage)
admin.site.register(PatientMedicalInfo)
