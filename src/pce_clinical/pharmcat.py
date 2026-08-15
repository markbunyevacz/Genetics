"""FR-300: run PharmCAT NamedAlleleMatcher + Phenotyper. Repo MATCHER_ON stays false."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

from pce_report.panel import PREPARE_12

ROOT = Path(__file__).resolve().parents[2]
PIN_PATH = ROOT / "docs" / "pce" / "Sources" / "official" / "pharmcat-3.4.0-pin.json"
PHARMCAT_VERSION = "3.4.0"
HLA_GENES = {"HLA-B", "HLA-A"}
UGT_TA_NOTE_HU = (
    "UGT1A1*28 a TATA-box (timin-adenin) ismétléshossz. Ezt a PharmCAT csak akkor hívja, "
    "ha a variáns fájlban megvan ez a hely. Ha nincs, a laboreredményt outside-callban kell beküldeni."
)
HLA_NOTE_HU = (
    "A HLA-B tipizálást a labor végzi. A PharmCAT NamedAlleleMatcher VCF pontmutációból "
    "HLA-allélt nem hív. A laboreredményt outside-callban kell beküldeni."
)
CNV_NOTE_HU = (
    "CYP2D6 kópiaszám, deléció, duplikáció és hibrid allél ebből a VCF-ből nem jön ki. "
    "A PharmCAT ezt research-módban SNV/kis-indel alapján hívja; ultragyors metabolizáló "
    "és gén-deléció ezért nem állítható. Ha a bemenetből a szerkezeti variáns nem "
    "meghatározható, a hívás INDETERMINATE, ha a PharmCAT több diplotípust ad, vagy "
    "a *1 a hiányzó helyekből jönne."
)


class PharmcatError(RuntimeError):
    pass


def _pin() -> dict[str, Any]:
    return json.loads(PIN_PATH.read_text(encoding="utf-8"))


def jar_path() -> Path:
    env = os.environ.get("PCE_PHARMCAT_JAR")
    if env:
        path = Path(env)
        if path.is_file():
            return path
    pin = _pin()
    local = ROOT / pin["runtime_path"]
    if local.is_file():
        return local
    return local


def _offline() -> bool:
    flag = os.environ.get("PCE_PHARMCAT_OFFLINE", "").strip().lower()
    if flag in {"1", "true", "yes", "on"}:
        return True
    ci = os.environ.get("CI", "").strip().lower()
    return ci in {"1", "true"}


def ensure_jar() -> Path:
    pin = _pin()
    path = jar_path()
    expected = pin["sha256"]
    if path.is_file():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest == expected:
            return path
        raise PharmcatError(f"PharmCAT jar sha256 mismatch: {digest}")
    if _offline():
        raise PharmcatError(
            f"PharmCAT jar missing at {path} (offline; CI must run fetch_software_ready_pins.py --jar-only)"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        pin["url"],
        headers={"User-Agent": "PrecisionClinicalEngine/0.1 (pharmcat-pin)"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        blob = resp.read()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != expected:
        raise PharmcatError(f"PharmCAT jar sha256 mismatch: {digest}")
    path.write_bytes(blob)
    return path


def java_bin() -> str:
    found = shutil.which("java")
    if not found:
        raise PharmcatError("java not on PATH; PharmCAT NamedAlleleMatcher needs a JRE")
    return found


def with_chr_prefix(text: str) -> str:
    """PharmCAT GRCh38 positions use chr1..chr22. Our gold VCFs omit the prefix."""
    out: list[str] = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            out.append(line)
            continue
        parts = line.split("\t")
        chrom = parts[0]
        if chrom and not chrom.lower().startswith("chr"):
            parts[0] = "chr" + chrom
        out.append("\t".join(parts))
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def run_matcher_and_phenotyper(vcf_text: str, *, workdir: Path | None = None) -> dict[str, Any]:
    """Call PharmCAT NamedAlleleMatcher then Phenotyper. CYP2D6 research mode is required."""
    jar = ensure_jar()
    java = java_bin()
    tmp = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="pce-pharmcat-"))
    tmp.mkdir(parents=True, exist_ok=True)
    vcf_path = tmp / "input.vcf"
    vcf_path.write_text(with_chr_prefix(vcf_text), encoding="utf-8")
    cmd = [
        java,
        "-jar",
        str(jar),
        "-matcher",
        "-phenotyper",
        "-research",
        "cyp2d6",
        "-vcf",
        str(vcf_path),
        "-o",
        str(tmp),
        "-bf",
        "pce",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        raise PharmcatError(
            "PharmCAT NamedAlleleMatcher/Phenotyper failed: "
            + (proc.stderr or proc.stdout or "")[-2000:]
        )
    match_path = tmp / "pce.match.json"
    pheno_path = tmp / "pce.phenotype.json"
    if not match_path.is_file() or not pheno_path.is_file():
        raise PharmcatError("PharmCAT did not write match.json and phenotype.json")
    match = json.loads(match_path.read_text(encoding="utf-8"))
    pheno = json.loads(pheno_path.read_text(encoding="utf-8"))
    return {
        "pharmcat_version": PHARMCAT_VERSION,
        "named_allele_matcher_version": (match.get("metadata") or {}).get("namedAlleleMatcherVersion"),
        "match": match,
        "phenotype": pheno,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _dip_name(row: dict[str, Any]) -> str | None:
    name = row.get("name") or row.get("label")
    if isinstance(name, str) and name.strip() and name != "Unknown/Unknown":
        return name.strip()
    return None


def _messages(rec: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for item in rec.get("messages") or []:
        if isinstance(item, dict) and item.get("message"):
            out.append(str(item["message"]))
        elif isinstance(item, str):
            out.append(item)
    return out


def _missing_count(match_row: dict[str, Any] | None) -> int:
    if not match_row:
        return 0
    md = match_row.get("matchData") or {}
    return len(md.get("missingPositions") or [])


def _looks_like_reference_call(name: str | None) -> bool:
    if not name:
        return False
    compact = name.replace(" ", "").lower()
    return compact in {"*1/*1", "reference/reference"} or "rs9923231 reference" in name.lower() or (
        "rs6025 reference" in name.lower()
    )


def coverage_from_pharmcat(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Map PharmCAT JSON to PREPARE-12 gene_coverage. Do not pick among unphased alternatives."""
    match = bundle["match"]
    pheno = bundle["phenotype"]
    by_match = {row.get("gene"): row for row in (match.get("results") or []) if row.get("gene")}
    reports = pheno.get("geneReports") or {}
    versions = []
    sources = []
    out: list[dict[str, Any]] = []
    for gene in PREPARE_12:
        rec = reports.get(gene) or {}
        match_row = by_match.get(gene)
        if rec.get("alleleDefinitionVersion"):
            versions.append(str(rec["alleleDefinitionVersion"]))
        if rec.get("alleleDefinitionSource"):
            sources.append(str(rec["alleleDefinitionSource"]))
        base = {
            "gene": gene,
            "pharmcat_absent_to_ref": False,
            "matcher_on": True,
            "diplotype": None,
            "phased": bool((match_row or {}).get("phased") or rec.get("phased")),
            "pharmcat_version": bundle.get("pharmcat_version"),
            "named_allele_matcher_version": bundle.get("named_allele_matcher_version"),
            "allele_definition_version": rec.get("alleleDefinitionVersion"),
            "allele_definition_source": rec.get("alleleDefinitionSource"),
            "phenotype_version": rec.get("phenotypeVersion"),
            "call_source": rec.get("callSource"),
        }
        if gene in HLA_GENES:
            out.append(
                {
                    **base,
                    "callability": "NOT_TESTED",
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": HLA_NOTE_HU,
                }
            )
            continue
        dips = list((match_row or {}).get("diplotypes") or [])
        names = [n for n in (_dip_name(d) for d in dips) if n]
        missing_n = _missing_count(match_row)
        msgs = _messages(rec)
        ref_or_missing = any("reference or missing" in m.lower() for m in msgs)
        if gene == "UGT1A1" and (not names or missing_n > 0):
            out.append(
                {
                    **base,
                    "callability": "NOT_TESTED",
                    "missing": (match_row or {}).get("matchData", {}).get("missingPositions") or [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": UGT_TA_NOTE_HU,
                }
            )
            continue
        if len(names) > 1:
            out.append(
                {
                    **base,
                    "callability": "INDETERMINATE",
                    "diplotype": None,
                    "ambiguous_diplotypes": names,
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": (
                        f"{gene}: a PharmCAT NamedAlleleMatcher {len(names)} diplotípust adott "
                        f"({', '.join(names)}), a VCF nincs fázisban. Nem választunk közülük. INDETERMINATE."
                    ),
                }
            )
            continue
        if len(names) == 1:
            name = names[0]
            if _looks_like_reference_call(name) and (missing_n > 0 or ref_or_missing):
                out.append(
                    {
                        **base,
                        "callability": "INDETERMINATE",
                        "diplotype": None,
                        "missing": [],
                        "naive_missing_to_ref_would_claim": name,
                        "note_hu": (
                            f"{gene}: a PharmCAT {name}-t adna, de definiáló hely hiányzik a VCF-ből "
                            "vagy a hívás a hiányzó helyet referenciának venné. Ez nem *1. INDETERMINATE."
                        ),
                    }
                )
                continue
            note = f"{gene}: PharmCAT NamedAlleleMatcher + Phenotyper: {name}."
            if gene == "CYP2D6":
                note = note + " " + CNV_NOTE_HU
            out.append(
                {
                    **base,
                    "callability": "CALLED",
                    "diplotype": name,
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "sv_determined": False if gene == "CYP2D6" else None,
                    "note_hu": note,
                }
            )
            continue
        out.append(
            {
                **base,
                "callability": "INDETERMINATE",
                "missing": [],
                "naive_missing_to_ref_would_claim": None,
                "note_hu": (
                    f"{gene}: a PharmCAT NamedAlleleMatcher nem adott egyértelmű diplotípust. Nem *1."
                ),
            }
        )
    allele_ver = next((v for v in versions if v), None)
    meta = pheno.get("metadata") or match.get("metadata") or {}
    if not allele_ver:
        allele_ver = (
            meta.get("alleleDefinitionVersion")
            or meta.get("pharmVarVersion")
            or meta.get("namedAlleleMatcherVersion")
        )
    cpic_data = next((row.get("phenotype_version") for row in out if row.get("phenotype_version")), None)
    if not cpic_data:
        cpic_data = meta.get("cpicVersion") or meta.get("phenotypeVersion") or allele_ver
    for row in out:
        row["pharmvar_version"] = allele_ver
        row["cpic_data_version"] = row.get("phenotype_version") or cpic_data
    return out
