# Importa a função responsável por realizar a conexão com o banco de dados.
from database import conectar

# Importa a biblioteca time para utilizar pausas no sistema.
import time


# ---------------------------------------------------------------------------
# FUNÇÃO AUXILIAR
# ---------------------------------------------------------------------------

# Garante que o usuário digite apenas números inteiros.
def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


# ---------------------------------------------------------------------------
# LISTAR SETORES
# ---------------------------------------------------------------------------

# Lista todos os setores cadastrados.
def listar_setor():

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta SQL para listar todos os setores.
        sql = """
        SELECT
            id_setor,
            nome_setor,
            descricao_setor
        FROM Setores
        ORDER BY nome_setor ASC;
        """

        cursor.execute(sql)

        dados = cursor.fetchall()

        # Caso não existam setores cadastrados.
        if not dados:
            print("Nenhum setor cadastrado.")
            return

        # Exibe todos os setores.
        for id_setor, nome, descricao in dados:
            print(f"ID: {id_setor} | Nome: {nome} | Descrição: {descricao}")

    except Exception as erro:
        print("Erro ao listar setores:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# CADASTRAR SETOR
# ---------------------------------------------------------------------------

# Cria um novo setor.
def criar_setor(nome_setor, descricao_setor):

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Insere um novo setor.
        sql = """
        INSERT INTO Setores
            (nome_setor, descricao_setor)
        VALUES (%s, %s);
        """

        cursor.execute(sql, (nome_setor, descricao_setor))

        # Salva as alterações.
        conexao.commit()

        print("Setor cadastrado com sucesso!")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao criar setor:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# ATUALIZAR SETOR
# ---------------------------------------------------------------------------

# Atualiza os dados de um setor.
def atualizar_setor(id_setor, nome_setor, descricao_setor):

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Atualiza nome e descrição do setor.
        sql = """
        UPDATE Setores
        SET
            nome_setor = %s,
            descricao_setor = %s
        WHERE id_setor = %s;
        """

        cursor.execute(sql, (nome_setor, descricao_setor, id_setor))

        # Salva as alterações.
        conexao.commit()

        # Verifica se o setor existe.
        if cursor.rowcount > 0:
            print("Setor atualizado com sucesso!")
        else:
            print("Setor não encontrado.")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao atualizar setor:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# DELETAR SETOR
# ---------------------------------------------------------------------------

# Remove um setor do banco de dados.
def deletar_setor(id_setor):

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Exclui o setor informado.
        sql = "DELETE FROM Setores WHERE id_setor = %s;"

        cursor.execute(sql, (id_setor,))

        # Salva as alterações.
        conexao.commit()

        # Verifica se o setor foi encontrado.
        if cursor.rowcount > 0:
            print("Setor excluído com sucesso!")
        else:
            print("Setor não encontrado.")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao deletar setor (verifique se ainda há máquinas vinculadas a ele):", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# MENU DE SETORES
# ---------------------------------------------------------------------------

# Menu principal responsável pelas operações dos setores.
def opcao_desejada_setor():

    while True:

        # Exibe o menu de opções.
        print("\n------Menu Setor------")
        print("1 - Listar setor")
        print("2 - Criar setor")
        print("3 - Atualizar setor")
        print("4 - Deletar setor")
        print("0 - Sair")

        opcao_setor = ler_inteiro("Coloque qual opção deseja: ")

        # Lista todos os setores.
        if opcao_setor == 1:

            print("\n--- Lista de Setores ---")

            listar_setor()

            time.sleep(2)

        # Cadastra um novo setor.
        elif opcao_setor == 2:

            print("\n--- Criar Setor ---")

            nome = input("Nome do setor: ")

            descricao = input("Descrição do setor: ")

            criar_setor(nome, descricao)

        # Atualiza um setor existente.
        elif opcao_setor == 3:

            print("\n--- Atualizar Setor ---")

            id_setor = ler_inteiro("ID do setor: ")

            nome = input("Novo nome: ")

            descricao = input("Nova descrição: ")

            atualizar_setor(id_setor, nome, descricao)

        # Remove um setor.
        elif opcao_setor == 4:

            print("\n--- Deletar Setor ---")

            id_setor = ler_inteiro("ID do setor: ")

            deletar_setor(id_setor)

        # Sai do menu.
        elif opcao_setor == 0:

            print("Voltando")

            break

        # Caso seja digitada uma opção inválida.
        else:
            print("Opção inválida!")