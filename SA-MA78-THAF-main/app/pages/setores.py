"""
Módulo: Setores
----------------------------------------------------------------------------
Extraído do app.py monolítico do SA-THAF.

Dependências externas esperadas (ajuste os imports conforme a estrutura
real do projeto):
    core.db  -> get_connection()
    core.ui  -> grafico_barras, dialog_confirmar_exclusao

Este módulo expõe:
    - Leitura (cacheada): listar_setores
    - CRUD: criar_setor, atualizar_setor, excluir_setor
    - Dialogs: dialog_novo_setor, dialog_editar_setor
    - render(): desenha a página completa de Setores
"""
import streamlit as st
import pandas as pd

from core.db import get_connection
from core.ui import grafico_barras, dialog_confirmar_exclusao


# ============================================================================
# LEITURA (SELECT) — cacheada
# ============================================================================
@st.cache_data(ttl=30)
def listar_setores():
    """Lista os setores com a contagem de máquinas e de usuários ativos
    vinculados a cada um."""
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


def _mapa_setores():
    """Utilitário reaproveitado por outros módulos (Máquinas, Usuários) para
    montar {nome_setor: id_setor} nos formulários. Mantido aqui para evitar
    dependência circular; pode ser movido para core.ui se preferir."""
    try:
        return {s["nome_setor"]: s["id_setor"] for s in listar_setores()}
    except Exception:
        return {}


# ============================================================================
# CRUD (INSERT / UPDATE / DELETE)
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


def excluir_setor(id_setor):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Setores WHERE id_setor = %s", (id_setor,))
    finally:
        conn.close()
    listar_setores.clear()


# ============================================================================
# DIALOGS
# ============================================================================
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
# PÁGINA — render()
# ============================================================================
def render():
    """Desenha a página completa de Setores. Chame a partir do roteador
    principal quando st.session_state.pagina == 'setores'."""
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
        return

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