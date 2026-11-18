from django.core.management.base import BaseCommand

from core.models import WasteCategory


class Command(BaseCommand):
    help = "Create the default HIPOS waste categories (safe to run more than once)."

    def handle(self, *args, **options):
        categories = [
            ("Biodegradable", "Food scraps, leaves, and other compostable waste."),
            ("Paper and Cardboard", "Paper, cartons, and cardboard packaging."),
            ("Plastic", "Plastic bottles, cups, wrappers, and containers."),
            ("Glass", "Glass bottles and other glass containers."),
            ("Metal", "Aluminum cans and other metal waste."),
            ("Residual", "Waste that cannot currently be reused or recycled."),
            ("Electronic Waste", "Small electronic waste requiring separate handling."),
            ("Other", "Waste that does not fit the listed categories."),
        ]
        created = 0
        for name, description in categories:
            _, was_created = WasteCategory.objects.get_or_create(name=name, defaults={"description": description})
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Waste categories ready. {created} new categories created."))
