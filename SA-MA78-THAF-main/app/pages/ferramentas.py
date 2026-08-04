"""
Módulo: Ferramentas (Almoxarifado de Ferramentas)
----------------------------------------------------------------------------
Extraído do app.py monolítico do SA-THAF.

Dependências externas esperadas (ajuste os imports conforme a estrutura
real do projeto):
    core.db  -> get_connection()
    core.ui  -> status_slug, grafico_barras, paginar_lista, dialog_confirmar_exclusao

Este módulo expõe:
    - Constantes: STATUS_FERRAMENTA_CORES, STATUS_FERRAMENTA_OPCOES
    - Leitura (cacheada): listar_ferramentas
    - CRUD: criar_ferramenta, atualizar_ferramenta, excluir_ferramenta
    - Dialogs: dialog_nova_ferramenta, dialog_editar_ferramenta
    - render(): desenha a página completa de Ferramentas
"""
import streamlit as st
import pandas as pd

from core.db import get_connection
from core.ui import status_slug, grafico_barras, paginar_lista, dialog_confirmar_exclusao


# ============================================================================
# CONSTANTES
# ============================================================================
STATUS_FERRAMENTA_CORES = {
    "Disponível": "#16a34a",
    "Solicitada": "#a16207",
    "Em Uso": "#2563eb",
    "Manutenção/Calibração": "#6d28d9",
    "Extraviada": "#dc2626",
}
STATUS_FERRAMENTA_OPCOES = list(STATUS_FERRAMENTA_CORES.keys())


# ============================================================================
# LEITURA (SELECT) — cacheada
# ============================================================================
@st.cache_data(ttl=30)
def listar_ferramentas(busca: str = ""):
    """Lista as ferramentas do almoxarifado, mostrando com quem está (quando
    em uso/atrasada/solicitada) a partir da movimentação mais recente em
    aberto (Movimentacao_Ferramentas + OS_Ferramentas)."""
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


# ============================================================================
# CRUD (INSERT / UPDATE / DELETE)
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


def excluir_ferramenta(id_ferramenta):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Almoxarifado_Ferramentas WHERE id_ferramenta = %s", (id_ferramenta,))
    finally:
        conn.close()
    listar_ferramentas.clear()


# ============================================================================
# DIALOGS
# ============================================================================
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
# PÁGINA — render()
# ============================================================================
def render():
    """Desenha a página completa de Ferramentas. Chame a partir do roteador
    principal quando st.session_state.pagina == 'ferramentas'."""
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
        return

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