import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Online", layout="wide")
st.title("📊 Dashboard com Dados em Tempo Real (Google Sheets)")

# URL da planilha no formato CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1LqoPwbgU0WSRkNh_DnOYCgUeTgaGuLSoCBxTQb1v4eg/export?format=csv"

@st.cache_data
def carregar_dados():
    df = pd.read_csv(sheet_url)
    df.columns = [col.strip() for col in df.columns]

    # Limpeza de dados
    df["Crédito Desejado (R$)"] = df["Crédito Desejado (R$)"].replace(
        {"R\$": "", ",": "", ".": ""}, regex=True
    ).astype(float)
    df["Data da Solicitação"] = pd.to_datetime(df["Data da Solicitação"], errors="coerce")

    return df

df = carregar_dados()

# FILTROS (opcional)
st.sidebar.header("🔎 Filtros")
corretor = st.sidebar.multiselect("Corretor Responsável", df["Corretor Responsável"].dropna().unique())
finalidade = st.sidebar.multiselect("Finalidade do Crédito", df["Finalidade do Crédito"].dropna().unique())
unidade = st.sidebar.multiselect("Unidade da Corretora", df["Unidade da Corretora"].dropna().unique())

df_filtrado = df.copy()
if corretor:
    df_filtrado = df_filtrado[df_filtrado["Corretor Responsável"].isin(corretor)]
if finalidade:
    df_filtrado = df_filtrado[df_filtrado["Finalidade do Crédito"].isin(finalidade)]
if unidade:
    df_filtrado = df_filtrado[df_filtrado["Unidade da Corretora"].isin(unidade)]

# GRÁFICOS

# 1. Total por finalidade
fig1 = px.bar(
    df_filtrado.groupby("Finalidade do Crédito")["Crédito Desejado (R$)"].sum().reset_index(),
    x="Finalidade do Crédito",
    y="Crédito Desejado (R$)",
    title="💰 Total de Crédito por Finalidade",
    color="Finalidade do Crédito"
)

# 2. Solicitações por corretor
df_corretores = df_filtrado["Corretor Responsável"].value_counts().reset_index()
df_corretores.columns = ["Corretor", "Quantidade"]
fig2 = px.bar(
    df_corretores,
    x="Corretor",
    y="Quantidade",
    title="👤 Solicitações por Corretor",
    color="Corretor"
)

# 3. Crédito por unidade
fig3 = px.pie(
    df_filtrado,
    names="Unidade da Corretora",
    values="Crédito Desejado (R$)",
    title="🏢 Distribuição de Crédito por Unidade"
)

# 4. Status da negociação
fig4 = px.pie(
    df_filtrado,
    names="Status da Negociação",
    title="📌 Status das Negociações"
)

# 5. Evolução temporal
df_tempo = df_filtrado.groupby("Data da Solicitação")["Crédito Desejado (R$)"].sum().reset_index()
fig5 = px.line(
    df_tempo,
    x="Data da Solicitação",
    y="Crédito Desejado (R$)",
    title="📈 Evolução de Crédito Solicitado"
)

# Layout
col1, col2 = st.columns(2)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
col3.plotly_chart(fig3, use_container_width=True)
col4.plotly_chart(fig4, use_container_width=True)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.caption("Atualizado em tempo real via Google Sheets ✨")
