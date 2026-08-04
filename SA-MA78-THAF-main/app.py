import hashlib
import json
from datetime import datetime, timedelta, time as dt_time
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
import textwrap
import pymysql
import streamlit as st
from dbutils.pooled_db import PooledDB

try:
    from googleapiclient.discovery import build as _google_build
    from google.oauth2 import service_account as _google_service_account
    GOOGLE_CALENDAR_LIB_OK = True
except ImportError:
    GOOGLE_CALENDAR_LIB_OK = False

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")


def agora_brasil():
    """Retorna o horário atual no fuso de Brasília, independente do fuso do servidor de banco."""
    return datetime.now(FUSO_BRASIL).replace(tzinfo=None)


st.set_page_config(
    page_title="Portal da Manutenção - Login",
    page_icon="🛠️",
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


# ------------------------------------------------------------------
# INTEGRAÇÃO COM O GOOGLE CALENDAR (conta de serviço, calendário único
# compartilhado da empresa — sem login individual por usuário)
#
# Configuração necessária em .streamlit/secrets.toml:
#
#   [google_calendar]
#   calendar_id = "algumacoisa@group.calendar.google.com"
#   service_account_json = """
#   { ... conteúdo do JSON da conta de serviço baixado no Google Cloud ... }
#   """
#
# Passos no Google Cloud: criar um projeto, ativar a "Google Calendar API",
# criar uma conta de serviço, gerar uma chave JSON, e por fim COMPARTILHAR
# o calendário da empresa com o e-mail da conta de serviço (algo como
# nome@projeto.iam.gserviceaccount.com), dando a ela permissão de
# "Fazer alterações nos eventos".
# ------------------------------------------------------------------
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]

GOOGLE_COLOR_POR_STATUS = {
    "Aberto": "11",        # tomate/vermelho
    "Em andamento": "9",   # mirtilo/azul
    "Concluído": "10",     # manjericão/verde
}


@st.cache_resource
def get_google_calendar():
    """Autentica com a conta de serviço e devolve {service, calendar_id}, ou
    None se a integração não estiver configurada/disponível. Nunca levanta
    exceção — qualquer problema fica registrado em st.session_state para ser
    mostrado de forma amigável na tela de Agenda."""
    if not GOOGLE_CALENDAR_LIB_OK:
        st.session_state["google_calendar_erro"] = (
            "Bibliotecas do Google Calendar não instaladas. Adicione "
            "'google-api-python-client' e 'google-auth' ao requirements.txt."
        )
        return None
    try:
        conf = st.secrets.get("google_calendar")
    except Exception:
        conf = None
    if not conf or "service_account_json" not in conf or "calendar_id" not in conf:
        return None
    try:
        info = json.loads(conf["service_account_json"])
        creds = _google_service_account.Credentials.from_service_account_info(info, scopes=GOOGLE_SCOPES)
        service = _google_build("calendar", "v3", credentials=creds, cache_discovery=False)
        st.session_state["google_calendar_erro"] = None
        return {"service": service, "calendar_id": conf["calendar_id"]}
    except Exception as e:
        st.session_state["google_calendar_erro"] = f"Falha ao autenticar com o Google: {e}"
        return None


def google_calendar_configurado() -> bool:
    return get_google_calendar() is not None


