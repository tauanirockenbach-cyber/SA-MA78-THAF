import hashlib
import pymysql
import streamlit as st

st.set_page_config(
    page_title="THAF Manutenção - Login",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# Conexão com o banco (credenciais em .streamlit/secrets.toml)
# ------------------------------------------------------------------
DB_CONF = st.secrets["mysql"]

# Usados apenas para preencher os campos dos botões de acesso rápido
# (demonstração). O login em si sempre consulta a tabela Usuarios já
# existente no banco — nada é criado por aqui.
SEED_USERS = [
    ("tauani@thaf.com", "tauani123", "role_admin_manutencao", "Administrador", "ALL PRIVILEGES"),
    ("felipe@thaf.com", "felipe123", "role_supervisor_manutencao", "Supervisor", "SELECT, INSERT, UPDATE, DELETE"),
    ("ana@thaf.com", "ana123", "role_tecnico_manutencao", "Técnico", "SELECT, INSERT"),
    ("henrique@thaf.com", "henrique123", "role_auditor_manutencao", "Auditor", "SELECT"),
]


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def get_connection():
    """Abre uma conexão nova com o MySQL do Aiven (SSL habilitado)."""
    return pymysql.connect(
        host=DB_CONF["host"],
        port=int(DB_CONF["port"]),
        user=DB_CONF["user"],
        password=DB_CONF["password"],
        database=DB_CONF["database"],
        ssl={"ssl": {}},  # Aiven exige conexão criptografada
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def get_client_ip() -> str:
    """Tenta obter o IP de origem da requisição (best effort)."""
    try:
        ip = getattr(st.context, "ip_address", None)
        if ip:
            return ip
        headers = getattr(st.context, "headers", {}) or {}
        forwarded = headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    except Exception:
        pass
    return "desconhecido"


def log_acesso(id_usuario, acao: str, sucesso: bool):
    """Registra a tentativa de acesso em Logs_Acesso."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO Logs_Acesso (id_usuario, data_hora, acao_acesso, ip_origem, sucesso_acesso) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (id_usuario, acao, get_client_ip(), sucesso),
                )
        finally:
            conn.close()
    except Exception:
        # Não deixa uma falha de log derrubar o fluxo de login
        pass


def autenticar(email: str, senha: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Seleciona o usuário pelo e-mail
            cur.execute("SELECT * FROM Usuarios WHERE email_usuario = %s", (email.strip().lower(),))
            row = cur.fetchone()
    finally:
        conn.close()

    # Compara usando o campo "senha" que é o nome real na sua tabela
    if row and row["senha"] == hash_senha(senha):
        # NOTA: Se você tiver a função log_acesso, use o id_usuario dela
        # log_acesso(row["id_usuario"], "LOGIN", True)
        return row

    return None


def buscar_ultimos_acessos(limit: int = 5):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # CORRIGIDO: Alterado u.email para u.email_usuario para bater com o banco
            cur.execute("""
                SELECT l.data_hora, COALESCE(u.email_usuario, '(usuário removido)') AS email,
                       l.acao_acesso, l.ip_origem, l.sucesso_acesso
                FROM Logs_Acesso l
                LEFT JOIN Usuarios u ON u.id_usuario = l.id_usuario
                ORDER BY l.data_hora DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


# ------------------------------------------------------------------
# Estado da sessão
# ------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email_input" not in st.session_state:
    st.session_state.email_input = ""
if "senha_input" not in st.session_state:
    st.session_state.senha_input = ""
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "db_error" not in st.session_state:
    st.session_state.db_error = None
def fill_demo(email):
    st.session_state.email_input = email
    for e, s, *_ in SEED_USERS:
        if e == email:
            st.session_state.senha_input = s


def quick_login(email):
    """Callback usado pelos botões de demonstração (roda antes do rerun,
    então pode alterar email_input/senha_input sem erro do Streamlit)."""
    fill_demo(email)
    do_login()


def do_login():
    try:
        row = autenticar(st.session_state.email_input, st.session_state.senha_input)
        if row:
            st.session_state.logged_in = True
            st.session_state.user_data = row
            st.session_state.login_error = False
        else:
            st.session_state.login_error = True
    except Exception as e:
        st.session_state.db_error = str(e)


# ------------------------------------------------------------------
# CSS — painel azul + painel branco, no estilo do mock
# ------------------------------------------------------------------
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding: 0 !important; max-width: 100% !important;}
.stApp {background: #ffffff;}
.blue-panel {
    background: linear-gradient(160deg, #1e3a8a 0%, #2563eb 55%, #3b82f6 100%);
    background-image: radial-gradient(circle, rgba(255,255,255,0.12) 1px, transparent 1px),
        linear-gradient(160deg, #1e3a8a 0%, #2563eb 55%, #3b82f6 100%);
    background-size: 22px 22px, cover;
    border-radius: 18px; padding: 48px 40px; height: 820px; color: white;
    display: flex; flex-direction: column; justify-content: space-between;
}
.brand-box {display: flex; align-items: center; gap: 12px;}
.brand-icon {background: rgba(255,255,255,0.18); border-radius: 12px; width: 46px; height: 46px;
    display: flex; align-items: center; justify-content: center; font-size: 22px;}
.brand-title {font-weight: 800; font-size: 18px; line-height: 1.1;}
.brand-sub {font-size: 12px; opacity: 0.8;}
.hero-title {font-size: 40px; font-weight: 800; line-height: 1.15; margin-top: 30px;}
.hero-desc {font-size: 14px; opacity: 0.85; margin-top: 14px; max-width: 460px; line-height: 1.5;}
.stats-row {display: flex; gap: 14px; margin-top: 34px;}
.stat-card {background: rgba(255,255,255,0.10); border-radius: 10px; padding: 14px 18px; flex: 1;}
.stat-num {font-size: 22px; font-weight: 800;}
.stat-label {font-size: 11px; opacity: 0.75;}
.maint-strip {margin-top: 28px; background: rgba(255,255,255,0.08); border: 1px dashed rgba(255,255,255,0.35);
    border-radius: 10px; padding: 14px 16px; font-size: 12.5px; display: flex; align-items: center; gap: 10px;}
.db-strip {margin-top: 10px; font-size: 11.5px; display: flex; align-items: center; gap: 8px; opacity: 0.85;}
.footer-note {font-size: 11.5px; opacity: 0.75; display: flex; align-items: center; gap: 6px;}
.white-panel {padding: 90px 60px;}
.login-title {font-size: 30px; font-weight: 800; color: #0f172a;}
.login-sub {color: #64748b; font-size: 14px; margin-bottom: 26px;}
div[data-testid="stTextInput"] input {border-radius: 8px !important; border: 1px solid #cbd5e1 !important; padding: 10px 12px !important;}
.stButton>button {width: 100%; border-radius: 8px; font-weight: 600;}
.entrar-btn button {background: #2563eb; color: white; border: none; padding: 10px 0;}
.entrar-btn button:hover {background: #1d4ed8; color: white;}
.demo-label {font-size: 11.5px; letter-spacing: 0.05em; color: #64748b; margin: 22px 0 10px 0;}
.demo-btn button {background: white; border: 1px solid #e2e8f0; text-align: left; padding: 10px 12px; color: #0f172a;}
.demo-btn button:hover {border-color: #2563eb; color: #2563eb;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# LOGADO
# ------------------------------------------------------------------
if st.session_state.logged_in:
    u = st.session_state.user_data
    
    # 1. 'nome_usuario' está correto!
    st.markdown(f"### ✅ Bem-vindo(a), {u['nome_usuario']}!")
    
    # 2. Corrigido para 'email_usuario'
    st.write(f"**E-mail:** {u['email_usuario']}")
    
    # 3. Corrigido para 'cargo_usuario'
    st.write(f"**Cargo aplicado:** `{u['cargo_usuario']}`")
    
    # 4. Tratamento seguro para 'permissoes' (já que a coluna não existe na tabela)
    # Usamos .get() com um valor padrão caso a chave não exista no dicionário
    permissoes = u.get('permissoes', 'Visualização Padrão')
    st.write(f"**Permissões:** {permissoes}")
    
    st.caption("Dados lidos em tempo real da tabela `Usuarios` no banco Manutencao (Aiven).")

    # 5. Ajustado para validar contra os cargos reais do seu ENUM (Administrador e Supervisor/Auditor)
    # Se você tiver um cargo específico para Auditor, adicione-o na tupla abaixo:
    if u["cargo_usuario"] in ("Administrador", "Supervisor"):
        with st.expander("📋 Últimos acessos registrados (Logs_Acesso)"):
            try:
                logs = buscar_ultimos_acessos(10)
                if logs:
                    st.table(logs)
                else:
                    st.info("Nenhum acesso registrado ainda.")
            except Exception as e:
                st.error(f"Não foi possível carregar os logs: {e}")

    if st.button("Sair"):
        st.session_state.logged_in = False
        st.session_state.user_data = None
        st.rerun()
    st.stop()

# ------------------------------------------------------------------
# TELA DE LOGIN
# ------------------------------------------------------------------
col_left, col_right = st.columns([1.05, 1], gap="large")

with col_left:
    st.markdown(f"""
    <div class="blue-panel">
        <div class="brand-box">
            <div class="brand-icon">🔧</div>
            <div>
                <div class="brand-title">THAF Manutenção</div>
                <div class="brand-sub">Gestão Industrial Corporativa</div>
            </div>
        </div>
        <div>
            <div class="hero-title">Controle total da<br>manutenção<br>industrial.</div>
            <div class="hero-desc">
                Ordens de serviço, máquinas, almoxarifado, ferramentas e matriz
                de risco EPI — unificados em uma única plataforma com controle
                de acesso por perfil.
            </div>
            <div class="stats-row">
                <div class="stat-card"><div class="stat-num">142</div><div class="stat-label">Máquinas</div></div>
                <div class="stat-card"><div class="stat-num">38</div><div class="stat-label">OS em aberto</div></div>
                <div class="stat-card"><div class="stat-num">99.2%</div><div class="stat-label">Disponibilidade</div></div>
            </div>
            <div class="maint-strip">🛠️ Próxima manutenção preventiva: <b>Torno CNC-04</b> em 3 dias</div>
            <div class="db-strip">{"🟢 Conectado ao banco Manutencao" if not st.session_state.db_error else "🔴 Falha ao conectar ao banco — veja detalhes ao lado"}</div>
        </div>
        <div class="footer-note">🛡️ Acesso segmentado por Roles (Admin, Supervisor, Técnico, Auditor)</div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="white-panel">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Acesse sua conta</div>', unsafe_allow_html=True)

    # ---- BOTÃO DE INICIALIZAÇÃO CORRIGIDO PARA A SUA TABELA ----
    if st.button("✨ Inicializar Usuários de Teste no Banco"):
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                # Lista de usuários adaptada às colunas e ENUMs da sua tabela
                usuarios_teste = [
                    ('Tauani Abreu', 'tauani@thaf.com', 'tauani123', 'Administrador', '(11) 99999-0001'),
                    ('Felipe Silva', 'felipe@thaf.com', 'felipe123', 'Supervisor', '(11) 99999-0002'),
                    ('Ana Clara', 'ana@thaf.com', 'ana123', 'Tecnico', '(11) 99999-0003'),
                    ('Henrique Souza', 'henrique@thaf.com', 'henrique123', 'Supervisor', '(11) 99999-0004')
                ]
                
                for nome, email, senha_pura, cargo, telefone in usuarios_teste:
                    cur.execute("""
                        INSERT INTO Usuarios (nome_usuario, email_usuario, senha, cargo_usuario, telefone_usuario, status_usuario)
                        VALUES (%s, %s, %s, %s, %s, 'Ativo')
                        ON DUPLICATE KEY UPDATE 
                            nome_usuario = VALUES(nome_usuario),
                            senha = VALUES(senha),
                            cargo_usuario = VALUES(cargo_usuario),
                            telefone_usuario = VALUES(telefone_usuario),
                            status_usuario = 'Ativo'
                    """, (nome, email, hash_senha(senha_pura), cargo, telefone))
            st.success("Usuários cadastrados com sucesso na Aiven! Agora o login vai funcionar.")
        except Exception as e:
            st.error(f"Erro ao cadastrar usuários: {e}")
    # -----------------------------------------------------------

    st.markdown('<div class="login-sub">Entre com suas credenciais corporativas para continuar.</div>', unsafe_allow_html=True)

    if st.session_state.db_error:
        st.error(f"Não foi possível conectar ao banco:\n\n{st.session_state.db_error}")

    st.text_input("E-mail", key="email_input", placeholder="nome@thaf.com")
    st.text_input("Senha", key="senha_input", type="password", placeholder="••••••••")

    if st.session_state.get("login_error"):
        st.error("E-mail ou senha inválidos.")
        st.session_state.login_error = False

    st.markdown('<div class="entrar-btn">', unsafe_allow_html=True)
    st.button("→  Entrar", on_click=do_login)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="demo-label">ACESSO RÁPIDO DE DEMONSTRAÇÃO</div>', unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown('<div class="demo-btn">', unsafe_allow_html=True)
        st.button("Administrador\ntauani@thaf.com", key="btn_admin",
                  on_click=quick_login, args=("tauani@thaf.com",))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="demo-btn">', unsafe_allow_html=True)
        st.button("Técnico\nana@thaf.com", key="btn_tec",
                  on_click=quick_login, args=("ana@thaf.com",))
        st.markdown('</div>', unsafe_allow_html=True)

    with d2:
        st.markdown('<div class="demo-btn">', unsafe_allow_html=True)
        st.button("Supervisor\nfelipe@thaf.com", key="btn_sup",
                  on_click=quick_login, args=("felipe@thaf.com",))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="demo-btn">', unsafe_allow_html=True)
        st.button("Auditor\nhenrique@thaf.com", key="btn_aud",
                  on_click=quick_login, args=("henrique@thaf.com",))
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.logged_in:
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
