import json
from datetime import datetime
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from events.models import Event


class Command(BaseCommand):
    help = (
        "Jednorázově doplní ověřené akce z 7. 11. 2026. Existující záznamy nepřepisuje."
    )

    def handle(self, *args, **options):
        path = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "reviewed_events_2026_11_07.json"
        )
        rows = json.loads(path.read_text())
        created = skipped = 0
        try:
            with transaction.atomic():
                for row in rows:
                    data = dict(row)
                    data["start_date"] = datetime.fromisoformat(data["start_date"])
                    if data["end_date"]:
                        data["end_date"] = datetime.fromisoformat(data["end_date"])
                    if (
                        Event.objects.filter(slug=data["slug"]).exists()
                        or Event.objects.filter(
                            title=data["title"], start_date=data["start_date"]
                        ).exists()
                    ):
                        skipped += 1
                        continue
                    event = Event(**data)
                    event.full_clean()
                    event.save()
                    created += 1
        except (ValidationError, ValueError, KeyError) as exc:
            raise CommandError(f"Import vrácen zpět: {exc}") from exc
        self.stdout.write(
            self.style.SUCCESS(f"Vytvořeno: {created}; přeskočeno: {skipped}.")
        )
