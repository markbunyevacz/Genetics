# VCF gold — hiányzó definiáló pozíció (FR-210)

Nem betegadat. A PCE nem hív csillag-allélt a VCF-ből (PharmCAT NamedAlleleMatcher ki; FR-300). A PharmCAT `--absent-to-ref` nincs hívva.

## Honnan vannak a SYN minták?

| Kérdés | Válasz |
| --- | --- |
| Hol van? | Ebben a mappában, a gyártó készítette a teszthez. |
| Kitől? | Nem a labor. Nem CDC-küldemény. SYN fájl. |
| Milyen pozíció? | Ensembl + NCBI dbSNP, lásd `defining-positions.v0.json` (SNV-k 2026-08-13 és 2026-08-14). |
| CDC GeT-RM? | Fizikai referenciaanyag labor-QC-hez: https://www.cdc.gov/lab-quality/php/get-rm/reference-materials.html — **nem** ezek a fájlok. |
| PharmCAT GitHub teszt-VCF? | Létezik; itt nem másoljuk, mert a `--absent-to-ref` vakon tilos. |

| Fájl | Hiányzó hely | Naiv missing-to-ref | Elvárt státusz |
| --- | --- | --- | --- |
| `called-cyp2d6-star4-hom.vcf` | — (gold called) | — | Matcher ON: CYP2D6 \*4/\*4 CALLED **és** CYP2C9 \*4/\*4 CALLED. CYP2C9\*4: PharmCAT 3.4.0 `CYP2C9_translation.json` rs56165452 GRCh38 10:94981297 T>C, GT 1/1. Nem Ensembl-pin. CYP2D6\*4: rs3892097 22:42128945 C>T, GT 1/1. |
| `missing-cyp2d6-star4.vcf` | rs3892097 CYP2D6*4 GRCh38 22:42128945 | Normal Metabolizer | `INDETERMINATE`, nem NORMAL |
| `missing-cyp2c19-star2.vcf` | rs4244285 CYP2C19*2 GRCh38 10:94781859 | Normal Metabolizer | `INDETERMINATE`, nem NORMAL |
| `missing-dpyd-star2a.vcf` | rs3918290 DPYD*2A GRCh38 1:97450058 | Normal Metabolizer | `INDETERMINATE`, nem NORMAL |
| `missing-cyp2c9-star3.vcf` | rs1057910 CYP2C9*3 GRCh38 10:94981296 | Normal Metabolizer | `INDETERMINATE`, nem NORMAL |

HLA-B és UGT1A1\*28 a katalógusban `not_snv` → `NOT_TESTED` (nincs kitalált HLA-SNV; rs8175347 NCBI `delins`). Matcher ki.

