import hashlib
import textwrap
from datetime import datetime
from zoneinfo import ZoneInfo
import pymysql
import streamlit as st

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")


def agora_brasil():
    """Retorna o horário atual no fuso de Brasília, independente do fuso do servidor de banco."""
    return datetime.now(FUSO_BRASIL).replace(tzinfo=None)

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

# Usuários REAIS da tabela Usuarios (existem de fato no banco, via inserts.sql),
# usados apenas para preencher os campos de e-mail/senha dos botões de acesso
# rápido. Nenhum usuário é criado por aqui — o login sempre consulta a tabela
# Usuarios já existente.
ACESSO_RAPIDO_USERS = [
    ("CEO", "tauani@empresa.com", "kL9vN2mX7pQ4wE1b"),
    ("Gerente", "henrique@empresa.com", "B4vN1mK8pL6qW3xC"),
    ("Supervisor", "carlos.silva@empresa.com", "mX3pL8vN5qW1bC7z"),
    ("Técnico", "mariana.costa@empresa.com", "H6nC2mX9pL4vN8qW"),
]


def hash_senha(senha: str) -> str:
    # ATENÇÃO: o banco foi populado usando a função SHA() do MySQL, que gera
    # um hash SHA-1 (não SHA-256). Por isso usamos sha1 aqui — precisa bater
    # exatamente com o que está gravado na coluna Usuarios.senha.
    # SHA-1 sem "salt" é criptograficamente fraco; se possível, migre para
    # bcrypt/argon2 futuramente e regrave as senhas de todos os usuários.
    return hashlib.sha1(senha.encode("utf-8")).hexdigest()


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
                    (id_usuario, agora_brasil(), acao, get_client_ip(), sucesso),
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
        return row

    return None


def buscar_ultimos_acessos(limit: int = 5):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
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
# Ordens de Serviço — schema real da tabela (confirmado pelo usuário):
# Ordens_Servico(id_os, tag_equipamento, descricao_falha, data_abertura,
#                 hh_inicio, hh_fim, status_os, id_usuario)
# Não existem colunas de Prioridade/Progresso/Custo — a tela usa só
# o que está de fato na tabela.
# ------------------------------------------------------------------
STATUS_OS_OPCOES = ["Aberto", "Em andamento", "Concluído"]


def listar_tecnicos():
    """Usuários com cargo Tecnico e status Ativo, para o seletor de responsável."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id_usuario, nome_usuario FROM Usuarios "
                "WHERE cargo_usuario = 'Tecnico' AND status_usuario = 'Ativo' "
                "ORDER BY nome_usuario"
            )
            return cur.fetchall()
    finally:
        conn.close()


def listar_ordens_servico(busca: str = ""):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT os.id_os, os.tag_equipamento, os.descricao_falha, os.data_abertura,
                       os.hh_inicio, os.hh_fim, os.status_os, os.id_usuario,
                       u.nome_usuario AS tecnico
                FROM Ordens_Servico os
                LEFT JOIN Usuarios u ON u.id_usuario = os.id_usuario
            """
            params = ()
            if busca:
                sql += " WHERE os.tag_equipamento LIKE %s OR os.descricao_falha LIKE %s OR u.nome_usuario LIKE %s"
                like = f"%{busca}%"
                params = (like, like, like)
            sql += " ORDER BY os.data_abertura DESC, os.id_os DESC"
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def criar_os(tag_equipamento, descricao_falha, data_abertura, hh_inicio, hh_fim, status_os, id_usuario):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Ordens_Servico
                    (tag_equipamento, descricao_falha, data_abertura, hh_inicio, hh_fim, status_os, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (tag_equipamento, descricao_falha, data_abertura, hh_inicio, hh_fim, status_os, id_usuario))
            return cur.lastrowid
    finally:
        conn.close()


