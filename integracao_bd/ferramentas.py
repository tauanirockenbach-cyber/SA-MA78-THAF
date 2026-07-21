# Importa a função responsável por conectar ao banco de dados
from database import conectar

# Importa a biblioteca time para utilizar pausas no programa
import time


# Função que garante que o usuário digite apenas números inteiros
def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


# Função que valida se a opção digitada está entre as opções permitidas
def ler_opcao_valida(mensagem, opcoes_validas):
    while True:
        valor = input(mensagem)
        if valor.lower() in opcoes_validas:
            return valor
        print("Opção inválida!")


# Função responsável por listar todas as ferramentas cadastradas
def listar_ferramentas():
    conexao = None
    cursor = None
    try:
        # Abre conexão com o banco de dados
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta SQL para buscar as ferramentas cadastradas
        sql = """
        SELECT
            id_ferramenta, nome_ferramenta, status_ferramenta
        FROM Almoxarifado_Ferramentas
        """

        # Executa a consulta
        cursor.execute(sql)

        # Armazena todos os registros encontrados
        dados = cursor.fetchall()

        # Caso não existam ferramentas cadastradas
        if not dados:
            print("Nenhuma ferramenta cadastrada.")
            return

        # Exibe cada ferramenta encontrada
        for ferramenta in dados:
            print(ferramenta)

    except Exception as erro:
        print("Erro ao listar ferramentas:", erro)

    finally:
        # Fecha o cursor
        if cursor:
            cursor.close()

        # Fecha a conexão com o banco
        if conexao:
            conexao.close()


# Função responsável por cadastrar uma nova ferramenta
def cadastrar_ferramenta(nome_ferramenta, status_ferramenta):
    conexao = None
    cursor = None
    try:
        # Abre conexão com o banco
        conexao = conectar()
        cursor = conexao.cursor()

        # O ID é AUTO_INCREMENT, portanto não precisa ser informado
        sql = """
        INSERT INTO Almoxarifado_Ferramentas
            (nome_ferramenta, status_ferramenta)
        VALUES (%s, %s)
        """

        # Valores que serão inseridos
        valores = (nome_ferramenta, status_ferramenta)

        # Executa o INSERT
        cursor.execute(sql, valores)

        # Salva as alterações no banco
        conexao.commit()

        print(f"Ferramenta {nome_ferramenta} cadastrada com sucesso!")

    except Exception as erro:
        # Cancela as alterações caso ocorra algum erro
        if conexao:
            conexao.rollback()

        print("Erro ao cadastrar ferramenta:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Função responsável por atualizar o status de uma ferramenta
def atualizar_status(id_ferramenta, status_ferramenta):
    conexao = None
    cursor = None
    try:
        # Abre conexão com o banco
        conexao = conectar()
        cursor = conexao.cursor()

        # Comando SQL para atualizar o status da ferramenta
        sql = """
        UPDATE Almoxarifado_Ferramentas
        SET status_ferramenta = %s
        WHERE id_ferramenta = %s
        """

        # Ordem dos valores deve ser igual à ordem dos %s da consulta SQL
        valores = (status_ferramenta, id_ferramenta)

        # Executa o UPDATE
        cursor.execute(sql, valores)

        # Salva as alterações
        conexao.commit()

        # Verifica se alguma linha foi alterada
        if cursor.rowcount > 0:
            print(f"Status da ferramenta {id_ferramenta} atualizado com sucesso!")
        else:
            print("Ferramenta não encontrada.")

    except Exception as erro:
        # Desfaz alterações caso ocorra erro
        if conexao:
            conexao.rollback()

        print("Erro ao atualizar status da ferramenta:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Função responsável por excluir uma ferramenta pelo ID
def deletar_ferramenta(id_ferramenta):
    conexao = None
    cursor = None
    try:
        # Abre conexão com o banco
        conexao = conectar()
        cursor = conexao.cursor()

        # Comando SQL para excluir a ferramenta
        sql = "DELETE FROM Almoxarifado_Ferramentas WHERE id_ferramenta = %s"

        # Executa o DELETE
        cursor.execute(sql, (id_ferramenta,))

        # Salva as alterações
        conexao.commit()

        # Verifica se alguma linha foi removida
        if cursor.rowcount > 0:
            print(f"Ferramenta {id_ferramenta} deletada com sucesso!")
        else:
            print("Ferramenta não encontrada.")

    except Exception as erro:
        # Desfaz alterações caso ocorra erro
        if conexao:
            conexao.rollback()

        print("Erro ao deletar ferramenta:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Menu principal do CRUD de ferramentas
def opcao_desejada_ferramenta():

    # Lista contendo todos os status permitidos
    opcoes_status = [
        'disponível',
        'solicitada',
        'em uso',
        'manutenção/calibração',
        'extraviada'
    ]

    # Mantém o menu em execução até que o usuário escolha sair
    while True:

        # Exibe o menu de opções
        print("\n------ Menu Ferramentas ------")
        print("1 - Listar ferramentas")
        print("2 - Cadastrar ferramenta")
        print("3 - Atualizar status da ferramenta")
        print("4 - Deletar ferramenta")
        print("0 - Sair")

        # Recebe a opção escolhida
        opcao_ferramenta = ler_inteiro("Coloque qual opção deseja: ")

        # Lista todas as ferramentas
        if opcao_ferramenta == 1:
            print("\n--- Lista de Ferramentas ---")

            listar_ferramentas()

            # Aguarda 2 segundos antes de voltar ao menu
            time.sleep(2)

        # Cadastra uma nova ferramenta
        elif opcao_ferramenta == 2:
            print("\n--- Cadastrar Ferramenta ---")

            nome = input("Nome da ferramenta: ")

            # Solicita um status válido
            status = ler_opcao_valida(
                "Status (Disponível, Solicitada, Em Uso, Manutenção/Calibração, Extraviada): ",
                opcoes_status
            )

            cadastrar_ferramenta(nome, status)

        # Atualiza o status de uma ferramenta existente
        elif opcao_ferramenta == 3:
            print("\n--- Atualizar Status da Ferramenta ---")

            id_f = ler_inteiro("Digite o ID da ferramenta que deseja atualizar: ")

            # Solicita o novo status
            status = ler_opcao_valida(
                "Novo status (Disponível, Solicitada, Em Uso, Manutenção/Calibração, Extraviada): ",
                opcoes_status
            )

            atualizar_status(id_f, status)

        # Exclui uma ferramenta
        elif opcao_ferramenta == 4:
            print("\n--- Deletar Ferramenta ---")

            id_f = ler_inteiro("Digite o ID da ferramenta que deseja deletar: ")

            deletar_ferramenta(id_f)

        # Encerra o menu
        elif opcao_ferramenta == 0:
            print("Voltando...")
            break

        # Caso o usuário digite uma opção inexistente
        else:
            print("Opção inválida!")