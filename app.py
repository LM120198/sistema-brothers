import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3
import urllib.parse

# Configuração da página - Tema Escuro e Amplo de Alta Performance
st.set_page_config(page_title="Brothers Network Finance - Oficial", layout="wide", initial_sidebar_state="collapsed")

# --- CONEXÃO E ESTRUTURA DO BANCO DE DADOS (PRESERVADA) ---
def conectar_banco():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    # Tabela de clientes existente
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT, WhatsApp TEXT, Data_Nascimento TEXT, Mensagem TEXT,
            Dia_Aniv INTEGER, Mes_Aniv INTEGER,
            T1_BoasVindas TEXT, T2_AnaliseCredito TEXT, T3_GatilhoOferta TEXT,
            T4_MsgWhats TEXT, T5_PosVenda TEXT
        )
    """)
    # NOVA TABELA: Sistema de Blog Dinâmico integrado
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Titulo TEXT, Autor TEXT, Data TEXT, Categoria TEXT, Conteudo TEXT, Imagem_Url TEXT
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

def carregar_posts():
    conn = sqlite3.connect("brothers.db")
    df = pd.read_sql_query("SELECT * FROM blog ORDER BY id DESC", conn)
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
                T1_BoasVindas=?, T2_AnaliseCredito=?, T3_GatilhoOferta=?, T4_MsgWhats=?, T5_PosVenda=?
            WHERE id=?
        """, (row['T1_BoasVindas'], row['T2_AnaliseCredito'], row['T3_GatilhoOferta'], row['T4_MsgWhats'], row['T5_PosVenda'], row['id']))
    conn.commit()
    conn.close()

# --- ALIMENTAÇÃO INICIAL DO BLOG (CONTEÚDO REAL DE STARTUP SE ESTIVER VAZIO) ---
def inicializar_conteudo_blog():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    check = cursor.execute("SELECT COUNT(*) FROM blog").fetchone()[0]
    if check == 0:
        posts_iniciais = [
            (
                "A Legalidade Oculta: Como as Liminares Judiciais Forçam a Restauração de Crédito",
                "Equipe Jurídica Brothers", "Direito Bancário",
                "Muitos empresários desconhecem que a manutenção de apontamentos negativos prescritos ou com discussões judiciais em andamento viola o Código de Defesa do Consumidor. Através de uma ação de obrigação de fazer combinada com pedido de tutela de urgência (liminar), é perfeitamente possível exigir a suspensão imediata dos efeitos das restrições nos órgãos de proteção ao crédito antes mesmo do julgamento do mérito. Isso devolve instantaneamente o score e o poder de barganha comercial da empresa, permitindo a captação de recursos quando a operação mais precisa.",
                "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&auto=format&fit=crop&q=60"
            ),
            (
                "Blindagem de Score e Alavancagem Financeira para Empresas em Crescimento",
                "Lucas - Gestão de Performance", "Finanças Corporativas",
                "Score alto não é vaidade, é custo de capital. Empresas com pontuações fragilizadas pagam até 40% a mais de taxa de juros em linhas de capital de giro. O processo de blindagem envolve a auditoria do Cadastro Positivo, a quitação estratégica de passivos voláteis e a contestação de consultas excessivas feitas por instituições financeiras sem autorização expressa. Ao limpar o histórico e calibrar o comportamento de crédito, o caixa da empresa respira e as portas do mercado de capitais se abrem com taxas de juros competitivas.",
                "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&auto=format&fit=crop&q=60"
            ),
            (
                "O Poder do Hub: Por Que o Networking de Elite Vale Mais que o Seu Capital",
                "Conselho Brothers Network", "Networking",
                "Dinheiro compra ferramentas, mas conexões compram mercados. Dentro da Brothers Network Finance Community, o nosso foco é criar pontes seguras entre detentores de capital e operadores de alta performance. Um insight compartilhado em nossa mesa de negócios sobre reestruturação patrimonial ou captação via fundos imobiliários já poupou milhões de reais aos membros neste trimestre. Fazer parte de um ecossistema blindado é o ativo definitivo para quem quer mitigar riscos jurídicos e exponenciar lucros.",
                "https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=800&auto=format&fit=crop&q=60"
            )
        ]
        cursor.executemany("INSERT INTO blog (Titulo, Autor, Categoria, Conteudo, Imagem_Url, Data) VALUES (?, ?, ?, ?, ?, '06/06/2026')", posts_iniciais)
        conn.commit()
    conn.close()

inicializar_conteudo_blog()

# --- CONTROLE DE ACESSO (SIDEBAR DISCRETA) ---
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
    st.sidebar.success("Modo Administrador Ativo")
    if st.sidebar.button("🔒 Sair do Painel (Logout)"):
        st.session_state.autenticado = False
        st.rerun()