def _to_time(valor):
    """Normaliza um valor de horário vindo do MySQL/streamlit para datetime.time
    (pymysql às vezes devolve colunas TIME como timedelta)."""
    if isinstance(valor, timedelta):
        total = int(valor.total_seconds())
        return dt_time(hour=(total // 3600) % 24, minute=(total % 3600) // 60, second=total % 60)
    return valor


def _nome_usuario_por_id(id_usuario):
    if not id_usuario:
        return None
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT nome_usuario FROM Usuarios WHERE id_usuario = %s", (id_usuario,))
            r = cur.fetchone()
            return r["nome_usuario"] if r else None
    finally:
        conn.close()


def _construir_evento_os(os_info: dict):
    data = os_info["data_abertura"]
    inicio = _to_time(os_info.get("hh_inicio")) or dt_time(8, 0)
    fim = _to_time(os_info.get("hh_fim"))
    inicio_dt = datetime.combine(data, inicio)
    if fim and fim > inicio:
        fim_dt = datetime.combine(data, fim)
    else:
        fim_dt = inicio_dt + timedelta(hours=1)

    return {
        "summary": f"OS #{os_info['id_os']} · {os_info['tag_equipamento']}",
        "description": (
            f"{os_info.get('descricao_falha') or ''}\n\n"
            f"Técnico: {os_info.get('tecnico') or '—'}\n"
            f"Status: {os_info.get('status_os')}\n"
            f"Gerado automaticamente pelo Portal da Manutenção."
        ),
        "start": {"dateTime": inicio_dt.isoformat(), "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": fim_dt.isoformat(), "timeZone": "America/Sao_Paulo"},
        "colorId": GOOGLE_COLOR_POR_STATUS.get(os_info.get("status_os"), "1"),
        "extendedProperties": {"private": {"thaf_id_os": str(os_info["id_os"])}},
    }


def _buscar_evento_google_por_os(id_os):
    gcal = get_google_calendar()
    if not gcal:
        return None
    try:
        resp = gcal["service"].events().list(
            calendarId=gcal["calendar_id"],
            privateExtendedProperty=f"thaf_id_os={id_os}",
            maxResults=1,
        ).execute()
        itens = resp.get("items", [])
        return itens[0] if itens else None
    except Exception as e:
        st.session_state["google_calendar_erro"] = f"Falha ao consultar o Google Calendar: {e}"
        return None


def sincronizar_os_google(os_info: dict):
    """Cria ou atualiza (upsert) o evento correspondente a uma OS no Google
    Calendar. Não faz nada (silenciosamente) se a integração não estiver
    configurada; nunca deixa uma falha do Google derrubar o fluxo de negócio."""
    gcal = get_google_calendar()
    if not gcal:
        return None
    try:
        corpo = _construir_evento_os(os_info)
        existente = _buscar_evento_google_por_os(os_info["id_os"])
        if existente:
            evento = gcal["service"].events().update(
                calendarId=gcal["calendar_id"], eventId=existente["id"], body=corpo,
            ).execute()
        else:
            evento = gcal["service"].events().insert(
                calendarId=gcal["calendar_id"], body=corpo,
            ).execute()
        st.session_state["google_calendar_erro"] = None
        buscar_eventos_google.clear()
        return evento
    except Exception as e:
        st.session_state["google_calendar_erro"] = f"Falha ao sincronizar SS #{os_info['id_os']} com o Google: {e}"
        return None


def excluir_evento_google(id_os):
    gcal = get_google_calendar()
    if not gcal:
        return
    try:
        existente = _buscar_evento_google_por_os(id_os)
        if existente:
            gcal["service"].events().delete(calendarId=gcal["calendar_id"], eventId=existente["id"]).execute()
            buscar_eventos_google.clear()
        st.session_state["google_calendar_erro"] = None
    except Exception as e:
        st.session_state["google_calendar_erro"] = f"Falha ao remover evento da SS #{id_os} no Google: {e}"


@st.cache_data(ttl=30)
def buscar_eventos_google(data_ini, data_fim):
    """Lista os eventos do calendário compartilhado dentro do intervalo
    [data_ini, data_fim]. Cada item retornado já indica se está vinculado a
    uma OS (via extendedProperties) ou se foi criado direto no Google
    ('externo') — usado para mostrar os dois mundos juntos na Agenda."""
    gcal = get_google_calendar()
    if not gcal:
        return []
    time_min = datetime.combine(data_ini, dt_time.min).isoformat() + "-03:00"
    time_max = datetime.combine(data_fim, dt_time.max).isoformat() + "-03:00"
    try:
        resp = gcal["service"].events().list(
            calendarId=gcal["calendar_id"],
            timeMin=time_min, timeMax=time_max,
            singleEvents=True, orderBy="startTime", maxResults=250,
        ).execute()
        eventos = []
        for item in resp.get("items", []):
            props = (item.get("extendedProperties") or {}).get("private") or {}
            eventos.append({
                "id_evento": item.get("id"),
                "id_os": props.get("thaf_id_os"),
                "titulo": item.get("summary") or "(sem título)",
                "descricao": item.get("description") or "",
                "inicio": item.get("start", {}).get("dateTime") or item.get("start", {}).get("date"),
                "fim": item.get("end", {}).get("dateTime") or item.get("end", {}).get("date"),
                "link": item.get("htmlLink"),
                "externo": "thaf_id_os" not in props,
            })
        st.session_state["google_calendar_erro"] = None
        return eventos
    except Exception as e:
        st.session_state["google_calendar_erro"] = f"Falha ao buscar eventos no Google: {e}"
        return []


def sincronizar_intervalo_com_google(ordens: list, data_ini, data_fim):
    """Reenvia (upsert) para o Google todas as OS do intervalo informado.
    Usado pelo botão manual '🔄 Sincronizar agora' da Agenda, cobrindo tanto
    OS novas quanto qualquer uma que tenha ficado dessincronizada."""
    if not google_calendar_configurado():
        return 0
    total = 0
    for o in ordens:
        if o["data_abertura"] and data_ini <= o["data_abertura"] <= data_fim:
            if sincronizar_os_google(o) is not None:
                total += 1
    return total


@st.cache_resource
def get_pool():
    """Cria (uma única vez por processo, graças ao cache_resource) um pool de
    conexões reutilizável com o MySQL. Evita abrir/fechar uma conexão TCP nova
    a cada rerun do Streamlit, que é o maior custo de latência das páginas."""
    return PooledDB(
        creator=pymysql,
        maxconnections=15,
        mincached=2,
        maxcached=5,
        blocking=True,
        ping=1,  # testa a conexão antes de entregá-la (reconecta se caiu)
        host=DB_CONF["host"],
        port=int(DB_CONF["port"]),
        user=DB_CONF["user"],
        password=DB_CONF["password"],
        database=DB_CONF["database"],
        ssl={"ssl": {}},
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def get_connection():
    """Pega uma conexão emprestada do pool. Continua suportando o mesmo
    padrão `conn = get_connection(); ... ; conn.close()` usado no resto do
    código — o `close()` aqui apenas devolve a conexão ao pool."""
    return get_pool().connection()


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


@st.cache_data(ttl=30)
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


@st.cache_data(ttl=30)
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


@st.cache_data(ttl=30)
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


@st.cache_data(ttl=30)
def listar_maquinas(busca: str = ""):
    """Lista as máquinas cadastradas, já com o modelo/fabricante (Modelos_Maquinas)
    e o setor (Setores) integrados via JOIN."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT m.tag_equipamento, m.numero_serie, m.localizacao_maquina,
                       m.tipo_manutencao_padrao, m.status_operacional, m.ultima_manutencao,
                       m.id_setor, m.id_maquina,
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


@st.cache_data(ttl=30)
def listar_modelos_maquinas():
    """Lista os modelos de máquina cadastrados em Modelos_Maquinas, usados para
    vincular uma nova máquina física (Maquinas.id_maquina) a um modelo já existente."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_maquina, nome_maquina, fabricante_maquina, nome_modelo, potencia_especificacao
                FROM Modelos_Maquinas
                ORDER BY nome_maquina
            """)
            return cur.fetchall()
    finally:
        conn.close()


@st.cache_data(ttl=30)
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


@st.cache_data(ttl=30)
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


@st.cache_data(ttl=30)
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


@st.cache_data(ttl=30)
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


@st.cache_data(ttl=30)
def listar_usuarios(busca: str = ""):
    """Lista os usuários com o nome do setor (JOIN com Setores)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT u.id_usuario, u.nome_usuario, u.email_usuario, u.cargo_usuario,
                       u.status_usuario, u.nivel_experiencia, u.disponibilidade_tecnico,
                       u.telefone_usuario, u.data_nasc_usuario, u.data_cadastro,
                       u.id_setor, s.nome_setor
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
            novo_id = cur.lastrowid
    finally:
        conn.close()
    listar_ordens_servico.clear()  # invalida o cache: a nova OS deve aparecer imediatamente
    sincronizar_os_google({
        "id_os": novo_id, "tag_equipamento": tag_equipamento, "descricao_falha": descricao_falha,
        "data_abertura": data_abertura, "hh_inicio": hh_inicio, "hh_fim": hh_fim,
        "status_os": status_os, "tecnico": _nome_usuario_por_id(id_usuario),
    })
    return novo_id


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
    listar_ordens_servico.clear()  # invalida o cache: a edição deve refletir imediatamente
    sincronizar_os_google({
        "id_os": id_os, "tag_equipamento": tag_equipamento, "descricao_falha": descricao_falha,
        "data_abertura": data_abertura, "hh_inicio": hh_inicio, "hh_fim": hh_fim,
        "status_os": status_os, "tecnico": _nome_usuario_por_id(id_usuario),
    })


def excluir_os(id_os):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Ordens_Servico WHERE id_os = %s", (id_os,))
    finally:
        conn.close()
    listar_ordens_servico.clear()  # invalida o cache: a OS excluída não deve mais aparecer
    excluir_evento_google(id_os)  # remove o evento correspondente no Google Calendar, se existir


def criar_maquina(tag_equipamento, numero_serie, localizacao_maquina, tipo_manutencao_padrao,
                   status_operacional, ultima_manutencao, id_setor, id_maquina):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Maquinas
                    (tag_equipamento, numero_serie, localizacao_maquina, tipo_manutencao_padrao,
                     status_operacional, ultima_manutencao, id_setor, id_maquina)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (tag_equipamento, numero_serie, localizacao_maquina, tipo_manutencao_padrao,
                  status_operacional, ultima_manutencao, id_setor, id_maquina))
    finally:
        conn.close()
    listar_maquinas.clear()  # invalida o cache: a nova máquina deve aparecer imediatamente
    listar_setores.clear()   # o total_maquinas por setor também muda


def atualizar_maquina(tag_original, tag_equipamento, numero_serie, localizacao_maquina,
                       tipo_manutencao_padrao, status_operacional, ultima_manutencao,
                       id_setor, id_maquina):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Maquinas
                SET tag_equipamento = %s, numero_serie = %s, localizacao_maquina = %s,
                    tipo_manutencao_padrao = %s, status_operacional = %s, ultima_manutencao = %s,
                    id_setor = %s, id_maquina = %s
                WHERE tag_equipamento = %s
            """, (tag_equipamento, numero_serie, localizacao_maquina, tipo_manutencao_padrao,
                  status_operacional, ultima_manutencao, id_setor, id_maquina, tag_original))
            if tag_original != tag_equipamento:
                # a tag é referenciada em Ordens_Servico; mantém o histórico apontando
                # para a nova tag quando o usuário decide renomeá-la.
                cur.execute(
                    "UPDATE Ordens_Servico SET tag_equipamento = %s WHERE tag_equipamento = %s",
                    (tag_equipamento, tag_original),
                )
    finally:
        conn.close()
    listar_maquinas.clear()
    listar_setores.clear()
    listar_ordens_servico.clear()


def excluir_maquina(tag_equipamento):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Maquinas WHERE tag_equipamento = %s", (tag_equipamento,))
    finally:
        conn.close()
    listar_maquinas.clear()
    listar_setores.clear()


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
if "tema" not in st.session_state:
    st.session_state.tema = "escuro"
if "login_tentativas" not in st.session_state:
    st.session_state.login_tentativas = 0
if "login_bloqueado_ate" not in st.session_state:
    st.session_state.login_bloqueado_ate = None

LIMITE_TENTATIVAS_LOGIN = 5
BLOQUEIO_SEGUNDOS = 30


def fill_demo(email, senha):
    st.session_state.email_input = email
    st.session_state.senha_input = senha


def quick_login(email, senha):
    fill_demo(email, senha)
    do_login()


def login_bloqueado():
    """Retorna quantos segundos faltam de bloqueio (0 se não estiver bloqueado)."""
    bloqueado_ate = st.session_state.login_bloqueado_ate
    if not bloqueado_ate:
        return 0
    restante = (bloqueado_ate - agora_brasil()).total_seconds()
    if restante <= 0:
        st.session_state.login_bloqueado_ate = None
        st.session_state.login_tentativas = 0
        return 0
    return int(restante) + 1


def do_login():
    if login_bloqueado() > 0:
        return

    email_tentativa = st.session_state.email_input.strip().lower()
    with st.spinner("Verificando credenciais..."):
        try:
            row = autenticar(st.session_state.email_input, st.session_state.senha_input)
            if row:
                st.session_state.logged_in = True
                st.session_state.user_data = row
                st.session_state.login_error = False
                st.session_state.login_tentativas = 0
                st.session_state.login_bloqueado_ate = None
                log_acesso(row["id_usuario"], "Login", True)
            else:
                st.session_state.login_error = True
                st.session_state.login_tentativas += 1
                if st.session_state.login_tentativas >= LIMITE_TENTATIVAS_LOGIN:
                    st.session_state.login_bloqueado_ate = agora_brasil() + timedelta(seconds=BLOQUEIO_SEGUNDOS)
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


def alternar_tema():
    st.session_state.tema = "claro" if st.session_state.tema == "escuro" else "escuro"


def paginar_lista(itens, chave: str, tamanho_pagina: int = 15):
    """Pagina uma lista em memória e desenha os controles de navegação
    (Anterior / Próxima + indicador de página). Evita renderizar centenas de
    linhas HTML de uma vez, o que é o maior custo de renderização das telas
    de listagem. Retorna apenas os itens da página atual."""
    chave_pagina = f"pagina_{chave}"
    if chave_pagina not in st.session_state:
        st.session_state[chave_pagina] = 0

    total_itens = len(itens)
    total_paginas = max((total_itens - 1) // tamanho_pagina + 1, 1)

    if st.session_state[chave_pagina] >= total_paginas:
        st.session_state[chave_pagina] = total_paginas - 1
    if st.session_state[chave_pagina] < 0:
        st.session_state[chave_pagina] = 0

    pagina_atual = st.session_state[chave_pagina]
    inicio = pagina_atual * tamanho_pagina
    fim = inicio + tamanho_pagina
    itens_pagina = itens[inicio:fim]

    if total_itens > tamanho_pagina:
        p1, p2, p3 = st.columns([1, 2, 1])
        with p1:
            if st.button("◀ Anterior", key=f"{chave}_prev", disabled=pagina_atual == 0, use_container_width=True):
                st.session_state[chave_pagina] -= 1
                st.rerun()
        with p2:
            st.markdown(
                f'<div style="text-align:center; font-size:12.5px; color:#94a3b8; padding-top:8px;">'
                f'Página {pagina_atual + 1} de {total_paginas} · {total_itens} registro(s)</div>',
                unsafe_allow_html=True,
            )
        with p3:
            if st.button("Próxima ▶", key=f"{chave}_next", disabled=pagina_atual >= total_paginas - 1, use_container_width=True):
                st.session_state[chave_pagina] += 1
                st.rerun()

    return itens_pagina


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

    cor_texto_eixo = "#94a3b8" if st.session_state.tema == "escuro" else "#64748b"
    cor_grade = "rgba(148,163,184,0.18)" if st.session_state.tema == "escuro" else "#eef2f7"

    eixo_valor = dict(showgrid=True, gridcolor=cor_grade, tickfont=dict(color=cor_texto_eixo, size=11.5), zeroline=False)
    eixo_categoria = dict(showgrid=False, tickfont=dict(color=cor_texto_eixo, size=11.5))

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

    fonte = dict(_FONTE_GRAFICOS, color=cor_texto_eixo)
    fig.update_layout(
        margin=dict(l=8, r=8, t=10, b=8),
        height=altura,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=fonte,
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

    cor_texto_eixo = "#94a3b8" if st.session_state.tema == "escuro" else "#64748b"
    cor_grade = "rgba(148,163,184,0.18)" if st.session_state.tema == "escuro" else "#eef2f7"

    fig = px.area(dados, x=categoria_col, y=coluna)
    fig.update_traces(
        line=dict(color=cor, width=2.5),
        fillcolor="rgba(37, 99, 235, 0.12)",
        mode="lines+markers",
        marker=dict(size=6, color=cor),
        hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>",
    )
    fonte = dict(_FONTE_GRAFICOS, color=cor_texto_eixo)
    fig.update_layout(
        margin=dict(l=8, r=8, t=10, b=8),
        height=altura,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=fonte,
        xaxis=dict(showgrid=False, tickfont=dict(color=cor_texto_eixo, size=11.5)),
        yaxis=dict(showgrid=True, gridcolor=cor_grade, tickfont=dict(color=cor_texto_eixo, size=11.5), zeroline=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _minutos_horario(valor):
    """Converte um horário (dt_time ou timedelta cru vindo do MySQL) em minutos
    desde 00:00. Retorna None se o valor for ausente/inválido."""
    t = _to_time(valor)
    if t is None:
        return None
    return t.hour * 60 + t.minute + t.second / 60


def calcular_duracao_horas(hh_inicio, hh_fim):
    """Duração em horas entre hh_inicio e hh_fim (mesmo dia). Retorna None
    quando os horários estão ausentes ou quando hh_fim não é posterior a
    hh_inicio (jornada mal registrada), para não distorcer o MTTR."""
    ini = _minutos_horario(hh_inicio)
    fim = _minutos_horario(hh_fim)
    if ini is None or fim is None or fim <= ini:
        return None
    return (fim - ini) / 60


def calcular_indicadores_manutencao(df_ordens, maquinas):
    """Calcula os indicadores clássicos de manutenção a partir das Ordens de
    Serviço já filtradas (período/técnico) e da lista de máquinas cadastradas:

    - MTTR (Mean Time To Repair): duração média das OS concluídas com
      horário de início e fim válidos.
    - MTBF (Mean Time Between Failures): intervalo médio, em dias, entre
      aberturas consecutivas de OS na mesma tag_equipamento.
    - Backlog: quantidade de OS ainda não concluídas, segmentada por
      faixa de idade (dias desde a abertura).
    - Disponibilidade: % de máquinas cadastradas com status "Operando".

    Retorna um dicionário com os valores agregados e os DataFrames já
    prontos para os gráficos."""
    hoje = agora_brasil().date()

    # ---------- MTTR ----------
    concluidas = df_ordens[df_ordens["status_os"] == "Concluído"].copy()
    if not concluidas.empty:
        concluidas["duracao_horas"] = concluidas.apply(
            lambda r: calcular_duracao_horas(r["hh_inicio"], r["hh_fim"]), axis=1
        )
    else:
        concluidas["duracao_horas"] = pd.Series(dtype=float)

    duracoes_validas = concluidas["duracao_horas"].dropna()
    mttr_horas = duracoes_validas.mean() if not duracoes_validas.empty else None

    if not concluidas.empty and concluidas["duracao_horas"].notna().any():
        concluidas["mes"] = pd.to_datetime(concluidas["data_abertura"].astype(str)).dt.to_period("M").astype(str)
        mttr_mensal = (
            concluidas.dropna(subset=["duracao_horas"])
            .groupby("mes")["duracao_horas"].mean()
            .rename_axis("Mês").reset_index(name="MTTR (h)")
            .sort_values("Mês").set_index("Mês")
        )
    else:
        mttr_mensal = pd.DataFrame()

    # ---------- MTBF ----------
    intervalos = []
    for _tag, grupo in df_ordens.sort_values("data_abertura").groupby("tag_equipamento"):
        datas = grupo["data_abertura"].tolist()
        for i in range(1, len(datas)):
            intervalos.append((datas[i] - datas[i - 1]).days)
    mtbf_dias = (sum(intervalos) / len(intervalos)) if intervalos else None

    # ---------- Backlog por idade ----------
    pendentes = df_ordens[df_ordens["status_os"] != "Concluído"].copy()

    def _faixa_idade(data_abertura):
        dias = (hoje - data_abertura).days
        if dias <= 7:
            return "0-7 dias"
        elif dias <= 15:
            return "8-15 dias"
        elif dias <= 30:
            return "16-30 dias"
        return "+30 dias"

    if not pendentes.empty:
        pendentes["faixa"] = pendentes["data_abertura"].apply(_faixa_idade)
        ordem_faixas = ["0-7 dias", "8-15 dias", "16-30 dias", "+30 dias"]
        df_backlog = (
            pendentes["faixa"].value_counts()
            .reindex(ordem_faixas).fillna(0).astype(int)
            .rename_axis("Faixa").reset_index(name="Quantidade").set_index("Faixa")
        )
    else:
        df_backlog = pd.DataFrame()

    # ---------- Disponibilidade dos equipamentos ----------
    total_maquinas = len(maquinas)
    operando = sum(1 for m in maquinas if m["status_operacional"] == "Operando")
    disponibilidade_pct = (operando / total_maquinas * 100) if total_maquinas else None

    return {
        "mttr_horas": mttr_horas,
        "mttr_mensal": mttr_mensal,
        "mtbf_dias": mtbf_dias,
        "backlog_total": len(pendentes),
        "df_backlog": df_backlog,
        "disponibilidade_pct": disponibilidade_pct,
    }


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
            with st.spinner("Salvando OS..."):
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
        with st.spinner("Salvando alterações..."):
            try:
                atualizar_os(row["id_os"], tag, desc, data_abertura, hh_inicio, hh_fim, status, mapa_tecnicos[tecnico_nome])
                st.success("OS atualizada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar no banco: {e}")


STATUS_OPERACIONAL_OPCOES = ["Operando", "Parado", "Em Manutenção"]


def _mapa_setores():
    try:
        return {s["nome_setor"]: s["id_setor"] for s in listar_setores()}
    except Exception:
        return {}


def _mapa_modelos():
    try:
        return {
            f'{m["nome_maquina"]} · {m["nome_modelo"]} ({m["fabricante_maquina"]})': m["id_maquina"]
            for m in listar_modelos_maquinas()
        }
    except Exception:
        return {}


@st.dialog("Nova Máquina")
def dialog_nova_maquina():
    mapa_setores = _mapa_setores()
    mapa_modelos = _mapa_modelos()

    if not mapa_setores:
        st.warning("Cadastre um setor antes de adicionar uma máquina.")
    if not mapa_modelos:
        st.warning("Nenhum modelo cadastrado em Modelos_Maquinas. Cadastre um modelo antes de continuar.")

    tag = st.text_input("Tag do equipamento", placeholder="Ex: TCV-002")
    numero_serie = st.text_input("Número de série")
    localizacao = st.text_input("Localização")
    tipo_manutencao = st.text_input("Tipo de manutenção padrão", placeholder="Ex: Preventiva mensal")
    c1, c2 = st.columns(2)
    with c1:
        status = st.selectbox("Status operacional", STATUS_OPERACIONAL_OPCOES)
    with c2:
        ultima_manutencao = st.date_input("Última manutenção", value=None)

    setor_nome = st.selectbox("Setor", list(mapa_setores.keys())) if mapa_setores else None
    modelo_nome = st.selectbox("Modelo da máquina", list(mapa_modelos.keys())) if mapa_modelos else None

    if st.button("Salvar Máquina", type="primary"):
        if not tag or not numero_serie or not localizacao or not setor_nome or not modelo_nome:
            st.error("Preencha tag, número de série, localização, setor e modelo.")
        else:
            with st.spinner("Salvando máquina..."):
                try:
                    criar_maquina(
                        tag, numero_serie, localizacao, tipo_manutencao, status,
                        ultima_manutencao, mapa_setores[setor_nome], mapa_modelos[modelo_nome],
                    )
                    st.success("Máquina criada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")


@st.dialog("Editar Máquina")
def dialog_editar_maquina(row):
    mapa_setores = _mapa_setores()
    mapa_modelos = _mapa_modelos()

    tag = st.text_input("Tag do equipamento", value=row["tag_equipamento"])
    numero_serie = st.text_input("Número de série", value=row["numero_serie"])
    localizacao = st.text_input("Localização", value=row["localizacao_maquina"])
    tipo_manutencao = st.text_input("Tipo de manutenção padrão", value=row["tipo_manutencao_padrao"] or "")
    c1, c2 = st.columns(2)
    with c1:
        status = st.selectbox(
            "Status operacional", STATUS_OPERACIONAL_OPCOES,
            index=STATUS_OPERACIONAL_OPCOES.index(row["status_operacional"])
            if row["status_operacional"] in STATUS_OPERACIONAL_OPCOES else 0,
        )
    with c2:
        ultima_manutencao = st.date_input("Última manutenção", value=row["ultima_manutencao"])

    nomes_setores = list(mapa_setores.keys())
    setor_atual = row.get("nome_setor")
    idx_setor = nomes_setores.index(setor_atual) if setor_atual in nomes_setores else 0
    setor_nome = st.selectbox("Setor", nomes_setores, index=idx_setor) if nomes_setores else None

    nomes_modelos = list(mapa_modelos.keys())
    modelo_atual = f'{row.get("nome_maquina")} · {row.get("nome_modelo")} ({row.get("fabricante_maquina")})'
    idx_modelo = nomes_modelos.index(modelo_atual) if modelo_atual in nomes_modelos else 0
    modelo_nome = st.selectbox("Modelo da máquina", nomes_modelos, index=idx_modelo) if nomes_modelos else None

    if st.button("Salvar alterações", type="primary"):
        with st.spinner("Salvando alterações..."):
            try:
                atualizar_maquina(
                    row["tag_equipamento"], tag, numero_serie, localizacao, tipo_manutencao, status,
                    ultima_manutencao, mapa_setores[setor_nome], mapa_modelos[modelo_nome],
                )
                st.success("Máquina atualizada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar no banco: {e}")


@st.dialog("Histórico de Manutenção")
def dialog_historico_maquina(row):
    """Monta o histórico de manutenção da máquina a partir das Ordens de Serviço
    já registradas para a sua tag_equipamento — sem depender de uma tabela extra."""
    st.markdown(f"**{row['tag_equipamento']}** · {row['nome_maquina']} ({row['nome_modelo']})")

    try:
        with st.spinner("Carregando histórico..."):
            ordens = listar_ordens_servico()
    except Exception as e:
        st.error(f"Não foi possível carregar o histórico: {e}")
        return

    historico = [o for o in ordens if o["tag_equipamento"] == row["tag_equipamento"]]

    if not historico:
        st.info("Nenhuma Ordem de Serviço registrada para esta máquina ainda.")
        return

    total = len(historico)
    concluidas = sum(1 for o in historico if o["status_os"] == "Concluído")
    k1, k2 = st.columns(2)
    k1.metric("OS registradas", total)
    k2.metric("Concluídas", concluidas)

    st.markdown("---")
    for o in historico:
        slug = status_slug(o["status_os"])
        st.markdown(
            f'<div class="os-row">'
            f'<b>{o["data_abertura"]}</b> · {o["hh_inicio"]} → {o["hh_fim"] or "—"} '
            f'<span class="status-badge status-{slug}">{o["status_os"]}</span><br>'
            f'<span class="os-cell">{o["descricao_falha"]}</span><br>'
            f'<span class="os-cell-muted">Técnico: {o["tecnico"] or "—"} · OS #{o["id_os"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ============================================================================
# SETORES — CRUD (criar/atualizar) + dialogs
# ============================================================================
def criar_setor(nome_setor, descricao_setor):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Setores (nome_setor, descricao_setor) VALUES (%s, %s)",
                (nome_setor, descricao_setor),
            )
    finally:
        conn.close()
    listar_setores.clear()


def atualizar_setor(id_setor, nome_setor, descricao_setor):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Setores SET nome_setor = %s, descricao_setor = %s WHERE id_setor = %s",
                (nome_setor, descricao_setor, id_setor),
            )
    finally:
        conn.close()
    listar_setores.clear()


@st.dialog("Novo Setor")
def dialog_novo_setor():
    nome = st.text_input("Nome do setor", placeholder="Ex: Manutenção Mecânica")
    descricao = st.text_area("Descrição", placeholder="Descrição opcional do setor")

    if st.button("Salvar Setor", type="primary"):
        if not nome:
            st.error("Informe o nome do setor.")
        else:
            with st.spinner("Salvando setor..."):
                try:
                    criar_setor(nome, descricao or None)
                    st.success("Setor criado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")


@st.dialog("Editar Setor")
def dialog_editar_setor(row):
    nome = st.text_input("Nome do setor", value=row["nome_setor"])
    descricao = st.text_area("Descrição", value=row["descricao_setor"] or "")

    if st.button("Salvar alterações", type="primary"):
        with st.spinner("Salvando alterações..."):
            try:
                atualizar_setor(row["id_setor"], nome, descricao or None)
                st.success("Setor atualizado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar no banco: {e}")


# ============================================================================
# ALMOXARIFADO — PEÇAS — CRUD (criar/atualizar) + dialogs
# ============================================================================
def criar_peca(nome_peca, quantidade_estoque, unidade_medida, custo_unitario):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Almoxarifado_Pecas
                    (nome_peca, quantidade_estoque, unidade_medida, custo_unitario)
                VALUES (%s, %s, %s, %s)
                """,
                (nome_peca, quantidade_estoque, unidade_medida, custo_unitario),
            )
    finally:
        conn.close()
    listar_pecas.clear()


def atualizar_peca(id_peca, nome_peca, quantidade_estoque, unidade_medida, custo_unitario):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE Almoxarifado_Pecas
                SET nome_peca = %s, quantidade_estoque = %s,
                    unidade_medida = %s, custo_unitario = %s
                WHERE id_peca = %s
                """,
                (nome_peca, quantidade_estoque, unidade_medida, custo_unitario, id_peca),
            )
    finally:
        conn.close()
    listar_pecas.clear()


@st.dialog("Nova Peça")
def dialog_nova_peca():
    nome = st.text_input("Nome da peça", placeholder="Ex: Rolamento 6205")
    c1, c2, c3 = st.columns(3)
    with c1:
        quantidade = st.number_input("Quantidade em estoque", min_value=0, step=1)
    with c2:
        unidade = st.text_input("Unidade de medida", placeholder="Ex: UN, KG, M")
    with c3:
        custo = st.number_input("Custo unitário (R$)", min_value=0.0, step=0.01, format="%.2f")

    if st.button("Salvar Peça", type="primary"):
        if not nome or not unidade:
            st.error("Preencha nome e unidade de medida.")
        else:
            with st.spinner("Salvando peça..."):
                try:
                    criar_peca(nome, int(quantidade), unidade, float(custo))
                    st.success("Peça criada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")


@st.dialog("Editar Peça")
def dialog_editar_peca(row):
    nome = st.text_input("Nome da peça", value=row["nome_peca"])
    c1, c2, c3 = st.columns(3)
    with c1:
        quantidade = st.number_input(
            "Quantidade em estoque", min_value=0, step=1,
            value=int(row["quantidade_estoque"]),
        )
    with c2:
        unidade = st.text_input("Unidade de medida", value=row["unidade_medida"])
    with c3:
        custo = st.number_input(
            "Custo unitário (R$)", min_value=0.0, step=0.01, format="%.2f",
            value=float(row["custo_unitario"]),
        )

    if st.button("Salvar alterações", type="primary"):
        with st.spinner("Salvando alterações..."):
            try:
                atualizar_peca(row["id_peca"], nome, int(quantidade), unidade, float(custo))
                st.success("Peça atualizada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar no banco: {e}")


# ============================================================================
# FERRAMENTAS — CRUD (criar/atualizar) + dialogs
# ============================================================================
def criar_ferramenta(nome_ferramenta, status_ferramenta):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Almoxarifado_Ferramentas (nome_ferramenta, status_ferramenta) VALUES (%s, %s)",
                (nome_ferramenta, status_ferramenta),
            )
    finally:
        conn.close()
    listar_ferramentas.clear()


def atualizar_ferramenta(id_ferramenta, nome_ferramenta, status_ferramenta):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Almoxarifado_Ferramentas SET nome_ferramenta = %s, status_ferramenta = %s WHERE id_ferramenta = %s",
                (nome_ferramenta, status_ferramenta, id_ferramenta),
            )
    finally:
        conn.close()
    listar_ferramentas.clear()


STATUS_FERRAMENTA_OPCOES = list(STATUS_FERRAMENTA_CORES.keys())


@st.dialog("Nova Ferramenta")
def dialog_nova_ferramenta():
    nome = st.text_input("Nome da ferramenta", placeholder='Ex: Torquímetro 1/2"')
    status = st.selectbox("Status", STATUS_FERRAMENTA_OPCOES)

    if st.button("Salvar Ferramenta", type="primary"):
        if not nome:
            st.error("Informe o nome da ferramenta.")
        else:
            with st.spinner("Salvando ferramenta..."):
                try:
                    criar_ferramenta(nome, status)
                    st.success("Ferramenta criada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")


@st.dialog("Editar Ferramenta")
def dialog_editar_ferramenta(row):
    nome = st.text_input("Nome da ferramenta", value=row["nome_ferramenta"])
    status = st.selectbox(
        "Status", STATUS_FERRAMENTA_OPCOES,
        index=STATUS_FERRAMENTA_OPCOES.index(row["status_ferramenta"])
        if row["status_ferramenta"] in STATUS_FERRAMENTA_OPCOES else 0,
    )
    st.caption(
        "⚠️ Alterar o status aqui não cria/fecha registros em "
        "Movimentacao_Ferramentas — use esta tela só para correções de cadastro."
    )

    if st.button("Salvar alterações", type="primary"):
        with st.spinner("Salvando alterações..."):
            try:
                atualizar_ferramenta(row["id_ferramenta"], nome, status)
                st.success("Ferramenta atualizada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar no banco: {e}")


# ============================================================================
# MATRIZ DE RISCOS / EPI — CRUD (criar/atualizar) + dialogs
# ============================================================================
def criar_risco(risco_nr01, epis_obrigatorios):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Matriz_Riscos_EPI (risco_nr01, epis_obrigatorios) VALUES (%s, %s)",
                (risco_nr01, epis_obrigatorios),
            )
    finally:
        conn.close()
    listar_riscos.clear()


def atualizar_risco(id_risco, risco_nr01, epis_obrigatorios):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Matriz_Riscos_EPI SET risco_nr01 = %s, epis_obrigatorios = %s WHERE id_risco = %s",
                (risco_nr01, epis_obrigatorios, id_risco),
            )
    finally:
        conn.close()
    listar_riscos.clear()


@st.dialog("Novo Risco")
def dialog_novo_risco():
    risco = st.text_input("Risco (NR-01)", placeholder="Ex: Risco de queda de altura")
    epis = st.text_area("EPIs obrigatórios", placeholder="Ex: Capacete, cinto de segurança, luvas")

    if st.button("Salvar Risco", type="primary"):
        if not risco or not epis:
            st.error("Preencha o risco e os EPIs obrigatórios.")
        else:
            with st.spinner("Salvando risco..."):
                try:
                    criar_risco(risco, epis)
                    st.success("Risco criado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")


@st.dialog("Editar Risco")
def dialog_editar_risco(row):
    risco = st.text_input("Risco (NR-01)", value=row["risco_nr01"])
    epis = st.text_area("EPIs obrigatórios", value=row["epis_obrigatorios"])

    if st.button("Salvar alterações", type="primary"):
        with st.spinner("Salvando alterações..."):
            try:
                atualizar_risco(row["id_risco"], risco, epis)
                st.success("Risco atualizado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar no banco: {e}")


# ============================================================================
# USUÁRIOS — CRUD (criar/atualizar) + dialogs
#
# AJUSTE as listas abaixo para o domínio real das colunas no seu MySQL,
# se houver ENUM/CHECK com valores diferentes destes:
# ============================================================================
CARGO_USUARIO_OPCOES = ["CEO", "Gerente", "Supervisor", "Tecnico"]
STATUS_USUARIO_OPCOES = ["Ativo", "Inativo"]
DISPONIBILIDADE_TECNICO_OPCOES = ["Disponível", "Em Campo", "Férias", "Afastado"]
NIVEL_EXPERIENCIA_OPCOES = ["Júnior", "Pleno", "Sênior"]


def criar_usuario(nome_usuario, email_usuario, senha, cargo_usuario, status_usuario,
                   nivel_experiencia, disponibilidade_tecnico, telefone_usuario,
                   data_nasc_usuario, id_setor):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Usuarios
                    (nome_usuario, email_usuario, senha, cargo_usuario, status_usuario,
                     nivel_experiencia, disponibilidade_tecnico, telefone_usuario,
                     data_nasc_usuario, data_cadastro, id_setor)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    nome_usuario, email_usuario.strip().lower(), hash_senha(senha),
                    cargo_usuario, status_usuario, nivel_experiencia, disponibilidade_tecnico,
                    telefone_usuario, data_nasc_usuario, agora_brasil(), id_setor,
                ),
            )
    finally:
        conn.close()
    listar_usuarios.clear()
    listar_setores.clear()   # total_usuarios por setor muda
    listar_tecnicos.clear()  # se o novo usuário for técnico ativo


def atualizar_usuario(id_usuario, nome_usuario, email_usuario, cargo_usuario, status_usuario,
                       nivel_experiencia, disponibilidade_tecnico, telefone_usuario,
                       data_nasc_usuario, id_setor, nova_senha=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if nova_senha:
                cur.execute(
                    """
                    UPDATE Usuarios
                    SET nome_usuario = %s, email_usuario = %s, senha = %s, cargo_usuario = %s,
                        status_usuario = %s, nivel_experiencia = %s, disponibilidade_tecnico = %s,
                        telefone_usuario = %s, data_nasc_usuario = %s, id_setor = %s
                    WHERE id_usuario = %s
                    """,
                    (
                        nome_usuario, email_usuario.strip().lower(), hash_senha(nova_senha),
                        cargo_usuario, status_usuario, nivel_experiencia, disponibilidade_tecnico,
                        telefone_usuario, data_nasc_usuario, id_setor, id_usuario,
                    ),
                )
            else:
                cur.execute(
                    """
                    UPDATE Usuarios
                    SET nome_usuario = %s, email_usuario = %s, cargo_usuario = %s,
                        status_usuario = %s, nivel_experiencia = %s, disponibilidade_tecnico = %s,
                        telefone_usuario = %s, data_nasc_usuario = %s, id_setor = %s
                    WHERE id_usuario = %s
                    """,
                    (
                        nome_usuario, email_usuario.strip().lower(), cargo_usuario, status_usuario,
                        nivel_experiencia, disponibilidade_tecnico, telefone_usuario,
                        data_nasc_usuario, id_setor, id_usuario,
                    ),
                )
    finally:
        conn.close()
    listar_usuarios.clear()
    listar_setores.clear()
    listar_tecnicos.clear()


@st.dialog("Novo Usuário")
def dialog_novo_usuario():
    mapa_setores = _mapa_setores()
    if not mapa_setores:
        st.warning("Cadastre um setor antes de adicionar um usuário.")

    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail", placeholder="nome@empresa.com")
    senha = st.text_input("Senha", type="password")

    c1, c2 = st.columns(2)
    with c1:
        cargo = st.selectbox("Cargo", CARGO_USUARIO_OPCOES)
    with c2:
        status = st.selectbox("Status", STATUS_USUARIO_OPCOES)

    is_tecnico = cargo == "Tecnico"
    c3, c4 = st.columns(2)
    with c3:
        nivel = st.selectbox("Nível de experiência", NIVEL_EXPERIENCIA_OPCOES)
    with c4:
        if is_tecnico:
            disponibilidade = st.selectbox("Disponibilidade", DISPONIBILIDADE_TECNICO_OPCOES)
        else:
            disponibilidade = None
            st.caption("Disponibilidade se aplica apenas a técnicos.")

    c5, c6 = st.columns(2)
    with c5:
        telefone = st.text_input("Telefone", placeholder="(00) 00000-0000")
    with c6:
        data_nasc = st.date_input("Data de nascimento", value=None)

    setor_nome = st.selectbox("Setor", list(mapa_setores.keys())) if mapa_setores else None

    if st.button("Salvar Usuário", type="primary"):
        if not nome or not email or not senha or not setor_nome:
            st.error("Preencha nome, e-mail, senha e setor.")
        else:
            with st.spinner("Salvando usuário..."):
                try:
                    criar_usuario(
                        nome, email, senha, cargo, status, nivel, disponibilidade,
                        telefone, data_nasc, mapa_setores[setor_nome],
                    )
                    st.success("Usuário criado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")


@st.dialog("Editar Usuário")
def dialog_editar_usuario(row):
    mapa_setores = _mapa_setores()

    nome = st.text_input("Nome completo", value=row["nome_usuario"])
    email = st.text_input("E-mail", value=row["email_usuario"])
    nova_senha = st.text_input("Nova senha (deixe em branco para manter a atual)", type="password")

    c1, c2 = st.columns(2)
    with c1:
        cargo = st.selectbox(
            "Cargo", CARGO_USUARIO_OPCOES,
            index=CARGO_USUARIO_OPCOES.index(row["cargo_usuario"])
            if row["cargo_usuario"] in CARGO_USUARIO_OPCOES else 0,
        )
    with c2:
        status = st.selectbox(
            "Status", STATUS_USUARIO_OPCOES,
            index=STATUS_USUARIO_OPCOES.index(row["status_usuario"])
            if row["status_usuario"] in STATUS_USUARIO_OPCOES else 0,
        )

    is_tecnico = cargo == "Tecnico"
    c3, c4 = st.columns(2)
    with c3:
        nivel = st.selectbox(
            "Nível de experiência", NIVEL_EXPERIENCIA_OPCOES,
            index=NIVEL_EXPERIENCIA_OPCOES.index(row["nivel_experiencia"])
            if row["nivel_experiencia"] in NIVEL_EXPERIENCIA_OPCOES else 0,
        )
    with c4:
        if is_tecnico:
            disp_atual = row.get("disponibilidade_tecnico")
            idx_disp = (
                DISPONIBILIDADE_TECNICO_OPCOES.index(disp_atual)
                if disp_atual in DISPONIBILIDADE_TECNICO_OPCOES else 0
            )
            disponibilidade = st.selectbox("Disponibilidade", DISPONIBILIDADE_TECNICO_OPCOES, index=idx_disp)
        else:
            disponibilidade = None
            st.caption("Disponibilidade se aplica apenas a técnicos.")

    c5, c6 = st.columns(2)
    with c5:
        telefone = st.text_input("Telefone", value=row["telefone_usuario"] or "")
    with c6:
        data_nasc = st.date_input("Data de nascimento", value=row["data_nasc_usuario"])

    nomes_setores = list(mapa_setores.keys())
    setor_atual = row.get("nome_setor")
    idx_setor = nomes_setores.index(setor_atual) if setor_atual in nomes_setores else 0
    setor_nome = st.selectbox("Setor", nomes_setores, index=idx_setor) if nomes_setores else None

    if st.button("Salvar alterações", type="primary"):
        with st.spinner("Salvando alterações..."):
            try:
                atualizar_usuario(
                    row["id_usuario"], nome, email, cargo, status, nivel, disponibilidade,
                    telefone, data_nasc, mapa_setores[setor_nome], nova_senha or None,
                )
                st.success("Usuário atualizado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar no banco: {e}")


@st.dialog("Confirmar exclusão")
def dialog_confirmar_exclusao(mensagem: str, funcao_excluir, *args):
    """Modal genérico de confirmação de exclusão, reutilizado por todas as
    telas do sistema. Só executa `funcao_excluir(*args)` se o usuário
    confirmar explicitamente — nunca exclui direto no clique da lixeira."""
    st.warning(f"⚠️ {mensagem}")
    st.caption("Esta ação não pode ser desfeita.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sim, excluir", type="primary", use_container_width=True):
            with st.spinner("Excluindo..."):
                try:
                    funcao_excluir(*args)
                    st.success("Excluído com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir: {e}")
    with c2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()


def excluir_setor(id_setor):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Setores WHERE id_setor = %s", (id_setor,))
    finally:
        conn.close()
    listar_setores.clear()


def excluir_peca(id_peca):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Almoxarifado_Pecas WHERE id_peca = %s", (id_peca,))
    finally:
        conn.close()
    listar_pecas.clear()


def excluir_ferramenta(id_ferramenta):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Almoxarifado_Ferramentas WHERE id_ferramenta = %s", (id_ferramenta,))
    finally:
        conn.close()
    listar_ferramentas.clear()


def excluir_risco(id_risco):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Matriz_Riscos_EPI WHERE id_risco = %s", (id_risco,))
    finally:
        conn.close()
    listar_riscos.clear()


def excluir_usuario(id_usuario):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Usuarios WHERE id_usuario = %s", (id_usuario,))
    finally:
        conn.close()
    listar_usuarios.clear()


# ------------------------------------------------------------------
# TEMA (claro/escuro) — paleta de cores conforme st.session_state.tema
# ------------------------------------------------------------------
if st.session_state.tema == "escuro":
    TEMA = dict(
        app_bg="#0b1220",
        sidebar_bg="#0f172a",
        card_bg="#111827",
        card_border="#1f2937",
        text_primary="#e5e7eb",
        text_secondary="#94a3b8",
        text_muted="#64748b",
        input_bg="#0b1220",
        input_border="#1f2937",
        table_header_border="#1f2937",
        row_border="#1f2937",
    )
else:
    TEMA = dict(
        app_bg="#f1f5f9",
        sidebar_bg="#0f172a",
        card_bg="#ffffff",
        card_border="#e2e8f0",
        text_primary="#0f172a",
        text_secondary="#64748b",
        text_muted="#64748b",
        input_bg="#ffffff",
        input_border="#e2e8f0",
        table_header_border="#e2e8f0",
        row_border="#e2e8f0",
    )

st.markdown(f"""
<style>
#MainMenu, header, footer {{visibility: hidden;}}
html, body {{margin: 0; padding: 0;}}
.block-container {{padding: 0 !important; max-width: 100% !important;}}
.stApp {{background: #0b1b3a;}}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {{padding: 0 !important;}}

/* ======================================================================
   TELA DE LOGIN — estilo "foguete", tons de azul, tela inteira
   ====================================================================== */
.st-key-unified_panel {{
    padding: 0;
    margin: 0;
    min-height: 100vh;
    display: grid !important;
    grid-template-columns: 48fr 52fr;
    align-items: stretch;
}}
.st-key-unified_panel > div,
.st-key-unified_panel > div > div,
.st-key-unified_panel > div > div > div {{
    height: 100%;
}}

/* ---------- Painel esquerdo: decorativo, foguete, várias tonalidades de azul ---------- */
.st-key-rocket_panel {{
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
}}
.st-key-rocket_panel::before {{
    content: "";
    position: absolute;
    top: -70px; right: -70px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
}}
.st-key-rocket_panel::after {{
    content: "";
    position: absolute;
    bottom: -90px; left: -50px;
    width: 240px; height: 240px;
    border-radius: 50%;
    background: rgba(56,189,248,0.30);
}}
.rocket-mid-circle {{
    position: absolute;
    top: 50%; left: 8%;
    transform: translateY(-50%);
    width: 26px; height: 26px;
    border-radius: 50%;
    background: rgba(255,255,255,0.18);
}}

.brand-box {{display: flex; align-items: center; gap: 14px; position: relative; z-index: 2;}}
.brand-icon {{
    background: rgba(255,255,255,0.18);
    border-radius: 16px;
    width: 56px; height: 56px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    flex-shrink: 0;
}}
.brand-title {{font-weight: 800; font-size: 21px; line-height: 1.1;}}
.brand-sub {{font-size: 13.5px; opacity: 0.8;}}

.rocket-stage {{
    position: relative;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
}}
.rocket-ring {{
    position: absolute;
    width: 320px; height: 320px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.18);
    background: rgba(255,255,255,0.04);
}}
.smoke-cloud {{
    position: absolute;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.40) 0%, rgba(255,255,255,0.08) 55%, transparent 72%);
    filter: blur(1px);
}}
.rocket-emoji {{
    position: relative;
    font-size: 128px;
    transform: rotate(-40deg);
    filter: drop-shadow(0 22px 22px rgba(2,6,23,0.55));
}}

