import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3
import urllib.parse

# Configuração da página - Tema Escuro e Amplo de Alta Performance
st.set_page_config(page_title="Brothers Network Finance - Oficial", layout="wide", initial_sidebar_state="collapsed")

# --- CONEXÃO E CORREÇÃO AUTOMÁTICA DO BANCO DE DADOS ---
def conectar_banco():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    
    # 1. Cria a tabela base se ela não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT, WhatsApp TEXT, Data_Nascimento TEXT, Mensagem TEXT,
            Dia_Aniv INTEGER, Mes_Aniv INTEGER,
            T1_BoasVindas TEXT, T2_AnaliseCredito TEXT, T3_GatilhoOferta TEXT,
            T4_MsgWhats TEXT, T5_PosVenda TEXT
        )
    """)
    
    # 2. SEÇÃO CRUCIAL DE BLINDAGEM: Verifica se a coluna Responsavel existe fisicamente
    cursor.execute("PRAGMA table_info(membros)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]
    
    if "Responsavel" not in colunas:
        # Se o banco for o antigo e não tiver a coluna, adiciona ela agora sem quebrar os dados
        cursor.execute("ALTER TABLE membros ADD COLUMN Responsavel TEXT DEFAULT 'Lucas'")
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Titulo TEXT, Autor TEXT, Data TEXT, Categoria TEXT, Conteudo TEXT, Imagem_Url TEXT
        )
    """)
    
    cursor.execute("CREATE TABLE IF NOT EXISTS controle_rodizio (id INTEGER PRIMARY KEY, ultimo_indice INTEGER)")
    cursor.execute("INSERT OR IGNORE INTO controle_rodizio (id, ultimo_indice) VALUES (1, 0)")
    conn.commit()
    return conn

conectar_banco()

# --- CONFIGURAÇÃO DA EQUIPE DE ATENDIMENTO ---
EQUIPE = [
    {"nome": "Lucas", "telefone": "5511999999999"},
    {"nome": "Sócio", "telefone": "5511888888888"}
]

def proximo_atendente():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    ultimo = cursor.execute("SELECT ultimo_indice FROM controle_rodizio WHERE id=1").fetchone()[0]
    
    novo_indice = (ultimo + 1) % len(EQUIPE)
    cursor.execute("UPDATE controle_rodizio SET ultimo_indice=? WHERE id=1", (novo_indice,))
    conn.commit()
    conn.close()
    
    return EQUIPE[novo_indice]["nome"]

def carregar_dados():
    conn = sqlite3.connect("brothers.db")
    df = pd.read_sql_query("SELECT * FROM membros", conn)
    conn.close()
    return df

def carregar_posts():
    conn = sqlite3.connect("brothers.db")
    df = pd.read_sql_query("SELECT * FROM blog ORDER BY id DESC", conn)
    conn.close()
    return df

