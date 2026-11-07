# WPA CZ-SK

Web československé sekce World Pheasant Association: https://wpacz-sk.com/
Django projekt pro veřejné informace, členství, druhy, akce a připravované chovatelské evidence.

## Co je zapojené

- Veřejné informační stránky a projekty jsou většinou statické šablony.
- Katalog druhů a detailní profily čtou databázi.
- Akce mají seznam, archiv, detail a správu v administraci.
- Kontakt a přihláška používají SMTP; příjemci se nastavují v prostředí.
- Členské profily, přihlášení a reset hesla existují; přihlašovací tlačítka jsou zatím skrytá.
- Členové jsou kombinací ručních řádků a databáze. Převod na plnou databázi je odložený.
- Články, roční census (`breeding`) a plemenná kniha (`studbook`) mají databázové základy;
  veřejné redakční a analytické obrazovky ani import členů/censusu nejsou implementované.

## Lokální spuštění

Python 3.13+, závislosti podle `pyproject.toml` / `uv.lock`, Node pro produkční CSS.
Konfigurace se načítá z `.env` o úroveň nad adresářem obsahujícím `manage.py`.
Hesla a celou databázi neukládejte do repozitáře.

```bash
uv sync
uv run python manage.py migrate
npm ci
npm run build
uv run python manage.py runserver
```

`npm run dev` sleduje změny stylů při vývoji. Po změnách tříd v šablonách se před
nasazením znovu sestaví a uloží `static/css/styles.css`. JavaScript má zvlášť zdrojovou
a minifikovanou verzi; po jeho úpravě použijte `make minify-js`.

## Kontroly

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run pytest -q
```

Testy používají `config.settings_test`, dočasnou SQLite a paměťový e-mailový backend.
Neodesílají skutečné e-maily. Vybrané testy jiných funkcí přeskakují DNS validaci přes
DEBUG; samostatné testy DNS validátoru ověřují jeho chování s řízenými odpověďmi.

## Pošta

Nastavují se `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`,
`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`,
`CONTACT_RECEIVER_EMAIL`, `APPLICATION_RECEIVER_EMAIL`.
Výchozí příjemci kontaktu a přihlášek jsou `matuskocik@gmail.com`; hodnoty prostředí
mají přednost. Veřejný kontaktní e-mail v hlavičce/GDPR může být od příjemce formuláře odlišný.
Django 6.0 používá `EMAIL_*`, Django 6.1 `MAILERS`; konfigurace podporuje obě varianty.
Lokální a serverová verze se mohou lišit — při diagnostice ověřte `python -m django --version`.

## Mapa stránek

`/sitemap.xml`: veřejné informační stránky, seznamy, aktivní druhy, veřejné akce a profily.
Nezahrnuje přihlášení, dashboard, editace ani neveřejné záznamy. `robots.txt` přístup nezabezpečuje.

## Nasazení na Roští

Nasazuje se `main`; běžná lokální práce probíhá v `develop`. Před migrací či importem
zálohujte databázi (pro SQLite použijte SQLite backup, ne prostou kopii živého souboru).
Zálohy uchovávejte mimo repozitář i veřejný adresář.

```bash
cd /srv/app
git pull --ff-only origin main
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check
supervisorctl restart app
supervisorctl status app
```

Příkazy spouštějte postupně a při chybě nepokračujte. Po nasazení ověřte veřejné stránky.
Migrace a Git nepřenášejí obsah lokální DB na server. Jednorázový přenos 12 ověřených
akcí je popsán v `events/README.md`; není automatický a existující záznamy nepřepisuje.

Podrobnosti jednotlivých aplikací jsou v jejich `README.md`.
