# faultDetection/management/commands/clear_faults.py

from django.core.management.base import BaseCommand
from faultDetection.models import ActiveFaultAlert

class Command(BaseCommand):
    help = "Clears all active fault alerts"

    def handle(self, *args, **kwargs):
        count, _ = ActiveFaultAlert.objects.all().delete()
        print("Active fault alerts cleared.")
        self.stdout.write(self.style.SUCCESS(f"✅ Cleared {count} active fault alerts."))
