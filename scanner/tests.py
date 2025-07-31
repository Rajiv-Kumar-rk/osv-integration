from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from scanner.models import Package, Vulnerability, ScanLog
from scanner.tasks import scan_packages
import os
import json

class PackageScannerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a dummy package.json for scanning
        self.package_data = {
            "dependencies": {
                "lodash": "4.17.20"
            }
        }

        with open("package.json", "w") as f:
            json.dump(self.package_data, f)

    def test_upload_package_json(self):
        """
        Test uploading a package.json file via the API.
        """
        with open("package.json", "rb") as file_obj:
            response = self.client.post(
                reverse("upload-package-json"),
                {'file': file_obj},
                format="multipart"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "Uploaded package.json")

    @patch("scanner.tasks.send_slack_message")  # Mock Slack notification
    @patch("scanner.tasks.call_osv_api")        # Mock OSV API call
    def test_scan_packages_creates_vulnerabilities(self, mock_osv_api, mock_slack):
        """
        Test vulnerability scan results in DB entries.
        """

        # Simulated OSV API response
        mock_osv_api.return_value = {
            "vulns": [
                {
                    "id": "GHSA-xyz",
                    "summary": "Example vulnerability",
                    "details": "Fixed in 4.17.21"
                }
            ]
        }

        mock_slack.return_value = None  # Slack call returns nothing

        # Run the scan
        scan_packages()

        self.assertEqual(Vulnerability.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(ScanLog.objects.count(), 1)

        vuln = Vulnerability.objects.first()
        self.assertEqual(vuln.package.name, "lodash")
        self.assertEqual(vuln.vuln_id, "GHSA-xyz")
        self.assertIn("Fixed in", vuln.details)

    @patch("scanner.tasks.send_slack_message")
    @patch("scanner.tasks.call_osv_api")
    def test_scan_packages_with_no_vulnerabilities(self, mock_osv_api, mock_slack):
        """
        Test scan when no vulnerabilities found.
        """
        mock_osv_api.return_value = {
            "vulns": []
        }
        mock_slack.return_value = None

        scan_packages()

        self.assertEqual(Vulnerability.objects.count(), 0)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(ScanLog.objects.count(), 1)

    def tearDown(self):
        # Cleanup package.json after each test
        if os.path.exists("package.json"):
            os.remove("package.json")
