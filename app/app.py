import hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
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
    return hashlib.sha1(senha.encode("utf-8")).hexdigest()


def get_connection():
    return pymysql.connect(
        host=DB_CONF["host"],
        port=int(DB_CONF["port"]),
        user=DB_CONF["user"],
        password=DB_CONF["password"],
        database=DB_CONF["database"],
        ssl={"ssl": {}},
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def get_client_ip() -> str:
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
        pass


def autenticar(email: str, senha: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Usuarios WHERE email_usuario = %s", (email.strip().lower(),))
            row = cur.fetchone()
    finally:
        conn.close()

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


STATUS_OS_OPCOES = ["Aberto", "Em andamento", "Concluído"]


def listar_tecnicos():
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


def listar_maquinas(busca: str = ""):
    """Lista as máquinas cadastradas, já com o modelo/fabricante (Modelos_Maquinas)
    e o setor (Setores) integrados via JOIN."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT m.tag_equipamento, m.numero_serie, m.localizacao_maquina,
                       m.tipo_manutencao_padrao, m.status_operacional, m.ultima_manutencao,
                       s.nome_setor,
                       mm.nome_maquina, mm.fabricante_maquina, mm.nome_modelo, mm.potencia_especificacao
                FROM Maquinas m
                JOIN Modelos_Maquinas mm ON mm.id_maquina = m.id_maquina
                JOIN Setores s ON s.id_setor = m.id_setor
            """
            params = ()
            if busca:
                sql += """
                    WHERE m.tag_equipamento LIKE %s OR mm.nome_maquina LIKE %s
                       OR mm.fabricante_maquina LIKE %s OR m.localizacao_maquina LIKE %s
                       OR s.nome_setor LIKE %s
                """
                like = f"%{busca}%"
                params = (like, like, like, like, like)
            sql += " ORDER BY m.tag_equipamento"
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def listar_setores():
    """Lista os setores com a contagem de máquinas e de usuários ativos vinculados a cada um."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.id_setor, s.nome_setor, s.descricao_setor,
                       (SELECT COUNT(*) FROM Maquinas m WHERE m.id_setor = s.id_setor) AS total_maquinas,
                       (SELECT COUNT(*) FROM Usuarios u
                         WHERE u.id_setor = s.id_setor AND u.status_usuario = 'Ativo') AS total_usuarios
                FROM Setores s
                ORDER BY s.nome_setor
            """)
            return cur.fetchall()
    finally:
        conn.close()


def listar_pecas(busca: str = ""):
    """Lista os itens do almoxarifado de peças, com filtro opcional por nome."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT id_peca, nome_peca, quantidade_estoque, unidade_medida, custo_unitario,
                       (quantidade_estoque * custo_unitario) AS valor_total
                FROM Almoxarifado_Pecas
            """
            params = ()
            if busca:
                sql += " WHERE nome_peca LIKE %s"
                params = (f"%{busca}%",)
            sql += " ORDER BY nome_peca"
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def listar_ferramentas(busca: str = ""):
    """Lista as ferramentas do almoxarifado, mostrando com quem está (quando em uso/atrasada/solicitada)
    a partir da movimentação mais recente em aberto (Movimentacao_Ferramentas + OS_Ferramentas)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT f.id_ferramenta, f.nome_ferramenta, f.status_ferramenta,
                    (SELECT u.nome_usuario
                       FROM Movimentacao_Ferramentas mv
                       JOIN OS_Ferramentas osf ON osf.id_os_ferramenta = mv.id_os_ferramenta
                       JOIN Usuarios u ON u.id_usuario = mv.id_usuario_solicitante
                      WHERE osf.id_ferramenta = f.id_ferramenta
                        AND mv.status_movimentacao IN ('Em Uso', 'Atrasado', 'Solicitado')
                      ORDER BY mv.data_retirada DESC LIMIT 1) AS com_quem,
                    (SELECT mv.data_devolucao_prevista
                       FROM Movimentacao_Ferramentas mv
                       JOIN OS_Ferramentas osf ON osf.id_os_ferramenta = mv.id_os_ferramenta
                      WHERE osf.id_ferramenta = f.id_ferramenta
                        AND mv.status_movimentacao IN ('Em Uso', 'Atrasado', 'Solicitado')
                      ORDER BY mv.data_retirada DESC LIMIT 1) AS devolucao_prevista
                FROM Almoxarifado_Ferramentas f
            """
            params = ()
            if busca:
                sql += " WHERE f.nome_ferramenta LIKE %s"
                params = (f"%{busca}%",)
            sql += " ORDER BY f.nome_ferramenta"
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def listar_riscos():
    """Lista a Matriz de Riscos (NR-01) / EPIs obrigatórios, com a contagem de OS
    em que cada risco foi associado (OS_Seguranca)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.id_risco, r.risco_nr01, r.epis_obrigatorios,
                       (SELECT COUNT(*) FROM OS_Seguranca os WHERE os.id_risco = r.id_risco) AS total_os
                FROM Matriz_Riscos_EPI r
                ORDER BY r.risco_nr01
            """)
            return cur.fetchall()
    finally:
        conn.close()


def listar_usuarios(busca: str = ""):
    """Lista os usuários com o nome do setor (JOIN com Setores)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT u.id_usuario, u.nome_usuario, u.email_usuario, u.cargo_usuario,
                       u.status_usuario, u.nivel_experiencia, u.disponibilidade_tecnico,
                       u.telefone_usuario, u.data_nasc_usuario, u.data_cadastro,
                       s.nome_setor
                FROM Usuarios u
                LEFT JOIN Setores s ON s.id_setor = u.id_setor
            """
            params = ()
            if busca:
                sql += """
                    WHERE u.nome_usuario LIKE %s OR u.email_usuario LIKE %s
                       OR u.cargo_usuario LIKE %s OR s.nome_setor LIKE %s
                """
                like = f"%{busca}%"
                params = (like, like, like, like)
            sql += " ORDER BY u.nome_usuario"
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
    fill_demo(email, senha)
    do_login()


def do_login():
    email_tentativa = st.session_state.email_input.strip().lower()
    try:
        row = autenticar(st.session_state.email_input, st.session_state.senha_input)
        if row:
            st.session_state.logged_in = True
            st.session_state.user_data = row
            st.session_state.login_error = False
            log_acesso(row["id_usuario"], "Login", True)
        else:
            st.session_state.login_error = True
            log_acesso(None, f"Login falhou (email: {email_tentativa})", False)
    except Exception as e:
        st.session_state.db_error = str(e)
        log_acesso(None, f"Login com erro (email: {email_tentativa})", False)


def do_logout():
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
        .replace("ã", "a").replace("ç", "c")
        .replace("/", "-").replace(" ", "-")
    )


# ------------------------------------------------------------------
# Paletas de cores por status, usadas nos gráficos Plotly (mesmas cores
# das badges de status já definidas em CSS, para manter consistência visual)
# ------------------------------------------------------------------
STATUS_OS_CORES = {"Aberto": "#dc2626", "Em andamento": "#2563eb", "Concluído": "#16a34a"}
STATUS_MAQUINA_CORES = {"Operando": "#16a34a", "Parado": "#dc2626", "Em Manutenção": "#2563eb"}
STATUS_FERRAMENTA_CORES = {
    "Disponível": "#16a34a",
    "Solicitada": "#a16207",
    "Em Uso": "#2563eb",
    "Manutenção/Calibração": "#6d28d9",
    "Extraviada": "#dc2626",
}
DISPONIBILIDADE_CORES = {
    "Disponível": "#16a34a",
    "Em Campo": "#2563eb",
    "Férias": "#a16207",
    "Afastado": "#dc2626",
}

