from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd
import pyreadstat


@dataclass
class FileSpec:
    file_stem: str
    variables: List[str]


def read_variable_spec(spec_path: str | Path) -> Dict[str, FileSpec]:
    df = pd.read_excel(spec_path, sheet_name=0)
    df.columns = [str(c).strip() for c in df.columns]

    file_col = "file_stem (Wave 1)"
    var_col = "var_name (Wave 1)"

    df[file_col] = df[file_col].ffill()
    df[var_col] = df[var_col].astype(str).str.strip()

    df = df[df[file_col].notna()]
    df = df[df[var_col].notna()]
    df = df[~df[var_col].isin(["nan", "NaN", "None", ""])]

    grouped = {}
    for stem, g in df.groupby(file_col, dropna=True):
        vars_ = g[var_col].dropna().astype(str).unique().tolist()
        grouped[str(stem).strip()] = FileSpec(file_stem=str(stem).strip(), variables=vars_)

    return grouped


def find_dta_file(root: str | Path, file_stem: str) -> Path:
    root = Path(root)
    matches = list(root.rglob(f"{file_stem}.dta"))
    if not matches:
        raise FileNotFoundError(f"Could not find {file_stem}.dta under {root}")
    return matches[0]


def available_columns(dta_path: str | Path) -> List[str]:
    _, meta = pyreadstat.read_dta(dta_path, metadataonly=True)
    return list(meta.column_names)


def choose_existing_columns(dta_path: str | Path, requested: List[str], extra_keys: List[str]) -> List[str]:
    cols = available_columns(dta_path)
    cols_lower = {c.lower(): c for c in cols}

    chosen = []
    for c in requested + extra_keys:
        if str(c).lower() in cols_lower:
            chosen.append(cols_lower[str(c).lower()])

    return list(dict.fromkeys(chosen))


def read_selected_columns(dta_path: str | Path, usecols: List[str]) -> pd.DataFrame:
    df, meta = pyreadstat.read_dta(dta_path, usecols=usecols)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def pick_first_existing(df: pd.DataFrame, candidates: List[str]):
    lower_map = {str(c).lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lower_map:
            return lower_map[c.lower()]
    return None


def normalize_string_id(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip()


def add_standard_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    hhid = pick_first_existing(out, ["hhid", "HHID"])
    pid = pick_first_existing(out, ["pid", "PID", "personid", "indid"])
    ea = pick_first_existing(out,["ea", "EA", "comm", "COMM", "commid", "COMMID", "community", "community_id", "Comcod", "COMCOD", "comcod"])
    district = pick_first_existing(out, ["district", "district_id", "dist"])

    if hhid is not None:
        out["hhid"] = normalize_string_id(out[hhid])
    if pid is not None:
        out["person_id"] = normalize_string_id(out[pid])
    if ea is not None:
        out["community_id"] = normalize_string_id(out[ea])
    if district is not None:
        out["district_id"] = normalize_string_id(out[district])

    out = out.loc[:, ~out.columns.duplicated()].copy()
    return out


def classify_file(stem: str) -> str:
    s = stem.upper()
    if s.startswith("AGSEC") or "GEOVARS" in s:
        return "agriculture"
    if s.startswith("GSEC") or s.startswith("HH"):
        return "household"
    if s.startswith("CSEC"):
        return "community"
    return "other"


def load_wave_sections(root: str | Path, spec_path: str | Path) -> Dict[str, pd.DataFrame]:
    spec = read_variable_spec(spec_path)

    extra_keys = [
        "hhid", "HHID",
        "pid", "PID", "personid", "indid",
        "ea", "EA",
        "comm", "COMM", "commid", "COMMID",
        "community", "community_id",
        "Comcod", "COMCOD", "comcod",
        "district", "DISTRICT", "district_id", "dist",
        "subcounty", "subcounty_id", "county", "parish",
        "region", "year", "Year"
    ]

    out = {}

    for stem, file_spec in spec.items():
        dta_path = find_dta_file(root, stem)
        usecols = choose_existing_columns(dta_path, file_spec.variables, extra_keys)

        if not usecols:
            print(f"Skipping {stem}: no requested columns found")
            continue

        df = read_selected_columns(dta_path, usecols)
        df = add_standard_keys(df)
        df["source_file"] = stem
        out[stem] = df

        print(f"Loaded {stem}: {df.shape[0]} rows, {df.shape[1]} cols")

    return out