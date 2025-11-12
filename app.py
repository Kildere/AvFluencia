import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

from src.data_loader import load_consolidacao, save_uploaded_file_and_get_paths
from src.state import get_state
from src.indicators import summarize_by_gre


# =========================
# CONFIGURAÇÃO GERAL
# =========================
st.set_page_config(page_title="Avaliação de Fluência — Dashboard", layout="wide")
state = get_state()

# =========================
# Funções para persistência automática
# =========================
DATA_PATH = "data/base_consolidada.csv"
os.makedirs("data", exist_ok=True)

def load_saved_data():
    """Carrega base salva localmente, se existir."""
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return None

def save_data(df: pd.DataFrame):
    """Salva base consolidada localmente."""
    df.to_csv(DATA_PATH, index=False)

# =========================
# Tenta carregar base salva
# =========================
df = load_saved_data()
if df is not None:
    st.success("✅ Base consolidada carregada automaticamente.")
else:
    st.warning("⚠️ Nenhuma base encontrada. Faça o primeiro upload abaixo.")


# # =========================
# # CABEÇALHO INSTITUCIONAL — versão final e estável
# # =========================
st.markdown("""
<style>
.header-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 120px; /* distância igual entre as três logos */
    margin-bottom: 8px;
}
.header-text {
    text-align: center;
    font-size: 22px;
    font-weight: 600;
    line-height: 1.4em;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# Exibição das três logos com Streamlit (garante carregamento local)
st.markdown("<div class='header-container'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.image("src/SIAVE.jpeg", width=200)

with col2:
    st.image("src/Governo Estado Paraiba SEE.png", width=800)

with col3:
    st.markdown(
        "<div style='display:flex; justify-content:flex-end;'>",
        unsafe_allow_html=True
    )
    st.image("src/CAED.png", width=160)
    st.markdown("</div>", unsafe_allow_html=True)

    

st.markdown("</div>", unsafe_allow_html=True)


# Texto centralizado
st.markdown("""
<div class='header-text'>
  GOVERNO DO ESTADO DA PARAÍBA<br>
  SECRETARIA DE ESTADO DA EDUCAÇÃO DA PARAÍBA<br>
  GERÊNCIA EXECUTIVA DE DESENVOLVIMENTO ESCOLAR, ACOMPANHAMENTO<br>
  E APOIO À GESTÃO PARA RESULTADOS DE APRENDIZAGEM – <b>GEDRA</b><br>
  GERÊNCIA OPERACIONAL DE AVALIAÇÃO EDUCACIONAL E DESENVOLVIMENTO ACADÊMICO – <b>GOAED</b>
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Base: aba **Consolidação** do arquivo Excel. Coluna D = INEP (CODIGOESCOLA).")


# =========================
# SIDEBAR / UPLOAD
# =========================
with st.sidebar:
    st.header("⚙️ Configurações")
    target_dir = st.text_input("Pasta de destino", value=os.getcwd())
    uploaded = st.file_uploader("Envie o arquivo Excel (.xlsx)", type=["xlsx"])
    st.divider()
    st.page_link("pages/1_Regionais_Geral.py", label="Ir para: Regionais Geral", icon="🌎")

if uploaded is not None:
    save_path, folder_path = save_uploaded_file_and_get_paths(uploaded, target_dir)
    df = load_consolidacao(save_path)
    save_data(df)  # <=== salva automaticamente a nova base
    st.success("✅ Base consolidada atualizada e salva com sucesso!")
elif df is None:
    st.info("Envie o arquivo Excel para iniciar.")
    st.stop()


# =========================
# FUNÇÃO DE COR (faixas de %)
# 0–50 verm.; 51–80 laranja; 81–99 amarelo; 100 verde
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
# GRÁFICO DE PIZZA (COM/SEM DATA)
# =========================
st.subheader("📊 Panorama Geral")
total = len(df)
com_data = int(df["HAS_DATE"].sum())
sem_data = int(total - com_data)

pizza_df = pd.DataFrame(
    {"Situação": ["Com Data", "Sem Data"], "Valor": [com_data, sem_data]}
)

fig_pizza = px.pie(
    pizza_df,
    names="Situação",
    values="Valor",
    color="Situação",
    color_discrete_map={"Com Data": "#43a047", "Sem Data": "#e53935"},
    title="Distribuição Geral — Escolas com e sem Data",
)
fig_pizza.update_traces(
    textposition="inside",
    textinfo="percent+label",
    insidetextfont=dict(size=14)
)
fig_pizza.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=60, b=20, l=10, r=10))
st.plotly_chart(fig_pizza, use_container_width=True)

st.divider()

# =========================
# BARRAS VERTICAIS POR GRE (% COM DATA)
# =========================
st.subheader("📈 % Com Data por GRE")

gre_summary = summarize_by_gre(df).copy()
# Renomear eixo X: "12ª REGIÃO DE ENSINO" -> "12ª GRE"
if "GRE" in gre_summary.columns:
    gre_summary["GRE"] = gre_summary["GRE"].str.replace("REGIÃO DE ENSINO", "GRE")

gre_summary["PCT_ROUND"] = gre_summary["PCT_COM_DATA"].round(1)
gre_summary = gre_summary.sort_values("PCT_ROUND", ascending=False)
gre_summary["COLOR"] = gre_summary["PCT_ROUND"].apply(color_by_pct)

fig_bar = px.bar(
    gre_summary,
    x="GRE",
    y="PCT_ROUND",
    text="PCT_ROUND",
    color="COLOR",
    color_discrete_map="identity",
)
fig_bar.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
fig_bar.update_layout(
    xaxis_title="GRE",
    yaxis_title="% Com Data",
    font=dict(size=14),
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False,
    margin=dict(l=10, r=10, t=30, b=40),
)
st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# Rodapé do arquivo
# =========================
try:
    if 'save_path' in locals():
        file_info_path = save_path  # Upload recente
    else:
        file_info_path = DATA_PATH  # Base consolidada salva

    if os.path.exists(file_info_path):
        st.caption(
            f"📄 Fonte de dados: {os.path.basename(file_info_path)} "
            f"• 🕒 Última atualização: {datetime.fromtimestamp(os.path.getmtime(file_info_path)).strftime('%d/%m/%Y %H:%M')}"
        )
except Exception as e:
    st.warning(f"⚠️ Não foi possível exibir as informações do arquivo: {e}")