_FONTE_GRAFICOS = dict(family="-apple-system, Segoe UI, Roboto, sans-serif", size=12.5, color="#334155")


def _formatar_rotulos(valores, moeda: bool):
    if moeda:
        return [
            f"R$ {v:,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")
            for v in valores
        ]
    return [f"{v:g}" for v in valores]


def grafico_barras(df, coluna, cores_mapa=None, cor_padrao="#2563eb", moeda=False, altura=280, horizontal=False):
    """Renderiza um gráfico de barras com Plotly a partir de um DataFrame cujo
    índice é a categoria e cuja coluna `coluna` traz o valor numérico. Substitui
    o st.bar_chart nativo por um visual mais rico (cores por status, rótulos,
    fundo transparente combinando com os cards do app)."""
    dados = df.reset_index()
    categoria_col = dados.columns[0]

    if horizontal:
        dados = dados.sort_values(coluna, ascending=True)

    rotulos = _formatar_rotulos(dados[coluna], moeda)
    cores = [cores_mapa.get(v, cor_padrao) for v in dados[categoria_col]] if cores_mapa else cor_padrao

    eixo_valor = dict(showgrid=True, gridcolor="#eef2f7", tickfont=dict(color="#64748b", size=11.5), zeroline=False)
    eixo_categoria = dict(showgrid=False, tickfont=dict(color="#64748b", size=11.5))

    if horizontal:
        fig = px.bar(dados, x=coluna, y=categoria_col, orientation="h")
        fig.update_traces(
            marker_color=cores, marker_line_width=0, text=rotulos, textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        )
        fig.update_layout(xaxis=eixo_valor, yaxis=eixo_categoria)
    else:
        fig = px.bar(dados, x=categoria_col, y=coluna)
        fig.update_traces(
            marker_color=cores, marker_line_width=0, text=rotulos, textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
        )
        fig.update_layout(xaxis=eixo_categoria, yaxis=eixo_valor)

    fig.update_layout(
        margin=dict(l=8, r=8, t=10, b=8),
        height=altura,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=_FONTE_GRAFICOS,
        showlegend=False,
        bargap=0.35,
        uniformtext_minsize=9,
        uniformtext_mode="hide",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def grafico_area(df, coluna, cor="#2563eb", altura=280):
    """Renderiza um gráfico de área/linha com Plotly para séries temporais
    (ex.: evolução mensal de Ordens de Serviço)."""
    dados = df.reset_index()
    categoria_col = dados.columns[0]

    fig = px.area(dados, x=categoria_col, y=coluna)
    fig.update_traces(
        line=dict(color=cor, width=2.5),
        fillcolor="rgba(37, 99, 235, 0.12)",
        mode="lines+markers",
        marker=dict(size=6, color=cor),
        hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=10, b=8),
        height=altura,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=_FONTE_GRAFICOS,
        xaxis=dict(showgrid=False, tickfont=dict(color="#64748b", size=11.5)),
        yaxis=dict(showgrid=True, gridcolor="#eef2f7", tickfont=dict(color="#64748b", size=11.5), zeroline=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


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


st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
html, body {margin: 0; padding: 0;}
.block-container {padding: 0 !important; max-width: 100% !important;}
.stApp {background: #0b1b3a;}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {padding: 0 !important;}

/* ======================================================================
   TELA DE LOGIN — estilo "foguete", tons de azul, tela inteira
   ====================================================================== */
.st-key-unified_panel {
    padding: 0;
    margin: 0;
    min-height: 100vh;
    display: grid !important;
    grid-template-columns: 48fr 52fr;
    align-items: stretch;
}
.st-key-unified_panel > div,
.st-key-unified_panel > div > div,
.st-key-unified_panel > div > div > div {
    height: 100%;
}

/* ---------- Painel esquerdo: decorativo, foguete, várias tonalidades de azul ---------- */
.st-key-rocket_panel {
    position: relative;
    overflow: hidden;
    min-height: 100vh;
    display: flex !important;
    flex-direction: column;
    justify-content: space-between;
    padding: 56px 48px;
    color: #ffffff;
    background:
        radial-gradient(circle at 12% 18%, rgba(255,255,255,0.14) 0 2px, transparent 2px),
        radial-gradient(circle at 42% 68%, rgba(255,255,255,0.10) 0 2px, transparent 2px),
        radial-gradient(circle at 72% 30%, rgba(255,255,255,0.14) 0 2px, transparent 2px),
        radial-gradient(circle at 85% 78%, rgba(255,255,255,0.10) 0 2px, transparent 2px),
        radial-gradient(circle at 25% 88%, rgba(255,255,255,0.10) 0 2px, transparent 2px),
        linear-gradient(150deg, #050e24 0%, #0c2a63 32%, #1d4ed8 62%, #38bdf8 100%);
    background-size: 60px 60px, 90px 90px, 70px 70px, 100px 100px, 80px 80px, cover;
}
.st-key-rocket_panel::before {
    content: "";
    position: absolute;
    top: -70px; right: -70px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
}
.st-key-rocket_panel::after {
    content: "";
    position: absolute;
    bottom: -90px; left: -50px;
    width: 240px; height: 240px;
    border-radius: 50%;
    background: rgba(56,189,248,0.30);
}
.rocket-mid-circle {
    position: absolute;
    top: 50%; left: 8%;
    transform: translateY(-50%);
    width: 26px; height: 26px;
    border-radius: 50%;
    background: rgba(255,255,255,0.18);
}

.brand-box {display: flex; align-items: center; gap: 14px; position: relative; z-index: 2;}
.brand-icon {
    background: rgba(255,255,255,0.18);
    border-radius: 16px;
    width: 56px; height: 56px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    flex-shrink: 0;
}
.brand-title {font-weight: 800; font-size: 21px; line-height: 1.1;}
.brand-sub {font-size: 13.5px; opacity: 0.8;}

.rocket-stage {
    position: relative;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
}
.rocket-ring {
    position: absolute;
    width: 320px; height: 320px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.18);
    background: rgba(255,255,255,0.04);
}
.smoke-cloud {
    position: absolute;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.40) 0%, rgba(255,255,255,0.08) 55%, transparent 72%);
    filter: blur(1px);
}
.rocket-emoji {
    position: relative;
    font-size: 128px;
    transform: rotate(-40deg);
    filter: drop-shadow(0 22px 22px rgba(2,6,23,0.55));
}

.rocket-tagline {
    position: relative;
    z-index: 2;
    font-size: 26px;
    font-weight: 800;
    line-height: 1.35;
    max-width: 380px;
}
.rocket-tagline span {
    display: block;
    font-size: 14.5px;
    font-weight: 400;
    color: rgba(255,255,255,0.75);
    margin-top: 10px;
}

/* ---------- Painel direito: cartão de login branco, cobrindo a tela toda ---------- */
.st-key-login_card {
    box-sizing: border-box;
    width: 100%;
    min-height: 100vh;
    padding: 72px 9vw;
    margin: 0;
    background: #ffffff;
    display: flex !important;
    flex-direction: column;
    justify-content: center;
}
.login-eyebrow {
    color: #2563eb;
    font-weight: 700;
    font-size: 12.5px;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.login-title {font-size: 40px; font-weight: 800; color: #0c1e3e; margin-bottom: 8px;}
.login-sub {color: #64748b; font-size: 15.5px; margin-bottom: 36px;}

div[data-testid="stTextInput"] label p {color: #334155 !important; font-size: 14.5px !important; font-weight: 600;}

div[data-testid="stTextInput"] input {
    border-radius: 999px !important;
    border: 1.5px solid #dbeafe !important;
    background: #f8fafc !important;
    color: #0c1e3e !important;
    padding: 16px 22px !important;
    font-size: 15.5px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.20) !important;
}
div[data-testid="stTextInput"] input::placeholder {color: #94a3b8 !important;}
div[data-testid="stTextInput"] {margin-bottom: 10px;}

.login-row {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 13.5px; color: #64748b; margin: 4px 4px 22px 4px;
}
.login-row .login-link {color: #2563eb; font-weight: 600; cursor: pointer;}

.stButton>button {width: 100%; border-radius: 999px; font-weight: 700; font-size: 16.5px;}

.st-key-entrar_btn_wrap button {
    background: linear-gradient(90deg, #1d4ed8 0%, #38bdf8 100%);
    color: #ffffff; border: none; padding: 17px 0; font-weight: 700; font-size: 16.5px;
    box-shadow: 0 12px 24px rgba(29,78,216,0.35);
}
.st-key-entrar_btn_wrap button:hover {filter: brightness(1.05);}

.demo-label {
    font-size: 12px; letter-spacing: 0.08em; color: #94a3b8;
    text-transform: uppercase; font-weight: 700; margin: 38px 0 14px 2px;
}
.st-key-demo_0 button, .st-key-demo_1 button,
.st-key-demo_2 button, .st-key-demo_3 button {
    background: #eff6ff;
    border: 1.5px solid #bfdbfe;
    border-radius: 14px;
    text-align: left; padding: 14px 16px;
    color: #1e3a8a;
    white-space: pre-line;
    font-size: 13.5px;
    font-weight: 600;
}
.st-key-demo_0 button:hover, .st-key-demo_1 button:hover,
.st-key-demo_2 button:hover, .st-key-demo_3 button:hover {
    border-color: #38bdf8; background: #dbeafe;
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

/* ---------- Tela de Máquinas: KPIs e gráficos ---------- */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 5px solid #2563eb;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 8px;
}
.kpi-card.kpi-green {border-left-color: #16a34a;}
.kpi-card.kpi-red {border-left-color: #dc2626;}
.kpi-card.kpi-blue {border-left-color: #0ea5e9;}
.kpi-value {font-size: 26px; font-weight: 800; color: #0f172a; line-height: 1.1;}
.kpi-label {font-size: 12.5px; color: #64748b; margin-top: 4px;}

.chart-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px 20px 6px 20px;
    margin-bottom: 16px;
}
.chart-title {font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 10px;}

.status-operando {background: #dcfce7; color: #15803d;}
.status-parado {background: #fee2e2; color: #b91c1c;}
.status-em-manutencao {background: #dbeafe; color: #1d4ed8;}

/* ---------- Tela de Setores ---------- */
.setor-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px 22px;
    height: 100%;
    box-sizing: border-box;
}
.setor-card-title {font-size: 16px; font-weight: 800; color: #0f172a; margin-bottom: 4px;}
.setor-card-desc {font-size: 12.5px; color: #64748b; margin-bottom: 16px; min-height: 32px;}
.setor-card-stats {display: flex; gap: 22px;}
.setor-stat-value {font-size: 22px; font-weight: 800; color: #2563eb; line-height: 1;}
.setor-stat-label {font-size: 11px; color: #94a3b8; margin-top: 3px;}

/* ---------- Tela de Almoxarifado — Peças ---------- */
.estoque-baixo {color: #b91c1c; font-weight: 700;}
.estoque-ok {color: #0f172a;}

/* ---------- Tela de Ferramentas ---------- */
.status-disponivel {background: #dcfce7; color: #15803d;}
.status-solicitada {background: #fef9c3; color: #a16207;}
.status-em-uso {background: #dbeafe; color: #1d4ed8;}
.status-manutencao-calibracao {background: #ede9fe; color: #6d28d9;}
.status-extraviada {background: #fee2e2; color: #b91c1c;}

/* ---------- Tela de Matriz de Risco / EPI ---------- */
.risco-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 5px solid #dc2626;
    border-radius: 14px;
    padding: 18px 20px;
    height: 100%;
    box-sizing: border-box;
}
.risco-card-title {font-size: 15px; font-weight: 800; color: #0f172a; margin-bottom: 8px;}
.risco-card-epis {font-size: 12.5px; color: #475569; line-height: 1.5; margin-bottom: 12px;}
.risco-card-tag {
    display: inline-block; font-size: 11px; font-weight: 700; color: #b91c1c;
    background: #fee2e2; border-radius: 20px; padding: 3px 10px;
}

/* ---------- Tela de Usuários ---------- */
.status-ativo {background: #dcfce7; color: #15803d;}
.status-inativo {background: #f1f5f9; color: #64748b;}
.status-em-campo {background: #dbeafe; color: #1d4ed8;}
.status-ferias {background: #fef9c3; color: #a16207;}
.status-afastado {background: #fee2e2; color: #b91c1c;}
.user-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: #2563eb; color: #ffffff; font-weight: 700; font-size: 13px;
    display: flex; align-items: center; justify-content: center;
}
.user-name-cell {display: flex; align-items: center; gap: 10px;}
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

        if st.session_state.pagina == "maquinas":
            st.markdown(
                '<div class="topbar-sub">Cadastro completo dos equipamentos, integrado a Modelos_Maquinas e Setores.</div>',
                unsafe_allow_html=True,
            )

            try:
                todas_maquinas = listar_maquinas()
            except Exception as e:
                st.error(f"Não foi possível carregar as máquinas: {e}")
                todas_maquinas = []

            total = len(todas_maquinas)
            operando = sum(1 for m in todas_maquinas if m["status_operacional"] == "Operando")
            parado = sum(1 for m in todas_maquinas if m["status_operacional"] == "Parado")
            manutencao = sum(1 for m in todas_maquinas if m["status_operacional"] == "Em Manutenção")

            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{total}</div>'
                f'<div class="kpi-label">Total de máquinas</div></div>', unsafe_allow_html=True)
            k2.markdown(
                f'<div class="kpi-card kpi-green"><div class="kpi-value">{operando}</div>'
                f'<div class="kpi-label">Operando</div></div>', unsafe_allow_html=True)
            k3.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{parado}</div>'
                f'<div class="kpi-label">Parado</div></div>', unsafe_allow_html=True)
            k4.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{manutencao}</div>'
                f'<div class="kpi-label">Em manutenção</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            g1, g2 = st.columns(2)
            with g1:
                st.markdown('<div class="chart-card"><div class="chart-title">Máquinas por status operacional</div>', unsafe_allow_html=True)
                if todas_maquinas:
                    df_status = (
                        pd.DataFrame(todas_maquinas)["status_operacional"]
                        .value_counts()
                        .rename_axis("Status")
                        .reset_index(name="Quantidade")
                        .set_index("Status")
                    )
                    grafico_barras(df_status, "Quantidade", cores_mapa=STATUS_MAQUINA_CORES)
                else:
                    st.caption("Sem dados para exibir.")
                st.markdown("</div>", unsafe_allow_html=True)
            with g2:
                st.markdown('<div class="chart-card"><div class="chart-title">Máquinas por setor</div>', unsafe_allow_html=True)
                if todas_maquinas:
                    df_setor = (
                        pd.DataFrame(todas_maquinas)["nome_setor"]
                        .value_counts()
                        .rename_axis("Setor")
                        .reset_index(name="Quantidade")
                        .set_index("Setor")
                    )
                    grafico_barras(df_setor, "Quantidade", cor_padrao="#2563eb", horizontal=True)
                else:
                    st.caption("Sem dados para exibir.")
                st.markdown("</div>", unsafe_allow_html=True)

            with st.container(key="topbar_search"):
                st.text_input(
                    "Buscar",
                    key="maquinas_busca",
                    placeholder="Buscar tag, máquina, fabricante, localização ou setor...",
                    label_visibility="collapsed",
                )

            try:
                maquinas = listar_maquinas(st.session_state.get("maquinas_busca", ""))
            except Exception as e:
                st.error(f"Não foi possível carregar as máquinas: {e}")
                maquinas = []

            st.markdown("<br>", unsafe_allow_html=True)

            if not maquinas:
                st.info("Nenhuma máquina encontrada.")
            else:
                h1, h2, h3, h4, h5, h6, h7 = st.columns([1, 2.2, 1.6, 1.8, 1.4, 1.3, 1.1])
                for col, texto in zip((h1, h2, h3, h4, h5, h6, h7),
                                       ("Tag", "Máquina / Modelo", "Fabricante", "Localização", "Setor", "Manutenção", "Status")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

                for row in maquinas:
                    with st.container(key=f"maq_row_{row['tag_equipamento']}"):
                        c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2.2, 1.6, 1.8, 1.4, 1.3, 1.1])
                        c1.markdown(f'<div class="os-cell"><b>{row["tag_equipamento"]}</b></div>', unsafe_allow_html=True)
                        c2.markdown(
                            f'<div class="os-cell">{row["nome_maquina"]}</div>'
                            f'<div class="os-cell-muted">{row["nome_modelo"]} · {row["numero_serie"]}</div>',
                            unsafe_allow_html=True,
                        )
                        c3.markdown(f'<div class="os-cell">{row["fabricante_maquina"]}</div>', unsafe_allow_html=True)
                        c4.markdown(f'<div class="os-cell">{row["localizacao_maquina"]}</div>', unsafe_allow_html=True)
                        c5.markdown(f'<div class="os-cell">{row["nome_setor"]}</div>', unsafe_allow_html=True)
                        c6.markdown(
                            f'<div class="os-cell">{row["tipo_manutencao_padrao"]}</div>'
                            f'<div class="os-cell-muted">Última: {row["ultima_manutencao"] or "—"}</div>',
                            unsafe_allow_html=True,
                        )
                        slug = status_slug(row["status_operacional"])
                        c7.markdown(f'<span class="status-badge status-{slug}">{row["status_operacional"]}</span>', unsafe_allow_html=True)

            st.stop()

        if st.session_state.pagina == "setores":
            st.markdown(
                '<div class="topbar-sub">Setores cadastrados, com máquinas e equipe ativa vinculadas.</div>',
                unsafe_allow_html=True,
            )

            try:
                setores = listar_setores()
            except Exception as e:
                st.error(f"Não foi possível carregar os setores: {e}")
                setores = []

            if not setores:
                st.info("Nenhum setor cadastrado.")
            else:
                colunas = st.columns(3)
                for idx, s in enumerate(setores):
                    with colunas[idx % 3]:
                        st.markdown(f"""
<div class="setor-card">
<div class="setor-card-title">🏭 {s["nome_setor"]}</div>
<div class="setor-card-desc">{s["descricao_setor"] or "Sem descrição cadastrada."}</div>
<div class="setor-card-stats">
<div><div class="setor-stat-value">{s["total_maquinas"]}</div><div class="setor-stat-label">MÁQUINAS</div></div>
<div><div class="setor-stat-value">{s["total_usuarios"]}</div><div class="setor-stat-label">EQUIPE ATIVA</div></div>
</div>
</div>
""", unsafe_allow_html=True)
                        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                g1, g2 = st.columns(2)
                df_setores = pd.DataFrame(setores).set_index("nome_setor")
                with g1:
                    st.markdown('<div class="chart-card"><div class="chart-title">Máquinas por setor</div>', unsafe_allow_html=True)
                    grafico_barras(df_setores, "total_maquinas", cor_padrao="#2563eb", horizontal=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                with g2:
                    st.markdown('<div class="chart-card"><div class="chart-title">Equipe ativa por setor</div>', unsafe_allow_html=True)
                    grafico_barras(df_setores, "total_usuarios", cor_padrao="#16a34a", horizontal=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            st.stop()

        if st.session_state.pagina == "almoxarifado":
            st.markdown(
                '<div class="topbar-sub">Itens em estoque, valores e disponibilidade de peças para as OS.</div>',
                unsafe_allow_html=True,
            )

            try:
                todas_pecas = listar_pecas()
            except Exception as e:
                st.error(f"Não foi possível carregar o almoxarifado: {e}")
                todas_pecas = []

            LIMITE_ESTOQUE_BAIXO = 10
            total_itens = len(todas_pecas)
            valor_total = sum(p["valor_total"] for p in todas_pecas) if todas_pecas else 0
            estoque_baixo = sum(1 for p in todas_pecas if p["quantidade_estoque"] < LIMITE_ESTOQUE_BAIXO)
            total_unidades = sum(p["quantidade_estoque"] for p in todas_pecas) if todas_pecas else 0

            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{total_itens}</div>'
                f'<div class="kpi-label">Itens cadastrados</div></div>', unsafe_allow_html=True)
            k2.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{total_unidades}</div>'
                f'<div class="kpi-label">Unidades em estoque</div></div>', unsafe_allow_html=True)
            k3.markdown(
                f'<div class="kpi-card kpi-green"><div class="kpi-value">R$ {valor_total:,.2f}</div>'
                f'<div class="kpi-label">Valor total em estoque</div></div>'.replace(",", "§").replace(".", ",").replace("§", "."),
                unsafe_allow_html=True)
            k4.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{estoque_baixo}</div>'
                f'<div class="kpi-label">Itens com estoque baixo (&lt;{LIMITE_ESTOQUE_BAIXO})</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if todas_pecas:
                df_pecas = pd.DataFrame(todas_pecas)
                g1, g2 = st.columns(2)
                with g1:
                    st.markdown('<div class="chart-card"><div class="chart-title">Top 10 peças por valor em estoque (R$)</div>', unsafe_allow_html=True)
                    df_top_valor = df_pecas.sort_values("valor_total", ascending=False).head(10).set_index("nome_peca")
                    grafico_barras(df_top_valor, "valor_total", cor_padrao="#2563eb", moeda=True, horizontal=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                with g2:
                    st.markdown('<div class="chart-card"><div class="chart-title">Top 10 peças por quantidade em estoque</div>', unsafe_allow_html=True)
                    df_top_qtd = df_pecas.sort_values("quantidade_estoque", ascending=False).head(10).set_index("nome_peca")
                    grafico_barras(df_top_qtd, "quantidade_estoque", cor_padrao="#0ea5e9", horizontal=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            with st.container(key="topbar_search"):
                st.text_input(
                    "Buscar",
                    key="pecas_busca",
                    placeholder="Buscar peça pelo nome...",
                    label_visibility="collapsed",
                )

            try:
                pecas = listar_pecas(st.session_state.get("pecas_busca", ""))
            except Exception as e:
                st.error(f"Não foi possível carregar o almoxarifado: {e}")
                pecas = []

            st.markdown("<br>", unsafe_allow_html=True)

            if not pecas:
                st.info("Nenhuma peça encontrada.")
            else:
                h1, h2, h3, h4, h5 = st.columns([2.6, 1.2, 1.2, 1.3, 1.3])
                for col, texto in zip((h1, h2, h3, h4, h5),
                                       ("Peça", "Qtd. em estoque", "Unidade", "Custo unitário", "Valor total")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

                for row in pecas:
                    with st.container(key=f"peca_row_{row['id_peca']}"):
                        c1, c2, c3, c4, c5 = st.columns([2.6, 1.2, 1.2, 1.3, 1.3])
                        c1.markdown(f'<div class="os-cell"><b>{row["nome_peca"]}</b></div>', unsafe_allow_html=True)
                        classe_qtd = "estoque-baixo" if row["quantidade_estoque"] < LIMITE_ESTOQUE_BAIXO else "estoque-ok"
                        c2.markdown(f'<div class="os-cell {classe_qtd}">{row["quantidade_estoque"]}</div>', unsafe_allow_html=True)
                        c3.markdown(f'<div class="os-cell">{row["unidade_medida"]}</div>', unsafe_allow_html=True)
                        c4.markdown(f'<div class="os-cell">R$ {row["custo_unitario"]:,.2f}</div>'.replace(",", "§").replace(".", ",").replace("§", "."), unsafe_allow_html=True)
                        c5.markdown(f'<div class="os-cell">R$ {row["valor_total"]:,.2f}</div>'.replace(",", "§").replace(".", ",").replace("§", "."), unsafe_allow_html=True)

            st.stop()

        if st.session_state.pagina == "ferramentas":
            st.markdown(
                '<div class="topbar-sub">Situação das ferramentas e com quem cada uma está no momento.</div>',
                unsafe_allow_html=True,
            )

            try:
                todas_ferramentas = listar_ferramentas()
            except Exception as e:
                st.error(f"Não foi possível carregar as ferramentas: {e}")
                todas_ferramentas = []

            total = len(todas_ferramentas)
            disponiveis = sum(1 for f in todas_ferramentas if f["status_ferramenta"] == "Disponível")
            em_uso = sum(1 for f in todas_ferramentas if f["status_ferramenta"] == "Em Uso")
            manutencao = sum(1 for f in todas_ferramentas if f["status_ferramenta"] == "Manutenção/Calibração")
            extraviadas = sum(1 for f in todas_ferramentas if f["status_ferramenta"] == "Extraviada")

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{total}</div>'
                f'<div class="kpi-label">Total de ferramentas</div></div>', unsafe_allow_html=True)
            k2.markdown(
                f'<div class="kpi-card kpi-green"><div class="kpi-value">{disponiveis}</div>'
                f'<div class="kpi-label">Disponíveis</div></div>', unsafe_allow_html=True)
            k3.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{em_uso}</div>'
                f'<div class="kpi-label">Em uso</div></div>', unsafe_allow_html=True)
            k4.markdown(
                f'<div class="kpi-card" style="border-left-color:#6d28d9;"><div class="kpi-value">{manutencao}</div>'
                f'<div class="kpi-label">Manutenção / Calibração</div></div>', unsafe_allow_html=True)
            k5.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{extraviadas}</div>'
                f'<div class="kpi-label">Extraviadas</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if todas_ferramentas:
                st.markdown('<div class="chart-card"><div class="chart-title">Ferramentas por status</div>', unsafe_allow_html=True)
                df_ferr_status = (
                    pd.DataFrame(todas_ferramentas)["status_ferramenta"]
                    .value_counts()
                    .rename_axis("Status")
                    .reset_index(name="Quantidade")
                    .set_index("Status")
                )
                grafico_barras(df_ferr_status, "Quantidade", cores_mapa=STATUS_FERRAMENTA_CORES)
                st.markdown("</div>", unsafe_allow_html=True)

            with st.container(key="topbar_search"):
                st.text_input(
                    "Buscar",
                    key="ferramentas_busca",
                    placeholder="Buscar ferramenta pelo nome...",
                    label_visibility="collapsed",
                )

            try:
                ferramentas = listar_ferramentas(st.session_state.get("ferramentas_busca", ""))
            except Exception as e:
                st.error(f"Não foi possível carregar as ferramentas: {e}")
                ferramentas = []

            st.markdown("<br>", unsafe_allow_html=True)

            if not ferramentas:
                st.info("Nenhuma ferramenta encontrada.")
            else:
                h1, h2, h3, h4 = st.columns([2.6, 1.4, 1.6, 1.6])
                for col, texto in zip((h1, h2, h3, h4), ("Ferramenta", "Status", "Com quem", "Devolução prevista")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

                for row in ferramentas:
                    with st.container(key=f"ferr_row_{row['id_ferramenta']}"):
                        c1, c2, c3, c4 = st.columns([2.6, 1.4, 1.6, 1.6])
                        c1.markdown(f'<div class="os-cell"><b>{row["nome_ferramenta"]}</b></div>', unsafe_allow_html=True)
                        slug = status_slug(row["status_ferramenta"])
                        c2.markdown(f'<span class="status-badge status-{slug}">{row["status_ferramenta"]}</span>', unsafe_allow_html=True)
                        c3.markdown(f'<div class="os-cell">{row["com_quem"] or "—"}</div>', unsafe_allow_html=True)
                        c4.markdown(f'<div class="os-cell">{row["devolucao_prevista"] or "—"}</div>', unsafe_allow_html=True)

            st.stop()

        if st.session_state.pagina == "matriz_risco":
            st.markdown(
                '<div class="topbar-sub">Matriz de Riscos (NR-01) e EPIs obrigatórios associados às Ordens de Serviço.</div>',
                unsafe_allow_html=True,
            )

            try:
                riscos = listar_riscos()
            except Exception as e:
                st.error(f"Não foi possível carregar a matriz de riscos: {e}")
                riscos = []

            if not riscos:
                st.info("Nenhum risco cadastrado.")
            else:
                total_riscos = len(riscos)
                mais_usado = max(riscos, key=lambda r: r["total_os"]) if riscos else None

                k1, k2 = st.columns(2)
                k1.markdown(
                    f'<div class="kpi-card"><div class="kpi-value">{total_riscos}</div>'
                    f'<div class="kpi-label">Riscos cadastrados</div></div>', unsafe_allow_html=True)
                k2.markdown(
                    f'<div class="kpi-card kpi-red"><div class="kpi-value">{mais_usado["risco_nr01"] if mais_usado else "—"}</div>'
                    f'<div class="kpi-label">Risco mais recorrente nas OS</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                colunas = st.columns(3)
                for idx, r in enumerate(riscos):
                    with colunas[idx % 3]:
                        st.markdown(f"""
<div class="risco-card">
<div class="risco-card-title">⚠️ {r["risco_nr01"]}</div>
<div class="risco-card-epis"><b>EPIs obrigatórios:</b> {r["epis_obrigatorios"]}</div>
<span class="risco-card-tag">{r["total_os"]} OS vinculada(s)</span>
</div>
""", unsafe_allow_html=True)
                        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="chart-card"><div class="chart-title">Riscos mais recorrentes nas Ordens de Serviço</div>', unsafe_allow_html=True)
                df_riscos = pd.DataFrame(riscos).sort_values("total_os", ascending=False).set_index("risco_nr01")
                grafico_barras(df_riscos, "total_os", cor_padrao="#dc2626", horizontal=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.stop()

        if st.session_state.pagina == "usuarios":
            st.markdown(
                '<div class="topbar-sub">Equipe cadastrada, cargos, setores e disponibilidade dos técnicos.</div>',
                unsafe_allow_html=True,
            )

            try:
                todos_usuarios = listar_usuarios()
            except Exception as e:
                st.error(f"Não foi possível carregar os usuários: {e}")
                todos_usuarios = []

            total = len(todos_usuarios)
            ativos = sum(1 for u in todos_usuarios if u["status_usuario"] == "Ativo")
            inativos = sum(1 for u in todos_usuarios if u["status_usuario"] == "Inativo")
            tecnicos_disponiveis = sum(
                1 for u in todos_usuarios
                if u["cargo_usuario"] == "Tecnico" and u["status_usuario"] == "Ativo"
                and u["disponibilidade_tecnico"] == "Disponível"
            )

            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{total}</div>'
                f'<div class="kpi-label">Usuários cadastrados</div></div>', unsafe_allow_html=True)
            k2.markdown(
                f'<div class="kpi-card kpi-green"><div class="kpi-value">{ativos}</div>'
                f'<div class="kpi-label">Ativos</div></div>', unsafe_allow_html=True)
            k3.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{inativos}</div>'
                f'<div class="kpi-label">Inativos</div></div>', unsafe_allow_html=True)
            k4.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{tecnicos_disponiveis}</div>'
                f'<div class="kpi-label">Técnicos disponíveis agora</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if todos_usuarios:
                df_usuarios = pd.DataFrame(todos_usuarios)
                g1, g2 = st.columns(2)
                with g1:
                    st.markdown('<div class="chart-card"><div class="chart-title">Usuários por cargo</div>', unsafe_allow_html=True)
                    df_cargo = (
                        df_usuarios["cargo_usuario"].value_counts()
                        .rename_axis("Cargo").reset_index(name="Quantidade").set_index("Cargo")
                    )
                    grafico_barras(df_cargo, "Quantidade", cor_padrao="#2563eb")
                    st.markdown("</div>", unsafe_allow_html=True)
                with g2:
                    st.markdown('<div class="chart-card"><div class="chart-title">Disponibilidade dos técnicos</div>', unsafe_allow_html=True)
                    df_tecnicos = df_usuarios[df_usuarios["cargo_usuario"] == "Tecnico"]
                    if not df_tecnicos.empty:
                        df_disp = (
                            df_tecnicos["disponibilidade_tecnico"].value_counts()
                            .rename_axis("Disponibilidade").reset_index(name="Quantidade").set_index("Disponibilidade")
                        )
                        grafico_barras(df_disp, "Quantidade", cores_mapa=DISPONIBILIDADE_CORES)
                    else:
                        st.caption("Nenhum técnico cadastrado.")
                    st.markdown("</div>", unsafe_allow_html=True)

            with st.container(key="topbar_search"):
                st.text_input(
                    "Buscar",
                    key="usuarios_busca",
                    placeholder="Buscar por nome, e-mail, cargo ou setor...",
                    label_visibility="collapsed",
                )

            try:
                usuarios = listar_usuarios(st.session_state.get("usuarios_busca", ""))
            except Exception as e:
                st.error(f"Não foi possível carregar os usuários: {e}")
                usuarios = []

            st.markdown("<br>", unsafe_allow_html=True)

            if not usuarios:
                st.info("Nenhum usuário encontrado.")
            else:
                h1, h2, h3, h4, h5, h6 = st.columns([2.2, 1.4, 1.4, 1.1, 1.4, 1.3])
                for col, texto in zip((h1, h2, h3, h4, h5, h6),
                                       ("Usuário", "Cargo", "Setor", "Status", "Disponibilidade", "Telefone")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

                for row in usuarios:
                    with st.container(key=f"user_row_{row['id_usuario']}"):
                        c1, c2, c3, c4, c5, c6 = st.columns([2.2, 1.4, 1.4, 1.1, 1.4, 1.3])
                        iniciais = "".join(p[0].upper() for p in row["nome_usuario"].split()[:2])
                        c1.markdown(
                            f'<div class="user-name-cell"><div class="user-avatar">{iniciais}</div>'
                            f'<div><div class="os-cell"><b>{row["nome_usuario"]}</b></div>'
                            f'<div class="os-cell-muted">{row["email_usuario"]}</div></div></div>',
                            unsafe_allow_html=True,
                        )
                        c2.markdown(
                            f'<div class="os-cell">{row["cargo_usuario"]}</div>'
                            f'<div class="os-cell-muted">{row["nivel_experiencia"] or "—"}</div>',
                            unsafe_allow_html=True,
                        )
                        c3.markdown(f'<div class="os-cell">{row["nome_setor"] or "—"}</div>', unsafe_allow_html=True)
                        slug_status = status_slug(row["status_usuario"])
                        c4.markdown(f'<span class="status-badge status-{slug_status}">{row["status_usuario"]}</span>', unsafe_allow_html=True)
                        if row["cargo_usuario"] == "Tecnico" and row["disponibilidade_tecnico"]:
                            slug_disp = status_slug(row["disponibilidade_tecnico"])
                            c5.markdown(f'<span class="status-badge status-{slug_disp}">{row["disponibilidade_tecnico"]}</span>', unsafe_allow_html=True)
                        else:
                            c5.markdown('<div class="os-cell-muted">—</div>', unsafe_allow_html=True)
                        c6.markdown(f'<div class="os-cell">{row["telefone_usuario"]}</div>', unsafe_allow_html=True)

            st.stop()

        if st.session_state.pagina == "dashboard":
            st.markdown(
                '<div class="topbar-sub">Visão geral da operação: ordens de serviço, ativos, equipe e estoque.</div>',
                unsafe_allow_html=True,
            )

            try:
                ordens_dash = listar_ordens_servico()
            except Exception as e:
                st.error(f"Não foi possível carregar as Ordens de Serviço: {e}")
                ordens_dash = []
            try:
                maquinas_dash = listar_maquinas()
            except Exception as e:
                st.error(f"Não foi possível carregar as máquinas: {e}")
                maquinas_dash = []
            try:
                pecas_dash = listar_pecas()
            except Exception as e:
                st.error(f"Não foi possível carregar o almoxarifado: {e}")
                pecas_dash = []
            try:
                usuarios_dash = listar_usuarios()
            except Exception as e:
                st.error(f"Não foi possível carregar os usuários: {e}")
                usuarios_dash = []

            LIMITE_ESTOQUE_BAIXO = 10

            total_os = len(ordens_dash)
            os_abertas = sum(1 for o in ordens_dash if o["status_os"] == "Aberto")
            os_andamento = sum(1 for o in ordens_dash if o["status_os"] == "Em andamento")
            os_concluidas = sum(1 for o in ordens_dash if o["status_os"] == "Concluído")

            total_maquinas = len(maquinas_dash)
            maquinas_paradas = sum(1 for m in maquinas_dash if m["status_operacional"] == "Parado")

            itens_estoque_baixo = sum(1 for p in pecas_dash if p["quantidade_estoque"] < LIMITE_ESTOQUE_BAIXO)

            tecnicos_disponiveis = sum(
                1 for u in usuarios_dash
                if u["cargo_usuario"] == "Tecnico" and u["status_usuario"] == "Ativo"
                and u["disponibilidade_tecnico"] == "Disponível"
            )

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{total_os}</div>'
                f'<div class="kpi-label">OS no total</div></div>', unsafe_allow_html=True)
            k2.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{os_abertas}</div>'
                f'<div class="kpi-label">OS em aberto</div></div>', unsafe_allow_html=True)
            k3.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{os_andamento}</div>'
                f'<div class="kpi-label">OS em andamento</div></div>', unsafe_allow_html=True)
            k4.markdown(
                f'<div class="kpi-card kpi-green"><div class="kpi-value">{os_concluidas}</div>'
                f'<div class="kpi-label">OS concluídas</div></div>', unsafe_allow_html=True)
            k5.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{maquinas_paradas}</div>'
                f'<div class="kpi-label">Máquinas paradas</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            g1, g2 = st.columns(2)
            with g1:
                st.markdown('<div class="chart-card"><div class="chart-title">Ordens de Serviço por status</div>', unsafe_allow_html=True)
                if ordens_dash:
                    df_os_status = (
                        pd.DataFrame(ordens_dash)["status_os"]
                        .value_counts()
                        .rename_axis("Status")
                        .reset_index(name="Quantidade")
                        .set_index("Status")
                    )
                    grafico_barras(df_os_status, "Quantidade", cores_mapa=STATUS_OS_CORES)
                else:
                    st.caption("Sem dados para exibir.")
                st.markdown("</div>", unsafe_allow_html=True)
            with g2:
                st.markdown('<div class="chart-card"><div class="chart-title">Abertura de OS por mês</div>', unsafe_allow_html=True)
                if ordens_dash:
                    df_os_mes = pd.DataFrame(ordens_dash)
                    df_os_mes["mes"] = pd.to_datetime(df_os_mes["data_abertura"].astype(str)).dt.to_period("M").astype(str)
                    df_os_mes = (
                        df_os_mes["mes"].value_counts()
                        .rename_axis("Mês")
                        .reset_index(name="Quantidade")
                        .sort_values("Mês")
                        .set_index("Mês")
                    )
                    grafico_area(df_os_mes, "Quantidade")
                else:
                    st.caption("Sem dados para exibir.")
                st.markdown("</div>", unsafe_allow_html=True)

            g3, g4 = st.columns(2)
            with g3:
                st.markdown('<div class="chart-card"><div class="chart-title">OS em aberto/andamento por técnico</div>', unsafe_allow_html=True)
                pendentes = [o for o in ordens_dash if o["status_os"] in ("Aberto", "Em andamento") and o["tecnico"]]
                if pendentes:
                    df_pend = (
                        pd.DataFrame(pendentes)["tecnico"]
                        .value_counts()
                        .rename_axis("Técnico")
                        .reset_index(name="Quantidade")
                        .set_index("Técnico")
                    )
                    grafico_barras(df_pend, "Quantidade", cor_padrao="#2563eb", horizontal=True)
                else:
                    st.caption("Nenhuma OS pendente com técnico atribuído.")
                st.markdown("</div>", unsafe_allow_html=True)
            with g4:
                st.markdown('<div class="chart-card"><div class="chart-title">Máquinas por status operacional</div>', unsafe_allow_html=True)
                if maquinas_dash:
                    df_maq_status = (
                        pd.DataFrame(maquinas_dash)["status_operacional"]
                        .value_counts()
                        .rename_axis("Status")
                        .reset_index(name="Quantidade")
                        .set_index("Status")
                    )
                    grafico_barras(df_maq_status, "Quantidade", cores_mapa=STATUS_MAQUINA_CORES)
                else:
                    st.caption("Sem dados para exibir.")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            alerta_col1, alerta_col2 = st.columns(2)
            alerta_col1.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{itens_estoque_baixo}</div>'
                f'<div class="kpi-label">Itens do almoxarifado com estoque baixo</div></div>', unsafe_allow_html=True)
            alerta_col2.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{tecnicos_disponiveis}</div>'
                f'<div class="kpi-label">Técnicos disponíveis agora</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="chart-card"><div class="chart-title">Últimas Ordens de Serviço</div>', unsafe_allow_html=True)
            if ordens_dash:
                ultimas = ordens_dash[:6]
                h1, h2, h3, h4, h5 = st.columns([0.6, 1.2, 2.6, 1.3, 1])
                for col, texto in zip((h1, h2, h3, h4, h5), ("OS", "Equipamento", "Descrição", "Técnico", "Status")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)
                for row in ultimas:
                    c1, c2, c3, c4, c5 = st.columns([0.6, 1.2, 2.6, 1.3, 1])
                    c1.markdown(f'<div class="os-cell">#{row["id_os"]}</div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="os-cell">{row["tag_equipamento"]}</div>', unsafe_allow_html=True)
                    c3.markdown(f'<div class="os-cell">{row["descricao_falha"]}</div>', unsafe_allow_html=True)
                    c4.markdown(f'<div class="os-cell">{row["tecnico"] or "—"}</div>', unsafe_allow_html=True)
                    slug = status_slug(row["status_os"])
                    c5.markdown(f'<span class="status-badge status-{slug}">{row["status_os"]}</span>', unsafe_allow_html=True)
            else:
                st.caption("Nenhuma OS cadastrada.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.stop()

        if st.session_state.pagina == "agenda":
            st.markdown(
                '<div class="topbar-sub">Programação das Ordens de Serviço por data e técnico.</div>',
                unsafe_allow_html=True,
            )

            try:
                ordens_agenda = listar_ordens_servico()
            except Exception as e:
                st.error(f"Não foi possível carregar as Ordens de Serviço: {e}")
                ordens_agenda = []

            hoje = agora_brasil().date()

            f1, f2 = st.columns([1, 3])
            with f1:
                data_selecionada = st.date_input("Ver ordens do dia", value=hoje, key="agenda_data")

            os_do_dia = [o for o in ordens_agenda if o["data_abertura"] == data_selecionada]
            os_do_dia.sort(key=lambda o: (o["hh_inicio"] is None, o["hh_inicio"]))

            os_semana = [
                o for o in ordens_agenda
                if o["data_abertura"] and hoje <= o["data_abertura"] <= hoje + timedelta(days=7)
            ]

            k1, k2, k3 = st.columns(3)
            k1.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{len(os_do_dia)}</div>'
                f'<div class="kpi-label">OS na data selecionada</div></div>', unsafe_allow_html=True)
            k2.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{len(os_semana)}</div>'
                f'<div class="kpi-label">OS nos próximos 7 dias</div></div>', unsafe_allow_html=True)
            pendentes_total = sum(1 for o in ordens_agenda if o["status_os"] != "Concluído")
            k3.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{pendentes_total}</div>'
                f'<div class="kpi-label">OS pendentes no total</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f'<div class="chart-title">Ordens de Serviço em {data_selecionada.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
            if not os_do_dia:
                st.info("Nenhuma OS agendada para esta data.")
            else:
                h1, h2, h3, h4, h5 = st.columns([1, 1.2, 2.4, 1.4, 1])
                for col, texto in zip((h1, h2, h3, h4, h5), ("Horário", "Equipamento", "Descrição", "Técnico", "Status")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)
                for row in os_do_dia:
                    with st.container(key=f"agenda_row_{row['id_os']}"):
                        c1, c2, c3, c4, c5 = st.columns([1, 1.2, 2.4, 1.4, 1])
                        c1.markdown(
                            f'<div class="os-cell">{row["hh_inicio"]} → {row["hh_fim"] or "—"}</div>',
                            unsafe_allow_html=True,
                        )
                        c2.markdown(f'<div class="os-cell"><b>{row["tag_equipamento"]}</b></div>', unsafe_allow_html=True)
                        c3.markdown(f'<div class="os-cell">{row["descricao_falha"]}</div>', unsafe_allow_html=True)
                        c4.markdown(f'<div class="os-cell">{row["tecnico"] or "—"}</div>', unsafe_allow_html=True)
                        slug = status_slug(row["status_os"])
                        c5.markdown(f'<span class="status-badge status-{slug}">{row["status_os"]}</span>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Próximos 7 dias</div>', unsafe_allow_html=True)
            for i in range(7):
                dia = hoje + timedelta(days=i)
                os_dia = [o for o in ordens_agenda if o["data_abertura"] == dia]
                with st.container(key=f"agenda_dia_{dia.isoformat()}"):
                    st.markdown(
                        f'<div class="os-row"><b>{dia.strftime("%d/%m/%Y")}</b> '
                        f'<span class="os-cell-muted">— {len(os_dia)} OS</span></div>',
                        unsafe_allow_html=True,
                    )

            st.stop()

        if st.session_state.pagina == "relatorios":
            st.markdown(
                '<div class="topbar-sub">Indicadores consolidados de manutenção, por período e por técnico.</div>',
                unsafe_allow_html=True,
            )

            try:
                ordens_rel = listar_ordens_servico()
            except Exception as e:
                st.error(f"Não foi possível carregar as Ordens de Serviço: {e}")
                ordens_rel = []

            if not ordens_rel:
                st.info("Nenhuma OS cadastrada para gerar relatórios.")
                st.stop()

            df_os = pd.DataFrame(ordens_rel)
            data_min = df_os["data_abertura"].min()
            data_max = df_os["data_abertura"].max()

            f1, f2 = st.columns(2)
            with f1:
                periodo = st.date_input(
                    "Período",
                    value=(data_min, data_max),
                    min_value=data_min,
                    max_value=data_max,
                    key="relatorios_periodo",
                )
            with f2:
                tecnicos_opcoes = ["Todos"] + sorted(df_os["tecnico"].dropna().unique().tolist())
                tecnico_filtro = st.selectbox("Técnico", tecnicos_opcoes, key="relatorios_tecnico")

            if isinstance(periodo, tuple) and len(periodo) == 2:
                data_ini, data_fim = periodo
            else:
                data_ini, data_fim = data_min, data_max

            df_filtro = df_os[(df_os["data_abertura"] >= data_ini) & (df_os["data_abertura"] <= data_fim)]
            if tecnico_filtro != "Todos":
                df_filtro = df_filtro[df_filtro["tecnico"] == tecnico_filtro]

            total_periodo = len(df_filtro)
            concluidas_periodo = int((df_filtro["status_os"] == "Concluído").sum())
            abertas_periodo = int((df_filtro["status_os"] == "Aberto").sum())
            andamento_periodo = int((df_filtro["status_os"] == "Em andamento").sum())
            taxa_conclusao = (concluidas_periodo / total_periodo * 100) if total_periodo else 0

            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{total_periodo}</div>'
                f'<div class="kpi-label">OS no período</div></div>', unsafe_allow_html=True)
            k2.markdown(
                f'<div class="kpi-card kpi-green"><div class="kpi-value">{concluidas_periodo}</div>'
                f'<div class="kpi-label">Concluídas</div></div>', unsafe_allow_html=True)
            k3.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{abertas_periodo + andamento_periodo}</div>'
                f'<div class="kpi-label">Em aberto/andamento</div></div>', unsafe_allow_html=True)
            k4.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{taxa_conclusao:.1f}%</div>'
                f'<div class="kpi-label">Taxa de conclusão</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            g1, g2 = st.columns(2)
            with g1:
                st.markdown('<div class="chart-card"><div class="chart-title">OS por status (período filtrado)</div>', unsafe_allow_html=True)
                if not df_filtro.empty:
                    df_status_rel = (
                        df_filtro["status_os"].value_counts()
                        .rename_axis("Status").reset_index(name="Quantidade").set_index("Status")
                    )
                    grafico_barras(df_status_rel, "Quantidade", cores_mapa=STATUS_OS_CORES)
                else:
                    st.caption("Sem dados para o período/técnico selecionado.")
                st.markdown("</div>", unsafe_allow_html=True)
            with g2:
                st.markdown('<div class="chart-card"><div class="chart-title">OS por técnico (período filtrado)</div>', unsafe_allow_html=True)
                if not df_filtro.empty and df_filtro["tecnico"].notna().any():
                    df_tec_rel = (
                        df_filtro["tecnico"].dropna().value_counts()
                        .rename_axis("Técnico").reset_index(name="Quantidade").set_index("Técnico")
                    )
                    grafico_barras(df_tec_rel, "Quantidade", cor_padrao="#2563eb", horizontal=True)
                else:
                    st.caption("Sem dados para o período/técnico selecionado.")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="chart-card"><div class="chart-title">Evolução mensal de abertura de OS</div>', unsafe_allow_html=True)
            if not df_filtro.empty:
                df_mensal = df_filtro.copy()
                df_mensal["mes"] = pd.to_datetime(df_mensal["data_abertura"].astype(str)).dt.to_period("M").astype(str)
                df_mensal = (
                    df_mensal["mes"].value_counts()
                    .rename_axis("Mês").reset_index(name="Quantidade")
                    .sort_values("Mês").set_index("Mês")
                )
                grafico_area(df_mensal, "Quantidade")
            else:
                st.caption("Sem dados para o período/técnico selecionado.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Detalhamento das Ordens de Serviço</div>', unsafe_allow_html=True)
            if df_filtro.empty:
                st.info("Nenhuma OS encontrada para os filtros selecionados.")
            else:
                st.dataframe(
                    df_filtro[["id_os", "tag_equipamento", "descricao_falha", "data_abertura", "tecnico", "status_os"]]
                    .rename(columns={
                        "id_os": "OS", "tag_equipamento": "Equipamento", "descricao_falha": "Descrição",
                        "data_abertura": "Abertura", "tecnico": "Técnico", "status_os": "Status",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )
                csv_bytes = df_filtro.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "⬇️ Exportar CSV",
                    data=csv_bytes,
                    file_name=f"relatorio_os_{data_ini}_{data_fim}.csv",
                    mime="text/csv",
                )

            st.stop()

        if st.session_state.pagina != "ordens_servico":
            st.markdown('<div class="topbar-sub">Esta página ainda não foi implementada.</div>', unsafe_allow_html=True)
            st.info("Em construção — por enquanto Ordens de Serviço, Máquinas, Setores, Almoxarifado de Peças, Ferramentas, Matriz de Risco/EPI e Usuários estão conectados ao banco.")
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
# TELA DE LOGIN — estilo "foguete", tons de azul, tela inteira
# ------------------------------------------------------------------
with st.container(key="unified_panel"):

    # ---------- Painel esquerdo: decorativo (foguete + gradiente multi-tom) ----------
    with st.container(key="rocket_panel"):
        st.markdown("""
<div class="brand-box">
<div class="brand-icon">🔧</div>
<div>
<div class="brand-title">THAF Manutenção</div>
<div class="brand-sub">Gestão Industrial</div>
</div>
</div>

<div class="rocket-mid-circle"></div>

<div class="rocket-stage">
<div class="rocket-ring"></div>
<div class="smoke-cloud"></div>
<div class="rocket-emoji">🚀</div>
</div>

<div class="rocket-tagline">
Gestão inteligente da manutenção industrial.
<span>Ordens de serviço, ativos, peças e equipe — tudo em um único lugar, sempre disponível.</span>
</div>
""", unsafe_allow_html=True)

    # ---------- Painel direito: cartão de login (cobre a tela inteira) ----------
    with st.container(key="login_card"):
        st.markdown('<div class="login-eyebrow">Bem-vindo de volta</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Acesse sua conta</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Entre com suas credenciais corporativas para continuar.</div>', unsafe_allow_html=True)

        if st.session_state.db_error:
            st.error(f"Não foi possível conectar ao banco:\n\n{st.session_state.db_error}")

        st.text_input("👤  E-mail", key="email_input", placeholder="nome@empresa.com")
        st.text_input("🔒  Senha", key="senha_input", type="password", placeholder="••••••••")

        st.markdown(
            '<div class="login-row"><span>☐ Lembrar de mim</span>'
            '<span class="login-link">Esqueceu a senha?</span></div>',
            unsafe_allow_html=True,
        )

        if st.session_state.get("login_error"):
            st.error("E-mail ou senha inválidos.")
            st.session_state.login_error = False

        with st.container(key="entrar_btn_wrap"):
            st.button("→  Entrar", on_click=do_login)

        st.markdown('<div class="demo-label">Acesso rápido (usuários reais)</div>', unsafe_allow_html=True)

        d1, d2 = st.columns(2)
        colunas = [d1, d2, d1, d2]
        for idx, (cargo, email, senha) in enumerate(ACESSO_RAPIDO_USERS):
            with colunas[idx]:
                with st.container(key=f"demo_{idx}"):
                    st.button(f"{cargo}\n{email}", key=f"btn_demo_{idx}",
                              on_click=quick_login, args=(email, senha))

        if st.session_state.logged_in:
            st.rerun()