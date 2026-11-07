# Akce WPA

Aplikace `events` spravuje vlastní a převzaté akce prostřednictvím Django administrace.
Šablony, views, URL a testy jsou uvnitř této aplikace.

## Veřejné stránky

- `/akce/` (`event_list`): veřejné připravované i právě probíhající akce, nejbližší první.
- `/akce/?archive=1`: proběhlé akce, nejnovější první.
- `/akce/<slug>/` (`event_detail`): detail veřejné akce. Neveřejný nebo chybějící záznam vrací 404.
- Stránkování: 12 akcí. Interní poznámky se veřejně nezobrazují.
- Sitemap zahrnuje veřejné detaily, včetně archivu. Neveřejné záznamy a prázdné slugy vynechává.

Rozhoduje konec akce, pokud je uveden; jinak začátek. `dates_only=True` znamená,
že skutečný čas není potvrzen: časy se nezobrazují a akce zůstává připravovaná
po celý poslední den podle časového pásma projektu. Přesun do archivu probíhá
při načtení stránky; nepotřebuje plánovanou úlohu.

## Přidání v administraci

Vyplňte název, slug, sekci, termín a případně místo, pořadatele, popis a program.
Zapněte `Veřejná`, až má být akce přístupná návštěvníkům.
U převzaté akce zapněte `Externí` a uveďte původní URL (`source_url`).
`external_url` je další odkaz, například na přihlášení. Obsah může být v originále;
žádné jazykové rozhraní ani automatický překlad není implementován.

Vlastní akce (`section=cz_sk`, `is_external=False`) automaticky dostane zelený rámik
v seznamu a štítek „Akce WPA CZ-SK“ v seznamu i detailu. Pořadí podle data se nemění.
`is_featured` je rezervované pole; nyní nezapíná další zvýraznění ani kartu na titulce.

## Jednorázový přenos doložených akcí

Po záloze databáze a `python manage.py migrate` lze ručně spustit:

```bash
python manage.py import_reviewed_events
```

Příkaz čte pouze `events/data/reviewed_events_2026_11_07.json`, nic nestahuje.
Nové záznamy jsou veřejné. Existující slug nebo stejný název a začátek přeskočí,
nepřepisuje ruční úpravy ani viditelnost. Chyba validace vrátí celý import zpět.
Soubor obsahuje termíny, zdrojové URL a interní poznámky o omezeních zdrojů.
Nejde o průběžnou synchronizaci; nové termíny doplňuje správce ručně.

## Testy

```bash
python -m pytest events/tests.py -q
```

Pokrytí: veřejnost/soukromí, řazení, archiv, hranice dne bez času, stránkování,
escapování obsahu, interní poznámky, zvýraznění vlastní akce a opakovaný import.