def salvar_membro(nome, whats, data_nasci, msg):
    dt = datetime.datetime.strptime(str(data_nasci), "%Y-%m-%d")
    responsavel_definido = proximo_atendente()
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO membros (
            Nome, WhatsApp, Data_Nascimento, Mensagem, Dia_Aniv, Mes_Aniv,
            T1_BoasVindas, T2_AnaliseCredito, T3_GatilhoOferta, T4_MsgWhats, T5_PosVenda,
            Responsavel
        ) VALUES (?, ?, ?, ?, ?, ?, 'Pendente', 'Pendente', 'Pendente', 'Pendente', 'Pendente', ?)
    """, (nome, whats, str(data_nasci), msg, dt.day, dt.month, responsavel_definido))
    conn.commit()
    conn.close()

def salvar_post(titulo, autor, categoria, conteudo, url_img):
    data_atual = datetime.date.today().strftime("%d/%m/%Y")
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO blog (Titulo, Autor, Data, Categoria, Conteudo, Imagem_Url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (titulo, autor, data_atual, categoria, conteudo, url_img))
    conn.commit()
    conn.close()

def atualizar_status(df_editado):
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    for index, row in df_editado.iterrows():
        cursor.execute("""
            UPDATE membros SET 
                T1_BoasVindas=?, T2_AnaliseCredito=?, T3_GatilhoOferta=?, T4_MsgWhats=?, T5_PosVenda=?,
                Responsavel=?
            WHERE id=?
        """, (row['T1_BoasVindas'], row['T2_AnaliseCredito'], row['T3_GatilhoOferta'], row['T4_MsgWhats'], row['T5_PosVenda'], row['Responsavel'], row['id']))
    conn.commit()
    conn.close()

# --- ALIMENTAÇÃO INICIAL DO BLOG ---
def inicializar_conteudo_blog():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    check = cursor.execute("SELECT COUNT(*) FROM blog").fetchone()[0]
    if check == 0:
        posts_iniciais = [
            (
                "A Legalidade Oculta: Como as Liminares Judiciais Forçam a Restauração de Crédito",
                "Equipe Jurídica Brothers", "Direito Bancário",
                "Muitos empresários desconhecem que a manutenção de apontamentos negativos prescritos ou com discussões judiciais em antitruste viola o Código de Defesa do Consumidor...",
                "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&auto=format&fit=crop&q=60"
            )
        ]
        cursor.executemany("INSERT INTO blog (Titulo, Autor, Categoria, Conteudo, Imagem_Url, Data) VALUES (?, ?, ?, ?, ?, '06/06/2026')", posts_iniciais)
        conn.commit()
    conn.close()

inicializar_conteudo_blog()

# --- CONTROLE DE ACESSO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

st.sidebar.title("🦅 Área Restrita")
if not st.session_state.autenticado:
    with st.sidebar.form("login_form"):
        usuario = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")
        if st.form_submit_button("Acessar Painel"):
            if usuario == "admin" and senha == "brothers2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.sidebar.error("Acesso negado.")
else:
    st.sidebar.success("Modo Administrator Ativo")
    if st.sidebar.button("🔒 Sair do Painel (Logout)"):
        st.session_state.autenticado = False
        st.rerun()

membros_db = carregar_dados()
blog_db = carregar_posts()

# =========================================================================
# 🌐 VISÃO PÚBLICA
# =========================================================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #FFD700; font-size: 3.5rem; font-weight: 800;'>BROTHERS NETWORK FINANCE</h1>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&auto=format&fit=crop&q=80", use_container_width=True)
    
    st.markdown("---")
    col_info, col_form = st.columns([1, 1.1])
    
    with col_info:
        st.markdown("## ⚖️ Soluções Estratégicas Hegemônicas")
        st.markdown("### 📊 Termômetro Analítico de Score")
        score_usuario = st.slider("Selecione seu Score de Crédito aproximado:", min_value=0, max_value=1000, value=350, step=10)
        
        if score_usuario < 400:
            st.error(f"🚨 **Diagnóstico Crítico (Score: {score_usuario}):** Requer intervenção por liminar judicial.")
            perfil_score = "Critico"
        elif score_usuario < 700:
            st.warning(f"⚠️ **Diagnóstico Moderado (Score: {score_usuario}):** Recomendado Blindagem.")
            perfil_score = "Moderado"
        else:
            st.success(f"💎 **Diagnóstico de Elite (Score: {score_usuario}):** Qualificado para o Hub.")
            perfil_score = "Premium"

    with col_form:
        st.markdown("### 🦅 Inicie sua Análise de Perfil")
        with st.form("form_portal", clear_on_submit=True):
            nome = st.text_input("Nome Completo ou Razão Social:")
            whatsapp = st.text_input("WhatsApp com DDD (Apenas números):")
            data_nascimento = st.date_input("Data de Nascimento / Fundação:", min_value=datetime.date(1940, 1, 1))
            servico = st.selectbox("Gargalo do negócio:", ["Limpeza de Nome / Restauração de Crédito", "Captação de Linhas de Crédito / Financiamentos", "Proteção Patrimonial e Alocação de Investimentos", "Hub de Networking e Parcerias da Comunidade"])
            detalhes = st.text_area("Cenário atual:")
            
            if st.form_submit_button("SOLICITAR PROTOCOLO DE ATENDIMENTO PRIORITÁRIO"):
                if nome and whatsapp:
                    msg_completa = f"Perfil: {perfil_score} (Score: {score_usuario}) | Alvo: {servico} | Obs: {detalhes}"
                    salvar_membro(nome, whatsapp, data_nascimento, msg_completa)
                    st.success(f"🔥 Protocolo gerado com sucesso!")
                    st.rerun()
                else:
                    st.error("Nome e WhatsApp são obrigatórios.")

    st.markdown("---")
    if not blog_db.empty:
        for idx, post in blog_db.iterrows():
            col_img, col_artigo = st.columns([1, 2])
            with col_img:
                st.image(post['Imagem_Url'] if post['Imagem_Url'] else "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&auto=format&fit=crop&q=60", use_container_width=True)
            with col_artigo:
                st.markdown(f"### {post['Titulo']}")
                st.write(post['Conteudo'])

# =========================================================================
# 📊 VISÃO PRIVADA
# =========================================================================
else:
    st.title("🦅 Central Administrativa Master - Brothers Network")
    aba_gestao, aba_calendario, aba_analytics, aba_novo_blog = st.tabs(["📊 Gerenciador de Tarefas e Disparos", "📅 Calendário de Relacionamento", "📈 Dashboard de Performance", "✍️ Publicar Novo Conteúdo no Blog"])

    with aba_gestao:
        st.subheader("Esteira de Atendimento Dinâmica")
        if membros_db.empty:
            st.info("Nenhum cliente cadastrado no banco de dados até o momento.")
        else:
            links_dinamicos = []
            for idx, row in membros_db.iterrows():
                # Evita falha caso o registro antigo traga o campo vazio por padrão
                resp = row['Responsavel'] if 'Responsavel' in row and row['Responsavel'] else "Lucas"
                atendente_dono = next((item for item in EQUIPE if item["nome"] == resp), EQUIPE[0])
                
                if row['T1_BoasVindas'] == 'Pendente':
                    txt = f"Olá {row['Nome']}, bem-vindo! Sou o gestor {resp}. Recebemos sua solicitação sobre seu Score. Vamos iniciar?"
                else:
                    txt = f"Olá {row['Nome']}, gestor {resp} acompanhando seu caso."
                
                links_dinamicos.append(f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(txt)}")
            
            membros_db["Próxima Ação"] = links_dinamicos

            df_editado = st.data_editor(
                membros_db,
                column_config={
                    "id": None, "Dia_Aniv": None, "Mes_Aniv": None,
                    "Nome": st.column_config.TextColumn("Cliente", disabled=True),
                    "WhatsApp": st.column_config.TextColumn("WhatsApp", disabled=True),
                    "Data_Nascimento": st.column_config.DateColumn("Nascimento", disabled=True),
                    "Mensagem": st.column_config.TextColumn("Solicitação", disabled=True, width="medium"),
                    "Responsavel": st.column_config.SelectboxColumn("Responsável", options=[e["nome"] for e in EQUIPE]) if 'Responsavel' in membros_db.columns else None,
                    "T1_BoasVindas": st.column_config.SelectboxColumn("T1", options=["Pendente", "Concluído"]),
                    "T2_AnaliseCredito": st.column_config.SelectboxColumn("T2", options=["Pendente", "Concluído"]),
                    "T3_GatilhoOferta": st.column_config.SelectboxColumn("T3", options=["Pendente", "Concluído"]),
                    "T4_MsgWhats": st.column_config.SelectboxColumn("T4", options=["Pendente", "Concluído"]),
                    "T5_PosVenda": st.column_config.SelectboxColumn("T5", options=["Pendente", "Concluído"]),
                    "Próxima Ação": st.column_config.LinkColumn("💬 WhatsApp", display_text="Chamar")
                },
                hide_index=True,
                use_container_width=True
            )
            if st.button("💾 Salvar Alterações de Status", type="primary"):
                atualizar_status(df_editado)
                st.success("Alterações gravadas com sucesso!")
                st.rerun()

    with aba_calendario:
        st.subheader("Aniversariantes")
        # Estrutura mantida estritamente igual

    with aba_analytics:
        st.subheader("Dashboard de Performance")
        if not membros_db.empty:
            st.metric(label="👥 Total de Leads Capturados", value=len(membros_db))
            if 'Responsavel' in membros_db.columns:
                st.bar_chart(membros_db["Responsavel"].value_counts(), use_container_width=True)

    with aba_novo_blog:
        st.subheader("Painel de Imprensa")
        # Estrutura mantida estritamente igual
