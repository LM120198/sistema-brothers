import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3
import urllib.parse

# Configuração da página
st.set_page_config(page_title="Brothers Network Finance", layout="wide")

# --- CONEXÃO COM O BANCO DE DADOS LOCAL COMPARTILHADO ---
def conectar_banco():
    conn = sqlite3.connect("brothers.db")
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
    conn.commit()
    return conn

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
            T1_BoasVindas, T2_AnaliseCredito, T3_GatilhoOferta, T4_MsgWhats, T5_PosVenda
        ) VALUES (?, ?, ?, ?, ?, ?, 'Pendente', 'Pendente', 'Pendente', 'Pendente', 'Pendente')
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

# --- CONTROLE DE SESSÃO DO LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# FORMULÁRIO DE LOGIN NA BARRA LATERAL (DISCRETO)
st.sidebar.title("Área Restrita")
if not st.session_state.autenticado:
    with st.sidebar.form("login_form"):
        usuario = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")
        botao_entrar = st.form_submit_button("Acessar Painel")
        if botao_entrar:
            if usuario == "admin" and senha == "brothers2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.sidebar.error("Usuário ou senha incorretos.")
else:
    st.sidebar.success("Você está logado como Admin")
    if st.sidebar.button("🔒 Sair (Logout)"):
        st.session_state.autenticado = False
        st.rerun()

# --- LOGIC DE EXIBIÇÃO DA TELA (CLIENTE VS SÓCIOS) ---

membros_db = carregar_dados()

if not st.session_state.autenticado:
    # -------------------------------------------------------------------------
    # TELA PÚBLICA: LANDING PAGE DE ELITE (O cliente só vê isso)
    # -------------------------------------------------------------------------
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🦅 BROTHERS NETWORK FINANCE</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #FFFFFF; font-weight: 300;'>A Elite do Mercado Financeiro e Soluções Estratégicas</h3>", unsafe_allow_html=True)
    st.write("\n")

    st.info("### ⚖️ Restauração de Crédito & Blindagem Patrimonial\nAtuamos de forma ágil através de **liminar judicial** para limpar o seu histórico e devolver o seu poder de compra no mercado.")
    st.markdown("---")

    col_info, col_form = st.columns([1, 1.2])

    with col_info:
        st.markdown("### Por que fazer parte?")
        st.markdown("🌐 **Networking de Elite**\nConexão direta com investidores e empresários.")
        st.markdown("⚡ **Atendimento Prioritário**\nNossa secretária monitora sua solicitação em tempo real.")
        st.markdown("🔒 **Privacidade Absoluta**\nSeus dados sob estrito sigilo bancário e jurídico.")
        st.write("\n")
        st.warning("⚠️ **Vagas Limitadas:** Comunidade restrita para garantir a velocidade das liminares.")

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
                    mensagem_completa = f"{servico} | Obs: {detalhes}"
                    salvar_membro(nome, whatsapp, data_nascimento, mensagem_completa)
                    st.success(f"🔥 Excelente, {nome}! Seus dados foram validados e o fluxo de atendimento foi iniciado.")
                else:
                    st.error("Por favor, preencha o Nome e o WhatsApp.")

