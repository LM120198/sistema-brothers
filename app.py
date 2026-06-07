import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3
import urllib.parse

# Configuração da página interna de gestão
st.set_page_config(page_title="Painel Interno - Brothers Network Finance", layout="wide")

# --- SISTEMA DE LOGIN ---
def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("<h1 style='text-align: center; color: #1F497D;'>🦅 Brothers Network Finance</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Painel Administrativo Restrito</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            with st.form("form_login"):
                usuario = st.text_input("Usuário:")
                senha = st.text_input("Senha:", type="password")
                botao_login = st.form_submit_button("Acessar Painel")
                
                if botao_login:
                    if usuario == "admin" and senha == "brothers2026":
                        st.session_state.autenticado = True
                        st.rerun()
                    else:
                        st.error("Acesso negado.")
        return False
    return True

# --- CONEXÃO COM O BANCO DE DADOS ---
def carregar_dados():
    conn = sqlite3.connect("brothers.db")
    # Garante que a tabela exista se o banco for limpo
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT, WhatsApp TEXT, Data_Nascimento TEXT, Mensagem TEXT,
            Dia_Aniv INTEGER, Mes_Aniv INTEGER,
            T1_BoasVindas TEXT, T2_AnaliseCredito TEXT, T3_GatilhoOferta TEXT,
            T4_MsgWhats TEXT, T5_PosVenda TEXT
        )
    """)
    df = pd.read_sql_query("SELECT * FROM membros", conn)
    conn.close()
    return df

def atualizar_status(df_editado):
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    for index, row in df_editado.iterrows():
        cursor.execute("""
            UPDATE membros SET 
                T1_BoasVindas=?, T2_AnaliseCredito=?, T3_GatilhoOferta=?, T4_MsgWhats=?, T5_PosVenda=?
            WHERE id=?
        """, (row['T1_BoasVindas'], row['T2_AnaliseCredito'], row['T3_GatilhoOferta'], row['T4_MsgWhats'], row['T5_PosVenda'], row['id']))
    conn.commit()
    conn.close()

# --- EXECUÇÃO DO PAINEL INTERNO ---
if verificar_login():
    
    if st.sidebar.button("🔒 Sair (Logout)"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("🦅 Central da Secretária - Brothers Network")
    st.markdown("---")

    membros_db = carregar_dados()

    aba_gestao, aba_calendario = st.tabs(["📊 Gerenciador de Tarefas e Disparos", "📅 Calendário de Relacionamento"])

    # --- ABA 1: GERENCIADOR DE TAREFAS ---
    with aba_gestao:
        st.subheader("Esteira de Produção e Atendimento")
        if membros_db.empty:
            st.info("Nenhum cliente cadastrado no banco de dados até o momento.")
        else:
            # Gerando links rápidos para o WhatsApp
            links_whats = []
            for idx, row in membros_db.iterrows():
                text_msg = f"Olá {row['Nome']}, seja bem-vindo à Brothers Network Finance. Vamos dar andamento à sua solicitação?"
                links_whats.append(f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(text_msg)}")
            
            membros_db["Ação"] = links_whats

            df_editado = st.data_editor(
                membros_db,
                column_config={
                    "id": None, "Dia_Aniv": None, "Mes_Aniv": None,
                    "Nome": st.column_config.TextColumn("Cliente", disabled=True, width="medium"),
                    "WhatsApp": st.column_config.TextColumn("WhatsApp", disabled=True),
                    "Data_Nascimento": st.column_config.DateColumn("Nascimento", disabled=True),
                    "Mensagem": st.column_config.TextColumn("Solicitação Inicial", disabled=True, width="large"),
                    "T1_BoasVindas": st.column_config.SelectboxColumn("T1: Boas-Vindas", options=["Pendente", "Concluído"]),
                    "T2_AnaliseCredito": st.column_config.SelectboxColumn("T2: Liminar/Crédito", options=["Pendente", "Concluído"]),
                    "T3_GatilhoOferta": st.column_config.SelectboxColumn("T3: Oferta", options=["Pendente", "Concluído"]),
                    "T4_MsgWhats": st.column_config.SelectboxColumn("T4: Aniversário", options=["Pendente", "Concluído"]),
                    "T5_PosVenda": st.column_config.SelectboxColumn("T5: Pós-Venda", options=["Pendente", "Concluído"]),
                    "Ação": st.column_config.LinkColumn("💬 WhatsApp", display_text="Chamar Cliente")
                },
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("💾 Salvar Alterações de Status", type="primary"):
                atualizar_status(df_editado)
                st.success("Alterações salvas com sucesso!")
                st.rerun()

    # --- ABA 2: CALENDÁRIO REFORMULADO (SEM ERRO VISUAL) ---
    with aba_calendario:
        st.subheader("Aniversariantes do Mês")
        hoje = datetime.date.today()
        
        meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_selecionado = st.selectbox("Selecione o Mês para Análise:", list(range(1, 13)), index=hoje.month - 1, format_func=lambda x: meses_nomes[x-1])
        
        if membros_db.empty:
            st.info("Nenhum cliente no banco de dados.")
        else:
            # Filtra aniversariantes do mês selecionado
            df_aniv_mes = membros_db[membros_db["Mes_Aniv"] == mes_selecionado]
            
            if df_aniv_mes.empty:
                st.write("Não há aniversariantes cadastrados neste mês.")
            else:
                # Exibe em formato de lista/cards limpos e modernos livres de erro de código
                for idx, row in df_aniv_mes.iterrows():
                    with st.container():
                        col_aniv1, col_aniv2, col_aniv3 = st.columns([1, 2, 2])
                        with col_aniv1:
                            st.metric(label="Dia do Aniversário", value=f"Dia {row['Dia_Aniv']}")
                        with col_aniv2:
                            st.markdown(f"**Cliente:** {row['Nome']}")
                            st.markdown(f"**Status de Contato:** `{row['T4_MsgWhats']}`")
                        with col_aniv3:
                            # Link direto para dar parabéns
                            msg_parabens = f"Parabéns, {row['Nome']}! Como presente da Brothers Network Finance, preparamos uma condição exclusiva para você hoje."
                            link_p = f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(msg_parabens)}"
                            st.link_button("🎉 Enviar Mensagem de Parabéns", link_p)
                        st.markdown("---")
