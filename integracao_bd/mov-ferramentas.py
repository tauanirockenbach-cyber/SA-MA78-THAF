from database import conectar

def listar_movimentacoes():

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT
        id_movimentacao,
        id_ferramenta,
        id_os,
        id_tecnico_solicitante,
        id_almoxarife_entregador,
        data_retirada,
        data_devolucao_prevista,
        data_devolucao_real,
        status_movimentacao,
        observacoes
    FROM Movimentacao_Ferramentas
    """

    cursor.execute(sql)
    dados = cursor.fetchall()

    for movimentacao in dados:
        print(movimentacao)

    cursor.close()
    conexao.close()


def cadastrar_movimentacao(id_ferramenta, id_os, id_tecnico_solicitante,
                           id_almoxarife_entregador, data_retirada,
                           data_devolucao_prevista, data_devolucao_real,
                           status_movimentacao, observacoes):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    INSERT INTO Movimentacao_Ferramentas
    (
        id_ferramenta,
        id_os,
        id_tecnico_solicitante,
        id_almoxarife_entregador,
        data_retirada,
        data_devolucao_prevista,
        data_devolucao_real,
        status_movimentacao,
        observacoes
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    valores = (
        id_ferramenta,
        id_os,
        id_tecnico_solicitante,
        id_almoxarife_entregador,
        data_retirada,
        data_devolucao_prevista,
        data_devolucao_real,
        status_movimentacao,
        observacoes
    )

    cursor.execute(sql, valores)
    conexao.commit()

    print("Movimentação cadastrada com sucesso!")

    cursor.close()
    conexao.close()


def atualizar_status(id_movimentacao, status_movimentacao):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    UPDATE Movimentacao_Ferramentas
    SET status_movimentacao = %s
    WHERE id_movimentacao = %s
    """

    valores = (status_movimentacao, id_movimentacao)

    cursor.execute(sql, valores)
    conexao.commit()

    print(f"Status da movimentação {id_movimentacao} atualizado com sucesso!")

    cursor.close()
    conexao.close()


def registrar_devolucao(id_movimentacao, data_devolucao_real):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    UPDATE Movimentacao_Ferramentas
    SET
        data_devolucao_real = %s,
        status_movimentacao = 'Devolvido'
    WHERE id_movimentacao = %s
    """

    valores = (data_devolucao_real, id_movimentacao)

    cursor.execute(sql, valores)
    conexao.commit()

    print(f"Devolução da movimentação {id_movimentacao} registrada com sucesso!")

    cursor.close()
    conexao.close()


def deletar_movimentacao(id_movimentacao):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    DELETE FROM Movimentacao_Ferramentas
    WHERE id_movimentacao = %s
    """

    valores = (id_movimentacao,)

    cursor.execute(sql, valores)
    conexao.commit()

    print(f"Movimentação {id_movimentacao} deletada com sucesso!")

    cursor.close()
    conexao.close()