.rocket-tagline {{
    position: relative;
    z-index: 2;
    font-size: 26px;
    font-weight: 800;
    line-height: 1.35;
    max-width: 380px;
}}
.rocket-tagline span {{
    display: block;
    font-size: 14.5px;
    font-weight: 400;
    color: rgba(255,255,255,0.75);
    margin-top: 10px;
}}

/* ---------- Painel direito: cartão de login, cobrindo a tela toda ---------- */
.st-key-login_card {{
    box-sizing: border-box;
    width: 100%;
    min-height: 100vh;
    padding: 72px 9vw;
    margin: 0;
    background: {TEMA['card_bg']};
    display: flex !important;
    flex-direction: column;
    justify-content: center;
}}
.login-eyebrow {{
    color: #2563eb;
    font-weight: 700;
    font-size: 12.5px;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    margin-bottom: 10px;
}}
.login-title {{font-size: 40px; font-weight: 800; color: {TEMA['text_primary']}; margin-bottom: 8px;}}
.login-sub {{color: {TEMA['text_secondary']}; font-size: 15.5px; margin-bottom: 36px;}}

div[data-testid="stTextInput"] label p {{color: {TEMA['text_primary']} !important; font-size: 14.5px !important; font-weight: 600;}}

div[data-testid="stTextInput"] input {{
    border-radius: 999px !important;
    border: 1.5px solid {TEMA['input_border']} !important;
    background: {TEMA['input_bg']} !important;
    color: {TEMA['text_primary']} !important;
    padding: 16px 22px !important;
    font-size: 15.5px !important;
}}
div[data-testid="stTextInput"] input:focus {{
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.20) !important;
}}
div[data-testid="stTextInput"] input::placeholder {{color: #94a3b8 !important;}}
div[data-testid="stTextInput"] {{margin-bottom: 10px;}}

.login-row {{
    display: flex; justify-content: space-between; align-items: center;
    font-size: 13.5px; color: {TEMA['text_secondary']}; margin: 4px 4px 22px 4px;
}}
.login-row .login-link {{color: #2563eb; font-weight: 600; cursor: pointer;}}

.stButton>button {{width: 100%; border-radius: 999px; font-weight: 700; font-size: 16.5px;}}

.st-key-entrar_btn_wrap button {{
    background: linear-gradient(90deg, #1d4ed8 0%, #38bdf8 100%);
    color: #ffffff; border: none; padding: 17px 0; font-weight: 700; font-size: 16.5px;
    box-shadow: 0 12px 24px rgba(29,78,216,0.35);
}}
.st-key-entrar_btn_wrap button:hover {{filter: brightness(1.05);}}
.st-key-entrar_btn_wrap button:disabled {{opacity: 0.55; box-shadow: none; cursor: not-allowed;}}

.demo-label {{
    font-size: 12px; letter-spacing: 0.08em; color: #94a3b8;
    text-transform: uppercase; font-weight: 700; margin: 38px 0 14px 2px;
}}
.st-key-demo_0 button, .st-key-demo_1 button,
.st-key-demo_2 button, .st-key-demo_3 button {{
    background: {"#111827" if st.session_state.tema == "escuro" else "#eff6ff"};
    border: 1.5px solid {"#1f2937" if st.session_state.tema == "escuro" else "#bfdbfe"};
    border-radius: 14px;
    text-align: left; padding: 14px 16px;
    color: {"#93c5fd" if st.session_state.tema == "escuro" else "#1e3a8a"};
    white-space: pre-line;
    font-size: 13.5px;
    font-weight: 600;
}}
.st-key-demo_0 button:hover, .st-key-demo_1 button:hover,
.st-key-demo_2 button:hover, .st-key-demo_3 button:hover {{
    border-color: #38bdf8; background: {"#1e293b" if st.session_state.tema == "escuro" else "#dbeafe"};
}}

.tema-toggle-wrap {{position: absolute; top: 28px; right: 28px; z-index: 3;}}
.st-key-tema_toggle_login button, .st-key-tema_toggle_app button {{
    width: auto; border-radius: 999px; padding: 8px 16px; font-size: 13px; font-weight: 700;
    background: {"rgba(255,255,255,0.10)" if st.session_state.tema == "escuro" else "#eff6ff"};
    color: {"#e5e7eb" if st.session_state.tema == "escuro" else "#1e3a8a"};
    border: 1.5px solid {"rgba(255,255,255,0.18)" if st.session_state.tema == "escuro" else "#bfdbfe"};
}}

/* ================================================================
   PÓS-LOGIN: sidebar + tela de Ordens de Serviço
   ================================================================ */
.stApp {{background: {TEMA['app_bg']};}}

.st-key-sidebar {{
    background: {TEMA['sidebar_bg']};
    min-height: 100vh;
    padding: 24px 16px;
    color: white;
}}
.sidebar-brand {{display: flex; align-items: center; gap: 10px; padding: 0 8px 20px 8px;}}
.sidebar-brand-icon {{
    background: #2563eb; border-radius: 10px; width: 38px; height: 38px;
    display: flex; align-items: center; justify-content: center; font-size: 17px;
}}
.sidebar-brand-title {{font-weight: 800; font-size: 14.5px; color: white; line-height: 1.1;}}
.sidebar-brand-sub {{font-size: 10.5px; color: rgba(255,255,255,0.55);}}
.sidebar-section-label {{
    font-size: 10.5px; letter-spacing: 0.06em; color: rgba(255,255,255,0.45);
    text-transform: uppercase; margin: 14px 8px 6px 8px;
}}
.st-key-sidebar .stButton>button {{
    background: transparent; color: rgba(255,255,255,0.75); border: none;
    text-align: left; font-weight: 500; font-size: 13.5px; padding: 8px 10px;
    border-radius: 8px;
}}
.st-key-sidebar .stButton>button:hover {{background: rgba(255,255,255,0.08); color: white;}}

.topbar-title {{font-size: 22px; font-weight: 800; color: {TEMA['text_primary']};}}
.topbar-breadcrumb {{font-size: 12.5px; color: {TEMA['text_muted']}; margin-bottom: 2px;}}
.topbar-sub {{color: {TEMA['text_secondary']}; font-size: 13.5px; margin: 4px 0 18px 0;}}

.status-badge {{
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11.5px; font-weight: 700;
}}
.status-aberto {{background: #fee2e2; color: #b91c1c;}}
.status-em-andamento {{background: #dbeafe; color: #1d4ed8;}}
.status-concluido {{background: #dcfce7; color: #15803d;}}

.os-row {{border-bottom: 1px solid {TEMA['row_border']}; padding: 10px 0;}}
.os-header {{font-size: 11.5px; letter-spacing: 0.04em; color: {TEMA['text_muted']}; text-transform: uppercase; padding-bottom: 8px; border-bottom: 1px solid {TEMA['table_header_border']};}}
.os-cell {{font-size: 13.5px; color: {TEMA['text_primary']};}}
.os-cell-muted {{font-size: 12px; color: {TEMA['text_muted']};}}

.st-key-topbar_search input {{
    border-radius: 8px !important; border: 1px solid {TEMA['input_border']} !important;
    background: {TEMA['input_bg']} !important; color: {TEMA['text_primary']} !important;
}}
.st-key-nova_os_btn button {{background: #2563eb; color: white; border: none; font-weight: 700;}}
.st-key-nova_os_btn button:hover {{background: #1d4ed8; color: white;}}
.st-key-logout_btn button {{background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca;}}

/* ---------- Tela de Máquinas: KPIs e gráficos ---------- */
.kpi-card {{
    background: {TEMA['card_bg']};
    border: 1px solid {TEMA['card_border']};
    border-left: 5px solid #2563eb;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 8px;
}}
.kpi-card.kpi-green {{border-left-color: #16a34a;}}
.kpi-card.kpi-red {{border-left-color: #dc2626;}}
.kpi-card.kpi-blue {{border-left-color: #0ea5e9;}}
.kpi-value {{font-size: 26px; font-weight: 800; color: {TEMA['text_primary']}; line-height: 1.1;}}
.kpi-label {{font-size: 12.5px; color: {TEMA['text_secondary']}; margin-top: 4px;}}

.chart-card {{
    background: {TEMA['card_bg']};
    border: 1px solid {TEMA['card_border']};
    border-radius: 12px;
    padding: 18px 20px 6px 20px;
    margin-bottom: 16px;
}}
.chart-title {{font-size: 14px; font-weight: 700; color: {TEMA['text_primary']}; margin-bottom: 10px;}}

.status-operando {{background: #dcfce7; color: #15803d;}}
.status-parado {{background: #fee2e2; color: #b91c1c;}}
.status-em-manutencao {{background: #dbeafe; color: #1d4ed8;}}

/* ---------- Tela de Setores ---------- */
.setor-card {{
    background: {TEMA['card_bg']};
    border: 1px solid {TEMA['card_border']};
    border-radius: 14px;
    padding: 20px 22px;
    height: 100%;
    box-sizing: border-box;
}}
.setor-card-title {{font-size: 16px; font-weight: 800; color: {TEMA['text_primary']}; margin-bottom: 4px;}}
.setor-card-desc {{font-size: 12.5px; color: {TEMA['text_secondary']}; margin-bottom: 16px; min-height: 32px;}}
.setor-card-stats {{display: flex; gap: 22px;}}
.setor-stat-value {{font-size: 22px; font-weight: 800; color: #2563eb; line-height: 1;}}
.setor-stat-label {{font-size: 11px; color: #94a3b8; margin-top: 3px;}}

/* ---------- Tela de Almoxarifado — Peças ---------- */
.estoque-baixo {{color: #b91c1c; font-weight: 700;}}
.estoque-ok {{color: {TEMA['text_primary']};}}

/* ---------- Tela de Ferramentas ---------- */
.status-disponivel {{background: #dcfce7; color: #15803d;}}
.status-solicitada {{background: #fef9c3; color: #a16207;}}
.status-em-uso {{background: #dbeafe; color: #1d4ed8;}}
.status-manutencao-calibracao {{background: #ede9fe; color: #6d28d9;}}
.status-extraviada {{background: #fee2e2; color: #b91c1c;}}

/* ---------- Tela de Matriz de Risco / EPI ---------- */
.risco-card {{
    background: {TEMA['card_bg']};
    border: 1px solid {TEMA['card_border']};
    border-left: 5px solid #dc2626;
    border-radius: 14px;
    padding: 18px 20px;
    height: 100%;
    box-sizing: border-box;
}}
.risco-card-title {{font-size: 15px; font-weight: 800; color: {TEMA['text_primary']}; margin-bottom: 8px;}}
.risco-card-epis {{font-size: 12.5px; color: {TEMA['text_secondary']}; line-height: 1.5; margin-bottom: 12px;}}
.risco-card-tag {{
    display: inline-block; font-size: 11px; font-weight: 700; color: #b91c1c;
    background: #fee2e2; border-radius: 20px; padding: 3px 10px;
}}

/* ---------- Tela de Usuários ---------- */
.status-ativo {{background: #dcfce7; color: #15803d;}}
.status-inativo {{background: #f1f5f9; color: #64748b;}}
.status-em-campo {{background: #dbeafe; color: #1d4ed8;}}
.status-ferias {{background: #fef9c3; color: #a16207;}}
.status-afastado {{background: #fee2e2; color: #b91c1c;}}
.user-avatar {{
    width: 34px; height: 34px; border-radius: 50%;
    background: #2563eb; color: #ffffff; font-weight: 700; font-size: 13px;
    display: flex; align-items: center; justify-content: center;
}}
.user-name-cell {{display: flex; align-items: center; gap: 10px;}}
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
            with st.container(key="tema_toggle_app"):
                icone_tema = "☀️ Modo claro" if st.session_state.tema == "escuro" else "🌙 Modo escuro"
                st.button(icone_tema, on_click=alternar_tema, use_container_width=True)
            st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
            with st.container(key="logout_btn"):
                if st.button("Sair", use_container_width=True):
                    with st.spinner("Saindo..."):
                        do_logout()
                    st.rerun()

    with col_main:
        top1, top2 = st.columns([2, 1])
        with top1:
            st.markdown('<div class="topbar-breadcrumb">Manutenção / Ordens de Serviço</div>', unsafe_allow_html=True)
            st.markdown('<div class="topbar-title">Ordens de Serviço</div>', unsafe_allow_html=True)
        with top2:
            st.markdown(
                f'<div style="text-align:right; font-size:13px; color:{TEMA["text_primary"]};">'
                f'<b>{u["nome_usuario"]}</b><br>'
                f'<span style="color:{TEMA["text_muted"]}; font-size:11.5px;">{u["cargo_usuario"]}</span></div>',
                unsafe_allow_html=True,
            )

        if st.session_state.pagina == "maquinas":
            st.markdown(
                '<div class="topbar-sub">Cadastro completo dos equipamentos, integrado a Modelos_Maquinas e Setores.</div>',
                unsafe_allow_html=True,
            )

            try:
                with st.spinner("Carregando máquinas..."):
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

            busca_col, botao_col = st.columns([3, 1])
            with busca_col:
                with st.container(key="topbar_search"):
                    st.text_input(
                        "Buscar",
                        key="maquinas_busca",
                        placeholder="Buscar tag, máquina, fabricante, localização ou setor...",
                        label_visibility="collapsed",
                    )
            with botao_col:
                with st.container(key="nova_maquina_btn"):
                    if st.button("+ Nova Máquina", use_container_width=True, key="btn_nova_maquina"):
                        dialog_nova_maquina()

            try:
                maquinas = listar_maquinas(st.session_state.get("maquinas_busca", ""))
            except Exception as e:
                st.error(f"Não foi possível carregar as máquinas: {e}")
                maquinas = []

            st.markdown("<br>", unsafe_allow_html=True)

            if not maquinas:
                st.info("Nenhuma máquina encontrada.")
            else:
                h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1, 2.2, 1.6, 1.8, 1.4, 1.3, 1.1, 0.9])
                for col, texto in zip((h1, h2, h3, h4, h5, h6, h7, h8),
                                       ("Tag", "Máquina / Modelo", "Fabricante", "Localização", "Setor", "Manutenção", "Status", "Ações")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

                maquinas_pagina = paginar_lista(maquinas, "maquinas")
                for row in maquinas_pagina:
                    with st.container(key=f"maq_row_{row['tag_equipamento']}"):
                        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 2.2, 1.6, 1.8, 1.4, 1.3, 1.1, 0.9])
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

                        with c8:
                            b1, b2, b3 = st.columns(3)
                            with b1:
                                if st.button("📜", key=f"historico_maq_{row['tag_equipamento']}", help="Histórico de manutenção"):
                                    dialog_historico_maquina(row)
                            with b2:
                                if st.button("✏️", key=f"editar_maq_{row['tag_equipamento']}"):
                                    dialog_editar_maquina(row)
                            with b3:
                                if st.button("🗑️", key=f"excluir_maq_{row['tag_equipamento']}"):
                                    dialog_confirmar_exclusao(
                                        f"Excluir a máquina {row['tag_equipamento']} permanentemente?",
                                        excluir_maquina, row["tag_equipamento"],
                                    )

            st.stop()

        if st.session_state.pagina == "setores":
            st.markdown(
                '<div class="topbar-sub">Setores cadastrados, com máquinas e equipe ativa vinculadas.</div>',
                unsafe_allow_html=True,
            )

            with st.container(key="nova_setor_btn"):
                if st.button("+ Novo Setor", key="btn_novo_setor"):
                    dialog_novo_setor()

            try:
                with st.spinner("Carregando setores..."):
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
                        bc1, bc2 = st.columns(2)
                        with bc1:
                            if st.button("Editar", key=f"editar_setor_{s['id_setor']}", use_container_width=True):
                                dialog_editar_setor(s)
                        with bc2:
                            if st.button("Excluir", key=f"excluir_setor_{s['id_setor']}", use_container_width=True):
                                dialog_confirmar_exclusao(
                                    f"Excluir o setor {s['nome_setor']} permanentemente?",
                                    excluir_setor, s["id_setor"],
                                )
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
                with st.spinner("Carregando almoxarifado..."):
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

            busca_col, botao_col = st.columns([3, 1])
            with busca_col:
                with st.container(key="topbar_search"):
                    st.text_input(
                        "Buscar",
                        key="pecas_busca",
                        placeholder="Buscar peça pelo nome...",
                        label_visibility="collapsed",
                    )
            with botao_col:
                with st.container(key="nova_peca_btn"):
                    if st.button("+ Nova Peça", use_container_width=True, key="btn_nova_peca"):
                        dialog_nova_peca()

            try:
                pecas = listar_pecas(st.session_state.get("pecas_busca", ""))
            except Exception as e:
                st.error(f"Não foi possível carregar o almoxarifado: {e}")
                pecas = []

            st.markdown("<br>", unsafe_allow_html=True)

            if not pecas:
                st.info("Nenhuma peça encontrada.")
            else:
                h1, h2, h3, h4, h5, h6 = st.columns([2.4, 1.1, 1.1, 1.2, 1.2, 0.8])
                for col, texto in zip((h1, h2, h3, h4, h5, h6),
                                       ("Peça", "Qtd. em estoque", "Unidade", "Custo unitário", "Valor total", "Ações")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

                pecas_pagina = paginar_lista(pecas, "pecas")
                for row in pecas_pagina:
                    with st.container(key=f"peca_row_{row['id_peca']}"):
                        c1, c2, c3, c4, c5, c6 = st.columns([2.4, 1.1, 1.1, 1.2, 1.2, 0.8])
                        c1.markdown(f'<div class="os-cell"><b>{row["nome_peca"]}</b></div>', unsafe_allow_html=True)
                        classe_qtd = "estoque-baixo" if row["quantidade_estoque"] < LIMITE_ESTOQUE_BAIXO else "estoque-ok"
                        c2.markdown(f'<div class="os-cell {classe_qtd}">{row["quantidade_estoque"]}</div>', unsafe_allow_html=True)
                        c3.markdown(f'<div class="os-cell">{row["unidade_medida"]}</div>', unsafe_allow_html=True)
                        c4.markdown(f'<div class="os-cell">R$ {row["custo_unitario"]:,.2f}</div>'.replace(",", "§").replace(".", ",").replace("§", "."), unsafe_allow_html=True)
                        c5.markdown(f'<div class="os-cell">R$ {row["valor_total"]:,.2f}</div>'.replace(",", "§").replace(".", ",").replace("§", "."), unsafe_allow_html=True)

                        with c6:
                            b1, b2 = st.columns(2)
                            with b1:
                                if st.button("✏️", key=f"editar_peca_{row['id_peca']}"):
                                    dialog_editar_peca(row)
                            with b2:
                                if st.button("🗑️", key=f"excluir_peca_{row['id_peca']}"):
                                    dialog_confirmar_exclusao(
                                        f"Excluir a peça {row['nome_peca']} permanentemente?",
                                        excluir_peca, row["id_peca"],
                                    )

            st.stop()

        if st.session_state.pagina == "ferramentas":
            st.markdown(
                '<div class="topbar-sub">Situação das ferramentas e com quem cada uma está no momento.</div>',
                unsafe_allow_html=True,
            )

            try:
                with st.spinner("Carregando ferramentas..."):
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

            busca_col, botao_col = st.columns([3, 1])
            with busca_col:
                with st.container(key="topbar_search"):
                    st.text_input(
                        "Buscar",
                        key="ferramentas_busca",
                        placeholder="Buscar ferramenta pelo nome...",
                        label_visibility="collapsed",
                    )
            with botao_col:
                with st.container(key="nova_ferramenta_btn"):
                    if st.button("+ Nova Ferramenta", use_container_width=True, key="btn_nova_ferramenta"):
                        dialog_nova_ferramenta()

            try:
                ferramentas = listar_ferramentas(st.session_state.get("ferramentas_busca", ""))
            except Exception as e:
                st.error(f"Não foi possível carregar as ferramentas: {e}")
                ferramentas = []

            st.markdown("<br>", unsafe_allow_html=True)

            if not ferramentas:
                st.info("Nenhuma ferramenta encontrada.")
            else:
                h1, h2, h3, h4, h5 = st.columns([2.4, 1.3, 1.5, 1.5, 0.8])
                for col, texto in zip((h1, h2, h3, h4, h5), ("Ferramenta", "Status", "Com quem", "Devolução prevista", "Ações")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

                ferramentas_pagina = paginar_lista(ferramentas, "ferramentas")
                for row in ferramentas_pagina:
                    with st.container(key=f"ferr_row_{row['id_ferramenta']}"):
                        c1, c2, c3, c4, c5 = st.columns([2.4, 1.3, 1.5, 1.5, 0.8])
                        c1.markdown(f'<div class="os-cell"><b>{row["nome_ferramenta"]}</b></div>', unsafe_allow_html=True)
                        slug = status_slug(row["status_ferramenta"])
                        c2.markdown(f'<span class="status-badge status-{slug}">{row["status_ferramenta"]}</span>', unsafe_allow_html=True)
                        c3.markdown(f'<div class="os-cell">{row["com_quem"] or "—"}</div>', unsafe_allow_html=True)
                        c4.markdown(f'<div class="os-cell">{row["devolucao_prevista"] or "—"}</div>', unsafe_allow_html=True)

                        with c5:
                            b1, b2 = st.columns(2)
                            with b1:
                                if st.button("✏️", key=f"editar_ferr_{row['id_ferramenta']}"):
                                    dialog_editar_ferramenta(row)
                            with b2:
                                if st.button("🗑️", key=f"excluir_ferr_{row['id_ferramenta']}"):
                                    dialog_confirmar_exclusao(
                                        f"Excluir a ferramenta {row['nome_ferramenta']} permanentemente?",
                                        excluir_ferramenta, row["id_ferramenta"],
                                    )

            st.stop()

        if st.session_state.pagina == "matriz_risco":
            st.markdown(
                '<div class="topbar-sub">Matriz de Riscos (NR-01) e EPIs obrigatórios associados às Ordens de Serviço.</div>',
                unsafe_allow_html=True,
            )

            with st.container(key="novo_risco_btn"):
                if st.button("+ Novo Risco", key="btn_novo_risco"):
                    dialog_novo_risco()

            try:
                with st.spinner("Carregando matriz de riscos..."):
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
                        bc1, bc2 = st.columns(2)
                        with bc1:
                            if st.button("Editar", key=f"editar_risco_{r['id_risco']}", use_container_width=True):
                                dialog_editar_risco(r)
                        with bc2:
                            if st.button("Excluir", key=f"excluir_risco_{r['id_risco']}", use_container_width=True):
                                dialog_confirmar_exclusao(
                                    f"Excluir o risco {r['risco_nr01']} permanentemente?",
                                    excluir_risco, r["id_risco"],
                                )
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
                with st.spinner("Carregando usuários..."):
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

            busca_col, botao_col = st.columns([3, 1])
            with busca_col:
                with st.container(key="topbar_search"):
                    st.text_input(
                        "Buscar",
                        key="usuarios_busca",
                        placeholder="Buscar por nome, e-mail, cargo ou setor...",
                        label_visibility="collapsed",
                    )
            with botao_col:
                with st.container(key="novo_usuario_btn"):
                    if st.button("+ Novo Usuário", use_container_width=True, key="btn_novo_usuario"):
                        dialog_novo_usuario()

            try:
                usuarios = listar_usuarios(st.session_state.get("usuarios_busca", ""))
            except Exception as e:
                st.error(f"Não foi possível carregar os usuários: {e}")
                usuarios = []

            st.markdown("<br>", unsafe_allow_html=True)

            if not usuarios:
                st.info("Nenhum usuário encontrado.")
            else:
                h1, h2, h3, h4, h5, h6, h7 = st.columns([2, 1.3, 1.3, 1, 1.3, 1.2, 0.8])
                for col, texto in zip((h1, h2, h3, h4, h5, h6, h7),
                                       ("Usuário", "Cargo", "Setor", "Status", "Disponibilidade", "Telefone", "Ações")):
                    col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

                usuarios_pagina = paginar_lista(usuarios, "usuarios")
                for row in usuarios_pagina:
                    with st.container(key=f"user_row_{row['id_usuario']}"):
                        c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1.3, 1.3, 1, 1.3, 1.2, 0.8])
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

                        with c7:
                            b1, b2 = st.columns(2)
                            with b1:
                                if st.button("✏️", key=f"editar_user_{row['id_usuario']}"):
                                    dialog_editar_usuario(row)
                            with b2:
                                if st.button("🗑️", key=f"excluir_user_{row['id_usuario']}"):
                                    dialog_confirmar_exclusao(
                                        f"Excluir o usuário {row['nome_usuario']} permanentemente?",
                                        excluir_usuario, row["id_usuario"],
                                    )

            st.stop()

        if st.session_state.pagina == "dashboard":
            st.markdown(
                '<div class="topbar-sub">Visão geral da operação: solicitações de serviço, ativos, equipe e estoque.</div>',
                unsafe_allow_html=True,
            )

            with st.spinner("Carregando dashboard..."):
                try:
                    ordens_dash = listar_ordens_servico()
                except Exception as e:
                    st.error(f"Não foi possível carregar as Solicitação de Serviço: {e}")
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
                    st.caption("Nenhuma SS pendente com técnico atribuído.")
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
            st.markdown('<div class="chart-card"><div class="chart-title">Últimas Solicitações de Serviço</div>', unsafe_allow_html=True)
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
                st.caption("Nenhuma SS cadastrada.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.stop()

        if st.session_state.pagina == "agenda":
            st.markdown(
                '<div class="topbar-sub">Programação das Solicitações de Serviço por data e técnico — integrada ao Google Calendar.</div>',
                unsafe_allow_html=True,
            )

            gcal_ativo = google_calendar_configurado()
            erro_gcal = st.session_state.get("google_calendar_erro")

            if not gcal_ativo:
                st.info(
                    "Google Calendar não configurado. Adicione a seção [google_calendar] em "
                    "secrets.toml para sincronizar as Solicitações de Serviço com um calendário compartilhado."
                )
            elif erro_gcal:
                st.warning(f"Google Calendar: {erro_gcal}")

            try:
                with st.spinner("Carregando solicitações de serviço..."):
                    ordens_agenda = listar_ordens_servico()
            except Exception as e:
                st.error(f"Não foi possível carregar as Solicitações de Serviço: {e}")
                ordens_agenda = []

            hoje = agora_brasil().date()

            f1, f2, f3 = st.columns([1, 2, 1])
            with f1:
                data_selecionada = st.date_input("Ver ordens do dia", value=hoje, key="agenda_data")
            with f3:
                st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                if st.button("🔄 Sincronizar agora", disabled=not gcal_ativo, use_container_width=True):
                    with st.spinner("Sincronizando com o Google Calendar..."):
                        qtd = sincronizar_intervalo_com_google(
                            ordens_agenda, hoje - timedelta(days=1), hoje + timedelta(days=7)
                        )
                    st.success(f"{qtd} SS sincronizada(s) com o Google Calendar.")
                    st.rerun()

            os_do_dia = [o for o in ordens_agenda if o["data_abertura"] == data_selecionada]
            os_do_dia.sort(key=lambda o: (o["hh_inicio"] is None, o["hh_inicio"]))

            os_semana = [
                o for o in ordens_agenda
                if o["data_abertura"] and hoje <= o["data_abertura"] <= hoje + timedelta(days=7)
            ]

            eventos_dia = buscar_eventos_google(data_selecionada, data_selecionada) if gcal_ativo else []
            eventos_externos_dia = [ev for ev in eventos_dia if ev["externo"]]

            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{len(os_do_dia)}</div>'
                f'<div class="kpi-label">SS na data selecionada</div></div>', unsafe_allow_html=True)
            k2.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{len(os_semana)}</div>'
                f'<div class="kpi-label">SS nos próximos 7 dias</div></div>', unsafe_allow_html=True)
            pendentes_total = sum(1 for o in ordens_agenda if o["status_os"] != "Concluído")
            k3.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{pendentes_total}</div>'
                f'<div class="kpi-label">SS pendentes no total</div></div>', unsafe_allow_html=True)
            k4.markdown(
                f'<div class="kpi-card" style="border-left-color:#6d28d9;"><div class="kpi-value">{len(eventos_externos_dia)}</div>'
                f'<div class="kpi-label">Eventos externos no Google (data selecionada)</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f'<div class="chart-title">Solicitações de Serviço em {data_selecionada.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
            if not os_do_dia:
                st.info("Nenhuma SS agendada para esta data.")
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

            if gcal_ativo:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f'<div class="chart-title">Eventos externos do Google Calendar em {data_selecionada.strftime("%d/%m/%Y")}</div>',
                    unsafe_allow_html=True,
                )
                st.caption("Eventos criados diretamente no calendário compartilhado, sem OS correspondente no sistema.")
                if not eventos_externos_dia:
                    st.info("Nenhum evento externo nesta data.")
                else:
                    for ev in eventos_externos_dia:
                        st.markdown(
                            f'<div class="os-row"><b>{ev["titulo"]}</b><br>'
                            f'<span class="os-cell-muted">{ev["inicio"]} → {ev["fim"]}'
                            + (f' · <a href="{ev["link"]}" target="_blank">abrir no Google</a>' if ev.get("link") else "")
                            + '</span></div>',
                            unsafe_allow_html=True,
                        )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Próximos 7 dias</div>', unsafe_allow_html=True)
            for i in range(7):
                dia = hoje + timedelta(days=i)
                os_dia = [o for o in ordens_agenda if o["data_abertura"] == dia]
                with st.container(key=f"agenda_dia_{dia.isoformat()}"):
                    st.markdown(
                        f'<div class="os-row"><b>{dia.strftime("%d/%m/%Y")}</b> '
                        f'<span class="os-cell-muted">— {len(os_dia)} SS</span></div>',
                        unsafe_allow_html=True,
                    )

            st.stop()

        if st.session_state.pagina == "relatorios":
            st.markdown(
                '<div class="topbar-sub">Indicadores consolidados de manutenção, por período e por técnico.</div>',
                unsafe_allow_html=True,
            )

            try:
                with st.spinner("Carregando solicitações de serviço..."):
                    ordens_rel = listar_ordens_servico()
            except Exception as e:
                st.error(f"Não foi possível carregar as Solicitações de Serviço: {e}")
                ordens_rel = []

            if not ordens_rel:
                st.info("Nenhuma SS cadastrada para gerar relatórios.")
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
                f'<div class="kpi-label">SS no período</div></div>', unsafe_allow_html=True)
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
                st.markdown('<div class="chart-card"><div class="chart-title">SS por status (período filtrado)</div>', unsafe_allow_html=True)
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
                st.markdown('<div class="chart-card"><div class="chart-title">SS por técnico (período filtrado)</div>', unsafe_allow_html=True)
                if not df_filtro.empty and df_filtro["tecnico"].notna().any():
                    df_tec_rel = (
                        df_filtro["tecnico"].dropna().value_counts()
                        .rename_axis("Técnico").reset_index(name="Quantidade").set_index("Técnico")
                    )
                    grafico_barras(df_tec_rel, "Quantidade", cor_padrao="#2563eb", horizontal=True)
                else:
                    st.caption("Sem dados para o período/técnico selecionado.")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="chart-card"><div class="chart-title">Evolução mensal de abertura de SS</div>', unsafe_allow_html=True)
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

            # ---------------------------------------------------------------
            # Indicadores de Manutenção (MTTR, MTBF, backlog por idade e
            # disponibilidade dos equipamentos), calculados sobre o mesmo
            # recorte de período/técnico já aplicado acima.
            # ---------------------------------------------------------------
            try:
                maquinas_rel = listar_maquinas()
            except Exception as e:
                st.error(f"Não foi possível carregar as máquinas para calcular a disponibilidade: {e}")
                maquinas_rel = []

            indicadores = calcular_indicadores_manutencao(df_filtro, maquinas_rel)

            mttr_display = (
                f"{indicadores['mttr_horas']:.1f} h" if indicadores["mttr_horas"] is not None else "—"
            )
            mtbf_display = (
                f"{indicadores['mtbf_dias']:.1f} d" if indicadores["mtbf_dias"] is not None else "—"
            )
            disponibilidade_display = (
                f"{indicadores['disponibilidade_pct']:.1f}%" if indicadores["disponibilidade_pct"] is not None else "—"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Indicadores de Manutenção</div>', unsafe_allow_html=True)
            st.caption(
                "MTTR e MTBF consideram apenas SS com horário de início/fim válidos; a "
                "disponibilidade reflete o cadastro atual de máquinas (não é filtrada por período)."
            )

            i1, i2, i3, i4 = st.columns(4)
            i1.markdown(
                f'<div class="kpi-card kpi-blue"><div class="kpi-value">{mttr_display}</div>'
                f'<div class="kpi-label">MTTR · Tempo médio de reparo</div></div>', unsafe_allow_html=True)
            i2.markdown(
                f'<div class="kpi-card kpi-green"><div class="kpi-value">{mtbf_display}</div>'
                f'<div class="kpi-label">MTBF · Tempo médio entre falhas</div></div>', unsafe_allow_html=True)
            i3.markdown(
                f'<div class="kpi-card kpi-red"><div class="kpi-value">{indicadores["backlog_total"]}</div>'
                f'<div class="kpi-label">Backlog · SS pendentes no período</div></div>', unsafe_allow_html=True)
            i4.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{disponibilidade_display}</div>'
                f'<div class="kpi-label">Disponibilidade dos equipamentos</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            gi1, gi2 = st.columns(2)
            with gi1:
                st.markdown('<div class="chart-card"><div class="chart-title">Backlog de manutenção por idade</div>', unsafe_allow_html=True)
                if not indicadores["df_backlog"].empty:
                    grafico_barras(indicadores["df_backlog"], "Quantidade", cor_padrao="#dc2626")
                else:
                    st.caption("Nenhuma SS pendente no período/técnico selecionado.")
                st.markdown("</div>", unsafe_allow_html=True)
            with gi2:
                st.markdown('<div class="chart-card"><div class="chart-title">MTTR ao longo do tempo (horas)</div>', unsafe_allow_html=True)
                if not indicadores["mttr_mensal"].empty:
                    grafico_area(indicadores["mttr_mensal"], "MTTR (h)", cor="#dc2626")
                else:
                    st.caption("Sem SS concluídas com horários registrados no período.")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Detalhamento das Solicitações de Serviço</div>', unsafe_allow_html=True)
            if df_filtro.empty:
                st.info("Nenhuma SS encontrada para os filtros selecionados.")
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
                    file_name=f"relatorio_ss_{data_ini}_{data_fim}.csv",
                    mime="text/csv",
                )

            st.stop()

        if st.session_state.pagina != "ordens_servico":
            st.markdown('<div class="topbar-sub">Esta página ainda não foi implementada.</div>', unsafe_allow_html=True)
            st.info("Em construção — por enquanto Solicitações de Serviço, Máquinas, Setores, Almoxarifado de Peças, Ferramentas, Matriz de Risco/EPI e Usuários estão conectados ao banco.")
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
                    key="ss_busca",
                    placeholder="Buscar SS, equipamento, técnico...",
                    label_visibility="collapsed",
                )
        with botao_col:
            with st.container(key="nova_os_btn"):
                if st.button("+ Nova SS", use_container_width=True):
                    dialog_nova_os()

        try:
            with st.spinner("Carregando solicitações de serviço..."):
                ordens = listar_ordens_servico(st.session_state.os_busca)
        except Exception as e:
            st.error(f"Não foi possível carregar as solicitações de Serviço: {e}")
            ordens = []

        st.markdown("<br>", unsafe_allow_html=True)

        if not ordens:
            st.info("Nenhuma Solicitação de Serviço encontrada.")
        else:
            h1, h2, h3, h4, h5, h6, h7 = st.columns([0.6, 1, 2.4, 1.3, 1.2, 1, 0.8])
            for col, texto in zip((h1, h2, h3, h4, h5, h6, h7),
                                   ("SS", "Equipamento", "Descrição", "Abertura", "Técnico", "Status", "Ações")):
                col.markdown(f'<div class="os-header">{texto}</div>', unsafe_allow_html=True)

            ordens_pagina = paginar_lista(ordens, "ordens_servico")
            for row in ordens_pagina:
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
                                dialog_confirmar_exclusao(
                                    f"Excluir a OS #{row['id_os']} ({row['tag_equipamento']}) permanentemente?",
                                    excluir_os, row["id_os"],
                                )

    st.stop()

# ------------------------------------------------------------------
# TELA DE LOGIN — estilo "foguete", tons de azul, tela inteira
# ------------------------------------------------------------------
segundos_bloqueio_restantes = login_bloqueado()

with st.container(key="unified_panel"):

    # ---------- Painel esquerdo: decorativo (foguete + gradiente multi-tom) ----------
    with st.container(key="rocket_panel"):
        st.markdown("""
<div class="brand-box">
<div class="brand-icon">🛠️</div>
<div>
<div class="brand-title">Portal da Manutenção</div>
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
Inovação com Eficiência e Simplicidade.
<span>Manutenção é Planejar, Executar, Monitorar e Aprimorar.</span>
</div>
""", unsafe_allow_html=True)

    # ---------- Painel direito: cartão de login (cobre a tela inteira) ----------
    with st.container(key="login_card"):
        top_login1, top_login2 = st.columns([3, 1])
        with top_login1:
            st.markdown('<div class="login-eyebrow">Bem-vindo de volta</div>', unsafe_allow_html=True)
        with top_login2:
            with st.container(key="tema_toggle_login"):
                icone_tema = "☀️ Claro" if st.session_state.tema == "escuro" else "🌙 Escuro"
                st.button(icone_tema, on_click=alternar_tema, use_container_width=True)

        st.markdown('<div class="login-title">Acesse sua conta</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Entre com suas credenciais corporativas para continuar.</div>', unsafe_allow_html=True)

        if st.session_state.db_error:
            st.error(f"Não foi possível conectar ao banco:\n\n{st.session_state.db_error}")

        if segundos_bloqueio_restantes > 0:
            st.warning(
                f"Tentativas de login incorreta. Tente novamente em {segundos_bloqueio_restantes} segundo(s)."
            )

        st.text_input(
            "👤  E-mail", key="email_input", placeholder="nome@empresa.com",
            disabled=segundos_bloqueio_restantes > 0,
        )
        st.text_input(
            "🔒  Senha", key="senha_input", type="password", placeholder="••••••••",
            disabled=segundos_bloqueio_restantes > 0,
        )

        st.markdown(
            '<div class="login-row"><span>☐ Lembrar senha</span>'
            '<span class="login-link">Esqueceu a senha?</span></div>',
            unsafe_allow_html=True,
        )

        if st.session_state.get("login_error") and segundos_bloqueio_restantes == 0:
            tentativas_restantes = max(LIMITE_TENTATIVAS_LOGIN - st.session_state.login_tentativas, 0)
            st.error(f"E-mail ou senha inválidos. Tentativas restantes: {tentativas_restantes}.")
            st.session_state.login_error = False

        with st.container(key="entrar_btn_wrap"):
            st.button("→  Entrar", on_click=do_login, disabled=segundos_bloqueio_restantes > 0)

        st.markdown('<div class="demo-label">Acesso rápido</div>', unsafe_allow_html=True)

        d1, d2 = st.columns(2)
        colunas = [d1, d2, d1, d2]
        for idx, (cargo, email, senha) in enumerate(ACESSO_RAPIDO_USERS):
            with colunas[idx]:
                with st.container(key=f"demo_{idx}"):
                    st.button(
                        f"{cargo}\n{email}", key=f"btn_demo_{idx}",
                        on_click=quick_login, args=(email, senha),
                        disabled=segundos_bloqueio_restantes > 0,
                    )

        if st.session_state.logged_in:
            st.rerun()

        if segundos_bloqueio_restantes > 0:
            import time
            time.sleep(1)
            st.rerun()