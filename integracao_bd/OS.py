from database import conectar

# ==========================================
# ORDENS DE SERVIÇO
# ==========================================

def listar_os():

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT
        id_os,
        tag_equipamento,
        descricao_falha,
        data_abertura,
        hh_inicio,
        hh_fim,
        status_os,
        id_tecnico_responsavel
    FROM Ordens_Servico
    """

    cursor.execute(sql)
    dados = cursor.fetchall()

    for os in dados:
        print(os)

    cursor.close()
    conexao.close()


def cadastrar_os(id_os, tag_equipamento, descricao_falha, data_abertura,
                 hh_inicio, hh_fim, status_os, id_tecnico_responsavel):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    INSERT INTO Ordens_Servico
    (
        id_os,
        tag_equipamento,
        descricao_falha,
        data_abertura,
        hh_inicio,
        hh_fim,
        status_os,
        id_tecnico_responsavel
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    valores = (
        id_os,
        tag_equipamento,
        descricao_falha,
        data_abertura,
        hh_inicio,
        hh_fim,
        status_os,
        id_tecnico_responsavel
    )

    cursor.execute(sql, valores)
    conexao.commit()

    print("Ordem de Serviço cadastrada com sucesso!")

    cursor.close()
    conexao.close()


def atualizar_status_os(id_os, status_os):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    UPDATE Ordens_Servico
    SET status_os = %s
    WHERE id_os = %s
    """

    valores = (status_os, id_os)

    cursor.execute(sql, valores)
    conexao.commit()

    print("Status atualizado com sucesso!")

    cursor.close()
    conexao.close()


def deletar_os(id_os):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    DELETE FROM Ordens_Servico
    WHERE id_os = %s
    """

    cursor.execute(sql, (id_os,))
    conexao.commit()

    print("Ordem de Serviço deletada com sucesso!")

    cursor.close()
    conexao.close()


# ==========================================
# OS_MATERIAIS
# ==========================================

def listar_materiais_os():

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT
        id_os_material,
        id_os,
        id_peca,
        quantidade_utilizada
    FROM OS_Materiais
    """

    cursor.execute(sql)
    dados = cursor.fetchall()

    for material in dados:
        print(material)

    cursor.close()
    conexao.close()


def cadastrar_material_os(id_os, id_peca, quantidade_utilizada):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    INSERT INTO OS_Materiais
    (
        id_os,
        id_peca,
        quantidade_utilizada
    )
    VALUES (%s,%s,%s)
    """

    valores = (
        id_os,
        id_peca,
        quantidade_utilizada
    )

    cursor.execute(sql, valores)
    conexao.commit()

    print("Material vinculado à OS com sucesso!")

    cursor.close()
    conexao.close()


def atualizar_quantidade_material(id_os_material, quantidade_utilizada):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    UPDATE OS_Materiais
    SET quantidade_utilizada = %s
    WHERE id_os_material = %s
    """

    cursor.execute(sql, (quantidade_utilizada, id_os_material))
    conexao.commit()

    print("Quantidade atualizada com sucesso!")

    cursor.close()
    conexao.close()


def deletar_material_os(id_os_material):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    DELETE FROM OS_Materiais
    WHERE id_os_material = %s
    """

    cursor.execute(sql, (id_os_material,))
    conexao.commit()

    print("Material removido da OS!")

    cursor.close()
    conexao.close()


# ==========================================
# OS_FERRAMENTAS
# ==========================================

def listar_ferramentas_os():

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT
        id_os_ferramenta,
        id_os,
        id_ferramenta
    FROM OS_Ferramentas
    """

    cursor.execute(sql)
    dados = cursor.fetchall()

    for ferramenta in dados:
        print(ferramenta)

    cursor.close()
    conexao.close()


def cadastrar_ferramenta_os(id_os, id_ferramenta):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    INSERT INTO OS_Ferramentas
    (
        id_os,
        id_ferramenta
    )
    VALUES (%s,%s)
    """

    cursor.execute(sql, (id_os, id_ferramenta))
    conexao.commit()

    print("Ferramenta vinculada à OS!")

    cursor.close()
    conexao.close()


def deletar_ferramenta_os(id_os_ferramenta):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    DELETE FROM OS_Ferramentas
    WHERE id_os_ferramenta = %s
    """

    cursor.execute(sql, (id_os_ferramenta,))
    conexao.commit()

    print("Ferramenta removida da OS!")

    cursor.close()
    conexao.close()


# ==========================================
# OS_SEGURANCA
# ==========================================

def listar_seguranca_os():

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT
        id_os_seguranca,
        id_os,
        id_risco
    FROM OS_Seguranca
    """

    cursor.execute(sql)
    dados = cursor.fetchall()

    for risco in dados:
        print(risco)

    cursor.close()
    conexao.close()


def cadastrar_seguranca_os(id_os, id_risco):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    INSERT INTO OS_Seguranca
    (
        id_os,
        id_risco
    )
    VALUES (%s,%s)
    """

    cursor.execute(sql, (id_os, id_risco))
    conexao.commit()

    print("Risco vinculado à OS!")

    cursor.close()
    conexao.close()


def deletar_seguranca_os(id_os_seguranca):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    DELETE FROM OS_Seguranca
    WHERE id_os_seguranca = %s
    """

    cursor.execute(sql, (id_os_seguranca,))
    conexao.commit()

    print("Risco removido da OS!")

    cursor.close()
    conexao.close()