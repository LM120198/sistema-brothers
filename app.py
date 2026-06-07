import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3
import urllib.parse

# Configuração da página - Limpa e Estável de Alta Performance
st.set_page_config(page_title="Brothers Network Finance - Oficial", layout="wide", initial_sidebar_state="collapsed")

# --- CONEXÃO E ESTRUTURA DO BANCO DE DADOS (100% PRESERVADA E REVISADA) ---
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
    cursor.execute("PRAGMA table_info(membros)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]
    if "Responsavel" not in colunas:
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

# --- CONFIGURAÇÃO DA EQUIPE OPERACIONAL ---
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
            T1_BoasVindas, T2_AnaliseCredito, T3_GatilhoOferta, T4_MsgWhats, T5_PosVenda, Responsavel
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
                T1_BoasVindas=?, T2_AnaliseCredito=?, T3_GatilhoOferta=?, T4_MsgWhats=?, T5_PosVenda=?, Responsavel=?
            WHERE id=?
        """, (row['T1_BoasVindas'], row['T2_AnaliseCredito'], row['T3_GatilhoOferta'], row['T4_MsgWhats'], row['T5_PosVenda'], row['Responsavel'], row['id']))
    conn.commit()
    conn.close()

# --- ARQUIVO CENTRAL DE ESTILO, ANIMAÇÕES E INTERATIVIDADE GLOBAL ---
st.markdown("""
<style>
    /* Força o plano de fundo escuro no Streamlit inteiro */
    .stApp, body, [data-testid="stAppViewContainer"] { 
        background-color: #0e0e12 !important; 
    }

    /* --- CORTINA DE INTRODUÇÃO ABSOLUTA (FULL SCREEN 100VW) --- */
    @keyframes recolherCortina {
        0% { transform: translateY(0); }
        100% { transform: translateY(-100vh); display: none; visibility: hidden; }
    }
    @keyframes neonPulse {
        0%, 100% { filter: drop-shadow(0 0 10px #FFD700) drop-shadow(0 0 20px #FFD700); transform: scale(1); }
        50% { filter: drop-shadow(0 0 30px #FFD700) drop-shadow(0 0 50px #FFD700); transform: scale(1.05); }
    }
    @keyframes typingEffect {
        from { width: 0; }
        to { width: 100%; }
    }

    #cortina-intro {
        position: fixed !important;
        top: 0 !important; left: 0 !important;
        width: 100vw !important; height: 100vh !important;
        background-color: #050508 !important;
        z-index: 9999999 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        animation: recolherCortina 0.8s cubic-bezier(0.77, 0, 0.175, 1) forwards !important;
        animation-delay: 3.8s !important;
        pointer-events: none !important;
    }

    .aguia-gigante {
        font-size: 8rem !important;
        animation: neonPulse 2s ease-in-out infinite !important;
        margin-bottom: 20px !important;
        user-select: none !important;
    }

    .texto-datilografado {
        color: #FFD700 !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        letter-spacing: 5px !important;
        overflow: hidden !important;
        white-space: nowrap !important;
        border-right: 3px solid #FFD700 !important;
        width: 0;
        animation: typingEffect 2.2s steps(30, end) forwards !important;
        animation-delay: 0.5s !important;
        text-align: center !important;
    }

    /* --- ENGENHARIA REFEITA DO EAGLEBOT FLUTUANTE (ANTI-OCULTAÇÃO) --- */
    .eagle-widget-fixed {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 9999998 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        pointer-events: auto !important;
    }
    .widget-bubble-live {
        background: #161622 !important;
        border: 2px solid #FFD700 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        color: #fff !important;
        font-size: 13px !important;
        text-align: center !important;
        width: 220px !important;
        margin-bottom: 15px !important;
        box-shadow: 0px 8px 24px rgba(0,0,0,0.8) !important;
        transition: all 0.3s ease !important;
    }
    .eagle-avatar-live {
        font-size: 4rem !important;
        user-select: none !important;
        cursor: pointer !important;
        animation: smoothFloat 2.5s ease-in-out infinite !important;
    }
    @keyframes smoothFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
    }
    .eagle-widget-fixed:hover .widget-bubble-live {
        background: #FFD700 !important;
        color: #000 !important;
        transform: scale(1.03);
    }
    .eagle-widget-fixed:hover .eagle-avatar-live {
        transform: scale(1.15);
    }
</style>

<!-- Injeção da Cortina Teatral de Abertura -->
<div id="cortina-intro">
    <div class="aguia-gigante">🦅</div>
    <div class="texto-datilografado">BROTHERS NETWORK FINANCE</div>
</div>
""", unsafe_allow_html=True)

# --- ABA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    with st.sidebar.form("login_form"):
        st.markdown("<h3 style='text-align:center; color:#FFD700;'>Área Restrita</h3>", unsafe_allow_html=True)
        usuario = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")
        if st.form_submit_button("Acessar Central"):
            if usuario == "admin" and senha == "brothers2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.sidebar.error("Acesso negado.")
else:
    st.sidebar.success("Modo Diretor Ativo")
    if st.sidebar.button("🔒 Sair do Painel"):
        st.session_state.autenticado = False
        st.rerun()

membros_db = carregar_dados()
blog_db = carregar_posts()

# =========================================================================
# 🌐 VISÃO PÚBLICA (PORTAL PREMIUM TOTALMENTE INTERATIVO)
# =========================================================================
if not st.session_state.autenticado:
    
    # Renderização Forçada do Mascote EagleBot no Canto Direito
    st.markdown("""
    <div class="eagle-widget-fixed">
        <div class="widget-bubble-live">
            🦅 <b>EagleBot:</b> Estou ativo! Passe o mouse em mim para ver as novidades e dicas de score.
        </div>
        <div class="eagle-avatar-live">🦅</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='color: #FFD700; font-size: 3.5rem; font-weight: 800; text-align:center;'>BROTHERS NETWORK FINANCE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #FFFFFF; font-size: 1.3rem; font-weight: 300; text-align:center;'>Seu Nome Limpo, Score Alto e Acesso às Melhores Linhas de Crédito do País</p>", unsafe_allow_html=True)
    st.write("\n")
    
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&auto=format&fit=crop&q=80", use_container_width=True)
    st.write("\n")
    
    st.markdown("---")
    col_info, col_form = st.columns([1, 1.1])
    
    with col_info:
        st.markdown("## 🏢 Como Nós Ajudamos Você e Sua Empresa")
        st.write("Estar com as portas do banco fechadas impede você de evoluir profissionalmente. Nosso time remove os rastros e consultas antigas que detonam seu perfil de forma justa, rápida e sem complicação.")
        
        st.markdown("### 📊 Teste Seu Score Abaixo:")
        score_usuario = st.slider("Selecione seu Score aproximado:", min_value=0, max_value=1000, value=350, step=10)
        
        if score_usuario < 400:
            st.error(f"🚨 **Perfil Bloqueado (Score: {score_usuario}):** Os bancos travam sua vida. **Nossa Solução:** Entramos com ação judicial urgente (liminar) para limpar seu histórico rápido.")
            perfil_score = "Critico"
        elif score_usuario < 700:
            st.warning(f"⚠️ **Risco Moderado (Score: {score_usuario}):** Você paga juros muito altos. **Nossa Solução:** Fazemos uma varredura técnica para calibrar seu score.")
            perfil_score = "Moderado"
        else:
            st.success(f"💎 **Perfil Elite (Score: {score_usuario}):** Aprovado para entrar no nosso Hub VIP de empresários e linhas exclusivas.")
            perfil_score = "Premium"
            
        st.markdown("---")
        st.write("• **Limpamos Seu Passado:** Retiramos apontamentos negativos do seu histórico definitivamente.")
        st.write("• **Agilidade Máxima:** Atuação focada em ordens urgentes do juiz.")
        st.warning("⚠️ **Vagas Limitadas:** Atendimentos restritos semanalmente para manter a velocidade.")
        
    with col_form:
        st.markdown("### 🦅 Solicite Uma Análise Gratuita do Seu Caso")
        with st.form("form_portal", clear_on_submit=True):
            nome = st.text_input("Seu Nome Completo ou Razão Social:")
            whatsapp = st.text_input("WhatsApp com DDD (Somente números):", placeholder="Ex: 11948086926")
            data_nascimento = st.date_input("Data de Nascimento ou Fundação:", min_value=datetime.date(1940, 1, 1))
            servico = st.selectbox("Qual o maior problema hoje?", ["Quero Limpar meu Nome / Subir meu Score Urgente", "Preciso de Empréstimo com Juros Baixos", "Quero Investimentos Lucrativos", "Quero Networking na Comunidade"])
            detalhes = st.text_area("Conte resumidamente o que aconteceu:")
            
            if st.form_submit_button("QUERO QUE A CENTRAL ANALISE MEU PERFIL AGORA"):
                if nome and whatsapp:
                    msg_completa = f"Perfil: {perfil_score} (Score: {score_usuario}) | Alvo: {servico} | Obs: {detalhes}"
                    salvar_membro(nome, whatsapp, data_nascimento, msg_completa)
                    st.success(f"🔥 Perfeito, {nome}! Triagem iniciada com sucesso.")
                    st.rerun()
                else:
                    st.error("Nome e WhatsApp são obrigatórios.")

    # HISTÓRIA E EQUIPE
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Nossa História & Quem Somos Nós</h2>", unsafe_allow_html=True)
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        st.image("https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&auto=format&fit=crop&q=60", use_container_width=True)
    with col_hist2:
        st.write("A **Brothers Network Finance** é formada por especialistas focados em direito bancário e mercado financeiro. Nosso propósito diário é quebrar as amarras burocráticas injustas dos bancos para que você recupere sua tranquilidade comercial de forma definitiva.")

    # DEPOIMENTOS
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Pessoas Reais, Resultados Reais</h2>", unsafe_allow_html=True)
    col_dep1, col_dep2, col_dep3 = st.columns(3)
    with col_dep1:
        st.markdown("<div style='background:#161622; padding:20px; border-radius:8px;'><blockquote><b>\"Tentei financiar um caminhão e recusaram. Em 10 dias a Brothers resolveu meu score.\"</b></blockquote><br><small>— Ricardo M., Empresário</small></div>", unsafe_allow_html=True)
    with col_dep2:
        st.markdown("<div style='background:#161622; padding:20px; border-radius:8px;'><blockquote><b>\"Eles limparam meu histórico de consultas antigas e hoje tenho crédito aprovado.\"</b></blockquote><br><small>— Dra. Amanda V., Médica</small></div>", unsafe_allow_html=True)
    with col_dep3:
        st.markdown("<div style='background:#161622; padding:20px; border-radius:8px;'><blockquote><b>\"Atendimento sério, transparente e muito rápido. Devolve a paz de espírito.\"</b></blockquote><br><small>— Carlos H., Autônomo</small></div>", unsafe_allow_html=True)

    # FAQ
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>❓ Dúvidas Comuns (FAQ)</h2>", unsafe_allow_html=True)
    with st.expander("Eu vou ter que pagar alguma coisa antes do meu processo iniciar?"):
        st.write("Nossa análise inicial é 100% gratuita via WhatsApp. Só fechamos após mostrar o que está travando o seu perfil.")

    # SEÇÃO DO BLOG
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>📰 Dicas da Nossa Equipe - Aprenda a Cuidar do Seu Crédito</h2>", unsafe_allow_html=True)
    if not blog_db.empty:
        for idx, post in blog_db.iterrows():
            col_img, col_artigo = st.columns([1, 2.5])
            with col_img:
                st.image(post['Imagem_Url'] if post['Imagem_Url'] else "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&auto=format&fit=crop&q=60", use_container_width=True)
            with col_artigo:
                st.markdown(f"🏷️ `{post['Categoria']}` | 📅 *Publicado em {post['Data']}*")
                st.markdown(f"### {post['Titulo']}")
                resumo_limpo = post['Conteudo'].replace("<p>", "").replace("</p>", "").replace("<br>", " ")[:180] + "..."
                st.markdown(resumo_limpo, unsafe_allow_html=True)
                
                if st.button("📖 Ler Artigo Didático Completo", key=f"pub_btn_{post['id']}"):
                    @st.dialog(post['Titulo'], width="large")
                    def render_dialog():
                        st.markdown(f"✍️ *Por {post['Autor']} em {post['Data']}*")
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.markdown(post['Conteudo'], unsafe_allow_html=True)
                    render_dialog()
            st.markdown("<br><hr style='border-top: 1px solid #222;'><br>", unsafe_allow_html=True)

# =========================================================================
# 📊 VISÃO PRIVADA (CRM INTERNO INTACTO)
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
                resp = row['Responsavel'] if 'Responsavel' in row and row['Responsavel'] else "Lucas"
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
                    "Responsavel": st.column_config.SelectboxColumn("Responsável", options=[e["nome"] for e in EQUIPE]),
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
        st.subheader("📅 Calendário de Relacionamento de Aniversariantes")
        hoje = datetime.date.today()
        meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_selecionado = st.selectbox("Selecione o Mês para Filtro:", list(range(1, 13)), index=hoje.month - 1, format_func=lambda x: meses_nomes[x-1])
        
        if membros_db.empty:
            st.info("Nenhum cliente cadastrado no sistema.")
        else:
            df_aniv_mes = membros_db[membros_db["Mes_Aniv"] == mes_selecionado]
            if df_aniv_mes.empty:
                st.write("Não há aniversariantes detectados para este mês.")
            else:
                for idx, row in df_aniv_mes.iterrows():
                    with st.container():
                        c1, c2, c3 = st.columns([1, 2, 2])
                        with c1:
                            st.metric(label="Dia do Mês", value=f"Dia {row['Dia_Aniv']}")
                        with c2:
                            st.markdown(f"**Membro:** {row['Nome']}<br>**Gestor:** `{row['Responsavel']}`", unsafe_allow_html=True)
                        with c3:
                            msg_p = f"Parabéns, {row['Nome']}! Gestor {row['Responsavel']} passando para liberar seu benefício na Brothers."
                            st.link_button("🎉 Enviar Mensagem", f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(msg_p)}")
                        st.markdown("---")

    with aba_analytics:
        st.subheader("Dashboard de Performance Geral")
        if not membros_db.empty:
            st.metric(label="👥 Total de Leads Capturados", value=len(membros_db))
            st.bar_chart(membros_db["Responsavel"].value_counts(), use_container_width=True)

    with aba_novo_blog:
        st.subheader("✍️ Criador de Conteúdo Livre")
        st.markdown("Cole o seu texto livremente. Se quiser dar formato em partes específicas, use HTML direto no campo:")
        st.code("Exemplos:\n<b>Texto em Negrito</b>\n<i>Texto em Itálico</i>\n<span style='color: gold;'>Texto Dourado</span>")
        
        b_titulo = st.text_input("Título da Postagem:")
        b_autor = st.text_input("Autor da Publicação:", value="Lucas - Central Brothers")
        b_cat = st.selectbox("Categoria Operacional:", ["Dicas Práticas", "Inteligência Financeira", "Passo a Passo", "Novidades do Hub"])
        b_img = st.text_input("URL da Imagem de Destaque:")
        b_conteudo = st.text_area("Escreva aqui o artigo completo com as tags que desejar:", height=300)
        
        if st.button("💥 ENVIAR E PUBLICAR ARTIGO IMEDIATAMENTE", type="primary"):
            if b_titulo and b_conteudo:
                salvar_post(b_titulo, b_autor, b_cat, b_conteudo, b_img)
                st.success("🔥 Artigo publicado com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o Título e o Conteúdo.")
