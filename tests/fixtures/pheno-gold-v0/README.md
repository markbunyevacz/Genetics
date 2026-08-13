# Fenokonverzió gold (pheno-gold-v0)

**N = 32** SYN eset. Ground truth: pin-elt FDA DDI 1-2. és 2-2. tábla, CPIC SSRI 2023, WHO ATC. **Nem** GeT-RM, **nem** a szabálytábla önmagára mért köre egy kitalált szegény-címkére.

| Mit mér | Elvárt |
| --- | --- |
| Funkcionális fenotípus | minden soron **üres** |
| NM→szegény metabolizáló | **nincs** (CPIC SSRI 2023: nincs konszenzus; FDA nem írja) |
| FDA 2-2 erős index | paroxetin `N06AB05`, fluoxetin `N06AB03` — `strong` rögzítve, címke nem |
| FDA 1-2 in vitro szelektív | kinidin `C01BA01` — **nem** Table 2-2 strong; a motor nem ír szegény címkét |
| WHO ATC | `N06AB10` eszcitaloprám nem erős CYP2D6 index-gátló ezen a listán |
| G3 | ≥90% **csak** ezen a halmazon. N=32: a 90% pontbecslés N<100 mellett széles CI |

A 60 szintetikus guideline-sor és a 100 GeT-RM diplotípus **más** halmaz (f1plus-gold / vcf-gold). Lásd PCE-SPEC §9.1.
