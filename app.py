import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3
import urllib.parse
import streamlit.components.v1 as components

# Configuração da página - Tema Escuro e Amplo de Alta Performance
st.set_page_config(page_title="Brothers Network Finance - Oficial", layout="wide", initial_sidebar_state="collapsed")

# --- CONEXÃO E ESTRUTURA DO BANCO DE DADOS (INALTERADA e PRESERVADA) ---
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
    """, (titulo, autor, data_atual, category=categoria, conteudo=conteudo, url_img=url_img))
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

# --- SISTEMA VISUAL DE ANIMAÇÕES E MASCOTE (CSS INJETADO) ---
st.markdown("""
<style>
    /* Fundo animado de partículas sutis */
    @keyframes moveParticles {
        0% { background-position: 0px 0px; }
        100% { background-position: 500px 1000px; }
    }
    .stApp {
        background-image: radial-gradient(circle, rgba(20,20,25,1) 0%, rgba(10,10,12,1) 100%);
        position: relative;
    }
    
    /* Mascote flutuante animado */
    @keyframes floatMascot {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(2deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    .mascote-container {
        animation: floatMascot 4s ease-in-out infinite;
        text-align: center;
        padding: 10px;
    }
    
    /* Transições suaves para os blocos */
    .stCard, .stAlert, div[data-testid="stForm"] {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stCard:hover, div[data-testid="stForm"]:hover {
        transform: translateY(-2px);
        box-shadow: 0px 10px 20px rgba(255, 215, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- CONTROLE DE ACESSO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

st.sidebar.title("🦅 Área Restrita")
if not st.session_state.autenticado:
    with st.sidebar.form("login_form"):
        # Apresentação do Mascote na área de Login
        st.markdown("<div class='mascote-container'><span style='font-size: 3rem;'>🤖🦅</span><br><small style='color:#FFD700;'><b>EagleBot:</b> Identifique-se, Diretor!</small></div>", unsafe_allow_html=True)
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
# 🌐 VISÃO PÚBLICA: PORTAL INSTITUCIONAL PREMIUM COM ANIMAÇÕES
# =========================================================================
if not st.session_state.autenticado:
    
    # Interação do Mascote no Topo da Página Principal
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.markdown("<h1 style='color: #FFD700; font-size: 3.5rem; font-weight: 800; margin-bottom:0;'>BROTHERS NETWORK FINANCE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #FFFFFF; font-size: 1.3rem; font-weight: 300;'>Seu Nome Limpo de Verdade, Score Alto e Acesso às Melhores Linhas de Crédito</p>", unsafe_allow_html=True)
    with col_header2:
        st.markdown("<div class='mascote-container'><span style='font-size: 4rem;'>🦅</span><br><b style='color:#FFD700; font-size:11px;'>EagleBot da Brothers</b></div>", unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&auto=format&fit=crop&q=80", use_container_width=True)
    
    st.markdown("---")
    col_info, col_form = st.columns([1, 1.1])
    
    with col_info:
        st.markdown("## 🏢 Como Nós Ajudamos Você e Sua Empresa")
        st.write("Estar com o nome travado ou com score baixo impede você de realizar seus maiores objetivos. Nós resolvemos isso direto na raiz do problema de forma rápida e clara.")
        
        st.markdown("### 📊 Teste Seu Score Abaixo:")
        score_usuario = st.slider("Selecione seu Score aproximado:", min_value=0, max_value=1000, value=350, step=10)
        
        if score_usuario < 400:
            st.error(f"🚨 **Perfil Bloqueado (Score: {score_usuario}):** Os bancos negam seus pedidos. **Nossa Solução:** Entramos com uma ação na Justiça exigindo a limpeza imediata do seu histórico para seu score subir rápido.")
            perfil_score = "Critico"
        elif score_usuario < 700:
            st.warning(f"⚠️ **Perfil de Risco Moderado (Score: {score_usuario}):** Você sofre com juros altos. **Nossa Solução:** Fazemos uma limpeza geral de consultas antigas para calibrar seu score.")
            perfil_score = "Moderado"
        else:
            st.success(f"💎 **Perfil Investidor/Elite (Score: {score_usuario}):** Perfil qualificado para entrar no nosso grupo VIP de empresários e ter acesso a investimentos.")
            perfil_score = "Premium"
            
        st.markdown("---")
        st.markdown("### 🏛️ O Que Fazemos de Forma Simples:")
        st.write("• **Limpamos Seu Passado:** Retiramos restrições antigas e injustas do seu histórico.")
        st.write("• **Sem Enrolação:** Pedimos ordens urgentes ao juiz para limpar seu nome antes do processo acabar.")
        st.warning("⚠️ **Vagas Limitadas:** Atendemos um número restrito de pessoas por semana para garantir velocidade.")
        
    with col_form:
        st.markdown("### 🦅 Solicite Uma Análise Gratuita do Seu Caso")
        with st.form("form_portal", clear_on_submit=True):
            nome = st.text_input("Seu Nome Completo ou Nome da Sua Empresa:")
            whatsapp = st.text_input("WhatsApp com DDD (Ex: 11948086926):", placeholder="Somente números")
            data_nascimento = st.date_input("Data de Nascimento ou Fundação:", min_value=datetime.date(1940, 1, 1))
            servico = st.selectbox("Qual o seu maior desejo ou problema hoje?", [
                "Quero Limpar meu Nome / Subir meu Score Urgente",
                "Preciso de Empréstimo ou Financiamento com Juros Baixos",
                "Quero Proteger meu Dinheiro e Fazer Investimentos Lucrativos",
                "Quero fazer parcerias de negócios e Networking na Comunidade"
            ])
            detalhes = st.text_area("Conte resumidamente o que aconteceu (Opcional):")
            
            if st.form_submit_button("QUERO QUE A SECRETÁRIA ANALISE MEU PERFIL AGORA"):
                if nome and whatsapp:
                    msg_completa = f"Perfil: {perfil_score} (Score: {score_usuario}) | Alvo: {servico} | Obs: {detalhes}"
                    salvar_membro(nome, whatsapp, data_nascimento, msg_completa)
                    st.success(f"🔥 Muito bem, {nome}! Triagem iniciada com sucesso.")
                    st.rerun()
                else:
                    st.error("Por favor, precisamos do seu Nome e WhatsApp.")

    # HISTÓRIA E EQUIPE
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Nossa História & Quem Somos Nós</h2>", unsafe_allow_html=True)
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        st.image("https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&auto=format&fit=crop&q=60", use_container_width=True)
    with col_hist2:
        st.write("A **Brothers Network Finance** é formada por especialistas do mercado de capitais e advogados em direito bancário.")
        st.write("Nosso propósito diário é destravar a sua vida financeira para você voltar a crescer, comprar seus bens e ter tranquilidade.")

    # DEPOIMENTOS
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Pessoas Reais, Resultados Reais</h2>", unsafe_allow_html=True)
    col_dep1, col_dep2, col_dep3 = st.columns(3)
    with col_dep1:
        st.markdown("> **\"Tentei financiar o caminhão da minha empresa e o banco recusou. Em 10 dias a Brothers resolveu meu score.\"**")
        st.caption("— **Ricardo M.**, Empresário")
    with col_dep2:
        st.markdown("> **\"Eu tinha vergonha de ir no banco. Eles limparam meu histórico antigo e hoje tenho crédito aprovado.\"**")
        st.caption("— **Dra. Amanda V.**, Médica")
    with col_dep3:
        st.markdown("> **\"Atendimento sério, transparente e muito rápido. Vale cada centavo pela paz de espírito.\"**")
        st.caption("— **Carlos H.**, Autônomo")

    # FAQ
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>❓ Dúvidas Comuns (FAQ)</h2>", unsafe_allow_html=True)
    with st.expander("Eu vou ter que pagar alguma coisa antes do meu processo iniciar?"):
        st.write("Nossa análise inicial é 100% gratuita via WhatsApp. Explicamos tudo antes de qualquer fechamento.")

    # SEÇÃO DO BLOG COM O SISTEMA LEIA MAIS REPARADO
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>📰 Dicas da Nossa Equipe - Aprenda a Cuidar do Seu Crédito</h2>", unsafe_allow_html=True)
    st.write("\n")

    if not blog_db.empty:
        for idx, post in blog_db.iterrows():
            col_img, col_artigo = st.columns([1, 2.5])
            with col_img:
                st.image(post['Imagem_Url'] if post['Imagem_Url'] else "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&auto=format&fit=crop&q=60", use_container_width=True)
            with col_artigo:
                st.markdown(f"🏷️ `{post['Categoria']}` | 📅 *Publicado em {post['Data']}*")
                st.markdown(f"### {post['Titulo']}")
                
                # Resumo limpo das primeiras linhas
                resumo_limpo = post['Conteudo'].replace("<p>", "").replace("</p>", "").replace("<br>", " ")[:180] + "..."
                st.markdown(resumo_limpo, unsafe_allow_html=True)
                
                # Correção estrutural do Dialog Pop-up
                if st.button("📖 Ler Artigo Didático Completo", key=f"pub_btn_{post['id']}"):
                    @st.dialog(post['Titulo'], width="large")
                    def render_dialog():
                        st.markdown(f"✍️ *Por {post['Autor']} em {post['Data']}*")
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.markdown(post['Conteudo'], unsafe_allow_html=True)
                    render_dialog()
            st.markdown("<br><hr style='border-top: 1px solid #222;'><br>", unsafe_allow_html=True)

# =========================================================================
# 📊 VISÃO PRIVADA: PAINEL MASTER COM BLOGGER EDITOR EM JAVASCRIPT/QUILL
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

    # --- ABA 2: CALENDÁRIO DE RELACIONAMENTO (CORRIGIDO) ---
    with aba_calendario:
        st.subheader("📅 Calendário de Relacionamento de Aniversariantes")
        hoje = datetime.date.today()
        meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_selecionado = st.selectbox("Selecione o Mês para Filtro:", list(range(1, 13)), index=hoje.month - 1, format_func=lambda x: meses_nomes[x-1])
        
        if membros_db.empty:
            st.info("Nenhum cliente cadastrado para mapeamento de aniversário.")
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
                            st.markdown(f"**Membro da Comunidade:** {row['Nome']}<br>**Gestor Vinculado:** `{row['Responsavel']}`", unsafe_allow_html=True)
                        with c3:
                            msg_p = f"Parabéns, {row['Nome']}! Gestor {row['Responsavel']} passando para liberar seu benefício exclusivo de aniversário na Brothers."
                            st.link_button("🎉 Disparar Mensagem de Parabéns", f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(msg_p)}")
                        st.markdown("---")

    # --- ABA 3: DASHBOARD ---
    with aba_analytics:
        st.subheader("Dashboard de Performance Geral")
        if not membros_db.empty:
            st.metric(label="👥 Total de Leads Capturados", value=len(membros_db))
            st.bar_chart(membros_db["Responsavel"].value_counts(), use_container_width=True)

    # --- ABA 4: O EDITOR DE TEXTO RICO REAL (ESTILO BLOGGER COMPLETO) ---
    with aba_novo_blog:
        st.subheader("✍️ Editor de Postagens Profissional WYSIWYG (Estilo Blogger)")
        st.markdown("Digite o texto, selecione os trechos com o mouse e use a barra de ferramentas para formatar livremente de forma cirúrgica.")
        
        b_titulo = st.text_input("Título da Postagem Comercial/Didática:")
        b_autor = st.text_input("Autor da Publicação:", value="Lucas - Central Brothers")
        b_cat = st.selectbox("Categoria Operacional:", ["Dicas Práticas", "Inteligência Financeira", "Passo a Passo", "Novidades do Hub"])
        b_img = st.text_input("URL da Imagem de Destaque:")
        
        st.markdown("---")
        st.markdown("#### 💻 Painel do Editor Visual Quill")
        
        # Injeção de Componente Rich Text Real via IFrame Javascript (Não quebra o Streamlit e funciona igual ao Blogger)
        quill_html = """
        <!-- Include stylesheet -->
        <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
        <div id="editor-container" style="height: 250px; background: #fff; color: #000;"></div>
        <!-- Include the Quill library -->
        <script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>
        <script>
          var quill = new Quill('#editor-container', {
            modules: { toolbar: [['bold', 'italic', 'underline'], [{ 'header': [1, 2, 3, false] }], [{ 'color': [] }, { 'background': [] }], [{ 'list': 'ordered'}, { 'list': 'bullet' }]] },
            theme: 'snow'
          });
          
          // Envia o HTML interno do editor para o Python em tempo real sempre que o usuário digita
          quill.on('text-change', function() {
             window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: quill.root.innerHTML
             }, '*');
          });
        </script>
        """
        
        # Executa o editor e captura o HTML puro gerado pelo mouse/teclado do usuário
        editor_data = components.html(quill_html, height=320)
        
        # Recupera o valor digitado de forma dinâmica e resolve o bug da Pré-Visualização ao Vivo
        if "conteudo_blogger" not in st.session_state:
            st.session_state.conteudo_blogger = ""
            
        if editor_data:
            st.session_state.conteudo_blogger = editor_data
            
        st.markdown("---")
        st.markdown("#### 👁️ Pré-visualização do Artigo ao Vivo (Renderização Real):")
        
        # Mostra o texto exatamente formatado como vai aparecer para o cliente
        st.markdown(f"<div style='background-color: #1a1a24; padding: 20px; border-radius: 8px; border: 1px solid #333;'>{st.session_state.conteudo_blogger}</div>", unsafe_allow_html=True)
        
        st.write("\n")
        if st.button("💥 ENVIAR E PUBLICAR ARTIGO IMEDIATAMENTE", type="primary"):
            if b_titulo and st.session_state.conteudo_blogger:
                salvar_post(b_titulo, b_autor, b_cat, st.session_state.conteudo_blogger, b_img)
                st.session_state.conteudo_blogger = ""
                st.success("🔥 Artigo didático publicado com sucesso na Home pública!")
                st.rerun()
            else:
                st.error("Por favor, precisamos que digite um Título e escreva o texto no editor.")
