import streamlit as st
import datetime
import sqlite3

# Configuração da página pública do cliente
st.set_page_config(page_title="Membros - Brothers Network Finance", layout="centered")

# --- CONEXÃO COM O BANCO DE DADOS COMPARTILHADO ---
def salvar_membro_landing(nome, whats, data_nasci, msg):
    try:
        dt = datetime.datetime.strptime(str(data_nasci), "%Y-%m-%d")
        conn = sqlite3.connect("brothers.db")
        cursor = conn.cursor()
        # Garante a criação se o arquivo for inicializado por aqui
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS membros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome TEXT, WhatsApp TEXT, Data_Nascimento TEXT, Mensagem TEXT,
                Dia_Aniv INTEGER, Mes_Aniv INTEGER,
                T1_BoasVindas TEXT, T2_AnaliseCredito TEXT, T3_GatilhoOferta TEXT,
                T4_MsgWhats TEXT, T5_PosVenda TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO membros (
                Nome, WhatsApp, Data_Nascimento, Mensagem, Dia_Aniv, Mes_Aniv,
                T1_BoasVindas, T2_AnaliseCredito, T3_GatilhoOferta, T4_MsgWhats, T5_PosVenda
            ) VALUES (?, ?, ?, ?, ?, ?, 'Pendente', 'Pendente', 'Pendente', 'Pendente', 'Pendente')
        """, (nome, whats, str(data_nasci), msg, dt.day, dt.month))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

# --- DESIGN DA LANDING PAGE PREMIUM ---

# Cabeçalho de Autoridade
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🦅 BROTHERS NETWORK FINANCE</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #FFFFFF; font-weight: 300;'>A Elite do Mercado Financeiro e Soluções Estratégicas</h3>", unsafe_allow_html=True)
st.write("\n")

# Banner de Solução de Dor (Headline Forte)
st.info("### ⚖️ Restauração de Crédito & Blindagem Patrimonial\nAtuamos de forma ágil através de **liminar judicial** para limpar o seu histórico e devolver o seu poder de compra no mercado.")

st.markdown("---")

# Divisão de Conteúdo (Benefícios vs Formulário)
col_info, col_form = st.columns([1, 1.2])

with col_info:
    st.markdown("### Por que fazer parte?")
    
    st.markdown("🌐 **Networking de Elite**\nConexão direta com investidores, empresários e grandes players do mercado financeiro.")
    
    st.markdown("⚡ **Atendimento Prioritário**\nNossa secretária eletrônica monitora sua solicitação em tempo real para dar agilidade ao processo.")
    
    st.markdown("🔒 **Privacidade Absoluta**\nSeus dados são protegidos sob sigilo bancário e jurídico estrito.")
    
    st.write("\n")
    st.warning("⚠️ **Vagas Limitadas:** Mantemos a comunidade restrita para garantir a qualidade das conexões e a velocidade das liminares.")

with col_form:
    st.markdown("### Solicite seu Atendimento")
    
    with st.form("form_captura", clear_on_submit=True):
        nome = st.text_input("Nome Completo:", placeholder="Digite seu nome")
        whatsapp = st.text_input("WhatsApp com DDD (Somente Números):", placeholder="Ex: 11999999999")
        data_nascimento = st.date_input("Data de Nascimento:", min_value=datetime.date(1940, 1, 1), max_value=datetime.date.today())
        
        opcoes_ajuda = [
            "Limpar Nome / Restauração de Crédito (Liminar Judicial)",
            "Acesso a Linhas de Crédito / Financiamentos",
            "Investimentos de Alta Performance",
            "Networking e Parcerias Comerciais"
        ]
        servico = st.selectbox("Qual seu objetivo principal hoje?", opcoes_ajuda)
        detalhes = st.text_area("Descreva brevemente o seu caso (Opcional):", placeholder="Ex: Preciso limpar meu score urgentemente...")
        
        botao_enviar = st.form_submit_button("QUERO FAZER PARTE DA COMUNIDADE")
        
        if botao_enviar:
            if nome and whatsapp:
                mensagem_completa = f"[{servico}] {detalhes}"
                sucesso = salvar_membro_landing(nome, whatsapp, data_nascimento, mensagem_completa)
                
                if sucesso:
                    st.success(f"🔥 Excelente, {nome}! Seus dados foram validados. Nossa Secretária Eletrônica já gerou seu protocolo e o fluxo de atendimento foi iniciado. Aguarde nosso contato no WhatsApp.")
                else:
                    st.error("Erro técnico ao salvar os dados. Tente novamente em instantes.")
            else:
                st.error("Por favor, preencha obrigatoriamente o Nome e o WhatsApp.")
