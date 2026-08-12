# Outbound — külső címzetteknek küldhető irattervezetek

| | |
| --- | --- |
| **Csomag** | PCE-SPEC-v1.2 Outbound |
| **Dátum** | 2026-08-12 |
| **Státusz** | TERVEZET — küldhető; **nem** aláírt állásfoglalás |
| **Gyártó** | `[Gyártó neve]` (A9: a `genetics` repo tulajdonos szervezete; **név nincs kitalálva**) |

Ez a mappa az F melléklet kéréseit **címzett-kész** iratokká alakítja. Kitöltés: a szögletes zárójelek (`[Gyártó neve]`, `[Partnerlabor]`, `[X]`, `[Y]`) a küldő tölti ki. Aláírás a címzetté.

**Nem** zárja le az OQ-05 / OQ-15 / OQ-16 / OQ-01 / OQ-03 kérdéseket. A F.6 tábla akkor töltődik, ha a címzett az itteni iraton dönt.

A v1.2 spec **fagyasztva** ([§10.2](../PCE-SPEC-v1.2.md)). Ezeket az iratokat **most** ki kell küldeni; a spec-írás nem folytatódik a válaszokig.

## Irattár

| Fájl | OQ | Címzett | Típus |
| --- | --- | --- | --- |
| [OQ-05-counsel-brief.md](OQ-05-counsel-brief.md) | OQ-05 | Külső jogi és szabályozási tanácsadó | Állásfoglalás-kérés |
| [OQ-16-dpo-dpia-kerdoiv.md](OQ-16-dpo-dpia-kerdoiv.md) | OQ-16 | DPO / DPIA munkacsoport | Igen/nem kontrollcsomag |
| [OQ-15-intezmenyi-ra-egyoldalas.md](OQ-15-intezmenyi-ra-egyoldalas.md) | OQ-15 | Intézményi RA / orvosigazgató / etikai bizottság | Jóváhagyási kérelem |
| [OQ-03-l3-term-sheet.md](OQ-03-l3-term-sheet.md) | OQ-03 | Partnerlaboratórium üzleti vezetése | Term sheet (nem szerződés) |
| [OQ-01-iso-eeszt-owner-csomag.md](OQ-01-iso-eeszt-owner-csomag.md) | OQ-01 | Ügyvezetés / belső RA | F0 feladatlista + kapuőr |

## Küldési sorrend (ajánlott)

1. **OQ-16** (DPO) — az F1s anonim út ettől függ.
2. **OQ-15** (intézmény) — OQ-16 után vagy vele párhuzamosan, de F1s HIS-csatlakozás OQ-16 nélkül nem indul.
3. **OQ-05** (counsel) — F1+ forgalmazási pozíció; független az F1s-től, de a dosszié ugyanaz.
4. **OQ-03** (labor) — F1+ COGS / REG-020; labornevet itt **nem** találunk ki.
5. **OQ-01** (belső) — 2026-09-30 ISO 9001 / 4. melléklet 2.1; C-000 tény azonnal.

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
| OQ-01 | EESZT „aszinkron FHIR + SSL az éles adatközpontba” | **NG-05**: nincs EESZT írás, nincs nyílt FHIR API. Regisztráció = ESZFK **Redmine** (5/F. §) |
| OQ-01 | ISO 9001 „megújítás” | Lehet, hogy **nincs** tanúsítvány; 2.1 = ISO 9001 **vagy** egyéb auditált szoftver-QMS; **nem** 13485 |

## Ami szándékosan üres

- Gyártó cégneve, labor neve, Ft-összeg, SLA-óra
- F.6 aláírások
- Counsel/DPO/RA *válasza*
