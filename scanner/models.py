from django.db import models

class Package(models.Model):
    name = models.CharField(max_length=255, null=False)
    version = models.CharField(max_length=50, null=False)
    last_scanned = models.DateTimeField(auto_now=True)

class Vulnerability(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='vulnerabilities')
    vuln_id = models.CharField(max_length=255)
    summary = models.TextField()
    details = models.TextField(null=True, blank=True)

class ScanLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    total_packages = models.IntegerField()
    vulnerable_packages = models.IntegerField()
