import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3
import urllib.parse

# Configuração da página - Tema Escuro e Amplo de Alta Performance
st.set_page_config(page_title="Brothers Network Finance - Oficial", layout="wide", initial_sidebar_state="collapsed")

# --- CONEXÃO E ESTRUTURA DO BANCO DE DADOS (100% PRESERVADA) ---
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

# --- CONFIGURAÇÃO DA EQUIPE ---
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

# --- ALIMENTAÇÃO INICIAL DO BLOG ---
def inicializar_conteudo_blog():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    check = cursor.execute("SELECT COUNT(*) FROM blog").fetchone()[0]
    if check == 0:
        posts_iniciais = [
            (
                "Como o Banco Analisa Seu Perfil Quando Você Pede um Empréstimo?",
                "Lucas - Central Brothers", "Dicas Práticas",
                "Muitas pessoas pagam suas contas em dia, mas continuam recebendo respostas negativas ao tentar um financiamento. O motivo real está nas consultas em massa que as lojas fazem no seu CPF, derrubando o score interno do mercado de forma injusta. Para corrigir isso e forçar os bancos a liberarem crédito limpo, nossa equipe atua direto na raiz do problema removendo esses rastros de forma definitiva.",
                "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&auto=format&fit=crop&q=60"
            )
        ]
        cursor.executemany("INSERT INTO blog (Titulo, Autor, Categoria, Conteudo, Imagem_Url, Data) VALUES (?, ?, ?, ?, ?, '06/06/2026')", posts_iniciais)
        conn.commit()
    conn.close()

inicializar_conteudo_blog()

