
import pandas as pd
from .data_loader import Columns

def summarize_by_gre(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(Columns.GRE)
          .agg(TOTAL_GRE=(Columns.CODIGOESCOLA, "count"), COM_DATA=("HAS_DATE", "sum"))
          .reset_index()
    )
    grouped["SEM_DATA"] = grouped["TOTAL_GRE"] - grouped["COM_DATA"]
    grouped["PCT_COM_DATA"] = (grouped["COM_DATA"] / grouped["TOTAL_GRE"] * 100)
    return grouped.sort_values("PCT_COM_DATA", ascending=False)

def summarize_by_gre_muni(df: pd.DataFrame) -> pd.DataFrame:
    totals = df.groupby(Columns.GRE)[Columns.CODIGOESCOLA].count().rename("TOTAL_GRE")
    base = (
        df.groupby([Columns.GRE, Columns.MUNICIPIO])
          .agg(TOTAL_MUNICIPIO=(Columns.CODIGOESCOLA, "count"), COM_DATA=("HAS_DATE", "sum"))
          .reset_index()
    )
    base = base.merge(totals, on=Columns.GRE, how="left")
    base["SEM_DATA"] = base["TOTAL_MUNICIPIO"] - base["COM_DATA"]
    base["PCT_COM_DATA"] = (base["COM_DATA"] / base["TOTAL_MUNICIPIO"] * 100)
    return base.sort_values(["PCT_COM_DATA", Columns.MUNICIPIO], ascending=[False, True])

def schools_table(df: pd.DataFrame) -> pd.DataFrame:
    out = df[[Columns.GRE, Columns.MUNICIPIO, Columns.ESCOLA, Columns.CODIGOESCOLA, Columns.DATAS, "HAS_DATE"]].copy()
    out["SITUACAO"] = out["HAS_DATE"].map({1: "COM DATA", 0: "SEM DATA"})
    return out.sort_values([Columns.GRE, Columns.MUNICIPIO, Columns.ESCOLA])