# Outbound — külső címzetteknek küldhető irattervezetek

| | |
| --- | --- |
| **Csomag** | PCE-SPEC-v1.2 Outbound |
| **Dátum** | 2026-08-12 |
| **Státusz** | TERVEZET — küldhető; **nem** aláírt állásfoglalás |
| **Gyártó** | `[Gyártó neve]` (A9: a `genetics` repo tulajdonos szervezete; **név nincs kitalálva**) |

Ez a mappa az F melléklet kéréseit **címzett-kész** iratokká alakítja. Kitöltés: a szögletes zárójelek (`[Gyártó neve]`, `[Partnerlabor]`, `[X]`, `[Y]`) a küldő tölti ki. Aláírás a címzetté.

**Nem** zárja le az OQ-05 / OQ-15 / OQ-16 / OQ-01 / OQ-03 kérdéseket. A F.6 tábla akkor töltődik, ha a címzett az itteni iraton dönt. A [G melléklet](../G-open-items.md) **javaslat** a pecsételőnek, nem pecsét.

A v1.2 spec **fagyasztva** ([§10.2](../PCE-SPEC-v1.2.md)). A spec-írás nem folytatódik a válaszokig. Pecsétekig **nincs** új architektúra-fejezet ([B](../B-architecture-and-interfaces.md) a két path). F1s HIS **nem** indul OQ-16+15 pecsét nélkül.

**Mikor megy ki az irat**

| Sáv | OQ | Mikor |
| --- | --- | --- |
| **Gyártói** (nincs vevő kell) | OQ-05 counsel; OQ-01 ISO/Redmine | **Most.** A nem-MDSW kérés és a 2026-09-30 QMS-kapu nem telephelyfüggő. |
| **Telephelyi** (név kell) | OQ-16 DPO → OQ-15 RA → OQ-03 labor | Amikor van **nevesített** intézmény / labor. Addig a core SYN-en fut; a flag-mátrix üres. |

A telephelyi lánc **kötött**: `OQ-16 → OQ-15 → OQ-03`. Az OQ-05 **nem** vár a kórházra; a 16→15→05 sorrend csak akkor él, ha a counsel-levelet szándékosan a telephelyi DPO után küldik. Default: OQ-05 a gyártói sávban, a telephelytől függetlenül.

## Irattár

| Fájl | OQ | Címzett | Típus |
| --- | --- | --- | --- |
| [OQ-05-counsel-brief.md](OQ-05-counsel-brief.md) | OQ-05 | Külső jogi és szabályozási tanácsadó | Állásfoglalás-kérés |
| [OQ-16-dpo-dpia-kerdoiv.md](OQ-16-dpo-dpia-kerdoiv.md) | OQ-16 | DPO / DPIA munkacsoport | Igen/nem kontrollcsomag |
| [OQ-16-kuldesi-csomag.md](OQ-16-kuldesi-csomag.md) | OQ-16 | Küldő (belső) | Boríték + változó-tábla; **első kimenő irat** |
| [OQ-15-intezmenyi-ra-egyoldalas.md](OQ-15-intezmenyi-ra-egyoldalas.md) | OQ-15 | Intézményi RA / orvosigazgató / etikai bizottság | Jóváhagyási kérelem |
| [OQ-03-l3-term-sheet.md](OQ-03-l3-term-sheet.md) | OQ-03 | Partnerlaboratórium üzleti vezetése | Term sheet (nem szerződés) |
| [OQ-01-iso-eeszt-owner-csomag.md](OQ-01-iso-eeszt-owner-csomag.md) | OQ-01 | Ügyvezetés / belső RA | F0 feladatlista + kapuőr |

## Küldési sorrend

**Gyártói (most):** OQ-05, OQ-01 — párhuzamosan is mehetnek.

**Telephelyi (nevesített megrendelőkor):**

`OQ-16 → OQ-15 → OQ-03`

1. **OQ-16** (DPO) — **első kimenő irat.** Boríték: [OQ-16-kuldesi-csomag.md](OQ-16-kuldesi-csomag.md). NEM → álnevesített út + FR-115 (kutatási/shadow). **Nem** kapcsolja ki a klinikai FR-100-at. Partnerlabor **nincs** ezen az iraton (az OQ-03). Gyártónév: A9, küldéskor, nem kitalálva.
2. **OQ-15** (intézményi RA) — **csak lezárt OQ-16 után**. Reviewer-vak HITL kérelem; HIS pecsét: OQ-15 **és** OQ-16.
3. **OQ-03** (labor) — REG-020 / opcionális `[Yl]`; labornevet itt **nem** találunk ki.

