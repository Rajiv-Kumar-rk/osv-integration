from django.contrib import admin
from .models import Package, Vulnerability, ScanLog

admin.site.register(Package)
admin.site.register(Vulnerability)
admin.site.register(ScanLog)