# --- CARREGAMENTO DOS BANCOS ---
membros_db = carregar_dados()
blog_db = carregar_posts()

# =========================================================================
# 🌐 VISÃO PÚBLICA: PORTAL INSTITUCIONAL & BLOG DE ELITE
# =========================================================================
if not st.session_state.autenticado:
    
    # HERO SECTION (Topo de Alto Padrão)
    st.markdown("<h1 style='text-align: center; color: #FFD700; font-size: 3.5rem; font-weight: 800;'>BROTHERS NETWORK FINANCE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFFFFF; font-size: 1.4rem; font-weight: 300;'>Inteligência Jurídica, Restauração de Crédito e Networking de Alta Performance</p>", unsafe_allow_html=True)
    
    # Imagem Principal do Portal
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&auto=format&fit=crop&q=80", use_container_width=True)
    st.write("\n")
    
    # BLOCO DE CONVERSÃO & CAPTURA
    st.markdown("---")
    col_info, col_form = st.columns([1, 1.1])
    
    with col_info:
        st.markdown("## ⚖️ Soluções Estratégicas Hegemônicas")
        st.write("\n")
        st.markdown("### 🏛️ Restauração via Liminar Judicial")
        st.write("Nossa equipe atua diretamente na raiz do problema, acionando mecanismos jurídicos para a suspensão de apontamentos e restrições nos órgãos de proteção ao crédito antes do julgamento do mérito, limpando seu histórico e devolvendo seu poder de compra imediatamente.")
        
        st.markdown("### 🌐 Comunidade e Hub de Negócios")
        st.write("Muito mais que um serviço: uma comunidade restrita de empresários, investidores e especialistas do mercado financeiro focados em blindagem, alavancagem e parcerias comerciais de alto nível.")
        st.write("\n")
        st.warning("⚠️ **Nota de Escassez:** O acesso à comunidade e a triagem de processos são limitados semanalmente para garantir a celeridade jurídica de cada membro.")
        
    with col_form:
        st.markdown("### 🦅 Inicie sua Análise de Perfil")
        with st.form("form_portal", clear_on_submit=True):
            nome = st.text_input("Nome Completo ou Razão Social:")
            whatsapp = st.text_input("WhatsApp com DDD (Apenas números):", placeholder="Ex: 11948086926")
            data_nascimento = st.date_input("Data de Nascimento / Fundação da Empresa:", min_value=datetime.date(1940, 1, 1))
            servico = st.selectbox("Qual o gargalo atual do seu negócio?", [
                "Necessidade urgente de Limpeza de Nome / Restauração de Crédito",
                "Captação de Linhas de Crédito e Financiamentos Estruturados",
                "Proteção Patrimonial e Alocação de Investimentos",
                "Desejo de entrar para o Hub de Networking da Comunidade"
            ])
            detalhes = st.text_area("Descreva o cenário atual (valores aproximados, restrições, etc.):")
            
            if st.form_submit_button("SOLICITAR PROTOCOLO DE ATENDIMENTO PRIORITÁRIO"):
                if nome and whatsapp:
                    msg_completa = f"[{servico}] {detalhes}"
                    salvar_membro(nome, whatsapp, data_nascimento, msg_completa)
                    st.success(f"🔥 Protocolo gerado com sucesso para {nome}! Nossa Secretária Eletrônica já direcionou seu perfil para a banca de análise.")
                else:
                    st.error("Nome e WhatsApp são obrigatórios para a triagem.")

    # SEÇÃO: NOSSA HISTÓRIA E EQUIPE (HUMANIZAÇÃO)
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Nossa História & Propósito</h2>", unsafe_allow_html=True)
    
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        st.image("https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&auto=format&fit=crop&q=60", use_container_width=True)
    with col_hist2:
        st.markdown("### Quem Somos")
        st.write("A **Brothers Network Finance** nasceu da união de profissionais do mercado de capitais e especialistas em direito bancário que perceberam uma grande falha no ecossistema de crédito brasileiro: a burocracia punitiva que asfixia empresas legítimas.")
        st.markdown("### Nossa Missão")
        st.write("Não oferecemos apenas assessoria; nós restabelecemos a dignidade financeira e operacional dos nossos membros. Criamos uma verdadeira coalizão onde soluções jurídicas agressivas de limpeza de nome encontram oportunidades reais de investimentos e parcerias empresariais.")

    # SEÇÃO: DEPOIMENTOS DE CLIENTES REAIS (PROVA SOCIAL)
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Casos de Sucesso da Comunidade</h2>", unsafe_allow_html=True)
    st.write("\n")
    
    col_dep1, col_dep2, col_dep3 = st.columns(3)
    with col_dep1:
        st.markdown("> **\"Conseguimos derrubar uma restrição indevida de R$ 450k em menos de 7 dias via liminar. Nosso score subiu e o giro da empresa voltou a rodar.\"**")
        st.caption("— **Ricardo M.**, Indústria Metalúrgica")
    with col_dep2:
        st.markdown("> **\"A Brothers não só limpou o histórico da minha holding como me conectou com o parceiro comercial que financiou nossa expansão.\"**")
        st.caption("— **Dra. Amanda V.**, Rede de Clínicas Médicas")
    with col_dep3:
        st.markdown("> **\"O diferencial é a seriedade e a discrição. O atendimento via central eletrônica nos mantém atualizados sem burocracia.\"**")
        st.caption("— **Carlos H.**, Construtora Incorporadora")

    # =========================================================================
    # O BLOG DE VERDADE COM IMAGENS E ARTIGOS REAIS
    # =========================================================================
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>📰 Inside the Network - Conteúdo e Inteligência Diária</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #BBBBBB;'>Mantenha-se atualizado com as análises da nossa equipe técnica</p>", unsafe_allow_html=True)
    st.write("\n")

    if blog_db.empty:
        st.info("Nenhuma postagem no blog encontrada.")
    else:
        for idx, post in blog_db.iterrows():
            col_img, col_artigo = st.columns([1, 2])
            with col_img:
                if post['Imagem_Url']:
                    st.image(post['Imagem_Url'], use_container_width=True)
                else:
                    st.image("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&auto=format&fit=crop&q=60", use_container_width=True)
            with col_artigo:
                st.markdown(f"🏷️ `{post['Categoria']}` | 📅 *Publicado em {post['Data']} por {post['Autor']}*")
                st.markdown(f"### {post['Titulo']}")
                st.write(post['Conteudo'])
            st.markdown("<br>", unsafe_allow_html=True)

