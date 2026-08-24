from django.core.management.base import BaseCommand

from batteries.models import BMSData, BMSMetrics
from batteries.services import compute_bms_metrics


class Command(BaseCommand):
    help = "Compute telemetry metrics for BMS uploads that do not have them yet."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Recompute metrics even for rows that already have them.",
        )

    def handle(self, *args, **options):
        qs = BMSData.objects.select_related("battery")
        if not options["all"]:
            qs = qs.filter(metrics__isnull=True)

        total = qs.count()
        created = 0
        failed = 0

        for bms in qs:
            try:
                metrics = compute_bms_metrics(bms.file)
                BMSMetrics.objects.update_or_create(bms_data=bms, defaults=metrics)
                created += 1
                self.stdout.write(
                    f"BMS {bms.id} ({bms.battery.battery_id}): "
                    f"cycles={metrics['cycle_count']} "
                    f"avg_temp={metrics['avg_temperature']} "
                    f"avg_voltage={metrics['avg_voltage']}"
                )
            except Exception as exc:
                failed += 1
                self.stderr.write(f"BMS {bms.id}: FAILED - {exc}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. processed={created}/{total} failed={failed}"
            )
        )
