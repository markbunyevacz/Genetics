# Laboratóriumi egyoldalas — F1+ white-label leletmotor (SKU-L)

| | |
| --- | --- |
| **Feladó** | `[Gyártó neve]` |
| **Címzett** | `[Partnerlaboratórium neve]` — ügyvezetés / laborvezető |
| **Tárgy** | White-label PGx-lelet: a ti diplotípusotok, a ti aláírásotok, verziózott irányelv-szöveg |
| **Státusz** | Ajánlati egyoldalas + a [term sheet](../Outbound/OQ-03-l3-term-sheet.md) kereskedelmi párja |

Tisztelt Laborvezető!

A genotípust **ti** hívjátok. A PCE nem FASTQ-ból allélt találgat (ez szándékos: NG-01). Azt vesszük át, amit már validáltatok, és **aláírásra kész** leletet adunk: arculat, pecsét helye, CPIC/DPWG/FDA **teljes gén-tábla**, guideline-verzió, callability.

Ez a v1 **fizető** termék. A klinikák tőletek veszik a vizsgálatot; tőlünk ti veszitek a lelet-infrastruktúrát.

---

## Mit old meg

| Ma | PCE F1+ |
| --- | --- |
| Kézi CPIC-tábla, elavult sablon | Verziózott kivonat, forrás + URL minden soron |
| Hiányzó VCF-pozíció = „normál” | Callability: `INDETERMINATE`, nem hamis NM |
| Nincs nyoma, melyik CPIC-verzió volt | Minden PDF-oldalon pipeline + guideline-verzió |
| 40 perc/lelet | Cél: p95 **&lt; 10 perc** az outside-call-tól az aláírásra kész fájlig (szoftver; az orvosi aláírás SLA külön) |

## Mit vállaltok ti

- Diplotípus / fenotípus-hívás, módszer, callability.
- **Minden** F1+ lelet szakorvosi aláírása (`[X]` órás SLA — term sheet).
- 2008/XXI. tanácsadás, beleegyezés, 12. § engedély — a szoftver kapuz, de a kötelezettség a tiétek.
- White-label: logo, pecsétszám, fejléc.

## Mit vállalunk mi

- Renderer, amely **nem** olvassa a beteg aktuális gyógyszerlistáját (nincs „mivel Ön X-et szed, váltson Y-ra”).
- A gén **teljes** publikált táblája, nem a felírt szerre szűrve.
- Nincs felugró CDSS a felírónak ebből a termékből.
- Kolofon: PCE = technológiai szállító, nem aláíró.

## Ár (kitöltendő)

| Tétel | Összeg |
| --- | --- |
| Havidíj | `[Y1]` Ft + ÁFA / hó (benne `[N]` lelet) |
| Volumensáv | `[Y2]` Ft + ÁFA / aláírt lelet vagy sávos csomag |
| Indítás / arculat | `[Y0]` Ft + ÁFA egyszeri |

Nincs „csak a hibás esetért fizetünk” modell: **aláírás nélküli validált lelet nincs**.

## Hatály

A szoftverlicenc **akkor** lép életbe, ha a külső counsel az F1+ rendeltetést a dosszié szerint nem-MDSW-nek (vagy a feltétel szerinti IIa eljárásnak) minősíti. Addig: fizetős bevezető, szintetikus + saját validációs esetek, éles beteglelet csak a labor QMS-e szerint.

Ha a counsel MDSW-t mond: a megépített motor IIa/CE pályára megy; a szerződés 30 napos újratárgyalás vagy felmondás (term sheet §5).

---

Következő lépés: a term sheet `[Partnerlabor]`, `[X]`, `[Y1]`/`[Y2]` kitöltése és LOI.

| | |
| --- | --- |
| Kapcsolat | `[név, e-mail, telefon]` |
| Melléklet | Term sheet; A.1; minta-PDF (szintetikus) |
