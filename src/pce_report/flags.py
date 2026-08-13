"""F1+ clinical renderer flags. Matcher stays off. No live CDS on this path."""

# FR-300 / FR-470. Do not set True in this package.
MATCHER_ON: bool = False

# Renderer must never import or call the shadow matcher.
LIVE_CDS: bool = False

# Hungarian product text. Do not say "a lelet olvas" — a PDF does not read.
GYOGYSZERLISTA_MEGJEGYZES_HU = (
    "Az aláírt laborlelet a meghívott génhez tartozó, publikált guideline-sorokat listázza. "
    "Nem a beteg aktuális gyógyszerfelírásaiból szűrt figyelmeztetés. "
    "A gyógyszerlista a kutatási úton a case-en tárolható; az aláírt JSON/PDF nem belőle készül."
)

# What MATCHER_ON=false means, in Hungarian, on the report and on VCF notes.
DIPLOTIPUS_FORRAS_HU = (
    "A csillag-allél diplotípust (például *1/*2) a partnerlabor adja (outside-call). "
    "A PCE nyers VCF-ből nem számolja ki a diplotípust: a PharmCAT NamedAlleleMatcher "
    "(az a program, amely a variánslistából csillag-allélt hívna) ki van kapcsolva "
    "(MATCHER_ON=false). VCF-nél csak azt ellenőrizzük, hogy a definiáló pozíció szerepel-e; "
    "hiányzó hely nem egyenlő a referencia-alléllal, és nem NORMAL. "
    "Bekapcsolás: változáskezelés + REG-010 újraértékelés, nem képernyőn lévő kapcsoló. "
    "Indok: ha a PCE maga hívná a diplotípust, az F1+ jobban hasonlítana diagnosztikai eszközre "
    "(FR-300, OQ-05)."
)
