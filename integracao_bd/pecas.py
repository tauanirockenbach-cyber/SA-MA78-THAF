# Importa a função responsável por realizar a conexão com o banco de dados.
from database import conectar


# ---------------------------------------------------------------------------
# LISTAR PEÇAS
# ---------------------------------------------------------------------------

# Lista todas as peças cadastradas no almoxarifado.
def listar_pecas():

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta SQL para listar todas as peças.
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

        # Armazena os registros encontrados.
        dados = cursor.fetchall()

        # Caso não exista nenhuma peça cadastrada.
        if not dados:
            print("Nenhuma peça cadastrada.")
            return

        # Exibe todas as peças.
        for peca in dados:
            print(peca)

    except Exception as erro:
        print("Erro ao listar peças:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# CADASTRAR PEÇA
# ---------------------------------------------------------------------------

# Cadastra uma nova peça no banco de dados.
def cadastrar_peca(nome_peca, quantidade_estoque, unidade_medida, custo_unitario):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Insere uma nova peça.
        # O campo id_peca é AUTO_INCREMENT e não precisa ser informado.
        sql = """
        INSERT INTO Almoxarifado_Pecas
            (nome_peca, quantidade_estoque, unidade_medida, custo_unitario)
        VALUES (%s, %s, %s, %s)
        """

        valores = (
            nome_peca,
            quantidade_estoque,
            unidade_medida,
            custo_unitario
        )

        cursor.execute(sql, valores)

        # Salva as alterações.
        conexao.commit()

        print(f"Peça '{nome_peca}' cadastrada com sucesso! (ID gerado: {cursor.lastrowid})")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao cadastrar peça (verifique nome duplicado ou valores negativos):", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# ATUALIZAR QUANTIDADE EM ESTOQUE
# ---------------------------------------------------------------------------

# Atualiza a quantidade disponível de uma peça.
def atualizar_quantidade_estoque(id_peca, quantidade_estoque):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Atualiza a quantidade em estoque.
        sql = """
        UPDATE Almoxarifado_Pecas
        SET quantidade_estoque = %s
        WHERE id_peca = %s
        """

        valores = (
            quantidade_estoque,
            id_peca
        )

        cursor.execute(sql, valores)

        # Salva as alterações.
        conexao.commit()

        # Verifica se a peça existe.
        if cursor.rowcount > 0:
            print(f"Quantidade da peça {id_peca} atualizada com sucesso!")
        else:
            print("Peça não encontrada.")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao atualizar quantidade (verifique se o valor não é negativo):", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# DELETAR PEÇA
# ---------------------------------------------------------------------------

# Remove uma peça do banco de dados.
def deletar_peca(id_peca):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Exclui a peça pelo ID.
        sql = "DELETE FROM Almoxarifado_Pecas WHERE id_peca = %s"

        cursor.execute(sql, (id_peca,))

        # Salva as alterações.
        conexao.commit()

        # Verifica se a peça foi encontrada.
        if cursor.rowcount > 0:
            print(f"Peça {id_peca} deletada com sucesso!")
        else:
            print("Peça não encontrada.")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao deletar peça:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ---------------------------------------------------------------------------

# Lê apenas números inteiros.
def ler_inteiro(mensagem):

    while True:

        valor = input(mensagem)

        try:
            return int(valor)

        except ValueError:
            print("Digite apenas números.")


# Lê apenas números decimais.
def ler_float(mensagem):

    while True:

        valor = input(mensagem)

        try:
            return float(valor)

        except ValueError:
            print("Digite apenas números (use ponto para decimais).")


# ---------------------------------------------------------------------------
# MENU DE PEÇAS
# ---------------------------------------------------------------------------

# Menu principal responsável pelas operações de peças.
def opcao_desejada_peca():

    while True:

        # Exibe o menu.
        print("\n------ Menu Peças ------")
        print("1 - Listar peças")
        print("2 - Criar peça")
        print("3 - Atualizar quantidade em estoque")
        print("4 - Deletar peça")
        print("0 - Sair")

        opcao_peca = ler_inteiro("Coloque qual opção deseja: ")

        # Lista todas as peças.
        if opcao_peca == 1:

            print("\n--- Lista de Peças ---")

            listar_pecas()

        # Cadastra uma nova peça.
        elif opcao_peca == 2:

            print("\n--- Criar Peça ---")

            nome_peca = input("Nome da Peça: ")

            quantidade_estoque = ler_inteiro("Quantidade em Estoque: ")

            unidade_medida = input(
                "Unidade de Medida (padrão: Unidade): "
            ) or "Unidade"

            custo_unitario = ler_float("Custo Unitário: ")

            cadastrar_peca(
                nome_peca,
                quantidade_estoque,
                unidade_medida,
                custo_unitario
            )

        # Atualiza a quantidade em estoque.
        elif opcao_peca == 3:

            print("\n--- Atualizar Quantidade em Estoque ---")

            id_peca = ler_inteiro(
                "Digite o ID da peça que deseja atualizar: "
            )

            quantidade_estoque = ler_inteiro(
                "Nova Quantidade em Estoque: "
            )

            atualizar_quantidade_estoque(
                id_peca,
                quantidade_estoque
            )

        # Remove uma peça.
        elif opcao_peca == 4:

            print("\n--- Deletar Peça ---")

            id_peca = ler_inteiro(
                "Digite o ID da peça que deseja deletar: "
            )

            deletar_peca(id_peca)

        # Sai do menu.
        elif opcao_peca == 0:

            print("Voltando...")

            break

        # Caso o usuário digite uma opção inválida.
        else:
            print("Opção inválida!")