def atualizar_os(id_os, tag_equipamento, descricao_falha, data_abertura, hh_inicio, hh_fim, status_os, id_usuario):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Ordens_Servico
                SET tag_equipamento = %s, descricao_falha = %s, data_abertura = %s,
                    hh_inicio = %s, hh_fim = %s, status_os = %s, id_usuario = %s
                WHERE id_os = %s
            """, (tag_equipamento, descricao_falha, data_abertura, hh_inicio, hh_fim, status_os, id_usuario, id_os))
    finally:
        conn.close()


def excluir_os(id_os):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Ordens_Servico WHERE id_os = %s", (id_os,))
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
if "pagina" not in st.session_state:
    st.session_state.pagina = "ordens_servico"
if "os_busca" not in st.session_state:
    st.session_state.os_busca = ""
if "os_confirmar_exclusao" not in st.session_state:
    st.session_state.os_confirmar_exclusao = None


def fill_demo(email, senha):
    st.session_state.email_input = email
    st.session_state.senha_input = senha


def quick_login(email, senha):
    """Callback usado pelos botões de acesso rápido (roda antes do rerun,
    então pode alterar email_input/senha_input sem erro do Streamlit)."""
    fill_demo(email, senha)
    do_login()


def do_login():
    """Autentica o usuário e SEMPRE registra a tentativa em Logs_Acesso,
    tanto em caso de sucesso quanto de falha."""
    email_tentativa = st.session_state.email_input.strip().lower()
    try:
        row = autenticar(st.session_state.email_input, st.session_state.senha_input)
        if row:
            st.session_state.logged_in = True
            st.session_state.user_data = row
            st.session_state.login_error = False
            # Log de sucesso: já temos o id_usuario real
            log_acesso(row["id_usuario"], "Login", True)
        else:
            st.session_state.login_error = True
            # Log de falha: não sabemos o id_usuario (pode nem existir),
            # então registramos None e deixamos o e-mail digitado na ação,
            # para permitir auditoria de tentativas de acesso.
            log_acesso(None, f"Login falhou (email: {email_tentativa})", False)
    except Exception as e:
        st.session_state.db_error = str(e)
        # Mesmo com erro de conexão/consulta, tenta registrar a tentativa
        log_acesso(None, f"Login com erro (email: {email_tentativa})", False)


def do_logout():
    """Registra o logout em Logs_Acesso antes de encerrar a sessão."""
    u = st.session_state.user_data
    if u:
        log_acesso(u["id_usuario"], "Logout", True)
    st.session_state.logged_in = False
    st.session_state.user_data = None


def ir_para(pagina: str):
    st.session_state.pagina = pagina


def status_slug(status: str) -> str:
    return (
        status.strip().lower()
        .replace("ê", "e").replace("é", "e").replace("í", "i").replace("ó", "o")
        .replace(" ", "-")
    )


@st.dialog("Nova Ordem de Serviço")
def dialog_nova_os():
    try:
        tecnicos = listar_tecnicos()
    except Exception as e:
        st.error(f"Não foi possível carregar os técnicos: {e}")
        return

    tag = st.text_input("Tag do equipamento", placeholder="Ex: TCV-002")
    desc = st.text_area("Descrição da falha")
    c1, c2, c3 = st.columns(3)
    with c1:
        data_abertura = st.date_input("Data de abertura")
    with c2:
        hh_inicio = st.time_input("Início")
    with c3:
        hh_fim = st.time_input("Fim")
    status = st.selectbox("Status", STATUS_OS_OPCOES)

    mapa_tecnicos = {t["nome_usuario"]: t["id_usuario"] for t in tecnicos}
    if not mapa_tecnicos:
        st.warning("Nenhum técnico ativo encontrado na tabela Usuarios.")
    tecnico_nome = st.selectbox("Técnico responsável", list(mapa_tecnicos.keys())) if mapa_tecnicos else None

    if st.button("Salvar OS", type="primary"):
        if not tag or not desc or not tecnico_nome:
            st.error("Preencha equipamento, descrição e técnico responsável.")
        else:
            try:
                criar_os(tag, desc, data_abertura, hh_inicio, hh_fim, status, mapa_tecnicos[tecnico_nome])
                st.success("OS criada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar no banco: {e}")


@st.dialog("Editar Ordem de Serviço")
def dialog_editar_os(row):
    try:
        tecnicos = listar_tecnicos()
    except Exception as e:
        st.error(f"Não foi possível carregar os técnicos: {e}")
        return

    tag = st.text_input("Tag do equipamento", value=row["tag_equipamento"])
    desc = st.text_area("Descrição da falha", value=row["descricao_falha"])
    c1, c2, c3 = st.columns(3)
    with c1:
        data_abertura = st.date_input("Data de abertura", value=row["data_abertura"])
    with c2:
        hh_inicio = st.time_input("Início", value=row["hh_inicio"])
    with c3:
        hh_fim = st.time_input("Fim", value=row["hh_fim"])
    status = st.selectbox("Status", STATUS_OS_OPCOES, index=STATUS_OS_OPCOES.index(row["status_os"]))

    mapa_tecnicos = {t["nome_usuario"]: t["id_usuario"] for t in tecnicos}
    nomes = list(mapa_tecnicos.keys())
    tecnico_atual = row.get("tecnico")
    idx_atual = nomes.index(tecnico_atual) if tecnico_atual in nomes else 0
    tecnico_nome = st.selectbox("Técnico responsável", nomes, index=idx_atual) if nomes else None

    if st.button("Salvar alterações", type="primary"):
        try:
            atualizar_os(row["id_os"], tag, desc, data_abertura, hh_inicio, hh_fim, status, mapa_tecnicos[tecnico_nome])
            st.success("OS atualizada com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar no banco: {e}")


# ------------------------------------------------------------------
# CSS — todas as classes abaixo batem 1:1 com o HTML usado mais adiante.
# Nada de classes "órfãs" (definidas mas não usadas) nem "fantasmas"
# (usadas no markdown mas ausentes aqui) — foi isso que quebrou o layout.
# ------------------------------------------------------------------
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
html, body {margin: 0; padding: 0;}
.block-container {padding: 0 !important; max-width: 100% !important;}
.stApp {background: #1e3a8a;}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {padding: 0 !important;}

/* ---------- PAINEL ÚNICO, TUDO AZUL, TELA INTEIRA ----------
   Sem cantos arredondados nem respiro externo: o painel preenche
   o viewport de ponta a ponta. */
.st-key-unified_panel {
    background: linear-gradient(160deg, #1e3a8a 0%, #2563eb 55%, #3b82f6 100%);
    background-image: radial-gradient(circle, rgba(255,255,255,0.12) 1px, transparent 1px),
        linear-gradient(160deg, #1e3a8a 0%, #2563eb 55%, #3b82f6 100%);
    background-size: 22px 22px, cover;
    border-radius: 0;
    padding: 60px 64px;
    min-height: 100vh;
    color: white;
}
.brand-box {display: flex; align-items: center; gap: 12px;}
.brand-icon {
    background: rgba(255,255,255,0.18);
    border-radius: 12px;
    width: 46px; height: 46px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
}
.brand-title {font-weight: 800; font-size: 18px; line-height: 1.1;}
.brand-sub {font-size: 12px; opacity: 0.8;}

.hero-image-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
}
.hero-image-wrap svg {max-width: 460px; width: 100%; height: auto;}

/* ---------- METADE DE LOGIN (dentro do mesmo painel azul) ---------- */
.st-key-login_card {
    padding-left: 24px;
}
.login-title {font-size: 28px; font-weight: 800; color: #ffffff;}
.login-sub {color: rgba(255,255,255,0.75); font-size: 13.5px; margin-bottom: 24px;}

/* rótulos "E-mail"/"Senha" do st.text_input, em branco no fundo azul */
div[data-testid="stTextInput"] label p {color: rgba(255,255,255,0.85) !important;}

div[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    background: rgba(255,255,255,0.92) !important;
    color: #0f172a !important;
    padding: 10px 12px !important;
}
div[data-testid="stTextInput"] input::placeholder {color: #64748b !important;}

.stButton>button {width: 100%; border-radius: 8px; font-weight: 600;}

.st-key-entrar_btn_wrap button {background: #ffffff; color: #1e3a8a; border: none; padding: 10px 0; font-weight: 700;}
.st-key-entrar_btn_wrap button:hover {background: #e2e8f0; color: #1e3a8a;}

.demo-label {font-size: 11.5px; letter-spacing: 0.05em; color: rgba(255,255,255,0.65); margin: 22px 0 10px 0;}
.st-key-demo_0 button, .st-key-demo_1 button,
.st-key-demo_2 button, .st-key-demo_3 button {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.3);
    text-align: left; padding: 10px 12px;
    color: #ffffff;
}
.st-key-demo_0 button:hover, .st-key-demo_1 button:hover,
.st-key-demo_2 button:hover, .st-key-demo_3 button:hover {
    border-color: #ffffff; background: rgba(255,255,255,0.18);
}

/* ================================================================
   PÓS-LOGIN: sidebar + tela de Ordens de Serviço
   ================================================================ */
.stApp {background: #f1f5f9;}

.st-key-sidebar {
    background: #0f172a;
    min-height: 100vh;
    padding: 24px 16px;
    color: white;
}
.sidebar-brand {display: flex; align-items: center; gap: 10px; padding: 0 8px 20px 8px;}
.sidebar-brand-icon {
    background: #2563eb; border-radius: 10px; width: 38px; height: 38px;
    display: flex; align-items: center; justify-content: center; font-size: 17px;
}
.sidebar-brand-title {font-weight: 800; font-size: 14.5px; color: white; line-height: 1.1;}
.sidebar-brand-sub {font-size: 10.5px; color: rgba(255,255,255,0.55);}
.sidebar-section-label {
    font-size: 10.5px; letter-spacing: 0.06em; color: rgba(255,255,255,0.45);
    text-transform: uppercase; margin: 14px 8px 6px 8px;
}
.st-key-sidebar .stButton>button {
    background: transparent; color: rgba(255,255,255,0.75); border: none;
    text-align: left; font-weight: 500; font-size: 13.5px; padding: 8px 10px;
    border-radius: 8px;
}
.st-key-sidebar .stButton>button:hover {background: rgba(255,255,255,0.08); color: white;}

.topbar-title {font-size: 22px; font-weight: 800; color: #0f172a;}
.topbar-breadcrumb {font-size: 12.5px; color: #94a3b8; margin-bottom: 2px;}
.topbar-sub {color: #64748b; font-size: 13.5px; margin: 4px 0 18px 0;}

.status-badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11.5px; font-weight: 700;
}
.status-aberto {background: #fee2e2; color: #b91c1c;}
.status-em-andamento {background: #dbeafe; color: #1d4ed8;}
.status-concluido {background: #dcfce7; color: #15803d;}

.os-row {border-bottom: 1px solid #e2e8f0; padding: 10px 0;}
.os-header {font-size: 11.5px; letter-spacing: 0.04em; color: #94a3b8; text-transform: uppercase; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;}
.os-cell {font-size: 13.5px; color: #0f172a;}
.os-cell-muted {font-size: 12px; color: #64748b;}

.st-key-topbar_search input {
    border-radius: 8px !important; border: 1px solid #e2e8f0 !important;
}
.st-key-nova_os_btn button {background: #2563eb; color: white; border: none; font-weight: 700;}
.st-key-nova_os_btn button:hover {background: #1d4ed8; color: white;}
.st-key-logout_btn button {background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# LOGADO — sidebar + telas internas
# ------------------------------------------------------------------
if st.session_state.logged_in:
    u = st.session_state.user_data

    MENU_ITEMS = [
        ("dashboard", "📊 Dashboard"),
        ("ordens_servico", "🧾 Ordens de Serviço"),
        ("agenda", "📅 Agenda"),
        ("maquinas", "⚙️ Máquinas"),
        ("almoxarifado", "📦 Almoxarifado – Peças"),
        ("ferramentas", "🔧 Ferramentas"),
        ("matriz_risco", "🛡️ Matriz de Risco / EPI"),
        ("relatorios", "📈 Relatórios"),
        ("usuarios", "👤 Usuários"),
        ("setores", "🏭 Setores"),
    ]

    col_side, col_main = st.columns([1, 4], gap="large")

    with col_side:
        with st.container(key="sidebar"):
            st.markdown("""
