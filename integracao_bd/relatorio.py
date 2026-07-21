from database import conectar
import time


# -----------------------------------------------------------------------------
# Lê um número inteiro informado pelo usuário.
# Enquanto um valor inválido for digitado, solicita novamente.
# -----------------------------------------------------------------------------
def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


# -----------------------------------------------------------------------------
# Relatório de quantidade de Ordens de Serviço (OS) por setor.
# -----------------------------------------------------------------------------
def relatorio_producao_por_setor():
    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco
        conexao = conectar()
        cursor = conexao.cursor()

        # Conta quantas OS existem por setor, através das máquinas vinculadas
        sql = """
        SELECT
            S.nome_setor,
            COUNT(O.id_os) AS total_os
        FROM Setores S
        LEFT JOIN Maquinas M
            ON M.id_setor = S.id_setor
        LEFT JOIN Ordens_Servico O
            ON O.tag_equipamento = M.tag_equipamento
        GROUP BY S.nome_setor
        ORDER BY total_os DESC
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        # Verifica se existem setores cadastrados
        if not dados:
            print("Nenhum setor cadastrado.")
            return

        # Exibe o relatório
        for nome_setor, total_os in dados:
            print(f"\nSetor: {nome_setor}")
            print(f"Total de OS: {total_os}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao gerar relatório de OS por setor:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# Relatório de quantidade de máquinas por setor.
# -----------------------------------------------------------------------------
def qnt_maq_setores():
    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco de dados
        conexao = conectar()
        cursor = conexao.cursor()

        # Conta quantas máquinas existem em cada setor
        # O LEFT JOIN garante que setores sem máquinas também sejam exibidos
        sql = """
        SELECT
            S.nome_setor,
            COUNT(M.id_maquina)
        FROM Setores S
        LEFT JOIN Maquinas M
            ON M.id_setor = S.id_setor
        GROUP BY S.nome_setor
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        # Verifica se existem setores cadastrados
        if not dados:
            print("Nenhum setor cadastrado.")
            return

        # Exibe o nome do setor e sua quantidade de máquinas
        for nome_setor, quantidade in dados:
            print(f"Setor: {nome_setor} | Quantidade de Máquinas: {quantidade}")

    except Exception as erro:
        print("Erro ao contar máquinas por setor:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# Menu principal de relatórios.
# -----------------------------------------------------------------------------
def opcao_desejada_relatorio():

    while True:
        # Exibe o menu de opções
        print("\n------ Menu Relatórios ------")
        print("1 - Relatório de OS por Setor")
        print("2 - Quantidade de Máquinas por Setor")
        print("0 - Sair")

        # Lê a opção escolhida
        opcao_relatorio = ler_inteiro("Coloque qual opção deseja: ")

        # ---------------------------------------------------------------------
        # Relatório de OS por setor
        # ---------------------------------------------------------------------
        if opcao_relatorio == 1:
            print("\n--- Relatório de OS por Setor ---")
            relatorio_producao_por_setor()
            time.sleep(2)

        # ---------------------------------------------------------------------
        # Relatório de máquinas por setor
        # ---------------------------------------------------------------------
        elif opcao_relatorio == 2:
            print("\n--- Máquinas por Setor ---")
            qnt_maq_setores()
            time.sleep(2)

        # ---------------------------------------------------------------------
        # Encerra o menu
        # ---------------------------------------------------------------------
        elif opcao_relatorio == 0:
            print("Voltando...")
            break

        # ---------------------------------------------------------------------
        # Caso seja digitada uma opção inexistente
        # ---------------------------------------------------------------------
        else:
            print("Opção inválida!")