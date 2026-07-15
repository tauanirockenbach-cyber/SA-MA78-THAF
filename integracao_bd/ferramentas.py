from database import conectar
import time


def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


def ler_opcao_valida(mensagem, opcoes_validas):
    while True:
        valor = input(mensagem)
        if valor.lower() in opcoes_validas:
            return valor
        print("Opção inválida!")


def listar_ferramentas():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT
            id_ferramenta, nome_ferramenta, status_ferramenta
        FROM Almoxarifado_Ferramentas
        """
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma ferramenta cadastrada.")
            return

        for ferramenta in dados:
            print(ferramenta)

    except Exception as erro:
        print("Erro ao listar ferramentas:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def cadastrar_ferramenta(nome_ferramenta, status_ferramenta):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # id_ferramenta é AUTO_INCREMENT, não precisa ser informado
        sql = """
        INSERT INTO Almoxarifado_Ferramentas
            (nome_ferramenta, status_ferramenta)
        VALUES (%s, %s)
        """
        valores = (nome_ferramenta, status_ferramenta)

        cursor.execute(sql, valores)
        conexao.commit()

        print(f"Ferramenta {nome_ferramenta} cadastrada com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao cadastrar ferramenta:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_status(id_ferramenta, status_ferramenta):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        UPDATE Almoxarifado_Ferramentas
        SET status_ferramenta = %s
        WHERE id_ferramenta = %s
        """
        # a ordem dos valores precisa bater com a ordem dos %s no SQL
        valores = (status_ferramenta, id_ferramenta)
        cursor.execute(sql, valores)
        conexao.commit()

        if cursor.rowcount > 0:
            print(f"Status da ferramenta {id_ferramenta} atualizado com sucesso!")
        else:
            print("Ferramenta não encontrada.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao atualizar status da ferramenta:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def deletar_ferramenta(id_ferramenta):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Almoxarifado_Ferramentas WHERE id_ferramenta = %s"
        cursor.execute(sql, (id_ferramenta,))
        conexao.commit()

        if cursor.rowcount > 0:
            print(f"Ferramenta {id_ferramenta} deletada com sucesso!")
        else:
            print("Ferramenta não encontrada.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao deletar ferramenta:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def opcao_desejada_ferramenta():
    opcoes_status = [
        'disponível', 'solicitada', 'em uso',
        'manutenção/calibração', 'extraviada'
    ]

    while True:
        print("\n------ Menu Ferramentas ------")
        print("1 - Listar ferramentas")
        print("2 - Cadastrar ferramenta")
        print("3 - Atualizar status da ferramenta")
        print("4 - Deletar ferramenta")
        print("0 - Sair")

        opcao_ferramenta = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_ferramenta == 1:
            print("\n--- Lista de Ferramentas ---")
            listar_ferramentas()
            time.sleep(2)

        elif opcao_ferramenta == 2:
            print("\n--- Cadastrar Ferramenta ---")
            nome = input("Nome da ferramenta: ")
            status = ler_opcao_valida(
                "Status (Disponível, Solicitada, Em Uso, Manutenção/Calibração, Extraviada): ",
                opcoes_status
            )

            cadastrar_ferramenta(nome, status)

        elif opcao_ferramenta == 3:
            print("\n--- Atualizar Status da Ferramenta ---")
            id_f = ler_inteiro("Digite o ID da ferramenta que deseja atualizar: ")
            status = ler_opcao_valida(
                "Novo status (Disponível, Solicitada, Em Uso, Manutenção/Calibração, Extraviada): ",
                opcoes_status
            )

            atualizar_status(id_f, status)

        elif opcao_ferramenta == 4:
            print("\n--- Deletar Ferramenta ---")
            id_f = ler_inteiro("Digite o ID da ferramenta que deseja deletar: ")
            deletar_ferramenta(id_f)

        elif opcao_ferramenta == 0:
            print("Voltando...")
            break

        else:
            print("Opção inválida!")