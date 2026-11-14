from django.core.exceptions import ValidationError


def validate_pdf_content(value):
    """Check the PDF header without consuming the uploaded file."""
    if not value:
        return
    position = None
    try:
        position = value.tell()
        value.seek(0)
        header = value.read(1024)
        if b"%PDF-" not in header:
            raise ValidationError("Soubor neobsahuje hlavičku PDF.")
    except (OSError, ValueError) as exc:
        raise ValidationError(
            "PDF soubor nelze přečíst. Nahrajte jej prosím znovu."
        ) from exc
    finally:
        if position is not None:
            value.seek(position)
