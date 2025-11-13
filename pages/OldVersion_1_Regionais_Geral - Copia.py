import streamlit as st
import plotly.express as px
import os
import pandas as pd

from src.state import get_state
from src.data_loader import Columns
from src.indicators import summarize_by_gre, summarize_by_gre_muni, schools_table

st.set_page_config(page_title="Regionais Geral", layout="wide")
st.title("🌎 Regionais Geral")
st.caption("Visão hierárquica: GRE → Município → Escola. Gráficos verticais, ordem decrescente, fundo branco.")

# =========================
# ✅ Carregar DataFrame ativo (mantendo compatibilidade com app principal)
# =========================
DATA_PATH = os.path.join("data", "base_consolidada.csv")
state = get_state()

if "df" in state and not state["df"].empty:
    df = state["df"]
elif os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    state["df"] = df
else:
    st.warning("⚠️ Carregue o arquivo na página principal (upload na barra lateral).")
    st.stop()

# =========================
# Função de cores (%)
# =========================
def color_by_pct(v: float) -> str:
    if v <= 50:
        return "#e53935"   # vermelho
    elif v <= 80:
        return "#fb8c00"   # laranja
    elif v < 100:
        return "#fdd835"   # amarelo
    else:
        return "#43a047"   # verde

# =========================
# 1️⃣ % COM DATA POR GRE
# =========================
st.subheader("1️⃣ % Com Data por GRE")

gre = summarize_by_gre(df).copy()
gre["GRE"] = gre["GRE"].str.replace("REGIÃO DE ENSINO", "GRE")
gre["PCT_ROUND"] = gre["PCT_COM_DATA"].round(1)
gre = gre.sort_values("PCT_ROUND", ascending=False)
gre["COLOR"] = gre["PCT_ROUND"].apply(color_by_pct)

fig_gre = px.bar(
    gre,
    x="GRE",
    y="PCT_ROUND",
    text="PCT_ROUND",
    color="COLOR",
    color_discrete_map="identity",
)
fig_gre.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
fig_gre.update_layout(
    xaxis_title="GRE",
    yaxis_title="% Com Data",
    font=dict(size=14),
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False,
    margin=dict(l=10, r=10, t=30, b=40),
)
st.plotly_chart(fig_gre, use_container_width=True)

st.divider()

# =========================
# 2️⃣ % COM DATA POR MUNICÍPIO
# =========================
st.subheader("2️⃣ % Com Data por Município (dentro da GRE)")

gre_opts = sorted(df[Columns.GRE].unique().tolist())
sel_gre = st.selectbox("Selecione a GRE:", options=gre_opts)

block = df[df[Columns.GRE] == sel_gre]
muni = summarize_by_gre_muni(block).copy()
muni["PCT_ROUND"] = muni["PCT_COM_DATA"].round(1)
muni = muni.sort_values("PCT_ROUND", ascending=False)
muni["COLOR"] = muni["PCT_ROUND"].apply(color_by_pct)

fig_muni = px.bar(
    muni,
    x=Columns.MUNICIPIO,
    y="PCT_ROUND",
    text="PCT_ROUND",
    color="COLOR",
    color_discrete_map="identity",
)
fig_muni.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
fig_muni.update_layout(
    xaxis_title="Município",
    yaxis_title="% Com Data",
    font=dict(size=14),
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False,
    margin=dict(l=10, r=10, t=30, b=40),
    height=600,
)
st.plotly_chart(fig_muni, use_container_width=True)

st.divider()

# =========================
# 3️⃣ TABELA DE ESCOLAS — situação (Com / Sem Data)
# =========================
st.subheader("3️⃣ Escolas — Situação e Dados")

tbl = schools_table(df)
st.dataframe(tbl, use_container_width=True)
st.caption("🟢 COM DATA | 🔴 SEM DATA — Filtre ou baixe a tabela se desejar.")
