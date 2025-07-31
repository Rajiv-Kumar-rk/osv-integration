from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .tasks import scan_packages
from .models import ScanLog, Package
from rest_framework import status
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils.crypto import get_random_string
import json

class UploadPackageJSON(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file_obj = request.FILES.get("file")

        if not file_obj or file_obj.name != "package.json":
            return Response({"error": "Invalid or missing file."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with open("package.json", "wb+") as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            scan_packages.delay()

            return Response({"status": "Uploaded package.json"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TriggerScan(APIView):
    def post(self, request):
        try:
            scan_packages.delay()
            return Response({"status": "Scan started"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ScanStats(APIView):
    def get(self, request):
        try:
            packages = Package.objects.all()
            total_packages = packages.count()
            vulnerable_qs = packages.filter(vulnerabilities__isnull=False).distinct()
            vulnerable_packages_count = vulnerable_qs.count()

            # Prepare detailed vulnerable package data
            vulnerable_details = []
            for package in vulnerable_qs:
                vuln_data = []
                for vuln in package.vulnerabilities.all():
                    vuln_data.append({
                        "id": vuln.vuln_id,
                        "summary": vuln.summary,
                        'details': vuln.details,
                    })
                vulnerable_details.append({
                    "package_name": package.name,
                    "package_version": package.version,
                    "vulnerabilities": vuln_data
                })

            return Response({
                "total_packages": total_packages,
                "vulnerable_packages": vulnerable_packages_count,
                "vulnerable_package_details": vulnerable_details
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class CreatePeriodicScanAPIView(APIView):
    def post(self, request):
        interval_type = request.data.get("interval_type", None)
        interval_value = request.data.get("interval_value", None)

        if not interval_type or not interval_value:
            return Response({"error": "'interval_type' and 'interval_value' are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate interval_value
        try:
            interval_value = int(interval_value)
            if interval_value <= 0:
                raise ValueError
        except ValueError:
            return Response({"error": "Invalid interval value"}, status=status.HTTP_400_BAD_REQUEST)

        interval_type = interval_type.lower()

        # Validate interval_type
        valid_types = {
            "seconds": IntervalSchedule.SECONDS,
            "minutes": IntervalSchedule.MINUTES,
            "hours": IntervalSchedule.HOURS
        }

        if interval_type not in valid_types:
            return Response({"error": f"Invalid interval_type. Must be one of {list(valid_types.keys())}"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create interval schedule
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=interval_value,
            period=valid_types[interval_type]
        )

        # Create a unique task name to avoid duplicate task names
        task_name = f"scan-every-{interval_value}-{interval_type}-{get_random_string(6)}"

        # Create periodic task
        PeriodicTask.objects.create(
            interval=schedule,
            name=task_name,
            task="scanner.tasks.scan_packages",
            kwargs=json.dumps({})
        )

        return Response({
            "message": f"Scheduled scan_packages every {interval_value} {interval_type}.",
            "task_name": task_name
        }, status=status.HTTP_201_CREATED)