# --- ANIMAÇÕES E IDENTIDADE VISUAL PREMIUM ---
st.markdown("""
<style>
    .stApp {
        background-image: radial-gradient(circle, rgba(20,20,25,1) 0%, rgba(10,10,12,1) 100%);
        position: relative;
    }
    @keyframes floatMascot {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    .mascote-container {
        animation: floatMascot 3.5s ease-in-out infinite;
        text-align: center;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- CONTROLE DE ACESSO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

st.sidebar.title("🦅 Área Restrita")
if not st.session_state.autenticado:
    with st.sidebar.form("login_form"):
        st.markdown("<div class='mascote-container'><span style='font-size: 2.5rem;'>🦅</span><br><small style='color:#FFD700;'><b>EagleBot:</b> Identifique-se, Diretor!</small></div>", unsafe_allow_html=True)
        usuario = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")
        if st.form_submit_button("Acessar Painel"):
            if usuario == "admin" and senha == "brothers2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.sidebar.error("Acesso negado.")
else:
    st.sidebar.success("Modo Admin Ativo")
    if st.sidebar.button("🔒 Sair do Painel"):
        st.session_state.autenticado = False
        st.rerun()

membros_db = carregar_dados()
blog_db = carregar_posts()

# =========================================================================
# 🌐 VISÃO PÚBLICA: PORTAL INSTITUCIONAL COMPLETO E DIDÁTICO
# =========================================================================
if not st.session_state.autenticado:
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.markdown("<h1 style='color: #FFD700; font-size: 3.5rem; font-weight: 800; margin-bottom:0;'>BROTHERS NETWORK FINANCE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #FFFFFF; font-size: 1.3rem; font-weight: 300;'>Seu Nome Limpo, Score Alto e Acesso às Melhores Linhas de Crédito</p>", unsafe_allow_html=True)
    with col_header2:
        st.markdown("<div class='mascote-container'><span style='font-size: 3.5rem;'>🦅</span><br><b style='color:#FFD700; font-size:11px;'>EagleBot Ativo</b></div>", unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&auto=format&fit=crop&q=80", use_container_width=True)
    st.write("\n")
    
    st.markdown("---")
    col_info, col_form = st.columns([1, 1.1])
    
    with col_info:
        st.markdown("## 🏢 Como Nós Ajudamos Você e Sua Empresa")
        st.write("Estar com o nome travado impede você de realizar seus objetivos profissionais e pessoais. Nós limpamos o seu rastro de forma simples, rápida e transparente.")
        
        st.markdown("### 📊 Teste Seu Score Abaixo:")
        score_usuario = st.slider("Selecione seu Score aproximado:", min_value=0, max_value=1000, value=350, step=10)
        
        if score_usuario < 400:
            st.error(f"🚨 **Perfil Bloqueado (Score: {score_usuario}):** Os bancos negam seus pedidos automaticamente. **Nossa Solução:** Limpamos seu histórico na justiça através de liminar urgente.")
            perfil_score = "Critico"
        elif score_usuario < 700:
            st.warning(f"⚠️ **Perfil de Risco Moderado (Score: {score_usuario}):** Você sofre com taxas de juros abusivas. **Nossa Solução:** Removemos consultas excessivas para calibrar seu score.")
            perfil_score = "Moderado"
        else:
            st.success(f"💎 **Perfil Elite (Score: {score_usuario}):** Totalmente pronto para o Hub VIP de networking corporativo e alocação de investimentos de alta performance.")
            perfil_score = "Premium"
            
        st.markdown("---")
        st.write("• **Limpamos Seu Passado:** Retiramos apontamentos negativos de forma definitiva do sistema.")
        st.write("• **Sem Enrolação:** Pedidos urgentes direcionados ao juiz antes do fim do processo.")
        st.warning("⚠️ **Vagas Limitadas:** Atendimento semanal restrito para manter a velocidade da equipe.")
        
    with col_form:
        st.markdown("### 🦅 Solicite Uma Análise Gratuita do Seu Caso")
        with st.form("form_portal", clear_on_submit=True):
            nome = st.text_input("Seu Nome Completo ou Razão Social:")
            whatsapp = st.text_input("WhatsApp com DDD (Ex: 11948086926):", placeholder="Somente números")
            data_nascimento = st.date_input("Data de Nascimento / Fundação:", min_value=datetime.date(1940, 1, 1))
            servico = st.selectbox("Qual o maior problema hoje?", ["Quero Limpar meu Nome / Subir meu Score Urgente", "Preciso de Empréstimo com Juros Baixos", "Quero Investimentos Lucrativos", "Quero Networking na Comunidade"])
            detalhes = st.text_area("Conte resumidamente o que aconteceu:")
            
            if st.form_submit_button("QUERO QUE A SECRETÁRIA ANALISE MEU PERFIL AGORA"):
                if nome and whatsapp:
                    msg_completa = f"Perfil: {perfil_score} (Score: {score_usuario}) | Alvo: {servico} | Obs: {detalhes}"
                    salvar_membro(nome, whatsapp, data_nascimento, msg_completa)
                    st.success(f"🔥 Muito bem, {nome}! Triagem iniciada com sucesso.")
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
        st.write("A **Brothers Network Finance** é formada por especialistas focados em direito bancário e mercado financeiro. Nosso propósito diário é quebrar as amarras burocráticas injustas dos bancos para que você recupere sua tranquilidade comercial.")

    # DEPOIMENTOS
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Pessoas Reais, Resultados Reais</h2>", unsafe_allow_html=True)
    col_dep1, col_dep2, col_dep3 = st.columns(3)
    with col_dep1:
        st.markdown("> **\"Tentei financiar um caminhão e recusaram. Em 10 dias a Brothers resolveu meu score juridicamente.\"**")
        st.caption("— **Ricardo M.**, Empresário")
    with col_dep2:
        st.markdown("> **\"Eles limparam meu histórico de consultas antigas e hoje tenho crédito aprovado em 3 bancos.\"**")
        st.caption("— **Dra. Amanda V.**, Médica")
    with col_dep3:
        st.markdown("> **\"Atendimento sério, transparente e muito rápido. Devolve a paz de espírito comercial.\"**")
        st.caption("— **Carlos H.**, Autônomo")

    # FAQ
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>❓ Dúvidas Comuns (FAQ)</h2>", unsafe_allow_html=True)
    with st.expander("Eu vou ter que pagar alguma coisa antes do meu processo iniciar?"):
        st.write("Nossa análise inicial é 100% gratuita via WhatsApp. Só fechamos após mostrar o que está travando o seu perfil.")

    # SEÇÃO DO BLOG COM O SISTEMA LEIA MAIS REPARADO
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
# 📊 VISÃO PRIVADA (CRM, CALENDÁRIO, GRAPHICS E O PUBLICADOR ATUALIZADO)
# =========================================================================
else:
    st.title("🦅 Central Administrativa Master - Brothers Network")
    aba_gestao, aba_calendario, aba_analytics, aba_novo_blog = st.tabs([
        "📊 Gerenciador de Tarefas e Disparos", 
        "📅 Calendário de Relacionamento", 
        "📈 Dashboard de Performance", 
        "✍️ Publicar Novo Conteúdo no Blog"
    ])

    # --- ABA 1: GERENCIADOR (CRM) ---
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
                    "T1": st.column_config.SelectboxColumn("T1", options=["Pendente", "Concluído"]),
                    "T2": st.column_config.SelectboxColumn("T2", options=["Pendente", "Concluído"]),
                    "T3": st.column_config.SelectboxColumn("T3", options=["Pendente", "Concluído"]),
                    "T4": st.column_config.SelectboxColumn("T4", options=["Pendente", "Concluído"]),
                    "T5": st.column_config.SelectboxColumn("T5", options=["Pendente", "Concluído"]),
                    "Próxima Ação": st.column_config.LinkColumn("💬 WhatsApp", display_text="Chamar")
                },
                hide_index=True,
                use_container_width=True
            )
            if st.button("💾 Salvar Alterações de Status", type="primary"):
                atualizar_status(df_editado)
                st.success("Alterações gravadas com sucesso!")
                st.rerun()

    # --- ABA 2: CALENDÁRIO ---
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

    # --- ABA 3: DASHBOARD ---
    with aba_analytics:
        st.subheader("Dashboard de Performance Geral")
        if not membros_db.empty:
            st.metric(label="👥 Total de Leads Capturados", value=len(membros_db))
            st.bar_chart(membros_db["Responsavel"].value_counts(), use_container_width=True)

    # --- ABA 4: O EDITOR DE TEXTO RICO (ACÓPLADO VISUALMENTE COMPLETO) ---
    with aba_novo_blog:
        st.subheader("✍️ Editor de Postagens Profissional (Estilo Blogger)")
        st.markdown("Monte seu artigo usando a formatação direta abaixo. Diferente da versão anterior, você pode aplicar estilos a frases específicas combinando os blocos de texto.")
        
        b_titulo = st.text_input("Título da Postagem:")
        b_autor = st.text_input("Autor da Publicação:", value="Lucas - Central Brothers")
        b_cat = st.selectbox("Categoria Operacional:", ["Dicas Práticas", "Inteligência Financeira", "Passo a Passo", "Novidades do Hub"])
        b_img = st.text_input("URL da Imagem de Destaque:")
        
        st.markdown("---")
        st.markdown("### 🛠️ Painel de Edição de Texto por Parágrafo")
        st.write("Escreva o parágrafo abaixo e marque as opções de formatação que deseja aplicar **somente a este bloco**:")
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            f_bold = st.checkbox("Texto em Negrito (Bold)")
        with col_f2:
            f_italic = st.checkbox("Texto em Itálico")
        with col_f3:
            f_header = st.checkbox("Transformar em Subtítulo")
        with col_f4:
            f_gold = st.checkbox("Texto na Cor Dourada (VIP)")
            
        texto_bloco = st.text_area("Escreva o parágrafo ou frase aqui:", height=100, placeholder="Ex: Este texto terá a formatação marcada acima...")
        
        # Processa a formatação selecionada de forma limpa e segura
        if texto_bloco:
            if f_bold:
                texto_bloco = f"<b>{texto_bloco}</b>"
            if f_italic:
                texto_bloco = f"<i>{texto_bloco}</i>"
            if f_header:
                texto_bloco = f"<h3>{texto_bloco}</h3>"
            if f_gold:
                texto_bloco = f"<span style='color: #FFD700;'>{texto_bloco}</span>"
                
        if "acumulador_html" not in st.session_state:
            st.session_state.acumulador_html = ""
            
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("➕ Inserir Bloco Formatado no Artigo"):
                if texto_bloco:
                    st.session_state.acumulador_html += texto_bloco + "<br><br>"
                    st.success("Bloco adicionado com sucesso ao documento!")
                else:
                    st.error("Escreva um texto antes de inserir.")
        with col_btn2:
            if st.button("🗑️ Limpar Rascunho Completo"):
                st.session_state.acumulador_html = ""
                st.rerun()
                
        st.markdown("---")
        st.markdown("### 👁️ Caixa de Edição Final do Artigo (Estilo Código/Texto do Blogger)")
        st.write("Abaixo está o texto consolidado com as formatações aplicadas. Você pode editar diretamente se quiser:")
        
        # O rascunho final onde a mágica acontece
        corpo_final_artigo = st.text_area("Conteúdo Completo (HTML/Rich Text):", value=st.session_state.acumulador_html, height=200)
        
        st.markdown("#### 📱 Pré-visualização Real da Postagem:")
        st.markdown(f"<div style='background-color: #1a1a24; padding: 20px; border-radius: 8px; border: 1px solid #333;'>{corpo_final_artigo}</div>", unsafe_allow_html=True)
        
        if st.button("💥 ENVIAR E PUBLICAR ARTIGO IMEDIATAMENTE", type="primary"):
            if b_titulo and corpo_final_artigo:
                salvar_post(b_titulo, b_autor, b_cat, corpo_final_artigo, b_img)
                st.session_state.acumulador_html = ""
                st.success("🔥 Artigo publicado com sucesso! Faça logout para ver o botão 'Leia Mais' na Home.")
                st.rerun()
            else:
                st.error("Preencha o Título e o Conteúdo antes de publicar.")
