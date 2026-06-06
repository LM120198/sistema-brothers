import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3

# Configuração da página com layout amplo
st.set_page_config(page_title="Brothers Network Finance - Sistema Master", layout="wide")

# --- SISTEMA DE LOGIN E SEGURANÇA ---
def verificar_login():
    """Cria uma tela de bloqueio e só libera o sistema se a senha estiver correta"""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("<h1 style='text-align: center; color: #1F497D;'>🦅 Brothers Network Finance</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Área Restrita - Faça Login para Acessar</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            with st.form("form_login"):
                usuario = st.text_input("Usuário:")
                senha = st.text_input("Senha:", type="password")
                botao_login = st.form_submit_button("Entrar no Sistema")
                
                if botao_login:
                    # Aqui ficam o usuário e senha padrão definidos para o teste
                    if usuario == "admin" and senha == "brothers2026":
                        st.session_state.autenticado = True
                        st.success("Acesso liberado!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
        return False
    return True

# --- CONEXÃO COM O BANCO DE DADOS (SQLITE) ---
def conectar_banco():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT, WhatsApp TEXT, Data_Nascimento TEXT, Mensagem TEXT,
            Dia_Aniv INTEGER, Mes_Aniv INTEGER,
            T1_BoasVindas TEXT, T2_AnaliseCredito TEXT, T3_GatilhoOferta TEXT,
            T4_MsgWhats TEXT, T5_PosVenda TEXT, T6_Fidelizacao TEXT,
            T7_Networking TEXT, T8_Upgrade TEXT, T9_Fechamento TEXT, T10_Arquivo TEXT
        )
    """)
    conn.commit()
    return conn

# Inicializa o banco de dados
conectar_banco()

def carregar_dados():
    conn = sqlite3.connect("brothers.db")
    df = pd.read_sql_query("SELECT * FROM membros", conn)
    conn.close()
    return df

def salvar_membro(nome, whats, data_nasci, msg):
    dt = datetime.datetime.strptime(str(data_nasci), "%Y-%m-%d")
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO membros (
            Nome, WhatsApp, Data_Nascimento, Mensagem, Dia_Aniv, Mes_Aniv,
            T1_BoasVindas, T2_AnaliseCredito, T3_GatilhoOferta, T4_MsgWhats, T5_PosVenda,
            T6_Fidelizacao, T7_Networking, T8_Upgrade, T9_Fechamento, T10_Arquivo
        ) VALUES (?, ?, ?, ?, ?, ?, 'Pendente', 'Pendente', 'Pendente', 'Pendente', 'Pendente', 'Pendente', 'Pendente', 'Pendente', 'Pendente', 'Pendente')
    """, (nome, whats, str(data_nasci), msg, dt.day, dt.month))
    conn.commit()
    conn.close()

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

