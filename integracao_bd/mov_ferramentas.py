from database import conectar
import time


def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


def ler_inteiro_opcional(mensagem):
    """Permite deixar em branco (retorna None) quando o campo aceita NULL."""
    while True:
        valor = input(mensagem)
        if valor.strip() == "":
            return None
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números ou deixe em branco.")


def ler_texto_opcional(mensagem):
    valor = input(mensagem).strip()
    return valor if valor else None


def ler_opcao_valida(mensagem, opcoes_validas):
    while True:
        valor = input(mensagem)
        if valor.lower() in opcoes_validas:
            return valor
        print("Opção inválida!")


def listar_movimentacoes():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT
            id_movimentacao,
            id_os_ferramenta,
            id_os,
            id_usuario_solicitante,
            id_usuario_entregador,
            data_retirada,
            data_devolucao_prevista,
            data_devolucao_real,
            status_movimentacao,
            observacoes
        FROM Movimentacao_Ferramentas
        """
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma movimentação cadastrada.")
            return

        for movimentacao in dados:
            print(movimentacao)

    except Exception as erro:
        print("Erro ao listar movimentações:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def cadastrar_movimentacao(id_os_ferramenta, id_os, id_usuario_solicitante,
                            id_usuario_entregador, data_retirada,
                            data_devolucao_prevista, observacoes):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # Toda movimentação nasce com status "Solicitado";
        # data_devolucao_real só é preenchida na devolução.
        sql = """
        INSERT INTO Movimentacao_Ferramentas
            (id_os_ferramenta, id_os, id_usuario_solicitante, id_usuario_entregador,
            data_retirada, data_devolucao_prevista, status_movimentacao, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            id_os_ferramenta, id_os, id_usuario_solicitante, id_usuario_entregador,
            data_retirada, data_devolucao_prevista, 'Solicitado', observacoes
        )

        cursor.execute(sql, valores)
        conexao.commit()

        print("Movimentação cadastrada com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        # id_os_ferramenta, id_os, id_usuario_solicitante e id_usuario_entregador
        # são FOREIGN KEY: erro comum aqui é informar um ID que não existe.
        print("Erro ao cadastrar movimentação (verifique se os IDs informados existem):", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_status(id_movimentacao, status_movimentacao):
    conexao = None
    cursor = None
    try:
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

        if cursor.rowcount > 0:
            print(f"Status da movimentação {id_movimentacao} atualizado com sucesso!")
        else:
            print("Movimentação não encontrada.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao atualizar status da movimentação:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def registrar_devolucao(id_movimentacao, data_devolucao_real):
    conexao = None
    cursor = None
    try:
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

        if cursor.rowcount > 0:
            print(f"Devolução da movimentação {id_movimentacao} registrada com sucesso!")
        else:
            print("Movimentação não encontrada.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao registrar devolução:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def deletar_movimentacao(id_movimentacao):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Movimentacao_Ferramentas WHERE id_movimentacao = %s"
        cursor.execute(sql, (id_movimentacao,))
        conexao.commit()

        if cursor.rowcount > 0:
            print(f"Movimentação {id_movimentacao} deletada com sucesso!")
        else:
            print("Movimentação não encontrada.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao deletar movimentação:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def opcao_desejada_movimentacao():
    opcoes_status = ['solicitado', 'em uso', 'atrasado', 'devolvido']

    while True:
        print("\n------ Menu Movimentação de Ferramentas ------")
        print("1 - Listar movimentações")
        print("2 - Cadastrar movimentação")
        print("3 - Atualizar status da movimentação")
        print("4 - Registrar devolução")
        print("5 - Deletar movimentação")
        print("0 - Sair")

        opcao_movimentacao = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_movimentacao == 1:
            print("\n--- Lista de Movimentações ---")
            listar_movimentacoes()
            time.sleep(2)

        elif opcao_movimentacao == 2:
            print("\n--- Cadastrar Movimentação ---")
            id_os_ferramenta = ler_inteiro("ID da ferramenta na OS (id_os_ferramenta): ")
            id_os = ler_inteiro("ID da Ordem de Serviço: ")
            id_usuario_solicitante = ler_inteiro("ID do usuário solicitante: ")
            id_usuario_entregador = ler_inteiro_opcional(
                "ID do usuário entregador (deixe em branco se ainda não definido): "
            )
            data_retirada = ler_texto_opcional(
                "Data de retirada AAAA-MM-DD HH:MM:SS (deixe em branco se ainda não retirou): "
            )
            data_devolucao_prevista = input("Data de devolução prevista (AAAA-MM-DD HH:MM:SS): ")
            observacoes = ler_texto_opcional("Observações (opcional): ")

            cadastrar_movimentacao(
                id_os_ferramenta, id_os, id_usuario_solicitante, id_usuario_entregador,
                data_retirada, data_devolucao_prevista, observacoes
            )

        elif opcao_movimentacao == 3:
            print("\n--- Atualizar Status da Movimentação ---")
            id_m = ler_inteiro("Digite o ID da movimentação que deseja atualizar: ")
            status = ler_opcao_valida(
                "Novo status (Solicitado, Em Uso, Atrasado, Devolvido): ",
                opcoes_status
            )

            atualizar_status(id_m, status)

        elif opcao_movimentacao == 4:
            print("\n--- Registrar Devolução ---")
            id_m = ler_inteiro("Digite o ID da movimentação a ser devolvida: ")
            data_devolucao_real = input("Data de devolução real (AAAA-MM-DD HH:MM:SS): ")

            registrar_devolucao(id_m, data_devolucao_real)

        elif opcao_movimentacao == 5:
            print("\n--- Deletar Movimentação ---")
            id_m = ler_inteiro("Digite o ID da movimentação que deseja deletar: ")
            deletar_movimentacao(id_m)

        elif opcao_movimentacao == 0:
            print("Voltando...")
            break

        else:
            print("Opção inválida!")