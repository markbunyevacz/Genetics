# Laboratóriumi csatlakozó — integrációs partner (nem a PCE-vevő)

| | |
| --- | --- |
| **Feladó** | `[Gyártó neve]` |
| **Címzett** | `[Laboratórium neve]` — a **klinikai vevő** kijelölt laborja |
| **Tárgy** | Outside-call / VCF csatlakozás a PCE rendszerhez |
| **Státusz** | Integrációs egyoldalas + [term sheet](../Outbound/OQ-03-l3-term-sheet.md) REG-020-hoz |

Tisztelt Laborvezető!

A PCE-t a **klinika / kórház** licenceli. Ti nem „leletmotort vesztek tőlünk mint kiskereskedelmi terméket”. Ti a **genotípus-forrás**: diplotípus, callability, ahol a ti QMS-etek kéri — aláírás.

A PCE szándékosan **nem** hív allélt FASTQ/IDAT-ból (NG-01). Ez a ti akkreditált körötök.

---

## Mit kérünk tőletek

- Strukturált outside-call (gén, diplotípus, módszer, dátum, opcionális fenotípus, callability) és/vagy VCF.
- Ha a klinika F1+ leletet ad ki a **ti** pecsétekkel: minden ilyen kimenet a ti szakorvosotok aláírása (`[X]` óra SLA).
- 12. § szerinti engedély, ha HU-ban ti végzitek a vizsgálatot.

## Mit kaptok

- Stabil API / fájlcsatorna, verziózott guideline a klinika tenancyjén — **ők** a szoftver ügyfelei.
- Opcionális: ha *ti is* tenancyt akartok (saját white-label a saját megrendelőiteknek), az külön rendszerlicenc, nem ez az alapértelmezés.

## Pénz

A vizsgálat díját a klinikának **ti** számlázzátok (a ti árlistátok). A PCE-licencet a klinika a gyártónak. **Nem** viszonteladótok a kórházi SKU-P-nek.

Opcionális saját white-label tenancy: ti fizetitek a gyártónak a `[Y1]`/`[Y2]` (mátrix `[Yl]`) — term sheet. A klinika tenancyjéhez csatlakozni: 0 szoftverdíj felétek.

---

Következő: REG-020 a `[Klinika]` tenancyjéhez, nem „a labor megvette a PCE-t”.

| | |
| --- | --- |
| Kapcsolat | `[név, e-mail, telefon]` |
| Klinikai vevő | `[Klinika neve]` |
