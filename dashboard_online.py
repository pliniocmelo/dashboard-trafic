import streamlit as st
import pandas as pd
import plotly.express as px

# ------ TEMA CUSTOMIZADO ------
def aplicar_estilo():
    st.markdown("""
        <style>
        body {
            background-color: #0f1117;
            color: white;
        }
        .stApp {
            background-color: #0f1117;
        }
        .stMetric label, .stMetric span {
            color: #c9a0ff !important;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .css-1v0mbdj.edgvbvh3 {
            color: #c9a0ff;
        }
        .css-1d391kg, .css-1avcm0n {
            width: 220px !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ------ CONFIGURAÇÃO INICIAL ------
st.set_page_config(page_title="Dashboard de Tráfego", layout="wide")
aplicar_estilo()
st.title("📊 Dashboard de Campanhas de Tráfego Hellu's")

# ------ CARREGAMENTO DE DADOS (SEM CACHE) ------
sheet_url = "https://docs.google.com/spreadsheets/d/1LqoPwbgU0WSRkNh_DnOYCgUeTgaGuLSoCBxTQb1v4eg/export?format=csv"

def carregar_dados():
    df = pd.read_csv(sheet_url)
    df.columns = [col.strip() for col in df.columns]

    colunas_numericas = ["Leads", "Alcance", "Impressões", "CPM", "CPL", "CPC", "CTR", "Cliques", "Valor usado"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("R\$", "", regex=True)
                .str.replace("%", "")
                .str.replace("\\.", "", regex=True)  # remove separador de milhar
                .str.replace(",", ".", regex=False)  # converte decimal para ponto
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

df = carregar_dados()

# ------ FILTROS ------
st.sidebar.markdown("## 🎯 Filtros")
campanhas = st.sidebar.multiselect("Campanhas", df["Campanha"].dropna().unique())
df_filtrado = df[df["Campanha"].isin(campanhas)] if campanhas else df

# ------ MÉTRICAS GERAIS ------
total_leads = df_filtrado["Leads"].sum()
total_gasto = df_filtrado["Valor usado"].sum()
total_ctr = df_filtrado["CTR"].mean()

col1, col2, col3 = st.columns([1,1,1])
col1.metric("📌 Total de Leads", f"{int(total_leads)}")
col2.metric("💰 Total Investido", f'R$ {total_gasto:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("📈 CTR Médio", f'{total_ctr:.2f}%')

st.markdown("---")

# ------ GRÁFICOS ------
colunas_para_graficos = ["Leads", "Alcance", "Impressões", "CPM", "CPL", "CPC", "CTR", "Cliques", "Valor usado"]
colunas_para_graficos = [col for col in colunas_para_graficos if col != "Campanha"]

grafico_idx = 0
while grafico_idx < len(colunas_para_graficos):
    colunas_linha = st.columns(2)
    for i in range(2):
        if grafico_idx >= len(colunas_para_graficos):
            break
        col = colunas_para_graficos[grafico_idx]
        with colunas_linha[i]:
            titulo = f"📊 {col} por Campanha"
            y_label = col + (" (%)" if col == "CTR" else "")
            formato_hover = "%{y:,.2f}%" if col == "CTR" else "R$ %{y:,.2f}" if col in ["CPM", "CPL", "CPC", "Valor usado"] else "%{y}"
            fig = px.bar(df_filtrado, x="Campanha", y=col, color="Campanha", title=titulo, labels={col: y_label})
            fig.update_traces(hovertemplate=f"<b>%{{x}}</b><br>{col}: {formato_hover}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)
        grafico_idx += 1

# ------ TABELA FINAL ------
df_visual = df_filtrado.copy()

for col in ["Valor usado", "CPM", "CPL", "CPC"]:
    if col in df_visual.columns:
        df_visual[col] = df_visual[col].apply(lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) else "")

if "CTR" in df_visual.columns:
    df_visual["CTR"] = df_visual["CTR"].apply(lambda x: f'{x:.2f}%' if pd.notnull(x) else "")

st.markdown("### 🗂️ Dados detalhados")
st.dataframe(df_visual, use_container_width=True)

st.markdown("---")
st.caption("Feito com 💜 por Hicon Soluções Integradas de Marketing e IA")