<div class="sidebar-brand">
<div class="sidebar-brand-icon">🔧</div>
<div>
<div class="sidebar-brand-title">THAF Manutenção</div>
<div class="sidebar-brand-sub">Gestão Industrial</div>
</div>
</div>
""", unsafe_allow_html=True)

            st.markdown('<div class="sidebar-section-label">Operação</div>', unsafe_allow_html=True)
            for chave, rotulo in MENU_ITEMS:
                st.button(rotulo, key=f"nav_{chave}", on_click=ir_para, args=(chave,), use_container_width=True)

            st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
            with st.container(key="logout_btn"):
                if st.button("Sair", use_container_width=True):
                    do_logout()
                    st.rerun()

    with col_main:
        top1, top2 = st.columns([2, 1])
        with top1:
            st.markdown('<div class="topbar-breadcrumb">Manutenção / Ordens de Serviço</div>', unsafe_allow_html=True)
            st.markdown('<div class="topbar-title">Ordens de Serviço</div>', unsafe_allow_html=True)
        with top2:
            st.markdown(
                f'<div style="text-align:right; font-size:13px; color:#0f172a;">'
                f'<b>{u["nome_usuario"]}</b><br>'
                f'<span style="color:#64748b; font-size:11.5px;">{u["cargo_usuario"]}</span></div>',
                unsafe_allow_html=True,
            )

        if st.session_state.pagina != "ordens_servico":
            st.markdown('<div class="topbar-sub">Esta página ainda não foi implementada.</div>', unsafe_allow_html=True)
            st.info("Em construção — por enquanto só a tela de Ordens de Serviço está conectada ao banco.")
            st.stop()

        st.markdown(
            '<div class="topbar-sub">Registro completo das intervenções — preventivas, corretivas e preditivas.</div>',
            unsafe_allow_html=True,
        )

        busca_col, botao_col = st.columns([3, 1])
        with busca_col:
            with st.container(key="topbar_search"):
                st.text_input(
                    "Buscar",
                    key="os_busca",
                    placeholder="Buscar OS, equipamento, técnico...",
                    label_visibility="collapsed",
                )
        with botao_col:
            with st.container(key="nova_os_btn"):
                if st.button("+ Nova OS", use_container_width=True):
                    dialog_nova_os()

        try:
            ordens = listar_ordens_servico(st.session_state.os_busca)
        except Exception as e:
            st.error(f"Não foi possível carregar as Ordens de Serviço: {e}")
            ordens = []

        st.markdown("<br>", unsafe_allow_html=True)

        if not ordens:
            st.info("Nenhuma Ordem de Serviço encontrada.")
        else:
            h1, h2, h3, h4, h5, h6, h7 = st.columns([0.6, 1, 2.4, 1.3, 1.2, 1, 0.8])
            for col, texto in zip((h1, h2, h3, h4, h5, h6, h7),
                                   ("OS", "Equipamento", "Descrição", "Abertura", "Técnico", "Status", "Ações")):
                col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

            for row in ordens:
                with st.container(key=f"os_row_{row['id_os']}"):
                    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.6, 1, 2.4, 1.3, 1.2, 1, 0.8])
                    c1.markdown(f'<div class="os-cell">#{row["id_os"]}</div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="os-cell"><b>{row["tag_equipamento"]}</b></div>', unsafe_allow_html=True)
                    c3.markdown(f'<div class="os-cell">{row["descricao_falha"]}</div>', unsafe_allow_html=True)
                    c4.markdown(
                        f'<div class="os-cell">{row["data_abertura"]}</div>'
                        f'<div class="os-cell-muted">{row["hh_inicio"]} → {row["hh_fim"] or "—"}</div>',
                        unsafe_allow_html=True,
                    )
                    c5.markdown(f'<div class="os-cell">{row["tecnico"] or "—"}</div>', unsafe_allow_html=True)
                    slug = status_slug(row["status_os"])
                    c6.markdown(f'<span class="status-badge status-{slug}">{row["status_os"]}</span>', unsafe_allow_html=True)

                    with c7:
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("✏️", key=f"editar_{row['id_os']}"):
                                dialog_editar_os(row)
                        with b2:
                            if st.button("🗑️", key=f"excluir_{row['id_os']}"):
                                st.session_state.os_confirmar_exclusao = row["id_os"]

                    if st.session_state.os_confirmar_exclusao == row["id_os"]:
                        st.warning(f"Excluir a OS #{row['id_os']} permanentemente?")
                        cc1, cc2 = st.columns(2)
                        with cc1:
                            if st.button("Sim, excluir", key=f"confirma_excluir_{row['id_os']}", type="primary"):
                                try:
                                    excluir_os(row["id_os"])
                                    st.session_state.os_confirmar_exclusao = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir: {e}")
                        with cc2:
                            if st.button("Cancelar", key=f"cancela_excluir_{row['id_os']}"):
                                st.session_state.os_confirmar_exclusao = None
                                st.rerun()

    st.stop()

# ------------------------------------------------------------------
# TELA DE LOGIN
# ------------------------------------------------------------------
with st.container(key="unified_panel"):
    col_left, col_right = st.columns([1.05, 1], gap="large")

    with col_left:
        hero_svg = textwrap.dedent("""\
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; min-height:520px;">
        <div class="brand-icon" style="width:64px; height:64px; font-size:30px; margin-bottom:36px;">🔧</div>
        <div class="hero-image-wrap">
        <svg viewBox="0 0 480 380" xmlns="http://www.w3.org/2000/svg">
        <circle cx="240" cy="190" r="170" fill="rgba(255,255,255,0.06)"/>
        <circle cx="240" cy="190" r="128" fill="rgba(255,255,255,0.05)"/>
        <g transform="translate(150,110)">
        <path fill="rgba(255,255,255,0.85)" d="M60 0 l10 18 a58 58 0 0 1 20 8 l19 -8 l14 14 l-8 19 a58 58 0 0 1 8 20 l18 10 v20 l-18 10 a58 58 0 0 1 -8 20 l8 19 l-14 14 l-19 -8 a58 58 0 0 1 -20 8 l-10 18 h-20 l-10 -18 a58 58 0 0 1 -20 -8 l-19 8 l-14 -14 l8 -19 a58 58 0 0 1 -8 -20 l-18 -10 v-20 l18 -10 a58 58 0 0 1 8 -20 l-8 -19 l14 -14 l19 8 a58 58 0 0 1 20 -8 z"/>
        <circle cx="50" cy="60" r="26" fill="#2563eb"/>
        </g>
        <g transform="translate(280,205)">
        <path fill="rgba(255,255,255,0.55)" d="M36 0 l6 11 a35 35 0 0 1 12 5 l12 -5 l8 8 l-5 12 a35 35 0 0 1 5 12 l11 6 v12 l-11 6 a35 35 0 0 1 -5 12 l5 12 l-8 8 l-12 -5 a35 35 0 0 1 -12 5 l-6 11 h-12 l-6 -11 a35 35 0 0 1 -12 -5 l-12 5 l-8 -8 l5 -12 a35 35 0 0 1 -5 -12 l-11 -6 v-12 l11 -6 a35 35 0 0 1 5 -12 l-5 -12 l8 -8 l12 5 a35 35 0 0 1 12 -5 z"/>
        <circle cx="30" cy="36" r="15" fill="#1e3a8a"/>
        </g>
        <g transform="translate(95,235) rotate(-35)">
        <rect x="0" y="0" width="14" height="90" rx="4" fill="rgba(255,255,255,0.9)"/>
        <rect x="-6" y="-26" width="26" height="30" rx="6" fill="rgba(255,255,255,0.9)"/>
        </g>
        <g transform="translate(325,110)">
        <circle cx="0" cy="0" r="22" fill="#22c55e"/>
        <path d="M-9 0 l6 7 l13 -15" stroke="white" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        </svg>
        </div>
        </div>
        """)
        st.markdown(hero_svg, unsafe_allow_html=True)

    with col_right:
        with st.container(key="login_card"):
            st.markdown('<div class="login-title">Acesse sua conta</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-sub">Entre com suas credenciais corporativas para continuar.</div>', unsafe_allow_html=True)

            if st.session_state.db_error:
                st.error(f"Não foi possível conectar ao banco:\n\n{st.session_state.db_error}")

            st.text_input("E-mail", key="email_input", placeholder="nome@empresa.com")
            st.text_input("Senha", key="senha_input", type="password", placeholder="••••••••")

            if st.session_state.get("login_error"):
                st.error("E-mail ou senha inválidos.")
                st.session_state.login_error = False

            with st.container(key="entrar_btn_wrap"):
                st.button("→  Entrar", on_click=do_login)

            st.markdown('<div class="demo-label">ACESSO RÁPIDO (USUÁRIOS REAIS)</div>', unsafe_allow_html=True)

            d1, d2 = st.columns(2)
            colunas = [d1, d2, d1, d2]
            for idx, (cargo, email, senha) in enumerate(ACESSO_RAPIDO_USERS):
                with colunas[idx]:
                    with st.container(key=f"demo_{idx}"):
                        st.button(f"{cargo}\n{email}", key=f"btn_demo_{idx}",
                                  on_click=quick_login, args=(email, senha))

            if st.session_state.logged_in:
                st.rerun()