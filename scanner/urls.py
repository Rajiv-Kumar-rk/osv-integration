from django.urls import path
from .views import UploadPackageJSON, TriggerScan, ScanStats, CreatePeriodicScanAPIView

urlpatterns = [
    path('upload/', UploadPackageJSON.as_view(), name="upload-package-json"),
    path('scan/', TriggerScan.as_view(), name="scan-packages"),
    path('stats/', ScanStats.as_view(), name="stats"),
    path("create-periodic-scan/", CreatePeriodicScanAPIView.as_view(), name="create-periodic-scan"),
]