**OQ-05** (gyártói counsel) — F1+ nem-MDSW *kérés*. Gén-szintű CPIC szöveg lehet Rule 11a. Nincs kórházi név kell. A válasz a telephely **F1+ ON/LOCK** (vagy IIa) flagjét adja, nem a HIS-csatlakozást.

**OQ-01** (belső) — 2026-09-30 ISO 9001 / 4. melléklet 2.1; C-000. **Nem** „ISO megújítás”. Redmine ≠ EESZT FHIR (NG-05).

A *pecsét* F.6. Párhuzamos telephelyi kiküldés **nincs**: a 15-ös irat OQ-16 válasz nélkül nem megy. Gyártói OQ-05/01 **nem** vár telephelyre.

## Mellékletek minden külső levélhez

A címzettnek a levél **mellett** menjen:

- [PCE-SPEC-v1.2.md](../PCE-SPEC-v1.2.md)
- [A melléklet](../A-intended-purpose-and-modules.md) (OQ-05, OQ-15)
- [E melléklet](../E-shadow-hitl.md) (OQ-16, OQ-15)
- [C melléklet](../C-eeszt-f0-checklist.md) (OQ-01)
- [F melléklet](../F-decision-package.md) (gyártói kérés, nem válasz)

## Javítások a felhasználói vázlathoz

A vázlatok **nem** lettek szó szerint átmásolva, ahol a v1.2 spec mást mond.

| Irat | Vázlatbeli hiba | Spec szerinti javítás |
| --- | --- | --- |
| OQ-05 | A counsel pecsétje előre „nem MDSW”-t igazol | Kérés + Igen/Nem/Feltétellel; gén-szintű CPIC szöveg továbbra is lehet Rule 11a |
| OQ-05 | Lazább intended purpose parafrázis | **A.1 szó szerinti** rendeltetés |
| OQ-16 | Anonim út = mintavételkor nincs betegi hozzájárulás | Anonim shadow **nem** kapcsolja ki a klinikai FR-100-at (6. § (2) / 8. §) |
| OQ-16 | „k < 5” mint küszöbnév | Cella elemszáma **&lt; k**; default **k ≥ 5** (A14) |
| OQ-15 | Art. 62 mentesség mint kész jogi tény | Gyártói *érv*; a RA dönt vagy továbbítja |
| OQ-03 | L3 = csak NG-01 riasztásra manuális felülbírálat; automatikus lelet ingyen | **NG-01** = non-goal (nincs saját hívás), nem riasztáskód. F1+ default = outside-call; **minden** leletet a labor orvosa ír alá |
| OQ-03 | Darabár csak kivételekre | Spec: havidíj + volumensáv; a `[Y]` placeholder a tárgyalásé |
| OQ-03 | Számlázási irány nyitott / labor viszonteladó | Default: klinika = SKU-P; labor `[Yl]` csak saját tenancy; **nem** viszonteladó |
| OQ-01 | EESZT „aszinkron FHIR + SSL az éles adatközpontba” | **NG-05**: nincs EESZT írás, nincs nyílt FHIR API. Regisztráció = ESZFK **Redmine** (5/F. §) |
| OQ-01 | ISO 9001 „megújítás” | Lehet, hogy **nincs** tanúsítvány; 2.1 = ISO 9001 **vagy** egyéb auditált szoftver-QMS; **nem** 13485 |
| OQ-15 | PREPARE p=0,0034; „súlyos” ADR; ápolási nap; PCE-RWE; shadow = Lancet ADR újramérés | **p=0,0075**; 21,0% vs 27,7%; OR 0,70; grade 2–5 + possible; HU nincs; F1s = HITL/G3, nem PREPARE-klon |
| OQ-05 | Tandem/punktum/mdxcro = nem-MDSW pecsét | L4; primer MDCG; gén-szintű CPIC szöveg továbbra is lehet 11a |
| OQ-16 | ClinLabomics = k≥5 bizonyíték | Nem; A14 assumption; Wen 2022 labor-bányászat |

## Ami szándékosan üres

- Gyártó cégneve, labor neve, Ft-összeg, SLA-óra — a küldő tölti a *kimenő másolaton*; a git placeholder marad (A9)
- F.6 aláírások
- Counsel/DPO/RA *válasza*
