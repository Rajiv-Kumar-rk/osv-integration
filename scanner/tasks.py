import os
import json
from celery import shared_task
from .models import Package, Vulnerability, ScanLog
from .utils import call_osv_api, send_slack_message
from django.utils.timezone import now

@shared_task
def scan_packages():
    path = os.path.join(os.getcwd(), "package.json")
    if not os.path.exists(path):
        return "package.json not found"

    with open(path) as f:
        data = json.load(f)

    dependencies = data.get("dependencies", {})
    new_vuln_count = 0

    for name, version in dependencies.items():
        pkg, created = Package.objects.get_or_create(name=name, version=version)

        if not created:
            continue  # Skip if already scanned

        osv_result = call_osv_api(name, version)
        vulns = osv_result.get("vulns", [])

        if not vulns:
            send_slack_message(f"Package - {name}\nPackage Version - {version}\nThe package is free from any vulnerabilities.\n🕒Scan Timestamp - {now()}")
        else:
            new_vuln_count += 1
            vuln_objects = []

            for v in vulns:
                vuln = Vulnerability(
                    package=pkg,
                    vuln_id=v["id"],
                    summary=v.get("summary", "No summary provided."),
                    details=v.get("details", "")
                )
                vuln_objects.append(vuln)

            # Bulk insert all at once
            Vulnerability.objects.bulk_create(vuln_objects)

            message = f"Package - {name}\nPackage Version - {version}\nBelow are the listed vulnerabilities:\n"

            for v in vulns:
                message += f"- ID: {v['id']}\n  Summary: {v.get('summary', 'No details')}\n"
            message += f"Scan Timestamp - {now()}"
            send_slack_message(message)

    ScanLog.objects.create(
        total_packages=len(dependencies),
        vulnerable_packages=new_vuln_count
    )
