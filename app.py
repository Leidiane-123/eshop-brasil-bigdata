import streamlit as st
import pandas as pd
from pymongo import MongoClient
import os
import plotly.express as px

# Configuração Inicial da Página
st.set_page_config(page_title="E-Shop Brasil - Big Data Console", layout="wide")

# Conexão com o MongoDB (Configurada para o ambiente Docker)
# O URI utiliza o nome do serviço definido no docker-compose
try:
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client['eshop_db']
    clientes = db['clientes']
    pedidos = db['pedidos']
except Exception as e:
    st.error(f"Erro ao ligar ao MongoDB: {e}")

# Interface Principal
st.title("🚀 E-Shop Brasil: Gestão e Análise de Big Data")
st.markdown("---")

# Barra Lateral para Navegação (Conforme Item 5.2 da Documentação)
st.sidebar.header("Módulos do Sistema")
opcao = st.sidebar.radio("Selecione a Operação:", 
    ["Dashboard de Visualização", "Ingestão de Dados", "Manutenção (Editar/Excluir)", "Inteligência e Concatenação"])

# --- 1. VISUALIZAÇÃO (READ) ---
if opcao == "Dashboard de Visualização":
    st.header("📋 Visualização de Registos")
    dados = list(clientes.find())
    if dados:
        df = pd.DataFrame(dados)
        # Limpeza do ID interno do Mongo para exibição
        st.dataframe(df.drop(columns=['_id']), use_container_width=True)
        
        # Insight Gráfico
        fig = px.histogram(df, x="regiao", title="Distribuição de Clientes por Região")
        st.plotly_chart(fig)
    else:
        st.info("O banco de dados está vazio. Vá ao módulo de Ingestão para adicionar dados.")

# --- 2. INSERÇÃO (CREATE) ---
elif opcao == "Ingestão de Dados":
    st.header("📥 Ingestão de Dados (Manual ou Lote)")
    
    with st.form("form_cliente"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail")
        with col2:
            regiao = st.selectbox("Região", ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"])
            valor = st.number_input("Valor de Compras (R$)", min_value=0.0, step=0.01)
        
        enviar = st.form_submit_button("Ingerir no MongoDB")
        
        if enviar:
            if nome and email:
                clientes.insert_one({"nome": nome, "email": email, "regiao": regiao, "valor": valor})
                st.success(f"Cliente {nome} integrado ao Cluster com sucesso!")
            else:
                st.error("Por favor, preencha os campos obrigatórios.")

# --- 3. MANUTENÇÃO (UPDATE/DELETE) ---
elif opcao == "Manutenção (Editar/Excluir)":
    st.header("🛠️ Manutenção de Registos")
    lista_clientes = [c['nome'] for c in clientes.find()]
    
    if lista_clientes:
        cliente_sel = st.selectbox("Selecione o Cliente para Gerir:", lista_clientes)
        operacao = st.radio("Ação:", ["Editar Valor", "Excluir Registo"])
        
        if operacao == "Editar Valor":
            novo_valor = st.number_input("Novo Valor Acumulado:", step=0.01)
            if st.button("Confirmar Atualização"):
                clientes.update_one({"nome": cliente_sel}, {"$set": {"valor": novo_valor}})
                st.success(f"Dados de {cliente_sel} atualizados.")
        
        elif operacao == "Excluir Registo":
            if st.button("⚠️ ELIMINAR PERMANENTEMENTE"):
                clientes.delete_one({"nome": cliente_sel})
                st.warning(f"Registo de {cliente_sel} removido do Big Data.")
                st.rerun()
    else:
        st.info("Nenhum dado disponível para manutenção.")

# --- 4. CONCATENAÇÃO E INTELIGÊNCIA (AGGREGATION FRAMEWORK) ---
elif opcao == "Inteligência e Concatenação":
    st.header("🧠 Concatenação e Análise Avançada")
    st.write("Processamento de grandes volumes utilizando Aggregation Pipelines.")
    
    if st.button("Executar Pipeline de Concatenação"):
        # Pipeline que agrupa por região e calcula métricas (Simulação de Big Data)
        pipeline = [
            {
                "$group": {
                    "_id": "$regiao",
                    "receita_total": {"$sum": "$valor"},
                    "media_por_cliente": {"$avg": "$valor"},
                    "contagem": {"$sum": 1}
                }
            },
            {"$sort": {"receita_total": -1}}
        ]
        resultado = list(clientes.aggregate(pipeline))
        
        if resultado:
            st.write("Dados Concatenados e Agregados:")
            st.table(resultado)
        else:
            st.warning("Dados insuficientes para processar a agregação.")