import json
from contextlib import ExitStack
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from articles.models import Article, Category


class Command(BaseCommand):
    help = "Jednorázově převede čtyři původní karty titulky do databáze a zkopíruje jejich soubory do media."

    def handle(self, *args, **options):
        manifest = (
            Path(__file__).resolve().parents[2] / "data" / "homepage_articles.json"
        )
        rows = json.loads(manifest.read_text())
        sources = []
        for row in rows:
            pdf = settings.BASE_DIR / "static" / "docs" / row["pdf"]
            image = settings.BASE_DIR / "static" / "images" / "articles" / row["image"]
            if not pdf.is_file() or not image.is_file():
                raise CommandError(f"Chybí původní soubory článku: {row['title']}")
            sources.append((row, pdf, image))
        created = skipped = 0
        attempted = []
        try:
            with transaction.atomic():
                for row, pdf_path, image_path in sources:
                    pub_date = date.fromisoformat(row["publication_date"])
                    if (
                        Article.objects.filter(slug=row["slug"]).exists()
                        or Article.objects.filter(
                            title=row["title"], publication_date=pub_date
                        ).exists()
                    ):
                        skipped += 1
                        continue
                    category, _ = Category.objects.get_or_create(
                        slug=row["category_slug"],
                        defaults={"name": row["category_name"]},
                    )
                    with ExitStack() as stack:
                        article = Article(
                            title=row["title"],
                            slug=row["slug"],
                            summary=row["summary"],
                            publication_date=pub_date,
                            category=category,
                            is_published=True,
                            pdf_title=row["title"],
                            published_in=row.get("published_in", ""),
                            note="Převzato z původní titulky 7. 11. 2026. Datum publikace odpovídá původní kartě; nejde nutně o datum vydání v původním zdroji. Autoři nebyli odhadováni.",
                        )
                        article.pdf_file = File(
                            stack.enter_context(pdf_path.open("rb")), name=pdf_path.name
                        )
                        article.main_image = File(
                            stack.enter_context(image_path.open("rb")),
                            name=image_path.name,
                        )
                        attempted.append(article)
                        article.full_clean()
                        article.save()
                    created += 1
        except Exception as exc:
            # Database rollback does not remove newly written storage files.
            for article in attempted:
                for field in (article.pdf_file, article.main_image):
                    if field and field._committed:
                        field.storage.delete(field.name)
            raise CommandError(f"Import vrácen zpět: {exc}") from exc
        self.stdout.write(
            self.style.SUCCESS(
                f"Vytvořeno: {created}; přeskočeno: {skipped}. Původní statické soubory zůstaly zachovány."
            )
        )