# =========================================================================
# 📊 VISÃO PRIVADA: GERENCIADOR, CALENDÁRIO & GERADOR DE POSTS DO BLOG
# =========================================================================
else:
    st.title("🦅 Central Administrativa Master - Brothers Network")
    st.markdown("---")

    aba_gestao, aba_calendario, aba_novo_blog = st.tabs([
        "📊 Gerenciador de Tarefas e Disparos", 
        "📅 Calendário de Relacionamento",
        "✍️ Publicar Novo Conteúdo no Blog"
    ])

    # --- ABA 1: GERENCIADOR (PRESERVADO INTEGRAMENTE) ---
    with aba_gestao:
        st.subheader("Esteira de Atendimento Dinâmica")
        if membros_db.empty:
            st.info("Nenhum cliente cadastrado no banco de dados até o momento.")
        else:
            links_dinamicos = []
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
                st.success("Esteira de atendimento gravada com sucesso!")
                st.rerun()

    # --- ABA 2: CALENDÁRIO (PRESERVADO INTEGRAMENTE) ---
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

    # --- ABA 3: GERADOR DE CONTEÚDO DINÂMICO PARA O BLOG ---
    with aba_novo_blog:
        st.subheader("Painel de Imprensa e Conteúdo Diário")
        st.markdown("Publique análises de mercado, notícias jurídicas ou atualizações da equipe diretamente na home do portal.")
        
        with st.form("form_novo_post", clear_on_submit=True):
            b_titulo = st.text_input("Título do Artigo:")
            b_autor = st.text_input("Autor do Texto (Ex: Seu Nome, Conselho Jurídico):", value="Diretoria Brothers")
            b_cat = st.selectbox("Categoria:", ["Direito Bancário", "Inteligência Financeira", "Networking", "Bastidores da Equipe", "Avisos Gerais"])
            b_img = st.text_input("URL de uma imagem de destaque (Opcional):", placeholder="https://images.unsplash.com/...", help="Pode pegar links de fotos profissionais de sites gratuitos como o Unsplash.")
            b_conteudo = st.text_area("Conteúdo Completo do Artigo (Escreva o texto real que será postado):", height=250)
            
            if st.form_submit_button("💥 PUBLICAR IMEDIATAMENTE NO PORTAL"):
                if b_titulo and b_conteudo:
                    salvar_post(b_titulo, b_autor, b_cat, b_conteudo, b_img)
                    st.success("🔥 Artigo publicado com sucesso! Faça logout para ver o resultado ao vivo na página do cliente.")
                else:
                    st.error("O artigo precisa obrigatoriamente de um Título e de um Conteúdo escrito.")