# --- SÓ RODA O SISTEMA SE O LOGIN FOR SUCESSO ---
if verificar_login():
    
    # Botão de Logout no topo da barra lateral
    if st.sidebar.button("🔒 Sair do Sistema (Logout)"):
        st.session_state.autenticado = False
        st.rerun()

    # Interface Principal
    st.title("🦅 Brothers Network Finance Community")
    st.subheader("Sistema Master de Gestão, Calendário e Secretária Eletrônica")

    aba1, aba2, aba3 = st.tabs(["🌐 1. Landing Page (Captura)", "📅 2. Calendário Mensal Expandido", "📊 3. Central da Secretária (Tarefas)"])

    membros_db = carregar_dados()

    # --- ABA 1: LANDING PAGE DE CAPTURA ---
    with aba1:
        st.header("Cadastro de Membros & Solicitação de Atendimento")
        st.markdown("---")
        col_lp1, col_lp2 = st.columns([1, 1])
        
        with col_lp1:
            st.markdown("### Deixe seus dados com a nossa Secretária Eletrônica")
            with st.form("form_lp", clear_on_submit=True):
                nome = st.text_input("Nome Completo:")
                whatsapp = st.text_input("WhatsApp (com DDD):", placeholder="Ex: 11948086926")
                data_nascimento = st.date_input("Data de Nascimento:", min_value=datetime.date(1940, 1, 1))
                mensagem = st.text_area("Como a Brothers Network pode te ajudar hoje?")
                
                botao_enviar = st.form_submit_button("Enviar para a Comunidade")
                
                if botao_enviar:
                    if nome and whatsapp:
                        salvar_membro(nome, whatsapp, data_nascimento, msg=mensagem)
                        st.success(f"Olá {nome}, seus dados foram recebidos com sucesso no banco de dados!")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha Nome e WhatsApp obrigatoriamente.")

        with col_lp2:
            st.markdown("### 📈 Benefícios da Comunidade")
            st.info("**Restauração de Crédito:** Atuação ágil via liminar judicial para limpar seu histórico.")
            st.info("**Networking de Elite:** Conexão direta com investidores e empresários do mercado financeiro.")

    # --- ABA 2: CALENDÁRIO MENSAL EXPANDIDO ---
    with aba2:
        st.header("Calendário Mensal de Relacionamento")
        hoje = datetime.date.today()
        mes_selecionado = st.selectbox("Selecione o Mês de Análise:", list(range(1, 13)), index=hoje.month - 1, format_func=lambda x: calendar.month_name[x].upper())
        
        cal = calendar.monthcalendar(hoje.year, mes_selecionado)
        nomes_dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        
        cols_dias = st.columns(7)
        for i, nome_dia in enumerate(nomes_dias):
            cols_dias[i].markdown(f"<p style='text-align:center; font-weight:bold; color:#1F497D;'>{nome_dia}</p>", unsafe_allow_html=True)
            
        for semana in cal:
            cols_semana = st.columns(7)
            for i, dia in enumerate(semana):
                if dia == 0:
                    cols_semana[i].write("")
                else:
                    df_dia = membros_db[(membros_db["Dia_Aniv"] == dia) & (membros_db["Mes_Aniv"] == mes_selecionado)] if not membros_db.empty else pd.DataFrame()
                    box_html = f"""
                    <div style="border:1px solid #D9D9D9; padding:8px; border-radius:5px; min-height:140px; background-color:#FFFFFF;">
                        <strong style="color:#4F81BD; font-size:14px;">{dia}</strong>
                    """
                    if not df_dia.empty:
                        for idx, row in df_dia.iterrows():
                            box_html += f"""
                            <div style="background-color:#F2F5F8; margin-top:4px; padding:4px; border-radius:3px; font-size:11px;">
                                🎂 <b>{row['Nome'].split()[0]}</b><br>
                                🟢 <i>Whats: {row['T4_MsgWhats']}</i>
                            </div>
                            """
                    box_html += "</div>"
                    cols_semana[i].markdown(box_html, unsafe_allow_html=True)

    # --- ABA 3: CENTRAL DA SECRETÁRIA ---
    with aba3:
        st.header("Gerenciador de Tarefas e Disparos")
        if membros_db.empty:
            st.warning("Nenhum membro cadastrado na Landing Page ainda.")
        else:
            df_editado = st.data_editor(
                membros_db,
                column_config={
                    "id": None,  # Esconde a coluna ID do banco para ficar limpo
                    "Nome": st.column_config.TextColumn("Membro", disabled=True),
                    "WhatsApp": st.column_config.TextColumn("WhatsApp", disabled=True),
                    "Data_Nascimento": st.column_config.DateColumn("Nascimento", disabled=True),
                    "Mensagem": st.column_config.TextColumn("Mensagem Solicitada", disabled=True),
                    "T1_BoasVindas": st.column_config.SelectboxColumn("T1: Boas-Vindas", options=["Pendente", "Concluído"]),
                    "T2_AnaliseCredito": st.column_config.SelectboxColumn("T2: Análise Liminar", options=["Pendente", "Concluído"]),
                    "T3_GatilhoOferta": st.column_config.SelectboxColumn("T3: Oferta", options=["Pendente", "Concluído"]),
                    "T4_MsgWhats": st.column_config.SelectboxColumn("T4: Whats Aniv.", options=["Pendente", "Concluído"]),
                    "T5_PosVenda": st.column_config.SelectboxColumn("T5: Pós-Venda", options=["Pendente", "Concluído"]),
                },
                hide_index=True
            )
            if st.button("Salvar Alterações de Status"):
                atualizar_status(df_editado)
                st.success("Painel de Controle e Banco de Dados atualizados com sucesso!")
                st.rerun()
