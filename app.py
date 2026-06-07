import streamlit as st
import pandas as pd
import datetime
import calendar
import sqlite3
import urllib.parse

# Configuração da página - Tema Escuro e Amplo de Alta Performance
st.set_page_config(page_title="Brothers Network Finance - Oficial", layout="wide", initial_sidebar_state="collapsed")

# --- CONEXÃO E CORREÇÃO AUTOMÁTICA DO BANCO DE DADOS (PRESERVADA) ---
def conectar_banco():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT, WhatsApp TEXT, Data_Nascimento TEXT, Mensagem TEXT,
            Dia_Aniv INTEGER, Mes_Aniv INTEGER,
            T1_BoasVindas TEXT, T2_AnaliseCredito TEXT, T3_GatilhoOferta TEXT,
            T4_MsgWhats TEXT, T5_PosVenda TEXT, Responsavel TEXT
        )
    """)
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

# --- ALIMENTAÇÃO INICIAL DIDÁTICA DO BLOG (EXPLICANDO O PROCESSO) ---
def inicializar_conteudo_blog():
    conn = sqlite3.connect("brothers.db")
    cursor = conn.cursor()
    check = cursor.execute("SELECT COUNT(*) FROM blog").fetchone()[0]
    if check == 0:
        posts_iniciais = [
            (
                "Guia Prático: O Que Fazer Quando o Banco Nega Crédito Mesmo Com o Nome Limpo?",
                "Lucas - Performance", "Dicas Práticas",
                "Muitas pessoas e empresas enfrentam uma situação muito frustrante: elas pagam suas contas, não possuem nenhuma restrição no CPF ou CNPJ, mas quando vão ao banco pedir um financiamento de veículo, imóvel ou cartão, a resposta é um sonoro 'não'.<br><br><b>Por que isso acontece?</b><br>O motivo oculto se chama <i>'Histórico de Consultas Excessivas'</i> ou score interno bloqueado. Toda vez que você tenta pedir crédito em várias lojas ou bancos seguidos, o sistema do mercado financeiro entende que você está desesperado por dinheiro e joga sua pontuação para baixo.<br><br><b>Como resolver na prática?</b><br>1. Evite colocar o CPF em aplicativos de simulação de crédito por 30 dias.<br>2. Ative o seu Cadastro Positivo de forma correta.<br>3. Caso o seu nome tenha sido negativado no passado de forma injusta ou abusiva, nossa equipe jurídica pode entrar com uma ação para apagar esse rastro de forma definitiva, forçando o mercado a subir seu score de maneira justa e rápida.",
                "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&auto=format&fit=crop&q=60"
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
    st.sidebar.success("Modo Admin Ativo")
    if st.sidebar.button("🔒 Sair do Painel"):
        st.session_state.autenticado = False
        st.rerun()

membros_db = carregar_dados()
blog_db = carregar_posts()

# =========================================================================
# 🌐 VISÃO PÚBLICA: DESIGN DE ELITE COM LINGUAGEM CLARA E ACESSÍVEL
# =========================================================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #FFD700; font-size: 3.5rem; font-weight: 800;'>BROTHERS NETWORK FINANCE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFFFFF; font-size: 1.3rem; font-weight: 300;'>Seu Nome Limpo de Verdade, Score Alto e Acesso às Melhores Linhas de Crédito do Mercado</p>", unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&auto=format&fit=crop&q=80", use_container_width=True)
    st.write("\n")
    
    st.markdown("---")
    col_info, col_form = st.columns([1, 1.1])
    
    with col_info:
        st.markdown("## 🏢 Como Nós Ajudamos Você e Sua Empresa")
        st.write("Estar com o nome travado ou com score baixo impede você de realizar seus maiores sonhos: seja comprar a casa própria da família, financiar um carro ou conseguir dinheiro para expandir sua empresa. Nós resolvemos isso direto na raiz do problema.")
        
        # --- TERMÔMETRO INTERATIVO REFORMULADO (LINGUAGEM CLARA) ---
        st.markdown("### 📊 Teste Seu Score Abaixo:")
        st.write("Arraste a barra para o seu score atual e veja o que está acontecendo com o seu perfil:")
        score_usuario = st.slider("Selecione seu Score aproximado:", min_value=0, max_value=1000, value=350, step=10)
        
        if score_usuario < 400:
            st.error(f"🚨 **Perfil Bloqueado (Score: {score_usuario}):** Com essa pontuação, os bancos negam qualquer pedido seu automático. **Nossa Solução:** Entramos com uma ação na Justiça exigindo que limpem o seu histórico imediatamente para que seu score suba em poucos dias.")
            perfil_score = "Critico"
        elif score_usuario < 700:
            st.warning(f"⚠️ **Perfil de Risco Moderado (Score: {score_usuario}):** Você até consegue aprovar algumas coisas, mas os bancos te cobram os maiores juros possíveis. **Nossa Solução:** Fazemos uma limpeza geral de consultas antigas para subir seu score para o nível máximo.")
            perfil_score = "Moderado"
        else:
            st.success(f"💎 **Perfil Investidor/Elite (Score: {score_usuario}):** Sua saúde financeira é excelente! Você está totalmente pronto para entrar no nosso grupo VIP de empresários e ter acesso a investimentos exclusivos de alta rentabilidade.")
            perfil_score = "Premium"
            
        st.markdown("---")
        st.markdown("### 🏛️ O Que Fazemos de Forma Simples:")
        st.write("• **Limpamos Seu Passado:** Retiramos restrições antigas e injustas do seu histórico através da justiça.")
        st.write("• **Sem Enrolação:** Nosso time entra com pedidos urgentes para o juiz mandar limpar o seu nome antes mesmo do processo acabar.")
        st.write("• **Segurança Total:** Suas informações são tratadas sob sigilo absoluto. Ninguém fica sabendo.")
        st.warning("⚠️ **Vagas Limitadas:** Atendemos um número restrito de pessoas por semana para garantir que cada processo seja resolvido com máxima velocidade.")
        
    with col_form:
        st.markdown("### 🦅 Solicite Uma Análise Gratuita do Seu Caso")
        with st.form("form_portal", clear_on_submit=True):
            nome = st.text_input("Seu Nome Completo ou Nome da Sua Empresa:")
            whatsapp = st.text_input("WhatsApp com DDD (Ex: 11948086926):", placeholder="Somente números")
            data_nascimento = st.date_input("Data de Nascimento ou Fundação da Empresa:", min_value=datetime.date(1940, 1, 1))
            servico = st.selectbox("Qual o seu maior desejo ou problema hoje?", [
                "Quero Limpar meu Nome / Subir meu Score Urgente",
                "Preciso de Empréstimo ou Financiamento com Juros Baixos",
                "Quero Proteger meu Dinheiro e Fazer Investimentos Lucrativos",
                "Quero fazer parcerias de negócios e Networking na Comunidade"
            ])
            detalhes = st.text_area("Conte resumidamente o que aconteceu (Opcional):", placeholder="Ex: Fui tentar financiar um carro e o banco recusou por conta do score...")
            
            if st.form_submit_button("QUERO QUE A SECRETÁRIA ANALISE MEU PERFIL AGORA"):
                if nome and whatsapp:
                    msg_completa = f"Perfil: {perfil_score} (Score: {score_usuario}) | Alvo: {servico} | Obs: {detalhes}"
                    salvar_membro(nome, whatsapp, data_nascimento, msg_completa)
                    st.success(f"🔥 Muito bem, {nome}! Seus dados foram recebidos. Nossa Secretária Eletrônica já agendou sua triagem e vai te chamar no WhatsApp.")
                    st.rerun()
                else:
                    st.error("Por favor, precisamos do seu Nome e WhatsApp para podermos te chamar.")

    # HISTÓRIA E EQUIPE
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Nossa História & Quem Somos Nós</h2>", unsafe_allow_html=True)
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        st.image("https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&auto=format&fit=crop&q=60", use_container_width=True)
    with col_hist2:
        st.write("A **Brothers Network Finance** não é apenas uma empresa fria de internet. Nós somos uma equipe formada por especialistas do mercado financeiro e advogados especialistas em direito bancário.")
        st.write("Nós nascemos porque cansadamos de ver bancos cobrando juros absurdos de pessoas trabalhadoras e bloqueando o crédito de empresas honestas por conta de regras de score injustas. Nosso propósito diário é destravar a sua vida financeira para você voltar a crescer, comprar seus bens e ter a tranquilidade que você e sua família merecem.")

    # DEPOIMENTOS
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Pessoas Reais, Resultados Reais</h2>", unsafe_allow_html=True)
    col_dep1, col_dep2, col_dep3 = st.columns(3)
    with col_dep1:
        st.markdown("> **\"Tentei financiar o caminhão da minha empresa e o banco recusou. Em 10 dias a Brothers resolveu meu score juridicamente e eu consegui comprar o veículo.\"**")
        st.caption("— **Ricardo M.**, Empresário")
    with col_dep2:
        st.markdown("> **\"Eu tinha vergonha de ir no banco pedir cartão de crédito. Eles limparam meu histórico antigo e hoje tenho crédito aprovado em 3 bancos diferentes.\"**")
        st.caption("— **Dra. Amanda V.**, Médica")
    with col_dep3:
        st.markdown("> **\"Atendimento sério, transparente e muito rápido. Vale cada centavo pela paz de espírito que nos devolve.\"**")
        st.caption("— **Carlos H.**, Autônomo")

    # FAQ
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>❓ Dúvidas Comuns (FAQ)</h2>", unsafe_allow_html=True)
    with st.expander("Eu vou ter que pagar alguma coisa antes do meu processo iniciar?"):
        st.write("Nossa equipe faz uma análise 100% gratuita do seu caso através do WhatsApp. Explicamos o que está travando o seu perfil antes de fecharmos qualquer parceria.")
    with st.expander("Meu nome realmente fica limpo com esse processo na justiça?"):
        st.write("Sim. A ação judicial obriga as instituições de proteção ao crédito a remover as consultas excessivas e históricos negativos antigos que puxam sua pontuação para baixo ilegalmente.")

    # =========================================================================
    # 📰 INSTALAÇÃO DO MECANISMO "LEIA MAIS" DINÂMICO
    # =========================================================================
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
                
                # Exibe apenas um resumo curto na tela principal para não poluir
                texto_limpo = post['Conteudo'].replace("<br>", " ").replace("<b>", "").replace("</i>", "")
                resumo = texto_limpo[:180] + "..."
                st.write(resumo)
                
                # POP-UP INTELIGENTE INTEGRADO: O botão "Leia Mais"
                if st.button("📖 Ler Artigo Didático Completo", key=f"btn_{post['id']}"):
                    @st.dialog(post['Titulo'], width="large")
                    def abrir_artigo_inteiro(conteudo, autor, data):
                        st.markdown(f"✍️ *Por {autor} em {data}*")
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.markdown(conteudo, unsafe_allow_html=True)
                    
                    abrir_artigo_inteiro(post['Conteudo'], post['Autor'], post['Data'])
            st.markdown("<br><hr style='border-top: 1px solid #222;'><br>", unsafe_allow_html=True)

# =========================================================================
# 📊 VISÃO PRIVADA: PAINEL COM EDITOR RICH TEXT (ESTILO BLOGGER)
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

    # --- ABA 1: GERENCIADOR (PRESERVADO) ---
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

    # --- ABA 2: CALENDÁRIO FIXADO ---
    with aba_calendario:
        st.subheader("📅 Aniversariantes do Mês")
        hoje = datetime.date.today()
        meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_selecionado = st.selectbox("Selecione o Mês:", list(range(1, 13)), index=hoje.month - 1, format_func=lambda x: meses_nomes[x-1])
        
        if membros_db.empty:
            st.info("Nenhum cliente cadastrado no sistema.")
        else:
            df_aniv_mes = membros_db[membros_db["Mes_Aniv"] == mes_selecionado]
            if df_aniv_mes.empty:
                st.write("Não há aniversariantes este mês.")
            else:
                for idx, row in df_aniv_mes.iterrows():
                    with st.container():
                        c1, c2, c3 = st.columns([1, 2, 2])
                        with c1:
                            st.metric(label="Dia", value=f"Dia {row['Dia_Aniv']}")
                        with c2:
                            st.markdown(f"**Cliente:** {row['Nome']} | **Responsável:** `{row['Responsavel']}`")
                        with c3:
                            msg_p = f"Parabéns, {row['Nome']}! Gestor {row['Responsavel']} passando para liberar seu benefício exclusivo de aniversário na Brothers."
                            st.link_button("🎉 Enviar Mensagem", f"https://api.whatsapp.com/send?phone={row['WhatsApp']}&text={urllib.parse.quote(msg_p)}")
                        st.markdown("---")

    # --- ABA 3: DASHBOARD ---
    with aba_analytics:
        st.subheader("Dashboard de Performance")
        if not membros_db.empty:
            st.metric(label="👥 Total de Leads Capturados", value=len(membros_db))
            st.bar_chart(membros_db["Responsavel"].value_counts(), use_container_width=True)

    # --- ABA 4: O NOVO EDITOR ESTILO BLOGGER (RICH TEXT VISUAL NATIVO) ---
    with aba_novo_blog:
        st.subheader("✍️ Editor de Postagens Profissional (Estilo Blogger)")
        st.markdown("Use as caixas de ferramentas visuais abaixo para criar textos dinâmicos e didáticos para instruir os clientes.")
        
        b_titulo = st.text_input("Título da Postagem:")
        b_autor = st.text_input("Autor da Dica:", value="Lucas - Central Brothers")
        b_cat = st.selectbox("Categoria Operacional:", ["Dicas Práticas", "Inteligência Financeira", "Passo a Passo", "Novidades do Hub"])
        b_img = st.text_input("URL da Foto de Destaque (Link público):", placeholder="https://images.unsplash.com/...")
        
        st.markdown("---")
        st.markdown("### 🖥️ Corpo do Artigo (Ferramentas de Formatação Estilo Rich Text)")
        
        # Criação de um menu de ferramentas visuais em colunas (Imita a barra do Blogger)
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            usar_negrito = st.checkbox("Bold (Negrito)")
        with col_t2:
            usar_italico = st.checkbox("Italic (Itálico)")
        with col_t3:
            criar_subtitulo = st.checkbox("Adicionar Subtítulo")
        with col_t4:
            texto_dourado = st.checkbox("Cor de Destaque Dourada")
            
        texto_puro = st.text_area("Digite o conteúdo do parágrafo abaixo:", height=150, placeholder="Escreva o bloco de texto aqui...")
        
        # Processamento visual automático em tempo real baseado nos cliques dos botões
        conteudo_processado = texto_puro
        if usar_negrito:
            conteudo_processado = f"<b>{conteudo_processado}</b>"
        if usar_italico:
            conteudo_processado = f"<i>{conteudo_processado}</i>"
        if criar_subtitulo:
            conteudo_processado = f"<h3>{conteudo_processado}</h3>"
        if texto_dourado:
            conteudo_processado = f"<span style='color: #FFD700;'>{conteudo_processado}</span>"
            
        # O Editor acumula os blocos na memória para visualização prévia antes de salvar
        if "bloco_artigo" not in st.session_state:
            st.session_state.bloco_artigo = ""
            
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("➕ Adicionar Bloco Formatado ao Artigo"):
                if texto_puro:
                    st.session_state.bloco_artigo += conteudo_processado + "<br><br>"
                    st.success("Bloco anexado com sucesso!")
                else:
                    st.error("Digite algum texto antes de anexar.")
        with col_b2:
            if st.button("🗑️ Limpar Rascunho"):
                st.session_state.bloco_artigo = ""
                st.rerun()
                
        st.markdown("#### 👁️ Pré-visualização do Artigo ao Vivo:")
        st.info("Caso queira pular o editor visual e colar um texto HTML completo pronto do Blogger diretamente, basta usar o botão de Limpar e colar no rascunho.")
        
        # Caixa de texto final editável contendo o HTML acumulado (Rich Text Completo)
        artigo_final_html = st.text_area("Código Final do Artigo (Editável):", value=st.session_state.bloco_artigo, height=180)
        st.markdown("<div style='background-color: #111; padding: 15px; border-radius: 5px;'>", unsafe_allow_html=True)
        st.markdown(artigo_final_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("💥 ENVIAR E PUBLICAR ARTIGO NO BLOG DA HOME", type="primary"):
            if b_titulo and artigo_final_html:
                salvar_post(b_titulo, b_autor, b_cat, artigo_final_html, b_img)
                st.session_state.bloco_artigo = ""
                st.success("🔥 Postagem didática publicada com sucesso! Faça logout para ver o mecanismo 'Leia Mais' em ação.")
                st.rerun()
            else:
                st.error("Por favor, preencha o Título e o Conteúdo do artigo.")
