# Core

Kontaktní formulář, společné validátory, kontext šablon a sitemap.

## Kontakt

`ContactView` odešle zprávu na `CONTACT_RECEIVER_EMAIL`, s odpovědí na adresu
odesílatele. Po přijetí hlavní zprávy odešle samostatné potvrzení návštěvníkovi.

- Hlavní zpráva selže nebo backend vrátí 0: HTTP 200 s vyplněným formulářem a chybou.
- Selže pouze potvrzení: přesměrování s upozorněním, že hlavní zpráva odešla a nemá se opakovat.
- Obě zprávy přijaty backendem: přesměrování s potvrzením úspěchu.
- SMTP přijetí samo o sobě nedokazuje doručení do schránky.

Formuláře používají Turnstile, honeypot, validaci a omezení počtu požadavků.
Produkční kontrola e-mailových domén ověřuje DNS; v DEBUG se přeskakuje.

## Sitemap a robots

`/sitemap.xml` obsahuje veřejné informační stránky a seznamy, aktivní druhy,
veřejné akce a veřejné profily. Prázdné slugy a neveřejné detaily vynechává.
Dynamické detaily uvádějí poslední změnu (`updated_at`). Autentizace, dashboard,
editace profilů a parametrické pohledy jako archiv nejsou samostatnými položkami.
Sitemap nepublikuje neveřejný obsah ani neobchází pravidla views.
`robots.txt` je vodítko pro roboty, nikoli řízení přístupu.

## Testy

`python -m pytest core/tests.py core/test_sitemaps.py -q`

Testy sitemap ověřují výsledné XML, dostupnost cílových URL a vyloučení neveřejných
záznamů. Kontaktní testy izolují cache limitování; ochrana v aplikaci zůstává zapnutá.
