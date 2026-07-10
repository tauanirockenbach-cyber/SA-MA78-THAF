from database import conectar
import time


def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


def qnt_maq_setores():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # Contagem direta em Maquinas: não precisa do join com Modelos_Maquinas,
        # que fazia a contagem depender de existir (ou não) um modelo cadastrado.
        sql = """
        SELECT S.nome_setor, COUNT(M.id_maquina)
        FROM Setores S
        LEFT JOIN Maquinas M ON M.id_setor = S.id_setor
        GROUP BY S.nome_setor;
        """
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum setor cadastrado.")
            return

        for nome_setor, quantidade in dados:
            print(f"Setor: {nome_setor} | Quantidade de Máquinas: {quantidade}")

    except Exception as erro:
        print("Erro ao contar máquinas por setor:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def listar_setor():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "SELECT id_setor, nome_setor, descricao_setor FROM Setores ORDER BY nome_setor ASC;"
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum setor cadastrado.")
            return

        for id_setor, nome, descricao in dados:
            print(f"ID: {id_setor} | Nome: {nome} | Descrição: {descricao}")

    except Exception as erro:
        print("Erro ao listar setores:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def criar_setor(nome_setor, descricao_setor):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "INSERT INTO Setores (nome_setor, descricao_setor) VALUES (%s, %s);"
        cursor.execute(sql, (nome_setor, descricao_setor))
        conexao.commit()

        print("Setor cadastrado com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao criar setor:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_setor(id_setor, nome_setor, descricao_setor):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "UPDATE Setores SET nome_setor = %s, descricao_setor = %s WHERE id_setor = %s;"
        cursor.execute(sql, (nome_setor, descricao_setor, id_setor))
        conexao.commit()

        if cursor.rowcount > 0:
            print("Setor atualizado com sucesso!")
        else:
            print("Setor não encontrado.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao atualizar setor:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def deletar_setor(id_setor):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Setores WHERE id_setor = %s;"
        cursor.execute(sql, (id_setor,))
        conexao.commit()

        if cursor.rowcount > 0:
            print("Setor excluído com sucesso!")
        else:
            print("Setor não encontrado.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        # Erro comum aqui: tentar deletar um setor que ainda tem máquinas
        # vinculadas (violação de chave estrangeira). Avisamos o usuário.
        print("Erro ao deletar setor (verifique se ainda há máquinas vinculadas a ele):", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def opcao_desejada_setor():
    while True:
        print("\n------Menu Setor------")
        print("1 = Listar setor")
        print("2 = Criar setor")
        print("3 = Atualizar setor")
        print("4 = Deletar setor")
        print("5 = Quantidade de maquina no setor")
        print("0 = Sair")

        opcao_setor = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_setor == 1:
            print("\n--- Lista de Setores ---")
            listar_setor()
            time.sleep(2)

        elif opcao_setor == 2:
            print("\n--- Criar Setor ---")
            nome = input("Nome do setor: ")
            descricao = input("Descrição do setor: ")
            criar_setor(nome, descricao)

        elif opcao_setor == 3:
            print("\n--- Atualizar Setor ---")
            id_setor = ler_inteiro("ID do setor: ")
            nome = input("Novo nome: ")
            descricao = input("Nova descrição: ")
            atualizar_setor(id_setor, nome, descricao)

        elif opcao_setor == 4:
            print("\n--- Deletar Setor ---")
            id_setor = ler_inteiro("ID do setor: ")
            deletar_setor(id_setor)

        elif opcao_setor == 5:
            print("\n--- Máquinas por Setor ---")
            qnt_maq_setores()

        elif opcao_setor == 0:
            print("Voltando")
            break

        else:
            print("Opção inválida!")