else:
    # -------------------------------------------------------------------------
    # TELA PRIVADA: PAINEL ADMINISTRATIVO (Só você e seu sócio logados vêem)
    # -------------------------------------------------------------------------
    st.title("🦅 Central Administrativa - Brothers Network")
    st.markdown("---")

    aba_gestao, aba_calendario = st.tabs(["📊 Gerenciador de Tarefas e Disparos", "📅 Calendário de Relacionamento"])

    # --- ABA 1: GERENCIADOR COM MENSAGENS INTELIGENTES ---
    with aba_gestao:
        st.subheader("Esteira de Atendimento Dinâmica")
        if membros_db.empty:
            st.info("Nenhum cliente cadastrado no banco de dados até o momento.")
        else:
            links_dinamicos = []
            
            # Algoritmo que lê os status e cria a mensagem certa para a fase certa
            for idx, row in membros_db.iterrows():
                if row['T1_BoasVindas'] == 'Pendente':
                    txt = f"Olá {row['Nome']}, seja bem-vindo à Brothers Network Finance! Recebemos sua solicitação sobre '{row['Mensagem']}'. Vamos iniciar seu atendimento?"
                elif row['T2_AnaliseCredito'] == 'Pendente':
                    txt = f"Olá {row['Nome']}! Seu processo avançou para a fase de Análise de Crédito e Liminar Judicial. Poderia me enviar seus documentos para darmos entrada?"
                elif row['T3_GatilhoOferta'] == 'Pendente':
                    txt = f"Excelente notícia, {row['Nome']}! Sua liminar/análise avançou. Conforme combinamos, liberamos uma oferta de upgrade de crédito exclusiva para o seu perfil. Vamos alinhar?"
                else:
                    txt = f"Olá {row['Nome']}, passando para acompanhar o andamento do seu caso com a Brothers Network. Como estão as coisas?"
                
                links_dinamicos.append(f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(txt)}")
            
            membros_db["Próxima Ação"] = links_dinamicos

            df_editado = st.data_editor(
                membros_db,
                column_config={
                    "id": None, "Dia_Aniv": None, "Mes_Aniv": None,
                    "Nome": st.column_config.TextColumn("Cliente", disabled=True, width="medium"),
                    "WhatsApp": st.column_config.TextColumn("WhatsApp", disabled=True),
                    "Data_Nascimento": st.column_config.DateColumn("Nascimento", disabled=True),
                    "Mensagem": st.column_config.TextColumn("Solicitação", disabled=True, width="medium"),
                    "T1_BoasVindas": st.column_config.SelectboxColumn("T1: Boas-Vindas", options=["Pendente", "Concluído"]),
                    "T2_AnaliseCredito": st.column_config.SelectboxColumn("T2: Liminar/Crédito", options=["Pendente", "Concluído"]),
                    "T3_GatilhoOferta": st.column_config.SelectboxColumn("T3: Oferta Upgrade", options=["Pendente", "Concluído"]),
                    "T4_MsgWhats": st.column_config.SelectboxColumn("T4: Aniversário", options=["Pendente", "Concluído"]),
                    "T5_PosVenda": st.column_config.SelectboxColumn("T5: Pós-Venda", options=["Pendente", "Concluído"]),
                    "Próxima Ação": st.column_config.LinkColumn("💬 WhatsApp Dinâmico", display_text="Enviar Mensagem da Fase")
                },
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("💾 Salvar Alterações de Status", type="primary"):
                atualizar_status(df_editado)
                st.success("Esteira atualizada com sucesso!")
                st.rerun()

    # --- ABA 2: CALENDÁRIO SEM ERROS VISUAIS ---
    with aba_calendario:
        st.subheader("Aniversariantes do Mês")
        hoje = datetime.date.today()
        meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_selecionado = st.selectbox("Selecione o Mês:", list(range(1, 13)), index=hoje.month - 1, format_func=lambda x: meses_nomes[x-1])
        
        if membros_db.empty:
            st.info("Nenhum cliente no banco de dados.")
        else:
            df_aniv_mes = membros_db[membros_db["Mes_Aniv"] == mes_selecionado]
            if df_aniv_mes.empty:
                st.write("Não há aniversariantes este mês.")
            else:
                for idx, row in df_aniv_mes.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 2])
                        with col1:
                            st.metric(label="Dia", value=f"Dia {row['Dia_Aniv']}")
                        with col2:
                            st.markdown(f"**Cliente:** {row['Nome']}")
                            st.markdown(f"**Contato de Niver:** `{row['T4_MsgWhats']}`")
                        with col3:
                            msg_p = f"Parabéns, {row['Nome']}! Como presente da Brothers Network, preparamos uma condição exclusiva de crédito para você hoje."
                            link_p = f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(msg_p)}"
                            st.link_button("🎉 Mandar Parabéns Comercial", link_p)
                        st.markdown("---")
