from database import conectar


def listar_pecas():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT
            p.id_peca,
            p.nome_peca,
            p.quantidade_estoque,
            p.unidade_medida,
            p.custo_unitario
        FROM Almoxarifado_Pecas AS p
        """
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma peça cadastrada.")
            return

        for peca in dados:
            print(peca)

    except Exception as erro:
        print("Erro ao listar peças:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def cadastrar_peca(nome_peca, quantidade_estoque, unidade_medida, custo_unitario):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # id_peca é AUTO_INCREMENT, não deve ser passado no INSERT
        sql = """
        INSERT INTO Almoxarifado_Pecas
            (nome_peca, quantidade_estoque, unidade_medida, custo_unitario)
        VALUES (%s, %s, %s, %s)
        """
        valores = (nome_peca, quantidade_estoque, unidade_medida, custo_unitario)

        cursor.execute(sql, valores)
        conexao.commit()

        print(f"Peça '{nome_peca}' cadastrada com sucesso! (ID gerado: {cursor.lastrowid})")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        # nome_peca é UNIQUE: erro comum aqui é tentar cadastrar um nome já existente.
        # Também pode falhar se quantidade_estoque < 0 ou custo_unitario < 0.00 (CHECK constraints).
        print("Erro ao cadastrar peça (verifique nome duplicado ou valores negativos):", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_quantidade_estoque(id_peca, quantidade_estoque):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        UPDATE Almoxarifado_Pecas
        SET quantidade_estoque = %s
        WHERE id_peca = %s
        """
        valores = (quantidade_estoque, id_peca)
        cursor.execute(sql, valores)
        conexao.commit()

        if cursor.rowcount > 0:
            print(f"Quantidade da peça {id_peca} atualizada com sucesso!")
        else:
            print("Peça não encontrada.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        # Pode falhar se quantidade_estoque for negativa (CHECK constraint)
        print("Erro ao atualizar quantidade (verifique se o valor não é negativo):", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def deletar_peca(id_peca):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Almoxarifado_Pecas WHERE id_peca = %s"
        cursor.execute(sql, (id_peca,))
        conexao.commit()

        if cursor.rowcount > 0:
            print(f"Peça {id_peca} deletada com sucesso!")
        else:
            print("Peça não encontrada.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao deletar peça:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


def ler_float(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return float(valor)
        except ValueError:
            print("Digite apenas números (use ponto para decimais).")


def opcao_desejada_peca():
    while True:
        print("\n------ Menu Peças ------")
        print("1 - Listar peças")
        print("2 - Criar peça")
        print("3 - Atualizar quantidade em estoque")
        print("4 - Deletar peça")
        print("0 - Sair")

        opcao_peca = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_peca == 1:
            print("\n--- Lista de Peças ---")
            listar_pecas()

        elif opcao_peca == 2:
            print("\n--- Criar Peça ---")
            nome_peca = input("Nome da Peça: ")
            quantidade_estoque = ler_inteiro("Quantidade em Estoque: ")
            unidade_medida = input("Unidade de Medida (padrão: Unidade): ") or "Unidade"
            custo_unitario = ler_float("Custo Unitário: ")

            cadastrar_peca(nome_peca, quantidade_estoque, unidade_medida, custo_unitario)

        elif opcao_peca == 3:
            print("\n--- Atualizar Quantidade em Estoque ---")
            id_peca = ler_inteiro("Digite o ID da peça que deseja atualizar: ")
            quantidade_estoque = ler_inteiro("Nova Quantidade em Estoque: ")

            atualizar_quantidade_estoque(id_peca, quantidade_estoque)

        elif opcao_peca == 4:
            print("\n--- Deletar Peça ---")
            id_peca = ler_inteiro("Digite o ID da peça que deseja deletar: ")
            deletar_peca(id_peca)

        elif opcao_peca == 0:
            print("Voltando...")
            break

        else:
            print("Opção inválida!")
    