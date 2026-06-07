import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3
import urllib.parse

# Configuração da página - Tema Escuro e Amplo de Alta Performance
st.set_page_config(page_title="Brothers Network Finance - Oficial", layout="wide", initial_sidebar_state="collapsed")

# --- BANCO DE DADOS PRESERVADO E EXPANDIDO COM SUPORTE A ATENDENTES ---
def conectar_banco():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    # Adicionada a coluna Responsavel de forma segura caso não exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT, WhatsApp TEXT, Data_Nascimento TEXT, Mensagem TEXT,
            Dia_Aniv INTEGER, Mes_Aniv INTEGER,
            T1_BoasVindas TEXT, T2_AnaliseCredito TEXT, T3_GatilhoOferta TEXT,
            T4_MsgWhats TEXT, T5_PosVenda TEXT,
            Responsavel TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Titulo TEXT, Autor TEXT, Data TEXT, Categoria TEXT, Conteudo TEXT, Imagem_Url TEXT
        )
    """)
    # Tabela interna para controlar de quem é a vez no rodízio
    cursor.execute("CREATE TABLE IF NOT EXISTS controle_rodizio (id INTEGER PRIMARY KEY, ultimo_indice INTEGER)")
    cursor.execute("INSERT OR IGNORE INTO controle_rodizio (id, ultimo_indice) VALUES (1, 0)")
    conn.commit()
    return conn

conectar_banco()

# --- CONFIGURAÇÃO DA EQUIPE DE ATENDIMENTO ---
# Mude os números fictícios abaixo para os telefones reais de vocês (com DDD e sem espaços)
EQUIPE = [
    {"nome": "Lucas", "telefone": "5511999999999"},
    {"nome": "Sócio", "telefone": "5511888888888"}
]

def proximo_atendente():
    """Algoritmo Round-Robin que define de quem é a vez de receber o cliente"""
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
    responsavel_definido = proximo_atendente() # Sorteia o dono do lead na hora da entrada
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
# 🌐 VISÃO PÚBLICA: PORTAL INSTITUCIONAL, TERMÔMETRO E BLOG
# =========================================================================
if not st.session_state.autenticado:
    
    st.markdown("<h1 style='text-align: center; color: #FFD700; font-size: 3.5rem; font-weight: 800;'>BROTHERS NETWORK FINANCE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFFFFF; font-size: 1.4rem; font-weight: 300;'>Inteligência Jurídica, Restauração de Crédito e Networking de Alta Performance</p>", unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&auto=format&fit=crop&q=80", use_container_width=True)
    st.write("\n")
    
    st.markdown("---")
    col_info, col_form = st.columns([1, 1.1])
    
    with col_info:
        st.markdown("## ⚖️ Soluções Estratégicas Hegemônicas")
        st.write("\n")
        st.markdown("### 📊 Termômetro Analítico de Score")
        st.write("Arraste a barra abaixo com base no seu cenário atual para ver o diagnóstico prévio do nosso algoritmo:")
        
        score_usuario = st.slider("Selecione seu Score de Crédito aproximado:", min_value=0, max_value=1000, value=350, step=10)
        
        if score_usuario < 400:
            st.error(f"🚨 **Diagnóstico Crítico (Score: {score_usuario}):** Sua pontuação atual está bloqueando seu crescimento econômico. Nossa banca jurídica pode intervir imediatamente através de uma ação com pedido de **liminar judicial**.")
            perfil_score = "Critico"
        elif score_usuario < 700:
            st.warning(f"⚠️ **Diagnóstico Moderado (Score: {score_usuario}):** Seu perfil possui chances médias de aprovação. Recomendamos nosso processo de **Blindagem de Histórico** corporativo.")
            perfil_score = "Moderado"
        else:
            st.success(f"💎 **Diagnóstico de Elite (Score: {score_usuario}):** Sua saúde financeira é excelente. Seu perfil está qualificado para o nosso **Hub de Networking**.")
            perfil_score = "Premium"
            
        st.markdown("---")
        st.markdown("### 🏛️ Restauração via Liminar Judicial")
        st.write("Nossa equipe atua acionando mecanismos jurídicos para a suspensão de apontamentos e restrições.")
        st.warning("⚠️ **Nota de Escassez:** O acesso à comunidade e a triagem de processos são limitados semanalmente.")
        
    with col_form:
        st.markdown("### 🦅 Inicie sua Análise de Perfil")
        with st.form("form_portal", clear_on_submit=True):
            nome = st.text_input("Nome Completo ou Razão Social:")
            whatsapp = st.text_input("WhatsApp com DDD (Apenas números):", placeholder="Ex: 11948086926")
            data_nascimento = st.date_input("Data de Nascimento / Fundação da Empresa:", min_value=datetime.date(1940, 1, 1))
            servico = st.selectbox("Qual o gargalo atual do seu negócio?", [
                "Limpeza de Nome / Restauração de Crédito",
                "Captação de Linhas de Crédito / Financiamentos",
                "Proteção Patrimonial e Alocação de Investimentos",
                "Hub de Networking e Parcerias da Comunidade"
            ])
            detalhes = st.text_area("Descreva o cenário atual:")
            
            if st.form_submit_button("SOLICITAR PROTOCOLO DE ATENDIMENTO PRIORITÁRIO"):
                if nome and whatsapp:
                    msg_completa = f"Perfil: {perfil_score} (Score: {score_usuario}) | Alvo: {servico} | Obs: {detalhes}"
                    salvar_membro(nome, whatsapp, data_nascimento, msg_completa)
                    st.success(f"🔥 Protocolo gerado com sucesso para {nome}!")
                    st.rerun()
                else:
                    st.error("Nome e WhatsApp são obrigatórios.")

    # SEÇÕES INSTITUCIONAIS
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Nossa História & Propósito</h2>", unsafe_allow_html=True)
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        st.image("https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&auto=format&fit=crop&q=60", use_container_width=True)
    with col_hist2:
        st.markdown("### Quem Somos")
        st.write("A **Brothers Network Finance** nasceu da união de profissionais do mercado de capitais e especialistas em direito bancário.")

    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Casos de Sucesso da Comunidade</h2>", unsafe_allow_html=True)
    col_dep1, col_dep2, col_dep3 = st.columns(3)
    with col_dep1:
        st.markdown("> **\"Conseguimos derrubar uma restrição indevida de R$ 450k em menos de 7 dias via liminar.\"**")
        st.caption("— **Ricardo M.**, Indústria Metalúrgica")

    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>📰 Inside the Network - Conteúdo e Inteligência Diária</h2>", unsafe_allow_html=True)
    if not blog_db.empty:
        for idx, post in blog_db.iterrows():
            col_img, col_artigo = st.columns([1, 2])
            with col_img:
                st.image(post['Imagem_Url'] if post['Imagem_Url'] else "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&auto=format&fit=crop&q=60", use_container_width=True)
            with col_artigo:
                st.markdown(f"🏷️ `{post['Categoria']}` | 📅 *Publicado em {post['Data']}*")
                st.markdown(f"### {post['Titulo']}")
                st.write(post['Conteudo'])
            st.markdown("<br>", unsafe_allow_html=True)

# =========================================================================
# 📊 VISÃO PRIVADA: PAINEL ADMINISTRATIVO MASTER EXPANDIDO
# =========================================================================
else:
    st.title("🦅 Central Administrativa Master - Brothers Network")
    st.markdown("---")

    aba_gestao, aba_calendario, aba_analytics, aba_novo_blog = st.tabs([
        "📊 Gerenciador de Tarefas e Disparos", 
        "📅 Calendário de Relacionamento",
        "📈 Dashboard de Performance",
        "✍️ Publicar Novo Conteúdo no Blog"
    ])

    # --- ABA 1: GERENCIADOR EXPANDIDO COM LINHAS DE WHATSAPP DIRECIONADAS ---
    with aba_gestao:
        st.subheader("Esteira de Atendimento Dinâmica com Divisão de Fila")
        if membros_db.empty:
            st.info("Nenhum cliente cadastrado no banco de dados até o momento.")
        else:
            links_dinamicos = []
            
            for idx, row in membros_db.iterrows():
                # Descobre qual o número do atendente responsável por esse lead específico
                atendente_dono = next((item for item in EQUIPE if item["nome"] == row['Responsavel']), EQUIPE[0])
                num_atendente = atendente_dono["telefone"]
                
                # Escolhe o script de acordo com a fase da esteira
                if row['T1_BoasVindas'] == 'Pendente':
                    txt = f"Olá {row['Nome']}, seja bem-vindo à Brothers Network Finance! Eu sou o gestor {row['Responsavel']}. Recebemos sua solicitação sobre '{row['Mensagem']}'. Vamos iniciar?"
                elif row['T2_AnaliseCredito'] == 'Pendente':
                    txt = f"Olá {row['Nome']}! Aqui é o {row['Responsavel']}. Seu processo avançou para a fase de Análise de Crédito e Liminar. Poderia me enviar seus documentos?"
                elif row['T3_GatilhoOferta'] == 'Pendente':
                    txt = f"Excelente notícia, {row['Nome']}! Aqui é o {row['Responsavel']}. Sua liminar avançou. Conforme combinamos, liberamos o seu upgrade de crédito corporativo!"
                else:
                    txt = f"Olá {row['Nome']}, gestor {row['Responsavel']} passando para acompanhar o andamento do seu caso."
                
                # GERA O LINK DE DISPARO QUE CHEGA PARA O CLIENTE NOTIFICANDO O ATENDENTE CORRETO
                # O link usa o WhatsApp do cliente para envio, contendo o nome do Dono do lead no texto
                links_dinamicos.append(f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(txt)}")
            
            membros_db["Próxima Ação"] = links_dinamicos

            df_editado = st.data_editor(
                membros_db,
                column_config={
                    "id": None, "Dia_Aniv": None, "Mes_Aniv": None,
                    "Nome": st.column_config.TextColumn("Cliente", disabled=True, width="medium"),
                    "WhatsApp": st.column_config.TextColumn("WhatsApp", disabled=True),
                    "Data_Nascimento": st.column_config.DateColumn("Nascimento", disabled=True),
                    "Mensagem": st.column_config.TextColumn("Solicitação / Diagnóstico do Score", disabled=True, width="medium"),
                    "Responsavel": st.column_config.SelectboxColumn("Responsável (Dono)", options=[e["nome"] for e in EQUIPE], width="small"),
                    "T1_BoasVindas": st.column_config.SelectboxColumn("T1: Boas-Vindas", options=["Pendente", "Concluído"]),
                    "T2_AnaliseCredito": st.column_config.SelectboxColumn("T2: Liminar/Crédito", options=["Pendente", "Concluído"]),
                    "T3_GatilhoOferta": st.column_config.SelectboxColumn("T3: Oferta Upgrade", options=["Pendente", "Concluído"]),
                    "T4_MsgWhats": st.column_config.SelectboxColumn("T4: Aniversário", options=["Pendente", "Concluído"]),
                    "T5_PosVenda": st.column_config.SelectboxColumn("T5: Pós-Venda", options=["Pendente", "Concluído"]),
                    "Próxima Ação": st.column_config.LinkColumn("💬 WhatsApp Dinâmico", display_text="Chamar")
                },
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("💾 Salvar Alterações de Status", type="primary"):
                atualizar_status(df_editado)
                st.success("Fila de distribuição e esteira gravadas com sucesso!")
                st.rerun()

    # --- ABA 2: CALENDÁRIO ---
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
                            st.markdown(f"**Cliente:** {row['Nome']} | **Dono do Lead:** `{row['Responsavel']}`")
                        with col3:
                            msg_p = f"Parabéns, {row['Nome']}! Gestor {row['Responsavel']} passando para liberar uma condição de crédito exclusiva para o seu aniversário."
                            link_p = f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(msg_p)}"
                            st.link_button("🎉 Mandar Parabéns do Responsável", link_p)
                        st.markdown("---")

    # --- ABA 3: DASHBOARD DE PERFORMANCE ---
    with aba_analytics:
        st.subheader("Métricas Gerais e Desempenho Operacional")
        if membros_db.empty:
            st.info("Aguardando entrada de dados para gerar os gráficos.")
        else:
            total_leads = len(membros_db)
            criticos = membros_db["Mensagem"].str.contains("Perfil: Critico", na=False).sum()
            t1_concluidos = (membros_db["T1_BoasVindas"] == "Concluído").sum()
            taxa_conversao = (t1_concluidos / total_leads) * 100 if total_leads > 0 else 0
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric(label="👥 Total de Leads Capturados", value=total_leads)
            with col_m2:
                st.metric(label="🚨 Perfis Críticos (Alvo Liminar)", value=criticos, delta="Atenção", delta_color="inverse")
            with col_m3:
                st.metric(label="⚡ Taxa de Primeiro Atendimento (T1)", value=f"{taxa_conversao:.1f}%")
            
            st.markdown("---")
            st.markdown("### 📈 Distribuição de Leads por Responsável (Equipe)")
            
            # Gráfico dinâmico que mostra quem está com mais trabalho na fila de rodízio
            contagem_rep = membros_db["Responsavel"].value_counts()
            st.bar_chart(contagem_rep, use_container_width=True)

    # --- ABA 4: BLOG MANAGER ---
    with aba_novo_blog:
        st.subheader("Painel de Imprensa e Conteúdo Diário")
        with st.form("form_novo_post", clear_on_submit=True):
            b_titulo = st.text_input("Título do Artigo:")
            b_autor = st.text_input("Autor do Texto:", value="Diretoria Brothers")
            b_cat = st.selectbox("Categoria:", ["Direito Bancário", "Inteligência Financeira", "Networking", "Bastidores da Equipe", "Avisos Gerais"])
            b_img = st.text_input("URL de uma imagem de destaque:")
            b_conteudo = st.text_area("Conteúdo Completo do Artigo:", height=250)
            
            if st.form_submit_button("💥 PUBLICAR IMEDIATAMENTE NO PORTAL"):
                if b_titulo and b_conteudo:
                    salvar_post(b_titulo, b_autor, b_cat, b_conteudo, b_img)
                    st.success("🔥 Artigo publicado com sucesso!")
                else:
                    st.error("O artigo precisa de um Título e de um Conteúdo.")
