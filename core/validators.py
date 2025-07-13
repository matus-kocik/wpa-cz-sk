import os
import re
from datetime import date

import dns.resolver
from django.core.exceptions import ValidationError
from phonenumbers import NumberParseException, is_valid_number, parse


def validate_human_name(value):
    if len(value.strip()) < 2:
        raise ValidationError("Toto pole musí mít alespoň 2 znaky.")
    if not re.match(r"^[A-Za-zÁÉÍÓÚÝĎŤŇŘŠČŽáéíóúýďťňřščžäëïöüÄËÏÖÜ' -]+$", value):
        raise ValidationError(
            "Může obsahovat pouze písmena, mezery, pomlčky nebo apostrof."
        )


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCKLIST_PATH = os.path.join(
    BASE_DIR, "core", "utils", "disposable_email_blocklist.conf"
)
ALLOWLIST_PATH = os.path.join(BASE_DIR, "core", "utils", "allowlist.conf")


def _load_domain_list(path):
    try:
        with open(path, encoding="utf-8") as f:
            return set(
                line.strip().lower()
                for line in f
                if line.strip() and not line.startswith("#")
            )
    except FileNotFoundError:
        return set()


BLOCKED_DOMAINS = _load_domain_list(BLOCKLIST_PATH)
ALLOWED_DOMAINS = _load_domain_list(ALLOWLIST_PATH)


def validate_email_domain(value):
    domain = value.split("@")[-1].lower()

    if domain in ALLOWED_DOMAINS:
        return

    if domain in BLOCKED_DOMAINS:
        raise ValidationError("Tato doména e-mailu není povolena (např. jednorázová).")

    try:
        dns.resolver.resolve(domain, "MX")
    except dns.resolver.NXDOMAIN:
        raise ValidationError("Doména e-mailu neexistuje.")
    except dns.resolver.NoAnswer:
        raise ValidationError("Doména e-mailu nemá platný MX záznam.")
    except dns.resolver.NoNameservers:
        raise ValidationError("Doména e-mailu nemá DNS záznamy.")
    except Exception:
        raise ValidationError("Nelze ověřit e-mailovou doménu.")


def validate_subject(value):
    value = value.strip()
    if len(value) < 3:
        raise ValidationError("Předmět musí mít alespoň 3 znaky.")
    if not re.search(r"[a-zA-Zá-žÁ-Ž]", value):
        raise ValidationError("Předmět musí obsahovat alespoň jedno písmeno.")


def validate_message_body(value):
    if len(value.strip()) < 10:
        raise ValidationError("Zpráva musí mít alespoň 10 znaků.")
    if not any(c.isalpha() for c in value):
        raise ValidationError("Zpráva musí obsahovat text.")


def validate_academic_title(value):
    if not re.match(r"^[A-Za-zČŠŽŤĎĚŇŘÁÉÍÓÚÝÄÖÜĽŔŮĚ\. ]*$", value):
        raise ValidationError("Titul může obsahovat pouze písmena, tečky a mezery.")


def validate_birth_date(value):
    today = date.today()
    min_date = date(1900, 1, 1)
    if value > today:
        raise ValidationError("Datum narození nemůže být v budoucnosti.")
    if value < min_date:
        raise ValidationError("Datum narození musí být po roce 1900.")

    age = (
        today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    )
    if age < 18:
        raise ValidationError("Musíte být starší 18 let.")


def validate_phone_number(value):
    if not value:
        return

    try:
        number = parse(value, None)
        if not is_valid_number(number):
            raise ValidationError(
                "Zadejte platné telefonní číslo v mezinárodním formátu, např. +420..."
            )
    except NumberParseException:
        raise ValidationError("Telefonní číslo má neplatný formát.")


def validate_street(value):
    street_regex = re.compile(r"^[A-Za-zÁÉÍÓÚÝČĎĚŇŘŠŤŽáéíóúýčďěňřšťž0-9\s.\-\/]+$")

    if not street_regex.match(value):
        raise ValidationError(
            "Ulice může obsahovat pouze písmena, čísla, mezery, pomlčky, lomítka a tečky."
        )


def validate_house_number(value):
    house_number_regex = re.compile(r"^[0-9A-Za-zÁÉÍÓÚÝČĎĚŇŘŠŤŽáéíóúýčďěňřšťž\s\/\-]+$")

    if not house_number_regex.match(value):
        raise ValidationError(
            "Číslo domu může obsahovat pouze čísla, písmena, mezery, lomítka a pomlčky."
        )


def validate_location_name(value):
    pattern = r"^[A-Za-zÁÉÍÓÚÝĎŤŇŘŠČŽäëïöüÄËÏÖÜáéíóúýďťňřščž0-9.,()'\- ]+$"
    if not re.match(pattern, value):
        raise ValidationError(
            "Toto pole může obsahovat pouze písmena, čísla, pomlčky, tečky a mezery."
        )


def validate_postal_code(value):
    if not re.match(r"^[\w\s\-]{3,10}$", value):
        raise ValidationError(
            "Zadejte platné PSČ – povolena čísla, písmena, mezery a pomlčky."
        )


def validate_notes(value):
    if len(value) > 256:
        raise ValidationError("Poznámka může mít maximálně 256 znaků.")

    if "<" in value or ">" in value:
        raise ValidationError("Poznámka nesmí obsahovat HTML tagy.")


def validate_plain_text(value):
    html_tag_pattern = re.compile(r"<[^>]+>")
    if html_tag_pattern.search(value):
        raise ValidationError("Text nesmí obsahovat HTML značky.")

    dangerous_patterns = [
        r"(javascript:)",
        r"(<script\b)",
        r"(<iframe\b)",
        r"(<object\b)",
        r"(<embed\b)",
        r"(<style\b)",
        r"(<link\b)",
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValidationError("Text obsahuje nepovolený nebo nebezpečný obsah.")

    return value
