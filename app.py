import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.express as px
import io

st.set_page_config(page_title="Análise de Rastreamento", layout="wide")
st.image("rastreio imagem.png", width=200)  # Altere para o nome do seu arquivo de imagem

st.title("📊 Sistema de Análise Logística de Rastreamento Veicular")

# Upload das planilhas
endereco_file = st.file_uploader("Importar planilha de endereços (motoristas e coordenadores)", type=["xls", "xlsx"])
feriado_file = st.file_uploader("Importar planilha de feriados do ano", type=["xls", "xlsx"])
rastreamento_file = st.file_uploader("Importar planilha de rastreamento", type=["xls", "xlsx"])
placas_file = st.file_uploader("(Opcional) Importar planilha com placas a serem analisadas", type=["xls", "xlsx"])

def ler_planilha(file):
    return pd.read_excel(file)

if endereco_file and feriado_file and rastreamento_file:
    df_enderecos = ler_planilha(endereco_file)
    df_feriados = ler_planilha(feriado_file)
    df_rastreamento = ler_planilha(rastreamento_file)

    if placas_file:
        df_placas = ler_planilha(placas_file)
        placas_filtrar = df_placas['Placa / Identificação'].astype(str).tolist()
        df_rastreamento = df_rastreamento[df_rastreamento['Placa / Identificação'].astype(str).isin(placas_filtrar)]

    st.success("✅ Todas as planilhas foram importadas com sucesso!")

    st.subheader("📍 Endereços")
    st.dataframe(df_enderecos)

    st.subheader("🗕️ Feriados")
    st.dataframe(df_feriados)

    feriados = pd.to_datetime(df_feriados['Data']).dt.date

    df_enderecos['Endereço'] = df_enderecos['Endereço'].astype(str)
    df_rastreamento['Endereço'] = df_rastreamento['Endereço'].astype(str)

    motoristas = df_enderecos[df_enderecos['Tipo'].str.lower() == 'motorista']['Endereço'].tolist()
    coordenadores = df_enderecos[df_enderecos['Tipo'].str.lower() == 'coordenador']['Endereço'].tolist()

    df_rastreamento['Data da Posição'] = pd.to_datetime(df_rastreamento['Data da Posição'])
    df_rastreamento['Data'] = df_rastreamento['Data da Posição'].dt.date
    df_rastreamento['Hora'] = df_rastreamento['Data da Posição'].dt.time
    df_rastreamento['Dia da Semana'] = df_rastreamento['Data da Posição'].dt.weekday

    st.sidebar.header("⚙️ Critérios de Análise")
    criterio_end_motorista = st.sidebar.checkbox("Presença em endereço de MOTORISTA", value=True)
    criterio_end_coordenador = st.sidebar.checkbox("Presença em endereço de COORDENADOR", value=True)
    criterio_feriado = st.sidebar.checkbox("Funcionamento em feriado", value=True)
    criterio_fds = st.sidebar.checkbox("Funcionamento no fim de semana", value=True)
    criterio_apos_18h = st.sidebar.checkbox("Funcionamento após as 18h", value=True)

    ocorrencias = []

    for _, row in df_rastreamento.iterrows():
        eventos = []
        endereco_atual = row['Endereço']
        data = row['Data']
        hora = row['Hora']
        ignicao = str(row['Ignição']).upper()
        velocidade = row.get('Velocidade (km/h)', 0)

        if criterio_end_motorista and any(end in endereco_atual for end in motoristas):
            eventos.append("Presença em endereço de MOTORISTA")
        if criterio_end_coordenador and any(end in endereco_atual for end in coordenadores):
            eventos.append("Presença em endereço de COORDENADOR")
        if criterio_feriado and data in feriados and (ignicao == "ON" or velocidade > 0):
            eventos.append("Funcionamento em feriado")
        if criterio_fds and row['Dia da Semana'] in [5, 6] and (ignicao == "ON" or velocidade > 0):
            eventos.append("Funcionamento no fim de semana")
        if criterio_apos_18h and hora > time(18, 0) and (ignicao == "ON" or velocidade > 0):
            eventos.append("Funcionamento após as 18h")

        ocorrencias.append("; ".join(eventos) if eventos else "")

    df_rastreamento['Ocorrências Encontradas'] = ocorrencias

    df_oc = df_rastreamento[df_rastreamento['Ocorrências Encontradas'] != ""].copy()

    st.subheader("📋 Rastreamento com Ocorrências")
    st.dataframe(df_oc)

    df_explode = df_oc.assign(ocorrencia=df_oc['Ocorrências Encontradas'].str.split("; ")).explode('ocorrencia')

    st.subheader("📈 Ocorrências por Tipo")
    fig_tipo = px.histogram(df_explode, x='ocorrencia', title="Distribuição de Ocorrências", text_auto=True)
    st.plotly_chart(fig_tipo, use_container_width=True)

    st.subheader("🗓️ Ocorrências por Data")
    fig_data = px.histogram(df_oc, x='Data', title="Ocorrências por Data", text_auto=True)
    st.plotly_chart(fig_data, use_container_width=True)

    # Gerar o arquivo Excel em memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_oc.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="📅 Baixar planilha com ocorrências",
        data=output,
        file_name="ocorrencias_rastreamento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("⚠️ Por favor, importe as três planilhas para começar a análise.")
