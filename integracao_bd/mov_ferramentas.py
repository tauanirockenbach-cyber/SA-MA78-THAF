# Importa a função responsável por conectar ao banco de dados
from database import conectar

# Importa a biblioteca time para utilizar pausas no sistema
import time


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

# Função que garante que o usuário digite apenas números inteiros.
def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


# Função que permite informar um número inteiro ou deixar o campo em branco.
# Caso fique em branco, retorna None.
def ler_inteiro_opcional(mensagem):
    while True:
        valor = input(mensagem)

        if valor.strip() == "":
            return None

        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números ou deixe em branco.")


# Função que permite informar um texto ou deixar o campo vazio.
# Caso fique vazio, retorna None.
def ler_texto_opcional(mensagem):
    valor = input(mensagem).strip()
    return valor if valor else None


# Função que verifica se a opção digitada pertence às opções permitidas.
def ler_opcao_valida(mensagem, opcoes_validas):
    while True:
        valor = input(mensagem)

        if valor.lower() in opcoes_validas:
            return valor

        print("Opção inválida!")


# ---------------------------------------------------------------------------
# CRUD - Movimentação de Ferramentas
# ---------------------------------------------------------------------------

# Lista todas as movimentações cadastradas.
def listar_movimentacoes():

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco de dados.
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta SQL para listar todas as movimentações.
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

        # Executa a consulta.
        cursor.execute(sql)

        # Obtém todos os registros encontrados.
        dados = cursor.fetchall()

        # Verifica se existem movimentações cadastradas.
        if not dados:
            print("Nenhuma movimentação cadastrada.")
            return

        # Exibe todas as movimentações.
        for movimentacao in dados:
            print(movimentacao)

    except Exception as erro:
        print("Erro ao listar movimentações:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Cadastra uma nova movimentação de ferramenta.
def cadastrar_movimentacao(id_os_ferramenta, id_os, id_usuario_solicitante,
                           id_usuario_entregador, data_retirada,
                           data_devolucao_prevista,status_movimentacao, observacoes):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Comando SQL responsável por cadastrar uma movimentação.
        sql = """
        INSERT INTO Movimentacao_Ferramentas
            (id_os_ferramenta, id_os, id_usuario_solicitante,
            id_usuario_entregador, data_retirada,
            data_devolucao_prevista, status_movimentacao, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Valores que serão enviados ao banco.
        valores = (
            id_os_ferramenta,
            id_os,
            id_usuario_solicitante,
            id_usuario_entregador,
            data_retirada,
            data_devolucao_prevista,
            status_movimentacao,
            observacoes
        )

        # Executa o INSERT.
        cursor.execute(sql, valores)

        # Salva as alterações.
        conexao.commit()

        print("Movimentação cadastrada com sucesso!")

    except Exception as erro:

        # Desfaz alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao cadastrar movimentação (verifique se os IDs informados existem):", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Atualiza o status de uma movimentação.
def atualizar_status(id_movimentacao, status_movimentacao):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Atualiza o status da movimentação.
        sql = """
        UPDATE Movimentacao_Ferramentas
        SET status_movimentacao = %s
        WHERE id_movimentacao = %s
        """

        valores = (status_movimentacao, id_movimentacao)

        cursor.execute(sql, valores)

        # Salva as alterações.
        conexao.commit()

        # Verifica se algum registro foi atualizado.
        if cursor.rowcount > 0:
            print(f"Status da movimentação {id_movimentacao} atualizado com sucesso!")
        else:
            print("Movimentação não encontrada.")

    except Exception as erro:

        # Desfaz alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao atualizar status da movimentação:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Registra a devolução de uma ferramenta.
def registrar_devolucao(id_movimentacao, data_devolucao_real):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Atualiza a data de devolução e altera automaticamente o status para Devolvido.
        sql = """
        UPDATE Movimentacao_Ferramentas
        SET
            data_devolucao_real = %s,
            status_movimentacao = 'Devolvido'
        WHERE id_movimentacao = %s
        """

        valores = (data_devolucao_real, id_movimentacao)

        cursor.execute(sql, valores)

        # Salva as alterações.
        conexao.commit()

        # Verifica se a movimentação existe.
        if cursor.rowcount > 0:
            print(f"Devolução da movimentação {id_movimentacao} registrada com sucesso!")
        else:
            print("Movimentação não encontrada.")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao registrar devolução:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Remove uma movimentação cadastrada.
def deletar_movimentacao(id_movimentacao):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Comando SQL responsável por excluir a movimentação.
        sql = "DELETE FROM Movimentacao_Ferramentas WHERE id_movimentacao = %s"

        cursor.execute(sql, (id_movimentacao,))

        # Confirma a exclusão.
        conexao.commit()

        # Verifica se algum registro foi removido.
        if cursor.rowcount > 0:
            print(f"Movimentação {id_movimentacao} deletada com sucesso!")
        else:
            print("Movimentação não encontrada.")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao deletar movimentação:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# Menu - Movimentação de Ferramentas
# ---------------------------------------------------------------------------

# Menu responsável pelas operações relacionadas às movimentações de ferramentas.
def opcao_desejada_movimentacao():

    # Lista de status permitidos.
    opcoes_status = ['solicitado', 'em uso', 'atrasado', 'devolvido']

    # Mantém o menu em execução até que o usuário escolha sair.
    while True:

        # Exibe o menu de opções.
        print("\n------ Menu Movimentação de Ferramentas ------")
        print("1 - Listar movimentações")
        print("2 - Cadastrar movimentação")
        print("3 - Atualizar status da movimentação")
        print("4 - Registrar devolução")
        print("5 - Deletar movimentação")
        print("0 - Sair")

        # Recebe a opção escolhida pelo usuário.
        opcao_movimentacao = ler_inteiro("Coloque qual opção deseja: ")

        # Lista todas as movimentações.
        if opcao_movimentacao == 1:
            print("\n--- Lista de Movimentações ---")
            listar_movimentacoes()
            time.sleep(2)

        # Cadastra uma nova movimentação.
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

            data_devolucao_prevista = input(
                "Data de devolução prevista (AAAA-MM-DD HH:MM:SS): "
            )

            observacoes = ler_texto_opcional("Observações (opcional): ")

            cadastrar_movimentacao(
                id_os_ferramenta,
                id_os,
                id_usuario_solicitante,
                id_usuario_entregador,
                data_retirada,
                data_devolucao_prevista,
                observacoes
            )

        # Atualiza o status de uma movimentação.
        elif opcao_movimentacao == 3:
            print("\n--- Atualizar Status da Movimentação ---")

            id_m = ler_inteiro("Digite o ID da movimentação que deseja atualizar: ")

            status = ler_opcao_valida(
                "Novo status (Solicitado, Em Uso, Atrasado, Devolvido): ",
                opcoes_status
            )

            atualizar_status(id_m, status)

        # Registra a devolução de uma ferramenta.
        elif opcao_movimentacao == 4:
            print("\n--- Registrar Devolução ---")

            id_m = ler_inteiro("Digite o ID da movimentação a ser devolvida: ")

            data_devolucao_real = input(
                "Data de devolução real (AAAA-MM-DD HH:MM:SS): "
            )

            registrar_devolucao(id_m, data_devolucao_real)

        # Exclui uma movimentação.
        elif opcao_movimentacao == 5:
            print("\n--- Deletar Movimentação ---")

            id_m = ler_inteiro("Digite o ID da movimentação que deseja deletar: ")

            deletar_movimentacao(id_m)

        # Retorna ao menu principal.
        elif opcao_movimentacao == 0:
            print("Voltando...")
            break

        # Caso seja digitada uma opção inválida.
        else:
            print("Opção inválida!")